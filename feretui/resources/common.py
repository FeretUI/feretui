# This file is a part of the FeretUI project
#
#    Copyright (C) 2023-2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""feretui.resources.common's module."""
from typing import TYPE_CHECKING

from markupsafe import Markup
from polib import POFile

from feretui.exceptions import ViewActionError
from feretui.request import Request
from feretui.resources.actions import Actionset, SelectedRowsAction
from feretui.response import Response
from feretui.session import Session

if TYPE_CHECKING:
    from feretui.feretui import FeretUI
    from feretui.translation import Translation


class MultiViewHeaderButtons:
    """MultiViewHeaderButtons class.

    Render the buttons for view multi.
    """

    def get_header_buttons(
        self: "MultiViewHeaderButtons",
        feretui: "FeretUI",
        session: Session,
        options: dict,
    ) -> list[Markup]:
        """Return the buttons for the multi view.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The Session
        :type session: :class:`feretui.session.Session`
        :param options: The options come from the body or the query string
        :type options: dict
        :return: The html pages
        :rtype: list[Markup]
        """
        res = []
        if self.create_button_redirect_to:
            res.append(
                Markup(feretui.render_template(
                    session,
                    'view-create-button',
                    create_view_qs=self.get_transition_querystring(
                        options,
                        view=self.create_button_redirect_to,
                    ),
                )),
            )

        return res


class ActionsMixinForView:
    """ActionsMixinForView class.

    Render the actions buttons aside
    """

    actions: list[Actionset] = []

    def __init__(
        self: "ActionsMixinForView",
        *args: tuple,
        **kwargs: dict,
    ) -> None:
        """ActionsMixinForView constructor."""
        super().__init__(*args, **kwargs)
        for actionset in self.actions:
            actionset.context = f'{self.context}:actionset'
            for action in actionset.actions:
                action.context = f'{self.context}:action:{action.method}'

    def export_catalog(
        self: "ActionsMixinForView",
        translation: "Translation",
        po: POFile,
    ) -> None:
        """Export the translations in the catalog.

        :param translation: The translation instance to add also inside it.
        :type translation: :class:`.Translation`
        :param po: The catalog instance
        :type po: PoFile_
        """
        super().export_catalog(translation, po)
        for actionset in self.actions:
            actionset.export_catalog(translation, po)

    def get_actions(
        self: "ActionsMixinForView",
        feretui: "FeretUI",
        session: Session,
    ) -> list[Markup]:
        """Return the actionset list renderer.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The Session
        :type session: :class:`feretui.session.Session`
        :return: The html pages
        :rtype: list[str]
        """
        return [
            actionset.render(feretui, session, self.resource.code, self.code)
            for actionset in self.actions
            if actionset.is_visible(session)
        ]

    def get_call_kwargs(
        self: "ActionsMixinForView",
        params: dict,  # noqa: ARG002
    ) -> dict:
        """Return the kwargs for the call with this view.

        :param params: request params
        :type params: dict
        :return: the kwargs from params
        :rtype: dict
        """
        return {}

    def call(
        self: "ActionsMixinForView",
        feretui: "FeretUI",
        request: Request,
    ) -> Response:
        """Call a method on the resource.

        .. note::

            If the method called return None then the
            view is rerendering

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param request: The request
        :type request: :class:`feretui.request.Request`
        :return: The page to display
        :rtype: :class:`feretui.response.Response`
        :exception: ViewActionError
        """
        if request.method is not Request.POST:
            raise ViewActionError(f'{request.method} is not the POST method')

        method = request.params.get('method')
        if isinstance(method, list):
            method = method[0]

        is_declared = False
        view_kwargs = {}
        for actionset in self.actions:
            for action in actionset.actions:
                if (
                    action.is_visible(request.session)
                    and action.method == method
                ):
                    if isinstance(action, SelectedRowsAction):
                        view_kwargs.update(self.get_call_kwargs(request.params))

                    is_declared = True
                    break

        if not is_declared:
            raise ViewActionError(
                f'The method {method} is not declared in the {self.resource}',
            )

        func = getattr(self.resource, method)
        res = func(feretui, request, **view_kwargs)
        if not res:
            qs = request.get_query_string_from_current_url()
            res = Response(Markup(self.render(feretui, request.session, qs)))

        if not isinstance(res, Response):
            res = Response(res)

        return res
