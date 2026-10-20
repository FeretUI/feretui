# This file is a part of the FeretUI project
#
#    Copyright (C) 2024-2026 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Tests for GridView and GridResource."""

from typing import Any

from wtforms import HiddenField, SelectField, StringField

from feretui import FeretUI, Session
from feretui.form import FeretUIForm
from feretui.resources.grid import (
    DefaultViewGrid,
    GridCRUD,
    GridCRUDResource,
    GridResource,
    GridView,
)
from feretui.resources.resource import Resource


class CardItemForm(FeretUIForm):
    """Test form for grid cards."""

    pk = HiddenField("ID")
    name = StringField("Item Name")
    image_url = StringField("Image")
    status = SelectField(
        "Status",
        choices=[
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("cancelled", "Cancelled"),
            ("other", "Other"),
        ],
    )
    category = StringField("Category")


class CardResource(GridResource, Resource):
    """Test resource with Grid view."""

    code = "card_items"
    label = "Card Items"
    Form = CardItemForm

    def filtered_reads(
        self, form_cls: Any, filters: Any, offset: int, limit: int
    ) -> dict[str, Any]:
        """Mock filtered_reads."""
        return {"total": 0, "forms": []}

    class MetaViewGrid(DefaultViewGrid):
        card_title_field = "name"
        card_image_field = "image_url"
        card_badge_field = "status"
        card_body_fields = ["category"]


class MinimalGridResource(GridResource, Resource):
    """Minimal test resource with default grid."""

    code = "minimal_cards"
    label = "Minimal Cards"
    Form = CardItemForm

    def filtered_reads(
        self, form_cls: Any, filters: Any, offset: int, limit: int
    ) -> dict[str, Any]:
        """Mock filtered_reads."""
        return {"total": 0, "forms": []}


class MyGridCRUDResource(GridCRUDResource):
    """Composite GridCRUD resource."""

    code = "crud_cards"
    label = "CRUD Cards"
    Form = CardItemForm

    def filtered_reads(
        self, form_cls: Any, filters: Any, offset: int, limit: int
    ) -> dict[str, Any]:
        """Mock filtered_reads."""
        return {"total": 0, "forms": []}


class TestGridResource:
    """Test suite for GridView and GridResource."""

    def test_build_view_and_defaults(self, feretui: FeretUI) -> None:
        """Test build_view creates GridView with configured defaults."""
        res = CardResource.build()
        assert "grid" in res.views
        view = res.views["grid"]
        assert isinstance(view, GridView)
        assert view.card_title_field == "name"
        assert view.card_image_field == "image_url"
        assert view.card_badge_field == "status"
        assert view.card_body_fields == ["category"]

    def test_build_view_sets_default_view_if_none(self) -> None:
        """Test build_view sets default_view to grid if not previously set."""
        class DynamicGridResource(GridResource, Resource):
            code = "dyn_cards"
            label = "Dyn Cards"
            Form = CardItemForm
            default_view = None

            def filtered_reads(
                self, form_cls: Any, filters: Any, offset: int, limit: int
            ) -> dict[str, Any]:
                return {"total": 0, "forms": []}

        res = DynamicGridResource()
        res.context = "test"
        view = res.build_view("MetaViewGrid")
        assert res.default_view == "grid"
        assert isinstance(view, GridView)

        # Call with other view name to hit super().build_view
        other = res.build_view("MetaViewOther")
        assert other is None

    def test_grid_crud_inheritance(self) -> None:
        """Test GridCRUDResource provides all expected CRUD views."""
        res = MyGridCRUDResource.build()
        assert res.default_view == "grid"
        assert GridCRUD == GridCRUDResource
        assert "grid" in res.views
        assert "create" in res.views
        assert "read" in res.views
        assert "edit" in res.views
        assert "delete" in res.views

    def test_format_card_field_value(self) -> None:
        """Test _format_card_field_value handles choices, lists, and strings."""
        view = GridView(CardResource())

        f = CardItemForm()
        f.status.data = "confirmed"
        assert view._format_card_field_value(f.status) == "Confirmed"

        f.status.data = "unknown"
        assert view._format_card_field_value(f.status) == "unknown"

        # List data
        class ListFieldForm(FeretUIForm):
            tags = StringField("Tags")

        lf = ListFieldForm()
        lf.tags.data = ["tag1", "tag2"]
        assert view._format_card_field_value(lf.tags) == "2 items"
        lf.tags.data = []
        assert view._format_card_field_value(lf.tags) == "-"

    def test_build_card(self, feretui: FeretUI) -> None:
        """Test _build_card compiles full card details dictionary."""
        res = CardResource.build()
        view: GridView = res.views["grid"]

        f1 = CardItemForm(data={
            "pk": "101",
            "name": "Super Gadget",
            "image_url": "https://example.com/gadget.png",
            "status": "confirmed",
            "category": "Electronics",
        })
        card1 = view._build_card(f1, feretui)
        assert card1["pk"] == "101"
        assert card1["title"] == "Super Gadget"
        assert card1["image_url"] == "https://example.com/gadget.png"
        assert card1["badge"] == "Confirmed"
        assert card1["badge_class"] == "is-success"
        assert len(card1["fields"]) == 1
        assert card1["fields"][0]["label"] == "Category"
        assert card1["fields"][0]["value"] == "Electronics"
        assert "pk=101" in card1["url"]
        assert "pk=101" in card1["goto_url"]

        # Card with draft status (is-info)
        f2 = CardItemForm(data={"pk": "102", "status": "draft"})
        card2 = view._build_card(f2, feretui)
        assert card2["badge_class"] == "is-info"

        # Card with cancelled status (is-danger)
        f3 = CardItemForm(data={"pk": "103", "status": "cancelled"})
        card3 = view._build_card(f3, feretui)
        assert card3["badge_class"] == "is-danger"

        # Card with other status (is-secondary)
        f4 = CardItemForm(data={"pk": "104", "status": "other"})
        card4 = view._build_card(f4, feretui)
        assert card4["badge_class"] == "is-secondary"

    def test_build_card_fallback_title(self, feretui: FeretUI) -> None:
        """Test _build_card fallback to first field or pk when title_field not set."""
        res = MinimalGridResource.build()
        view: GridView = res.views["grid"]

        # First field has name
        f1 = CardItemForm(data={"pk": "1", "name": "Item A"})
        card1 = view._build_card(f1, feretui)
        assert card1["title"] == "Item A"

        # Fallback to pk
        f2 = CardItemForm(data={"pk": "42"})
        f2.name.data = ""
        f2.image_url.data = ""
        f2.status.data = ""
        f2.category.data = ""
        card2 = view._build_card(f2, feretui)
        assert card2["title"] == "42"

    def test_render_grid_view(
        self,
        feretui: FeretUI,
        session: Session,
        frequest: Any,  # noqa: ARG002
    ) -> None:
        """Test rendering grid view with cards, search filter, and empty state."""
        res = CardResource.build()
        view: GridView = res.views["grid"]

        # Mock forms
        forms = [
            CardItemForm(data={"pk": "1", "name": "Alpha Product", "category": "A"}),
            CardItemForm(data={"pk": "2", "name": "Beta Service", "category": "B"}),
        ]
        view.render_kwargs = lambda *args, **kwargs: {  # noqa: ARG005
            "dataset": {"forms": forms, "total": len(forms)},
            "label": "Card Items",
            "paginations": [],
            "view_switchers": [],
            "header_buttons": [],
            "quick_filters": [],
            "actions": [],
            "rcode": "card_items",
            "vcode": "grid",
            "group_by_options": [],
            "search_query": "",
        }

        # 1. Full render
        html = view.render(feretui, session, {})
        assert "feretui-grid-view" in html
        assert "Alpha Product" in html
        assert "Beta Service" in html
        assert "feretui-cards-grid" in html

        # 2. Search filter matching Alpha
        html_search = view.render(feretui, session, {"search": "Alpha"})
        assert "Alpha Product" in html_search
        assert "Beta Service" not in html_search

        # 3. Search filter with no matches (empty state)
        html_empty = view.render(feretui, session, {"search": "NonExistent"})
        assert "No records found." in html_empty
