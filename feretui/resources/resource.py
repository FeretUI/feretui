# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Module feretui.resource.

The main class to create a resource.
"""

import inspect
from collections.abc import Callable
from copy import deepcopy
from typing import TYPE_CHECKING, Any

from markupsafe import Markup
from polib import POFile

from feretui.exceptions import ResourceError
from feretui.helper import (
    action_for_authenticated_user,
    menu_for_authenticated_user,
    page_for_authenticated_user_or_goto,
)
from feretui.menus import Menu, ToolBarMenu
from feretui.pages import login, page_404
from feretui.request import Request
from feretui.resources.view import View
from feretui.response import Response
from feretui.session import Session

if TYPE_CHECKING:
    from feretui.feretui import FeretUI
    from feretui.translation import Translation


class Resource:
    """Resource class."""

    code: str = None
    label: str = None
    menu: Menu = ToolBarMenu("", page="resource")
    menu_visibility: Callable = staticmethod(menu_for_authenticated_user)
    page_visibility: Callable = staticmethod(
        page_for_authenticated_user_or_goto(login),
    )
    action_security: Callable = staticmethod(action_for_authenticated_user)
    default_view: str = None

    class Form:
        """The Form class."""

    def __init__(self: "Resource") -> None:
        """Resource class."""
        self.views: dict[str, View] = {}

    def __str__(self: "Resource") -> str:
        """Return the resource as a string."""
        return f"<{self.__class__.__name__} code={self.code}>"

    def get_defaults(
        self: "Resource",
        session: Session,  # noqa: ARG002
    ) -> dict[str, Any]:
        """Return default form values for a new record.

        :param session: The user session
        :type session: :class:`feretui.session.Session`
        :return: Dictionary of default field values
        :rtype: dict[str, Any]
        """
        return {}

    def before_create(
        self: "Resource",
        session: Session,  # noqa: ARG002
        form: object,  # noqa: ARG002
    ) -> None:
        """Lifecycle hook executed before persisting a new record.

        :param session: The user session
        :type session: :class:`feretui.session.Session`
        :param form: Validated creation form
        """

    def after_create(
        self: "Resource",
        session: Session,  # noqa: ARG002
        pk: object,  # noqa: ARG002
    ) -> None:
        """Lifecycle hook executed after creating a new record.

        :param session: The user session
        :type session: :class:`feretui.session.Session`
        :param pk: Primary key of created record
        :type pk: object
        """

    def before_update(
        self: "Resource",
        session: Session,  # noqa: ARG002
        form: object,  # noqa: ARG002
    ) -> None:
        """Lifecycle hook executed before updating an existing record.

        :param session: The user session
        :type session: :class:`feretui.session.Session`
        :param form: Validated update form
        """

    def after_update(
        self: "Resource",
        session: Session,  # noqa: ARG002
        form: object,  # noqa: ARG002
    ) -> None:
        """Lifecycle hook executed after updating an existing record.

        :param session: The user session
        :type session: :class:`feretui.session.Session`
        :param form: Form with updated values
        """

    def before_delete(
        self: "Resource",
        session: Session,  # noqa: ARG002
        pks: list[object],  # noqa: ARG002
    ) -> None:
        """Lifecycle hook executed before deleting records.

        :param session: The user session
        :type session: :class:`feretui.session.Session`
        :param pks: Primary keys of records to delete
        :type pks: list[object]
        """

    def after_delete(
        self: "Resource",
        session: Session,  # noqa: ARG002
        pks: list[object],  # noqa: ARG002
    ) -> None:
        """Lifecycle hook executed after deleting records.

        :param session: The user session
        :type session: :class:`feretui.session.Session`
        :param pks: Primary keys of deleted records
        :type pks: list[object]
        """

    def get_view_switchers(
        self: "Resource",
        feretui: "FeretUI",
        session: Session,
        options: dict,
    ) -> list[dict[str, Any]]:
        """Return available collection view switcher buttons.

        :param feretui: The feretui instance
        :param session: The user session
        :param options: Current request query options
        :return: List of switcher dicts (view, label, icon, is_active, url,
            goto_url)
        """
        current_view = options.get("view", self.default_view)
        collection_views = [
            ("list", "List", "ti ti-list"),
            ("kanban", "Kanban", "ti ti-layout-kanban"),
            ("grid", "Grid", "ti ti-layout-grid"),
            ("calendar", "Calendar", "ti ti-calendar"),
            ("graph", "Graph", "ti ti-chart-bar"),
        ]
        available: list[dict[str, Any]] = []
        for view_code, label, icon in collection_views:
            if view_code in self.views:
                view_obj = self.views[view_code]
                if hasattr(view_obj, "is_visible") and not view_obj.is_visible(
                    session
                ):
                    continue
                opt = options.copy()
                opt["page"] = "resource"
                opt["resource"] = self.code
                opt["view"] = view_code
                opt.pop("pk", None)
                query_items = [f"{k}={v}" for k, v in opt.items()]
                qs = "&".join(query_items)
                url = f"/?{qs}"
                goto_url = f"{feretui.base_url}/action/goto?{qs}"
                available.append(
                    {
                        "view": view_code,
                        "label": label,
                        "icon": icon,
                        "is_active": (view_code == current_view),
                        "url": url,
                        "goto_url": goto_url,
                    }
                )

        return available if len(available) > 1 else []

    def export_catalog(
        self: "Resource",
        translation: "Translation",
        po: POFile,
    ) -> None:
        """Export the translations in the catalog.

        :param translation: The translation instance to add also inside it.
        :type translation: :class:`.Translation`
        :param po: The catalog instance
        :type po: PoFile_
        """
        po.append(translation.define(f"{self.context}:label", self.label))
        for view in self.views.values():
            view.export_catalog(translation, po)

    @classmethod
    def build(cls: "Resource") -> None:
        """Build the additional part of the resource."""
        if not cls.code:
            raise ResourceError("No code defined")

        if not cls.label:
            raise ResourceError("No label defined")

        cls.menu = deepcopy(cls.menu)

        if not cls.menu.label:
            cls.menu.label = cls.label

        cls.menu.visible_callback = cls.menu_visibility

        cls.menu.querystring["resource"] = cls.code
        cls.context = f"resource:{cls.code}"
        if (
            cls.page_visibility is None
            and "action_security" not in cls.__dict__
        ):
            cls.action_security = None

        resource = cls()
        for attr in dir(cls):
            if attr.startswith("MetaView") and inspect.isclass(
                getattr(cls, attr),
            ):
                view = resource.build_view(attr)
                if view:
                    resource.views[view.code] = view

        return resource

    def get_meta_view_class(self: "Resource", view_cls_name: str) -> list:
        """Return all the meta view class.

        :param view_cls_name: The name of the meta class
        :type view_cls_name: Class
        :return: list of the class
        :rtype: list
        """
        return [
            getattr(cls, view_cls_name)
            for cls in self.__class__.__mro__
            if view_cls_name in cls.__dict__
        ]

    def build_view(
        self: "Resource",
        view_cls_name: str,
    ) -> View:
        """Return the view instance in fonction of the MetaView attributes.

        :param view_cls_name: name of the meta attribute
        :type view_cls_name: str
        :return: An instance of the view
        :rtype: :class:`feretui.resources.view.View`
        """

    def get_label(
        self: "Resource",
        feretui: "FeretUI",
        session: Session,
    ) -> str:
        """Return the translated label.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The Session
        :type session: :class:`feretui.session.Session`
        :rtype: str.
        """
        return feretui.translation.get(
            session.lang,
            f"{self.context}:label",
            self.label,
        )

    def render(
        self: "Resource",
        feretui: "FeretUI",
        session: Session,
        options: dict,  # noqa: ARG002
    ) -> str:
        """Render the resource.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The Session
        :type session: :class:`feretui.session.Session`
        :param options: The options come from the body or the query string
        :type options: dict
        :return: The html page in
        :rtype: str.
        """
        viewcode = options.setdefault("view", self.default_view)
        if isinstance(viewcode, list):
            viewcode = viewcode[0]

        if not viewcode:
            func = page_404
        else:
            if (
                viewcode == "update"
                and "update" not in self.views
                and "edit" in self.views
            ):
                viewcode = "edit"
            elif (
                viewcode == "edit"
                and "edit" not in self.views
                and "update" in self.views
            ):
                viewcode = "update"
            view = self.views.get(viewcode)
            func = page_404 if not view else view.render

        if self.page_visibility:
            func = self.page_visibility(func)

        return Markup(
            feretui.render_template(
                session,
                "feretui-page-resource",
                view=Markup(func(feretui, session, options)),
                code=self.code,
            ),
        )

    def _resolve_viewcode(
        self: "Resource",
        options: dict,
        qs: dict,
        action: str | None,
        query: dict,
    ) -> str | None:
        """Resolve view code with update/edit aliasing and fallback."""
        viewcode = options.get("view") or query.get("view") or qs.get("view")
        if isinstance(viewcode, list):
            viewcode = viewcode[0]

        if (
            viewcode == "update"
            and "update" not in self.views
            and "edit" in self.views
        ):
            return "edit"
        if (
            viewcode == "edit"
            and "edit" not in self.views
            and "update" in self.views
        ):
            return "update"

        if not viewcode and action in ("save", "onchange"):
            pk_val = options.get("pk") or qs.get("pk")
            if pk_val:
                return "edit" if "edit" in self.views else self.default_view
            return "create" if "create" in self.views else self.default_view

        return viewcode

    def router(
        self: "Resource",
        feretui: "FeretUI",
        request: Request,
    ) -> Response:
        """Resource entry point actions.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param request: The request
        :type request: :class:`feretui.request.Request`
        :return: The page to display
        :rtype: :class:`feretui.response.Response`
        """
        qs = request.get_query_string_from_current_url()
        options = (
            request.query if request.method == Request.GET else request.params
        ) or {}
        action = options.get("action") or request.query.get("action")
        if isinstance(action, list):
            action = action[0]

        if not action:
            raise ResourceError("No action defined in the query string")

        viewcode = self._resolve_viewcode(
            options,
            qs,
            action,
            request.query,
        )

        view = self.views.get(viewcode) if viewcode else None
        if view and hasattr(view, action):
            func = getattr(view, action)
        elif hasattr(self, action):
            func = getattr(self, action)
        else:
            if not viewcode:
                raise ResourceError("No view defined in the query string")

            if not view:
                raise ResourceError(f"No view {viewcode} defined in {self}")

            raise ResourceError(
                f"{self.code} - {viewcode} has no method {action}",
            )

        if self.action_security:
            func = self.action_security(func)

        return func(feretui, request)
