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
from typing import TYPE_CHECKING

from markupsafe import Markup
from polib import POFile

from feretui.exceptions import ResourceError
from feretui.helper import (
    action_for_authenticated_user,
    menu_for_authenticated_user,
    page_for_authenticated_user_or_goto,
)
from feretui.menus import Menu, ToolBarMenu
from feretui.pages import page_404
from feretui.request import Request
from feretui.resources.view import View
from feretui.response import Response
from feretui.session import Session
from feretui.thread import local

if TYPE_CHECKING:
    from feretui.feretui import FeretUI
    from feretui.translation import Translation


class Resource:
    """Resource class."""

    code: str = None
    label: str = None
    menu: Menu = ToolBarMenu(
        '',
        page="resource",
        visible_callback=menu_for_authenticated_user,
    )
    page_security: Callable = staticmethod(
        page_for_authenticated_user_or_goto(page_404))
    action_security: Callable = staticmethod(action_for_authenticated_user)
    default_view: str = None

    class Form:
        """The Form class."""

    def __init__(self: "Resource") -> None:
        """Resource class."""
        self.views: dict[str, View] = {}

    def __str__(self: "Resource") -> str:
        """Return the resource as a string."""
        return f'<{self.__class__.__name__} code={self.code}>'

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
        po.append(translation.define(f'{self.context}:label', self.label))
        for view in self.views.values():
            view.export_catalog(translation, po)

    @classmethod
    def build(cls: "Resource") -> None:
        """Build the additional part of the resource."""
        if not cls.code:
            raise ResourceError('No code defined')

        if not cls.label:
            raise ResourceError('No label defined')

        if not cls.menu.label:
            cls.menu.label = cls.label

        cls.menu.querystring['resource'] = cls.code
        cls.context = f'resource:{cls.code}'
        resource = cls()
        for attr in dir(cls):
            if (
                attr.startswith('MetaView')
                and inspect.isclass(getattr(cls, attr))
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
        return list({
            getattr(cls, view_cls_name)
            for cls in self.__class__.__mro__
            if hasattr(cls, view_cls_name)
        })

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

    def get_label(self: "Resource") -> None:
        """Return the translated label."""
        return local.feretui.translation.get(
            local.lang, f'{self.context}:label', self.label,
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
        viewcode = options.setdefault('view', self.default_view)
        if isinstance(viewcode, list):
            viewcode = viewcode[0]

        if not viewcode:
            func = page_404
        else:
            view = self.views.get(viewcode)
            func = page_404 if not view else view.render

        if self.page_security:
            func = self.page_security(func)

        return feretui.render_template(
            session,
            'feretui-page-resource',
            view=Markup(func(feretui, session, options)),
            code=self.code,
        )

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
            request.query
            if request.method == Request.GET
            else request.params
        )
        viewcode = qs.get('view')
        if isinstance(viewcode, list):
            viewcode = viewcode[0]

        if not viewcode:
            raise ResourceError('No view defined in the query string')

        view = self.views.get(viewcode)
        if not view:
            raise ResourceError(f'No view {viewcode} defined in {self}')

        action = options.get('action')
        if isinstance(action, list):
            action = action[0]

        if not action:
            raise ResourceError('No action defined in the query string')

        if not hasattr(view, action):
            raise ResourceError(
                f'{self.code} - {viewcode} has no method {action}')

        func = getattr(view, action)
        if self.action_security:
            func = self.action_security(func)

        return func(feretui, request)
