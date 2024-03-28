# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Module feretui.resource.

The resource is a set of View to représente one data.

* :class:`.Resource`

::

    myferet.register_resource(
        'code of the resource',
        'label',
    )
    class MyResource(Resource):
        pass
"""
from collections.abc import Callable
from typing import TYPE_CHECKING

from polib import POFile

from feretui.exceptions import ResourceError
from feretui.helper import (
    menu_for_authenticated_user,
    page_for_authenticated_user_or_goto,
)
from feretui.menus import Menu, ToolBarMenu
from feretui.pages import page_404
from feretui.request import Request
from feretui.response import Response
from feretui.session import Session

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
    page_security = staticmethod(page_for_authenticated_user_or_goto(page_404))
    action_security: Callable = None

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

    @classmethod
    def build(cls: "Resource") -> None:
        """Build the additional part of the resource."""
        if not cls.code:
            raise ResourceError('No code defined')

        if not cls.label:
            raise ResourceError('No label defined')

        if not cls.menu.label:
            cls.menu.label = cls.label

        cls.context = f'resource:{cls.code}'

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
        func = None

        if not func:
            func = page_404

        if self.page_security:
            return self.page_security(func)(feretui, session, options)

        return func(feretui, session, options)

    def router(
        self: "Resource",
        feretui: "FeretUI",  # noqa: ARG002
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
        if request.method in (Request.GET,):
            action = request.query.get('action')  # pragma: no cover
        else:
            action = request.params.get('action')

        if isinstance(action, list):
            action = action[0]  # pragma: no cover

        if not action:
            raise ResourceError('No action defined in the query string')

        return ''  # pragma: no cover
