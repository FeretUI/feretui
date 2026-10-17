"""Tests for KanbanView and KResource."""

import pytest
from wtforms import SelectField, StringField

from feretui.exceptions import ResourceError
from feretui.form import FeretUIForm
from feretui.request import Request
from feretui.resources.kanban import KanbanView, KResource
from feretui.resources.resource import Resource


class TaskForm(FeretUIForm):
    pk = StringField("ID")
    title = StringField("Title")
    assignee = StringField("Assignee")
    status = SelectField(
        "Status",
        choices=[("todo", "To Do"), ("in_progress", "In Progress"), ("done", "Done")],
        default="todo",
    )


class TaskResource(KResource, Resource):
    code = "tasks"
    label = "Tasks"
    Form = TaskForm

    def __init__(self) -> None:
        super().__init__()
        self.moves: list[tuple[str, str, int | None]] = []
        self.cards_data = [
            {"pk": "1", "title": "Setup CI", "assignee": "Alice", "status": "todo"},
            {"pk": "2", "title": "Design UI", "assignee": "Bob", "status": "in_progress"},
            {"pk": "3", "title": "Deploy v1", "assignee": "Alice", "status": "done"},
            {"pk": "4", "title": "Legacy Item", "assignee": "Charlie", "status": "unknown"},
        ]

    def filtered_reads(
        self,
        form_cls,
        filters,
        offset: int,
        limit: int,
    ) -> dict:
        forms = []
        for item in self.cards_data:
            f = form_cls(data=item)
            f.pk.data = item["pk"]
            forms.append(f)
        return {"forms": forms, "total": len(forms)}

    def move_card(self, pk: str, stage: str, index: int | None = None) -> None:
        self.moves.append((pk, stage, index))


class TestKanban:
    """Test suite for KanbanView and KResource."""

    def test_kresource_build_view(self) -> None:
        res = TaskResource()
        res.context = "test"
        view = res.build_view("MetaViewKanban")
        assert isinstance(view, KanbanView)
        assert view.code == "kanban"
        assert res.default_view == "kanban"

        # Base move_card in KResource does not fail
        base_res = KResource()
        base_res.move_card("1", "done", 0)

    def test_kanban_get_columns_explicit(self) -> None:
        class CustomKanbanView(KanbanView):
            columns = [("a", "Alpha"), ("b", "Beta")]

        res = TaskResource()
        res.context = "test"
        view = CustomKanbanView(res)
        cols = view.get_columns([])
        assert cols == [("a", "Alpha"), ("b", "Beta")]

    def test_kanban_get_columns_from_form_field(self) -> None:
        res = TaskResource()
        res.context = "test"
        view = KanbanView(res)
        cols = view.get_columns([])
        assert cols == [("todo", "To Do"), ("in_progress", "In Progress"), ("done", "Done")]

    def test_kanban_get_columns_from_data_discovery(self, feretui, frequest) -> None:
        class DynForm(FeretUIForm):
            pk = StringField()
            phase = StringField()

        class DynResource(KResource, Resource):
            code = "dyn"
            Form = DynForm

            class MetaViewKanban:
                column_field = "phase"

            def filtered_reads(self, form_cls, filters, offset, limit):
                return {"forms": [], "total": 0}

        res = DynResource()
        res.context = "test"
        view = res.build_view("MetaViewKanban")

        f1 = view.form_cls()
        f1.phase.data = "planning"
        f2 = view.form_cls()
        f2.phase.data = "execution"

        cols = view.get_columns([f1, f2])
        assert cols == [("planning", "Planning"), ("execution", "Execution")]

        # Empty forms returns default column
        assert view.get_columns([]) == [("default", "Default")]

    def test_kanban_render_board(self, feretui, session) -> None:
        class ConfiguredKanbanView(KanbanView):
            card_title_field = "title"
            card_body_fields = ["assignee"]
            do_click_on_entry_redirect_to = "read"

        res = TaskResource()
        res.context = "test"
        view = ConfiguredKanbanView(res)

        html = view.render(feretui, session, {})
        assert 'class="container is-fluid feretui-kanban-view"' in html
        assert 'class="feretui-kanban-board"' in html
        assert 'data-stage="todo"' in html
        assert 'data-stage="in_progress"' in html
        assert 'data-stage="done"' in html
        assert "Setup CI" in html
        assert "Alice" in html
        assert 'hx-trigger="dblclick"' in html
        assert "action=goto" in html
        assert "view=read" in html
        assert "action=move_card" in html

    def test_kanban_render_card_fallback_title(self, feretui, session) -> None:
        class MinimalForm(FeretUIForm):
            pk = StringField()
            status = StringField()

        class MinimalResource(KResource, Resource):
            code = "min"
            Form = MinimalForm

            def filtered_reads(self, form_cls, filters, offset, limit):
                f = form_cls()
                f.pk.data = "PK99"
                f.status.data = "todo"
                return {"forms": [f], "total": 1}

        res = MinimalResource()
        res.context = "test"
        view = KanbanView(res)
        html = view.render(feretui, session, {})
        assert "PK99" in html

    def test_kanban_move_card_action(self, feretui, session) -> None:
        res = TaskResource()
        res.context = "test"
        view = KanbanView(res)

        # Successful move via POST params
        request = Request(
            session=session,
            method=Request.POST,
            params={"pk": "2", "stage": "done", "index": "0"},
        )
        response = view.move_card(feretui, request)
        assert response.status_code == 200
        assert res.moves == [("2", "done", 0)]

        # Missing params raises ResourceError
        bad_req = Request(
            session=session,
            method=Request.POST,
            params={"pk": "2"},
        )
        with pytest.raises(ResourceError, match="Missing 'pk' or 'stage'"):
            view.move_card(feretui, bad_req)

    def test_kanban_get_columns_from_bound_form(self, feretui, frequest) -> None:
        class BoundChoiceForm(FeretUIForm):
            pk = StringField()
            phase = StringField()

        class BoundRes(KResource, Resource):
            code = "bound"
            Form = BoundChoiceForm

            class MetaViewKanban:
                column_field = "phase"

            def filtered_reads(self, form_cls, filters, offset, limit):
                return {"forms": [], "total": 0}

        res = BoundRes()
        res.context = "test"
        view = res.build_view("MetaViewKanban")
        f = view.form_cls()
        f.phase.choices = [("dyn1", "Dyn 1")]
        cols = view.get_columns([f])
        assert cols == [("dyn1", "Dyn 1")]

    def test_kanban_card_title_from_first_non_pk_field(
        self,
        feretui,
        session,
    ) -> None:
        class TitleForm(FeretUIForm):
            pk = StringField()
            status = StringField()
            desc = StringField()

        class TitleResource(KResource, Resource):
            code = "title_res"
            Form = TitleForm

            def filtered_reads(self, form_cls, filters, offset, limit):
                f = form_cls()
                f.pk.data = "PK10"
                f.status.data = "todo"
                f.desc.data = "Card Description"
                return {"forms": [f], "total": 1}

        res = TitleResource()
        res.context = "test"
        view = KanbanView(res)
        html = view.render(feretui, session, {})
        assert "Card Description" in html

    def test_kresource_build_view_delegation(self) -> None:
        from feretui.resources.list import LResource, ListView

        class BothResource(KResource, LResource, Resource):
            code = "both"
            Form = TaskForm

            def filtered_reads(self, form_cls, filters, offset, limit):
                return {"forms": [], "total": 0}

        res = BothResource()
        res.context = "test"
        res.default_view = None
        kanban_view = res.build_view("MetaViewKanban")
        assert res.default_view == "kanban"
        assert isinstance(kanban_view, KanbanView)

        # Super build_view delegation to LResource
        list_view = res.build_view("MetaViewList")
        assert isinstance(list_view, ListView)

