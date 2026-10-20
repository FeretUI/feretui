# This file is a part of the FeretUI project
#
#    Copyright (C) 2026 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Unit tests for feretui.contrib.sqla."""

import datetime
from decimal import Decimal
import pytest

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    Integer,
    Numeric,
    String,
    Text,
    create_engine,
    select,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from wtforms.fields import StringField

from feretui.context import set_context
from feretui.contrib.sqla import SQLAlchemyResource, model_to_form
from feretui.exceptions import ResourceError
from feretui.feretui import FeretUI
from feretui.form import FeretUIForm
from feretui.request import Request
from feretui.session import Session


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Float, default=0.0)
    cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.0"))
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_date: Mapped[datetime.date] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.now,
    )


class SkuItem(Base):
    __tablename__ = "sku_items"

    sku: Mapped[str] = mapped_column(String(50), primary_key=True)
    title: Mapped[str] = mapped_column(String(50), default="")


@pytest.fixture(scope="module")
def sqla_engine():
    """Create in-memory SQLite engine and tables."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def sqla_session(sqla_engine):
    """Provide clean session and clear table after test."""
    session_factory = sessionmaker(bind=sqla_engine)
    session = session_factory()
    yield session
    session.rollback()
    session.close()


class TestSQLAlchemyResource:
    """Test suite for SQLAlchemyResource and model_to_form."""

    def test_model_to_form_all_types(self) -> None:
        """Test model_to_form automatic type detection and exclusion."""
        form_cls = model_to_form(Item, exclude={"cost"})
        assert issubclass(form_cls, FeretUIForm)
        with set_context(FeretUI(), Request(Session())):
            form = form_cls()
            fields = form._fields
            assert "pk" in fields
            assert "name" in fields
            assert "description" in fields
            assert "price" in fields
            assert "cost" not in fields
            assert "quantity" in fields
            assert "is_active" in fields
            assert "created_date" in fields
            assert "created_at" in fields

    def test_model_to_form_with_existing_base(self) -> None:
        """Test model_to_form preserving custom base_form fields."""

        class CustomBase(FeretUIForm):
            custom_field = StringField("Custom Field")

        form_cls = model_to_form(Item, base_form=CustomBase)
        with set_context(FeretUI(), Request(Session())):
            form = form_cls()
            assert "custom_field" in form._fields
            assert "name" in form._fields

    def test_crud_lifecycle(self, sqla_engine, sqla_session) -> None:
        """Test full CRUD lifecycle with SQLAlchemyResource."""
        session_factory = sessionmaker(bind=sqla_engine)

        class ItemResource(SQLAlchemyResource):
            code = "item"
            label = "Item"
            model = Item

        ItemResource.session_factory = session_factory
        res = ItemResource.build()
        feret = FeretUI()
        req = Request(Session())

        with set_context(feret, req):
            # 1. Create
            create_form = res.Form(
                data={
                    "name": "Widget A",
                    "description": "A fine widget",
                    "price": 19.99,
                    "is_active": True,
                },
            )
            pk = res.create(create_form)
            assert pk is not None

            # 2. Read
            read_form = res.read(res.Form, pk)
            assert read_form.name.data == "Widget A"
            assert read_form.price.data == 19.99
            assert read_form.is_active.data is True

            # 3. Filtered reads
            ds = res.filtered_reads(res.Form, [], 0, 10)
            assert ds["total"] == 1
            assert len(ds["forms"]) == 1
            assert ds["forms"][0].name.data == "Widget A"

            # Filter with match
            ds_matched = res.filtered_reads(
                res.Form,
                [("name", ["Widget A"])],
                0,
                10,
            )
            assert ds_matched["total"] == 1

            # Filter with in_
            ds_in = res.filtered_reads(
                res.Form,
                [("name", ["Widget A", "Widget B"])],
                0,
                10,
            )
            assert ds_in["total"] == 1

            # Filter with no match
            ds_empty = res.filtered_reads(
                res.Form,
                [("name", ["Nonexistent"])],
                0,
                10,
            )
            assert ds_empty["total"] == 0

            # Filter with search
            ds_search = res.filtered_reads(
                res.Form,
                [("search", ["Widget"])],
                0,
                10,
            )
            assert ds_search["total"] == 1
            assert ds_search["forms"][0].name.data == "Widget A"

            # Filter with explicit search_fields
            res.search_fields = ["name"]
            ds_search_fields = res.filtered_reads(
                res.Form,
                [("q", ["A"])],
                0,
                10,
            )
            assert ds_search_fields["total"] == 1

            # Filter with search no match
            ds_search_none = res.filtered_reads(
                res.Form,
                [("search", ["ZZZ"])],
                0,
                10,
            )
            assert ds_search_none["total"] == 0

            # 4. Update
            update_form = res.Form(
                data={
                    "pk": pk,
                    "name": "Widget Updated",
                    "price": 29.99,
                    "is_active": False,
                },
            )
            res.update([update_form])

            refreshed = res.read(res.Form, pk)
            assert refreshed.name.data == "Widget Updated"
            assert refreshed.price.data == 29.99
            assert refreshed.is_active.data is False

            # 5. Delete
            res.delete([pk])
            with pytest.raises(ResourceError):
                res.read(res.Form, pk)

    def test_session_factory_variants(self, sqla_session) -> None:
        """Test callable returning raw session and direct session context manager."""

        class DirectRes(SQLAlchemyResource):
            code = "direct"
            label = "Direct"
            model = Item
            session_factory = lambda _self=None: sqla_session  # noqa: E731

        res = DirectRes.build()
        with res.get_db_session() as db:
            assert db is sqla_session

        class ObjRes(SQLAlchemyResource):
            code = "obj"
            label = "Obj"
            model = Item
            session_factory = sqla_session

        res2 = ObjRes.build()
        with res2.get_db_session() as db:
            assert db is sqla_session

    def test_read_missing_error(self, sqla_engine) -> None:
        """Test read with non-existent PK raises ResourceError."""
        session_factory = sessionmaker(bind=sqla_engine)

        class ItemResource(SQLAlchemyResource):
            code = "item"
            label = "Item"
            model = Item

        ItemResource.session_factory = session_factory
        res = ItemResource.build()
        feret = FeretUI()
        req = Request(Session())
        with set_context(feret, req), pytest.raises(ResourceError):
            res.read(res.Form, "999999")

    def test_no_model_guards(self) -> None:
        """Test operations when no model is configured."""
        res = SQLAlchemyResource()
        assert res.filtered_reads(FeretUIForm, [], 0, 10) == {
            "total": 0,
            "forms": [],
        }

        with pytest.raises(ResourceError):
            res.create(FeretUIForm())

        with pytest.raises(ResourceError):
            res.read(FeretUIForm, "1")

        with pytest.raises(ResourceError):
            res.update([FeretUIForm()])

        with pytest.raises(ResourceError):
            res.delete(["1"])

    def test_sku_item_string_pk(self, sqla_engine) -> None:
        """Test model with string primary key and explicit primary_key_attr."""
        session_factory = sessionmaker(bind=sqla_engine)

        class SkuResource(SQLAlchemyResource):
            code = "sku_item"
            label = "SKU Item"
            model = SkuItem
            primary_key_attr = "sku"

        SkuResource.session_factory = session_factory
        res = SkuResource.build()
        feret = FeretUI()
        req = Request(Session())

        with set_context(feret, req):
            create_form = res.Form(
                data={
                    "pk": "SKU-100",
                    "sku": "SKU-100",
                    "title": "Widget 100",
                },
            )
            pk = res.create(create_form)
            assert pk == "SKU-100"

            read_form = res.read(res.Form, "SKU-100")
            assert read_form.title.data == "Widget 100"

            update_form = res.Form(
                data={"pk": "SKU-100", "title": "Widget 100 Updated"},
            )
            res.update([update_form])

            refreshed = res.read(res.Form, "SKU-100")
            assert refreshed.title.data == "Widget 100 Updated"

            res.delete(["SKU-100"])
            with pytest.raises(ResourceError):
                res.read(res.Form, "SKU-100")

    def test_custom_form_preserved(self) -> None:
        """Test that explicit Form with custom fields is preserved."""

        class CustomResource(SQLAlchemyResource):
            code = "custom"
            label = "Custom"
            model = Item

            class Form(FeretUIForm):
                pk = StringField("PK")
                custom_only = StringField("Custom Only")

        res = CustomResource.build()
        assert hasattr(res.Form, "custom_only")

    def test_update_missing_and_non_int_pk(self, sqla_engine) -> None:
        """Test update with missing PK and non-int PK."""
        session_factory = sessionmaker(bind=sqla_engine)

        class ItemResource(SQLAlchemyResource):
            code = "item"
            label = "Item"
            model = Item

        ItemResource.session_factory = session_factory
        res = ItemResource.build()
        feret = FeretUI()
        req = Request(Session())

        with set_context(feret, req):
            form1 = res.Form(data={"pk": "999999", "name": "Does not exist"})
            form2 = res.Form(data={"pk": "non_int_pk", "name": "Invalid int"})
            res.update([form1, form2])

    def test_get_primary_key_attr_fallback(self) -> None:
        """Test primary key attr fallback when model is None or has no PK."""

        class NoModelResource(SQLAlchemyResource):
            pass

        assert NoModelResource.get_primary_key_attr() == "id"

    def test_session_factory_callable_returning_cm(self, sqla_engine) -> None:
        """Test callable returning context manager."""
        session_factory = sessionmaker(bind=sqla_engine)

        class CMResource(SQLAlchemyResource):
            code = "cm"
            label = "CM"
            model = Item

        CMResource.session_factory = session_factory
        res = CMResource.build()
        with res.get_db_session() as db:
            assert db is not None

    def test_session_factory_plain_object_without_enter(self) -> None:
        """Test plain session object without __enter__."""

        class DummySession:
            pass

        dummy = DummySession()

        class PlainResource(SQLAlchemyResource):
            code = "plain"
            label = "Plain"
            model = Item

        PlainResource.session_factory = dummy
        res = PlainResource.build()
        with res.get_db_session() as db:
            assert db is dummy

    def test_move_card(self, sqla_engine) -> None:
        """Test move_card on SQLAlchemyResource."""
        session_factory = sessionmaker(bind=sqla_engine)

        class TaskModel(Base):
            __tablename__ = "kanban_tasks"
            id: Mapped[int] = mapped_column(
                Integer,
                primary_key=True,
                autoincrement=True,
            )
            title: Mapped[str] = mapped_column(String(50))
            status: Mapped[str] = mapped_column(String(20), default="todo")

        Base.metadata.create_all(sqla_engine)

        with session_factory() as db:
            t = TaskModel(title="Kanban Task", status="todo")
            db.add(t)
            db.commit()
            tid = str(t.id)

        class TaskResource(SQLAlchemyResource):
            code = "ktask"
            label = "Task"
            model = TaskModel

        TaskResource.session_factory = session_factory
        res = TaskResource.build()

        # No model guard
        with pytest.raises(ResourceError):
            SQLAlchemyResource().move_card("1", "done")

        # Non-existent int item and non-int string item
        res.move_card("99999", "done")
        res.move_card("not-an-int", "done")

        # Kanban view custom column_field
        class DummyKanbanView:
            column_field = "status"

        res.views = {"kanban": DummyKanbanView()}

        # Successful move
        res.move_card(tid, "done")
        with session_factory() as db:
            refreshed = db.scalar(
                select(TaskModel).where(TaskModel.id == int(tid)),
            )
            assert refreshed.status == "done"

        # Successful move with list arguments
        res.move_card([tid], ["draft"])
        with session_factory() as db:
            refreshed = db.scalar(
                select(TaskModel).where(TaskModel.id == int(tid)),
            )
            assert refreshed.status == "draft"

        # Model with stage attribute instead of status
        class StageModel(Base):
            __tablename__ = "stage_tasks"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
            stage: Mapped[str] = mapped_column(String(20), default="s1")

        Base.metadata.create_all(sqla_engine)
        with session_factory() as db:
            sm = StageModel(stage="s1")
            db.add(sm)
            db.commit()
            sm_id = str(sm.id)

        class StageResource(SQLAlchemyResource):
            code = "stask"
            label = "Stage Task"
            model = StageModel

        StageResource.session_factory = session_factory
        s_res = StageResource.build()
        s_res.move_card(sm_id, "s2")
        with session_factory() as db:
            refreshed_stage = db.scalar(
                select(StageModel).where(StageModel.id == int(sm_id)),
            )
            assert refreshed_stage.stage == "s2"

    def test_is_auto_sequence_and_pk_db_generated(self) -> None:
        from sqlalchemy import Column
        from feretui.contrib.sqla import is_auto_sequence_column

        # Auto PK integer
        col_int = Column("id", Integer, primary_key=True, autoincrement=True)
        assert is_auto_sequence_column(col_int) is True

        # Non PK
        col_non_pk = Column("name", String(50), primary_key=False)
        assert is_auto_sequence_column(col_non_pk) is False

        # Manual PK string
        col_str_pk = Column("code", String(20), primary_key=True, autoincrement=False)
        assert is_auto_sequence_column(col_str_pk) is False

        # PK with server_default
        col_uuid = Column("uid", String(36), primary_key=True, server_default="uuid()")
        assert is_auto_sequence_column(col_uuid) is True

        # PK with default
        col_default = Column("seq_id", Integer, primary_key=True, default=1)
        assert is_auto_sequence_column(col_default) is True

        # Test model_to_form with manual PK vs auto PK
        class NaturalModel(Base):
            __tablename__ = "natural_items"
            code: Mapped[str] = mapped_column(String(20), primary_key=True)
            name: Mapped[str] = mapped_column(String(50))

        # Auto: code is manual PK => included in form
        auto_form = model_to_form(NaturalModel, pk_db_generated="auto")()
        assert "code" in auto_form._fields
        assert "pk" in auto_form._fields

        # Forced True: code omitted from form inputs
        forced_form = model_to_form(NaturalModel, pk_db_generated=True)()
        assert "code" not in forced_form._fields
        assert "pk" in forced_form._fields

    def test_sqla_crud_mixin(self, sqla_engine) -> None:
        from feretui.contrib.sqla import SQLACrudMixin

        session_factory = sessionmaker(bind=sqla_engine)

        class CrudItem(Base, SQLACrudMixin):
            __tablename__ = "crud_items"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
            name: Mapped[str] = mapped_column(String(50))
            category: Mapped[str] = mapped_column(String(50), default="general")

        Base.metadata.create_all(sqla_engine)
        with session_factory() as db:
            ci1 = CrudItem(name="A", category="c1")
            ci2 = CrudItem(name="B", category="c2")
            ci3 = CrudItem(name="C", category="c1")
            db.add_all([ci1, ci2, ci3])
            db.commit()
            ci1_id, ci2_id = ci1.id, ci2.id

        with session_factory() as db:
            # get_by_id
            item = CrudItem.get_by_id(db, ci1_id)
            assert item is not None
            assert item.name == "A"

            # search_records with filters and pagination
            res = CrudItem.search_records(db, filters={"category": "c1"}, limit=10)
            assert len(res) == 2
            assert {r.name for r in res} == {"A", "C"}

            # search_records with list filter and order_by
            res2 = CrudItem.search_records(
                db,
                filters={"category": ["c1", "c2"]},
                order_by=CrudItem.name.desc(),
            )
            assert len(res2) == 3
            assert res2[0].name == "C"

            # get_by_id on non-existent
            assert CrudItem.get_by_id(db, 99999) is None

            # delete_records
            CrudItem.delete_records(db, [ci1_id, ci2_id])
            assert CrudItem.get_by_id(db, ci1_id) is None
            assert CrudItem.get_by_id(db, ci2_id) is None

        # Model with non-id PK get_by_id
        class CodeItem(Base, SQLACrudMixin):
            __tablename__ = "code_items"
            code: Mapped[str] = mapped_column(String(10), primary_key=True)
            desc: Mapped[str] = mapped_column(String(50))

        Base.metadata.create_all(sqla_engine)
        with session_factory() as db:
            c = CodeItem(code="ABC", desc="Desc")
            db.add(c)
            db.commit()

        with session_factory() as db:
            fetched = CodeItem.get_by_id(db, "ABC")
            assert fetched is not None
            assert fetched.desc == "Desc"

        # Model without primary key fallback
        class NoPkStub(SQLACrudMixin):
            pass

        assert NoPkStub.get_by_id(None, "1") is None

    def test_cascade_delete_and_one2many_protection(
        self,
        sqla_engine,
    ) -> None:
        from sqlalchemy import ForeignKey
        from sqlalchemy.orm import relationship
        from feretui.form import One2ManyField

        session_factory = sessionmaker(bind=sqla_engine)

        class OrderParent(Base):
            __tablename__ = "order_parents"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
            ref: Mapped[str] = mapped_column(String(50))
            lines = relationship(
                "OrderChild",
                cascade="all, delete-orphan",
                backref="parent",
            )

        class OrderChild(Base):
            __tablename__ = "order_children"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
            parent_id: Mapped[int] = mapped_column(Integer, ForeignKey("order_parents.id"))
            detail: Mapped[str] = mapped_column(String(50))

        Base.metadata.create_all(sqla_engine)
        with session_factory() as db:
            parent = OrderParent(
                ref="ORD-01",
                lines=[OrderChild(detail="Line 1"), OrderChild(detail="Line 2")],
            )
            db.add(parent)
            db.commit()
            pid = str(parent.id)

        class ParentResource(SQLAlchemyResource):
            code = "parent_res"
            label = "Parent"
            model = OrderParent

        ParentResource.session_factory = session_factory
        res = ParentResource.build()

        # Update test with One2ManyField: lines should not be wiped
        class DummyFormWithO2M(FeretUIForm):
            pk = StringField()
            ref = StringField()
            lines = One2ManyField()

        f = DummyFormWithO2M()
        f.pk.data = pid
        f.ref.data = "ORD-01-UPDATED"
        f.lines.data = []  # Empty list should NOT overwrite lines

        res.update([f])
        with session_factory() as db:
            p = db.scalar(select(OrderParent).where(OrderParent.id == int(pid)))
            assert p.ref == "ORD-01-UPDATED"
            # Verify lines were NOT deleted
            assert len(p.lines) == 2

        # Create test with One2ManyField: should not set empty list
        f_new = DummyFormWithO2M()
        f_new.ref.data = "ORD-NEW"
        f_new.lines.data = []
        new_pid = res.create(f_new)
        assert new_pid is not None

        # Integer string conversion test
        class OrderChildResource(SQLAlchemyResource):
            code = "child_res"
            label = "Child"
            model = OrderChild

        OrderChildResource.session_factory = session_factory
        child_res = OrderChildResource.build()

        class ChildForm(FeretUIForm):
            pk = StringField()
            parent_id = StringField()
            detail = StringField()

        cf = ChildForm()
        cf.parent_id.data = str(new_pid)
        cf.detail.data = "New Child"
        cid = child_res.create(cf)
        with session_factory() as db:
            child_inst = db.scalar(select(OrderChild).where(OrderChild.id == int(cid)))
            assert child_inst.parent_id == int(new_pid)

        # Update child with string parent_id
        cf_up = ChildForm()
        cf_up.pk.data = cid
        cf_up.parent_id.data = str(pid)
        cf_up.detail.data = "Updated Child"
        child_res.update([cf_up])
        with session_factory() as db:
            child_up = db.scalar(select(OrderChild).where(OrderChild.id == int(cid)))
            assert child_up.parent_id == int(pid)

        # Delete test: verify ORM cascade deletes child records
        res.delete([pid])
        with session_factory() as db:
            p_after = db.scalar(select(OrderParent).where(OrderParent.id == int(pid)))
            assert p_after is None
            # Child lines must also be deleted by ORM cascade
            children = db.scalars(
                select(OrderChild).where(OrderChild.parent_id == int(pid)),
            ).all()
            assert len(children) == 0

        # Create with manual PK
        class ManualPkModel(Base):
            __tablename__ = "manual_pk_models"
            code: Mapped[str] = mapped_column(String(20), primary_key=True)
            name: Mapped[str] = mapped_column(String(50))

        Base.metadata.create_all(sqla_engine)

        class ManualPkResource(SQLAlchemyResource):
            code = "manual_res"
            label = "Manual"
            model = ManualPkModel
            pk_db_generated = False

        ManualPkResource.session_factory = session_factory
        m_res = ManualPkResource.build()

        class ManualForm(FeretUIForm):
            pk = StringField()
            code = StringField()
            name = StringField()

        mf = ManualForm()
        mf.pk.data = "MN-01"
        mf.code.data = "MN-01"
        mf.name.data = "Manual Item"
        created_pk = m_res.create(mf)
        assert created_pk == "MN-01"

        # Create with auto PK and empty string
        class AutoItemForm(FeretUIForm):
            pk = StringField()
            name = StringField()
            id = StringField()

        class AutoItemResource(SQLAlchemyResource):
            code = "auto_res"
            label = "Auto"
            model = Item
            pk_db_generated = True

        AutoItemResource.session_factory = session_factory
        ai_res = AutoItemResource.build()
        a_form = AutoItemForm()
        a_form.pk.data = None
        a_form.name.data = "Auto Item with empty id"
        a_form.id.data = ""
        auto_pk = ai_res.create(a_form)
        assert auto_pk.isdigit()

    def test_x2many_reconciliation(self, sqla_engine) -> None:
        from sqlalchemy import ForeignKey
        from sqlalchemy.orm import relationship, sessionmaker
        from feretui.form import One2ManyField

        session_factory = sessionmaker(bind=sqla_engine)

        class ParentModel(Base):
            __tablename__ = "parent_models"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
            ref: Mapped[str] = mapped_column(String(50))
            lines = relationship(
                "ChildModel",
                cascade="all, delete-orphan",
                backref="parent",
            )

        class ChildModel(Base):
            __tablename__ = "child_models"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
            parent_id: Mapped[int] = mapped_column(Integer, ForeignKey("parent_models.id"))
            detail: Mapped[str] = mapped_column(String(50))
            qty: Mapped[int] = mapped_column(Integer, default=1)
            price: Mapped[float] = mapped_column(Float, default=0.0)

        Base.metadata.create_all(sqla_engine)

        class ParentO2MResource(SQLAlchemyResource):
            code = "parent_o2m"
            label = "Parent O2M"
            model = ParentModel

        ParentO2MResource.session_factory = session_factory
        res = ParentO2MResource.build()

        class OrderForm(FeretUIForm):
            pk = StringField()
            ref = StringField()
            lines = One2ManyField(
                columns=[("detail", "Detail"), ("qty", "Qty"), ("price", "Price")],
                embedded=True,
            )

        # 1. Create with child lines submitted as formdata
        formdata = {
            "ref": "ORD-X2M-1",
            "lines__present": "1",
            "lines[0][detail]": "Created Line 1",
            "lines[0][qty]": "5",
            "lines[0][price]": "19.99",
            "lines[1][detail]": "Created Line 2",
        }
        form = OrderForm(formdata=formdata)
        assert len(form.lines.data) == 2
        assert form.lines.is_submitted is True
        pid = res.create(form)

        with session_factory() as db:
            p = db.scalar(select(ParentModel).where(ParentModel.id == int(pid)))
            assert p is not None
            assert len(p.lines) == 2
            line_details = {l.detail for l in p.lines}
            assert "Created Line 1" in line_details
            assert "Created Line 2" in line_details
            line1 = next(l for l in p.lines if l.detail == "Created Line 1")
            line2 = next(l for l in p.lines if l.detail == "Created Line 2")
            assert line1.qty == 5
            assert abs(line1.price - 19.99) < 0.001

        # 2. Update: modify line1, delete line2, add line3
        update_data = {
            "pk": pid,
            "ref": "ORD-X2M-1-MODIFIED",
            "lines__present": "1",
            "lines[0][id]": str(line1.id),
            "lines[0][detail]": "Updated Line 1",
            "lines[0][qty]": "10",
            "lines[0][price]": "29.50",
            "lines[1][detail]": "New Line 3",
        }
        up_form = OrderForm(formdata=update_data)
        assert len(up_form.lines.data) == 2
        res.update([up_form])

        with session_factory() as db:
            p_up = db.scalar(select(ParentModel).where(ParentModel.id == int(pid)))
            assert p_up.ref == "ORD-X2M-1-MODIFIED"
            assert len(p_up.lines) == 2
            up_details = {l.detail for l in p_up.lines}
            assert "Updated Line 1" in up_details
            assert "New Line 3" in up_details
            assert "Created Line 2" not in up_details
            line1_up = next(l for l in p_up.lines if l.detail == "Updated Line 1")
            assert line1_up.qty == 10
            assert abs(line1_up.price - 29.50) < 0.001

        # 3. Update with JSON string formdata
        import json
        json_formdata = {
            "pk": pid,
            "ref": "ORD-JSON",
            "lines": json.dumps([{"detail": "JSON Line"}]),
        }
        json_form = OrderForm(formdata=json_formdata)
        assert len(json_form.lines.data) == 1
        res.update([json_form])

        with session_factory() as db:
            p_json = db.scalar(select(ParentModel).where(ParentModel.id == int(pid)))
            assert len(p_json.lines) == 1
            assert p_json.lines[0].detail == "JSON Line"

        # 4. Update with empty lines (user deleted all rows)
        clear_data = {
            "pk": pid,
            "ref": "ORD-EMPTY",
            "lines__present": "1",
        }
        clear_form = OrderForm(formdata=clear_data)
        assert len(clear_form.lines.data) == 0
        assert clear_form.lines.is_submitted is True
        res.update([clear_form])

        with session_factory() as db:
            p_empty = db.scalar(select(ParentModel).where(ParentModel.id == int(pid)))
            assert len(p_empty.lines) == 0

        # 5. Test rendering wrap_one2many in readonly and embedded modes
        feretui = FeretUI()
        session = Session()
        render_form = OrderForm(formdata={"lines[0][detail]": "Test Row"})
        with set_context(feretui, Request(session=session)):
            html_edit = str(render_form.lines(readonly=False))
            assert "lines[0][detail]" in html_edit
            assert "lines-row-template" in html_edit
            assert "addOne2ManyRow" in html_edit

            html_ro = str(render_form.lines(readonly=True))
            assert "lines[0][detail]" not in html_ro
            assert "addOne2ManyRow" not in html_ro

        # 6. Branch coverage on save_relations edge cases
        class DummyForm(FeretUIForm):
            lines = StringField("Lines")

        dummy_form = DummyForm()
        dummy_parent = ParentModel(ref="DUMMY")
        with session_factory() as db:
            res.save_relations(db, dummy_parent, dummy_form)  # line 408

        order_form_none = OrderForm()
        order_form_none.lines.data = None
        with session_factory() as db:
            res.save_relations(db, dummy_parent, order_form_none)  # line 412

        dummy_parent_no_rel = ParentModel(ref="NO_REL")
        dummy_parent_no_rel.__dict__["lines"] = None
        order_form_sub = OrderForm()
        order_form_sub.lines.data = ["not-a-dict"]
        order_form_sub.lines.is_submitted = True
        with session_factory() as db:
            res.save_relations(db, dummy_parent_no_rel, order_form_sub)  # line 424
            res.save_relations(db, dummy_parent, order_form_sub)  # line 435




