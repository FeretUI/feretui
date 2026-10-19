# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Module feretui.resources.kanban.

The Kanban resource displays data as cards grouped by stage columns.

* :class:`.KanbanView`
* :class:`.KResource`
"""

from typing import TYPE_CHECKING, Any

from markupsafe import Markup

from feretui.exceptions import ResourceError
from feretui.form import FeretUIForm
from feretui.request import Request
from feretui.resources.common import LabelMixinForView, MultiView
from feretui.resources.view import View, view_action_validator
from feretui.response import Response
from feretui.session import Session

from .resource import Resource

if TYPE_CHECKING:
    from feretui.feretui import FeretUI


class DefaultViewKanban:
    """Default value for the view kanban."""

    label: str = None
    limit: int = 200
    create_button_redirect_to: str = None
    delete_button_redirect_to: str = None
    do_click_on_entry_redirect_to: str = None
    column_field: str = "status"
    columns: list[tuple[str, str]] | None = None
    card_title_field: str | None = None
    card_body_fields: list[str] | None = None


class KanbanView(MultiView, LabelMixinForView, View):
    """Kanban view for ERP-style cards grouped by stages."""

    code: str = "kanban"
    limit: int = 200
    create_button_redirect_to: str = None
    delete_button_redirect_to: str = None
    do_click_on_entry_redirect_to: str = None
    column_field: str = "status"
    columns: list[tuple[str, str]] | None = None
    card_title_field: str | None = None
    card_body_fields: list[str] | None = None

    def get_columns(
        self: "KanbanView",
        forms: list[FeretUIForm],
    ) -> list[tuple[str, str]]:
        """Return list of (key, label) stages for kanban columns."""
        if self.columns:
            return list(self.columns)

        if hasattr(self.form_cls, self.column_field):
            unbound = getattr(self.form_cls, self.column_field)
            if hasattr(unbound, "kwargs") and "choices" in unbound.kwargs:
                choices = unbound.kwargs["choices"]
                if choices:
                    return list(choices)

        if forms:
            first_field = getattr(forms[0], self.column_field, None)
            if (
                first_field
                and hasattr(first_field, "choices")
                and first_field.choices
            ):
                return list(first_field.choices)

        seen: list[tuple[str, str]] = []
        for form in forms:
            f = getattr(form, self.column_field, None)
            val = str(f.data) if f and f.data is not None else ""
            if val and (val, val.title()) not in seen:
                seen.append((val, val.title()))

        if not seen:
            seen = [("default", "Default")]

        return seen

    def _build_card(
        self: "KanbanView",
        form: FeretUIForm,
    ) -> tuple[str, dict[str, Any]]:
        """Build a single card dictionary and return (column_value, card)."""
        pk = (
            str(form.pk.data)
            if hasattr(form, "pk") and form.pk.data is not None
            else ""
        )
        col_val = ""
        if hasattr(form, self.column_field):
            field = getattr(form, self.column_field)
            col_val = str(field.data) if field.data is not None else ""

        if self.card_title_field and hasattr(form, self.card_title_field):
            title = str(getattr(form, self.card_title_field).data or "")
        else:
            title = ""
            for field in form:
                if field.name not in ("pk", self.column_field):
                    title = str(field.data or "")
                    break
            if not title:
                title = pk

        body = []
        if self.card_body_fields:
            for b_name in self.card_body_fields:
                if hasattr(form, b_name):
                    b_field = getattr(form, b_name)
                    body.append(
                        {
                            "name": b_name,
                            "label": str(
                                b_field.label.text if b_field.label else b_name
                            ),
                            "value": str(
                                b_field.data if b_field.data is not None else ""
                            ),
                        },
                    )

        card = {
            "pk": pk,
            "title": title,
            "body": body,
            "form": form,
        }
        return col_val, card

    def build_kanban_board(
        self: "KanbanView",
        forms: list[FeretUIForm],
        stages: list[tuple[str, str]],
    ) -> list[dict[str, Any]]:
        """Group forms into stage columns with card details."""
        columns_data = []
        grouped: dict[str, list[dict[str, Any]]] = {
            str(k): [] for k, _ in stages
        }

        for form in forms:
            col_val, card = self._build_card(form)
            if col_val in grouped:
                grouped[col_val].append(card)
            elif grouped:
                first_key = stages[0][0]
                grouped[str(first_key)].append(card)

        for key, label in stages:
            columns_data.append(
                {
                    "key": str(key),
                    "label": label,
                    "cards": grouped.get(str(key), []),
                },
            )

        return columns_data

    @view_action_validator(methods=[Request.POST])
    def move_card(
        self: "KanbanView",
        feretui: "FeretUI",  # noqa: ARG002
        request: Request,
    ) -> Response:
        """Handle card drop from drag-and-drop.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param request: The request
        :type request: :class:`feretui.request.Request`
        :return: HTTP 200 response
        :rtype: :class:`feretui.response.Response`
        """
        pk = request.params.get("pk") or (
            request.form.get("pk") if request.form else None
        )
        stage = request.params.get("stage") or (
            request.form.get("stage") if request.form else None
        )
        index_val = request.params.get("index") or (
            request.form.get("index") if request.form else None
        )
        index = int(index_val) if index_val is not None else None

        if not pk or not stage:
            raise ResourceError(
                "Missing 'pk' or 'stage' parameter in move_card"
            )

        self.resource.move_card(pk, stage, index)
        return Response("", status_code=200)

    def render(
        self: "KanbanView",
        feretui: "FeretUI",
        session: Session,
        options: dict,
    ) -> str:
        """Render kanban board."""
        kwargs = self.render_kwargs(feretui, session, options)
        dataset = kwargs.get("dataset", {})
        forms = dataset.get("forms", [])

        stages = self.get_columns(forms)
        columns = self.build_kanban_board(forms, stages)

        move_url = (
            f"{feretui.base_url}/action/resource"
            f"?action=move_card&resource={self.resource.code}&view={self.code}"
        )

        return Markup(
            feretui.render_template(
                session,
                "feretui-resource-kanban",
                columns=columns,
                move_url=move_url,
                **kwargs,
            ),
        )


class KResource:
    """KResource class."""

    default_view: str = "kanban"
    MetaViewKanban = DefaultViewKanban

    def build_view(
        self: "KResource",
        view_cls_name: str,
    ) -> Resource:
        """Return the view instance in function of the MetaView attributes.

        :param view_cls_name: Name of the meta attribute
        :type view_cls_name: str
        :return: An instance of the view
        :rtype: :class:`feretui.resources.view.View`
        """
        if view_cls_name.startswith("MetaViewKanban"):
            meta_view_cls = self.get_meta_view_class(view_cls_name)
            meta_view_cls.append(KanbanView)
            view_cls = type(
                "KanbanView",
                tuple(meta_view_cls),
                {},
            )
            if not self.default_view:
                self.default_view = view_cls.code

            return view_cls(self)

        return super().build_view(view_cls_name)

    def move_card(
        self: "KResource",
        pk: str,
        stage: str,
        index: int | None = None,
    ) -> None:
        """Update card stage when dragged to a new column.

        .. warning:: must be overwritten or provided by another base class
                     for persistence.

        :param pk: Primary key of card
        :type pk: str
        :param stage: New stage key
        :type stage: str
        :param index: New index within column
        :type index: int | None
        """
        if hasattr(super(), "move_card"):
            super().move_card(pk, stage, index)
