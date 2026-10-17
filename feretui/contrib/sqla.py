# This file is a part of the FeretUI project
#
#    Copyright (C) 2026 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""SQLAlchemy ORM integration for FeretUI."""

from collections.abc import Iterator
from contextlib import AbstractContextManager, contextmanager, suppress
from typing import TYPE_CHECKING, Any

from wtforms.fields import (
    BooleanField,
    DateField,
    DateTimeField,
    Field,
    FloatField,
    HiddenField,
    IntegerField,
    StringField,
    TextAreaField,
)
from wtforms.validators import DataRequired

from feretui.exceptions import ResourceError
from feretui.form import FeretUIForm
from feretui.resources import LCRUDResource
from feretui.resources.resource import Resource

try:
    from sqlalchemy import (
        Boolean,
        Date,
        DateTime,
        Float,
        Integer,
        Numeric,
        Text,
        delete,
        func,
        inspect,
        select,
    )
except ImportError as err:  # pragma: no cover
    raise ImportError(
        "sqlalchemy is missing => pip install feretui[sqla]",
    ) from err

if TYPE_CHECKING:
    from feretui.feretui import FeretUI  # noqa: F401


def _column_to_field(col: object) -> Field:
    """Map a SQLAlchemy column to a WTForms field."""
    validators = []
    if not col.nullable and not col.primary_key and col.default is None:
        validators.append(DataRequired())

    label = col.name.replace("_", " ").title()

    if isinstance(col.type, Boolean):
        return BooleanField(label, validators=validators)
    if isinstance(col.type, Integer):
        return IntegerField(label, validators=validators)
    if isinstance(col.type, Numeric | Float):
        return FloatField(label, validators=validators)
    if isinstance(col.type, DateTime):
        return DateTimeField(label, validators=validators)
    if isinstance(col.type, Date):
        return DateField(label, validators=validators)
    if isinstance(col.type, Text):
        return TextAreaField(label, validators=validators)
    return StringField(label, validators=validators)


def model_to_form(
    model: type[Any],
    base_form: type[FeretUIForm] = FeretUIForm,
    exclude: set[str] | list[str] | None = None,
) -> type[FeretUIForm]:
    """Generate a WTForms Form from a SQLAlchemy declarative model.

    :param model: SQLAlchemy declarative model class
    :type model: type
    :param base_form: Base form class
    :type base_form: type[:class:`feretui.form.FeretUIForm`]
    :param exclude: Set of column names to exclude
    :type exclude: set[str] | list[str] | None
    :return: A generated FeretUIForm subclass
    :rtype: type[:class:`feretui.form.FeretUIForm`]
    """
    exclude_set = set(exclude or [])
    fields: dict[str, Any] = (
        {
            key: val
            for key, val in getattr(base_form, "__dict__", {}).items()
            if not key.startswith("_") and key != "Meta"
        }
        if base_form and base_form is not FeretUIForm
        else {}
    )

    mapper = inspect(model)

    if "pk" not in fields:
        fields["pk"] = HiddenField("ID")

    for col in mapper.columns:
        if col.name in exclude_set or col.name in fields:
            continue
        fields[col.name] = _column_to_field(col)

    form_name = f"{model.__name__}AutoForm"
    if base_form is None or not issubclass(base_form, FeretUIForm):
        actual_bases = (FeretUIForm,)
    else:
        actual_bases = (base_form,)

    return type(form_name, actual_bases, fields)


class SQLAlchemyResource(LCRUDResource, Resource):
    """Semi-automatic CRUD generation from SQLAlchemy Declarative models."""

    model: type[Any] | None = None
    session_factory: Any | None = None
    primary_key_attr: str | None = None

    def get_db_session(
        self: "SQLAlchemyResource",
    ) -> AbstractContextManager[object]:
        """Return a SQLAlchemy session or context manager."""
        factory = self.session_factory
        res = factory() if callable(factory) else factory

        if hasattr(res, "__enter__"):
            return res

        @contextmanager
        def _cm() -> Iterator[object]:
            yield res

        return _cm()

    @classmethod
    def get_primary_key_attr(cls: type["SQLAlchemyResource"]) -> str:
        """Get the primary key attribute name from model or configuration."""
        if cls.primary_key_attr:
            return cls.primary_key_attr

        if cls.model:
            mapper = inspect(cls.model)
            pks = [c.name for c in mapper.primary_key]
            if pks:
                return pks[0]

        return "id"

    @classmethod
    def build(cls: type["SQLAlchemyResource"]) -> Resource:
        """Automatically create the Form if not provided."""
        if cls.model:
            existing_form = getattr(cls, "Form", None)
            has_custom_fields = bool(
                existing_form
                and hasattr(existing_form, "__dict__")
                and any(not k.startswith("_") for k in existing_form.__dict__),
            )
            if not has_custom_fields:
                cls.Form = model_to_form(
                    cls.model,
                    base_form=existing_form or FeretUIForm,
                )

        return super().build()

    def get_pk(self: "SQLAlchemyResource", instance: object) -> str:
        """Return string representation of the primary key of an instance."""
        pk_attr = self.get_primary_key_attr()
        return str(getattr(instance, pk_attr))

    def filtered_reads(
        self: "SQLAlchemyResource",
        form_cls: type[FeretUIForm],
        filters: list[tuple[str, list[str]]],
        offset: int,
        limit: int,
    ) -> dict[str, Any]:
        """Fetch filtered records, count, and return dataset."""
        if not self.model:
            return {"total": 0, "forms": []}

        with self.get_db_session() as db:
            query = select(self.model)

            for field_name, values in filters:
                if hasattr(self.model, field_name) and values:
                    col = getattr(self.model, field_name)
                    if len(values) == 1:
                        query = query.where(col == values[0])
                    else:
                        query = query.where(col.in_(values))

            count_query = select(func.count()).select_from(query.subquery())
            total = db.scalar(count_query) or 0

            query = query.offset(offset).limit(limit)
            instances = db.scalars(query).all()

            forms = []
            for inst in instances:
                data = {"pk": self.get_pk(inst)}
                for col_name in form_cls()._fields:
                    if col_name == "pk":
                        continue
                    if hasattr(inst, col_name):
                        data[col_name] = getattr(inst, col_name)

                forms.append(form_cls(data=data))

            return {"total": total, "forms": forms}

    def create(self: "SQLAlchemyResource", form: FeretUIForm) -> str:
        """Create a new model instance from form data."""
        if not self.model:
            raise ResourceError("No model configured for SQLAlchemyResource")

        with self.get_db_session() as db:
            inst = self.model()
            pk_attr = self.get_primary_key_attr()
            for name, field in form._fields.items():
                if name == "pk":
                    if field.data is not None and not getattr(
                        inst,
                        pk_attr,
                        None,
                    ):
                        setattr(inst, pk_attr, field.data)
                elif hasattr(self.model, name) and field.data is not None:
                    setattr(inst, name, field.data)

            db.add(inst)
            db.commit()
            return self.get_pk(inst)

    def read(
        self: "SQLAlchemyResource",
        form_cls: type[FeretUIForm],
        pk: str,
    ) -> FeretUIForm:
        """Read a record by primary key."""
        if not self.model:
            raise ResourceError("No model configured for SQLAlchemyResource")

        with self.get_db_session() as db:
            pk_attr = self.get_primary_key_attr()
            col = getattr(self.model, pk_attr)
            inst = db.scalar(select(self.model).where(col == pk))
            if not inst:
                with suppress(ValueError, TypeError):
                    inst = db.scalar(select(self.model).where(col == int(pk)))

            if not inst:
                raise ResourceError(f"{self.model.__name__}[{pk}] not found")

            data = {"pk": str(pk)}
            for col_name in form_cls()._fields:
                if col_name != "pk" and hasattr(inst, col_name):
                    data[col_name] = getattr(inst, col_name)

            return form_cls(data=data)

    def update(
        self: "SQLAlchemyResource",
        forms: list[FeretUIForm],
    ) -> None:
        """Update model instances from form data."""
        if not self.model:
            raise ResourceError("No model configured for SQLAlchemyResource")

        with self.get_db_session() as db:
            pk_attr = self.get_primary_key_attr()
            col = getattr(self.model, pk_attr)
            for form in forms:
                pk = form.pk.data
                inst = db.scalar(select(self.model).where(col == pk))
                if not inst:
                    with suppress(ValueError, TypeError):
                        inst = db.scalar(
                            select(self.model).where(col == int(pk)),
                        )

                if inst:
                    for name, field in form._fields.items():
                        if (
                            name not in ("pk", pk_attr)
                            and hasattr(self.model, name)
                            and field.data is not None
                        ):
                            setattr(inst, name, field.data)

            db.commit()

    def delete(self: "SQLAlchemyResource", pks: list[str]) -> None:
        """Delete model instances by primary keys."""
        if not self.model:
            raise ResourceError("No model configured for SQLAlchemyResource")

        with self.get_db_session() as db:
            pk_attr = self.get_primary_key_attr()
            col = getattr(self.model, pk_attr)
            cast_pks: list[Any] = []
            for pk in pks:
                cast_pks.append(pk)
                with suppress(ValueError, TypeError):
                    cast_pks.append(int(pk))

            stmt = delete(self.model).where(col.in_(cast_pks))
            db.execute(stmt)
            db.commit()

    def move_card(
        self: "SQLAlchemyResource",
        pk: str,
        stage: str,
        index: int | None = None,  # noqa: ARG002
    ) -> None:
        """Update card stage when dragged in Kanban view."""
        if not self.model:
            raise ResourceError("No model configured for SQLAlchemyResource")

        with self.get_db_session() as db:
            pk_attr = self.get_primary_key_attr()
            col = getattr(self.model, pk_attr)
            inst = db.scalar(select(self.model).where(col == pk))
            if not inst:
                with suppress(ValueError, TypeError):
                    inst = db.scalar(select(self.model).where(col == int(pk)))

            if inst:
                col_field = "status"
                if hasattr(self, "views") and "kanban" in self.views:
                    col_field = getattr(
                        self.views["kanban"],
                        "column_field",
                        "status",
                    )
                if hasattr(inst, col_field):
                    setattr(inst, col_field, stage)
                elif hasattr(inst, "stage"):
                    inst.stage = stage

                db.commit()
