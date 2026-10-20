# This file is a part of the FeretUI project
#
#    Copyright (C) 2024-2026 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Module feretui.resources.grid.

The Grid resource displays data as responsive cards / tiles in a mosaic grid.

* :class:`.GridView`
* :class:`.GridResource`
* :class:`.GridCRUDResource`
"""

import html
from typing import TYPE_CHECKING, Any

from markupsafe import Markup
from wtforms import Field

from feretui.form import FeretUIForm
from feretui.resources.common import LabelMixinForView, MultiView
from feretui.resources.create import CResource
from feretui.resources.delete import DResource
from feretui.resources.read import RResource
from feretui.resources.update import UResource
from feretui.resources.view import View
from feretui.session import Session

from .resource import Resource

if TYPE_CHECKING:
    from feretui.feretui import FeretUI


class DefaultViewGrid:
    """Default values for the view grid."""

    label: str = None
    limit: int = 40
    create_button_redirect_to: str = None
    delete_button_redirect_to: str = None
    do_click_on_entry_redirect_to: str = "read"
    card_title_field: str | None = None
    card_body_fields: list[str] | None = None
    card_image_field: str | None = None
    card_badge_field: str | None = None
    quick_filters: list = []
    group_by_fields: list[tuple[str, str]] = []


class GridView(MultiView, LabelMixinForView, View):
    """Grid / Card gallery view for responsive visual catalogs."""

    code: str = "grid"
    limit: int = 40
    create_button_redirect_to: str = None
    delete_button_redirect_to: str = None
    do_click_on_entry_redirect_to: str = "read"
    card_title_field: str | None = None
    card_body_fields: list[str] | None = None
    card_image_field: str | None = None
    card_badge_field: str | None = None
    group_by_fields: list[tuple[str, str]] = []

    def _format_card_field_value(
        self: "GridView",
        field: Field,
    ) -> str:
        """Format a form field value for presentation on the grid card."""
        val = field.data if field.data is not None else ""
        if hasattr(field, "choices") and field.choices:
            for c_val, c_lbl in field.choices:
                if str(c_val) == str(val):
                    return str(c_lbl)
        elif isinstance(val, list):
            return "-" if not val else f"{len(val)} items"
        return str(val)

    def _get_card_title(self, form: FeretUIForm, pk: str) -> str:
        """Resolve title text for grid card."""
        if self.card_title_field and hasattr(form, self.card_title_field):
            title = str(getattr(form, self.card_title_field).data or "")
            if title:
                return title
        for field in form:
            if field.name not in ("pk", "id") and field.data:
                return str(field.data)
        return pk

    def _get_card_badge(self, form: FeretUIForm) -> tuple[str | None, str]:
        """Resolve badge text and CSS class for grid card."""
        if not self.card_badge_field or not hasattr(
            form, self.card_badge_field
        ):
            return None, "is-secondary"
        b_field = getattr(form, self.card_badge_field)
        badge = self._format_card_field_value(b_field)
        b_val = str(b_field.data or "").lower()
        if b_val in ("done", "active", "confirmed", "success"):
            return badge, "is-success"
        if b_val in ("draft", "pending", "in_progress"):
            return badge, "is-info"
        if b_val in ("cancelled", "canceled", "rejected", "error"):
            return badge, "is-danger"
        return badge, "is-secondary"

    def _get_card_fields(self, form: FeretUIForm) -> list[dict[str, str]]:
        """Extract body field details for grid card."""
        body_fields = self.card_body_fields
        if body_fields is None:
            body_fields = [
                f.name
                for f in form
                if f.name not in ("pk", "id", self.card_title_field or "")
                and f.type
                not in ("HiddenField", "One2ManyField", "Many2ManyField")
            ][:4]

        fields_data = []
        for b_name in body_fields:
            if hasattr(form, b_name):
                f = getattr(form, b_name)
                lbl = f.label.text if f.label else b_name
                fields_data.append(
                    {
                        "name": b_name,
                        "label": str(lbl),
                        "value": self._format_card_field_value(f),
                    }
                )
        return fields_data

    def _build_card(
        self: "GridView",
        form: FeretUIForm,
        feretui: "FeretUI",
    ) -> dict[str, Any]:
        """Build dictionary of card presentation details from a form."""
        pk = (
            str(form.pk.data)
            if hasattr(form, "pk") and form.pk.data is not None
            else ""
        )
        title = self._get_card_title(form, pk)

        image_url = None
        if self.card_image_field and hasattr(form, self.card_image_field):
            img_val = getattr(form, self.card_image_field).data
            if img_val:
                image_url = str(img_val)

        badge, badge_class = self._get_card_badge(form)
        fields_data = self._get_card_fields(form)

        target = self.do_click_on_entry_redirect_to or "read"
        url = (
            f"?page=resource&resource={self.resource.code}"
            f"&view={target}&pk={pk}"
        )
        goto_url = (
            f"{feretui.base_url}/action/goto?page=resource&resource="
            f"{self.resource.code}&view={target}&pk={pk}"
        )

        return {
            "pk": pk,
            "title": html.escape(title),
            "image_url": image_url,
            "badge": html.escape(badge) if badge else None,
            "badge_class": badge_class,
            "fields": fields_data,
            "url": url,
            "goto_url": goto_url,
        }

    def render(
        self: "GridView",
        feretui: "FeretUI",
        session: Session,
        options: dict,
    ) -> Markup:
        """Render the grid view."""
        kwargs = self.render_kwargs(feretui, session, options)
        dataset = kwargs.get("dataset", {})
        forms = dataset.get("forms", [])

        # Filter by search if provided
        search_query = (options.get("search") or "").strip()
        if search_query:
            filtered_forms = []
            for form in forms:
                match = False
                for field in form:
                    if (
                        field.data
                        and search_query.lower() in str(field.data).lower()
                    ):
                        match = True
                        break
                if match:
                    filtered_forms.append(form)
            forms = filtered_forms

        cards = [self._build_card(f, feretui) for f in forms]

        return Markup(
            feretui.render_template(
                session,
                "feretui-resource-grid",
                cards=cards,
                **kwargs,
            )
        )


class GridResource:
    """Resource mixin providing Grid view support."""

    default_view: str = "grid"
    MetaViewGrid = DefaultViewGrid

    def build_view(
        self: "GridResource",
        view_cls_name: str,
    ) -> Resource:
        """Return view instance for MetaViewGrid."""
        if view_cls_name.startswith("MetaViewGrid"):
            meta_view_cls = self.get_meta_view_class(view_cls_name)
            meta_view_cls.append(GridView)
            view_cls = type(
                "GridView",
                tuple(meta_view_cls),
                {},
            )
            if not self.default_view:
                self.default_view = view_cls.code

            return view_cls(self)

        return super().build_view(view_cls_name)


class GridCRUDResource(
    GridResource,
    CResource,
    RResource,
    UResource,
    DResource,
    Resource,
):
    """Composite shortcut providing Grid, Create, Read, Update, Delete views."""

    default_view = "grid"


GridCRUD = GridCRUDResource
