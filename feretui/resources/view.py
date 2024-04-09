# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Module feretui.responses.view.

The main class to construct a view
"""
import urllib
from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING

from polib import POFile

from feretui.exceptions import ViewActionError, ViewFormError
from feretui.form import FeretUIForm
from feretui.pages import page_404
from feretui.request import Request, RequestMethod
from feretui.response import Response
from feretui.session import Session
from feretui.response import Response

if TYPE_CHECKING:
    from feretui.feretui import FeretUI
    from feretui.resources.resource import Resource
    from feretui.translation import Translation


def view_action_validator(
    methods: list[RequestMethod] = None,
) -> Callable:
    """Validate the action callback.

    ::

        class MyView:

            @view_action_validator(methods=[RequestMethod.POST])
            def my_action(self, feretui, request):
                return Response(...)

    .. note::

        The response of the callback must be a
        :class:`feretui.response.Response`

    :param methods: The request methods of the action, if None the action can
                    be called with any request method, else allow only the
                    defined request methods.
    :type methods: list[:class:`feretui.request.RequestMethod`]
    :return: a wrapper function:
    :rtype: Callable
    """
    if methods is not None and not isinstance(methods, list):
        methods = [methods]

    def wrapper_function(func: Callable) -> Callable:
        @wraps(func)
        def wrapper_call(
            self: "View",
            feret: "FeretUI",
            request: Response,
        ) -> Response:
            if methods is not None and request.method not in methods:
                raise ViewActionError(
                    f"The received method is {request.method} "
                    f"but waiting method {methods}",
                )

            response = func(self, feret, request)
            if not isinstance(response, Response):
                raise ViewActionError(
                    f"The response '{response}' is not an instance of Response",
                )

            return response

        return wrapper_call

    return wrapper_function


class ViewForm:
    """View Form for translation."""

    @classmethod
    def get_context(cls: "ViewForm") -> str:
        """Return the context for the translation."""
        if hasattr(cls, 'view'):
            return f'{cls.view.context}:form:{cls.__name__}'

        return ''


class View:
    """View class."""

    code: str = None

    class Form:
        """Form class."""

    def __init__(self: "View", resource: "Resource") -> None:
        """View class.

        :param resource: The resource instance
        :type resource: :class:`feretui.resources.resource.Resource`
        """
        self.resource = resource
        self.context = resource.context + f':view:{self.code}'
        self.form_cls = self.get_form_cls()

    def get_label(self: "View") -> str:
        """Return the translated label."""
        return self.resource.get_label()

    def export_catalog(
        self: "View",
        translation: "Translation",
        po: POFile,
    ) -> None:
        """Export the translations in the catalog.

        :param translation: The translation instance to add also inside it.
        :type translation: :class:`.Translation`
        :param po: The catalog instance
        :type po: PoFile_
        """
        self.form_cls.export_catalog(translation, po)

    def render(
        self: "View",
        feretui: "FeretUI",
        session: Session,
        options: dict,
    ) -> str:
        """Render the view.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The Session
        :type session: :class:`feretui.session.Session`
        :param options: The options come from the body or the query string
        :type options: dict
        :return: The html page in
        :rtype: str.
        """
        return page_404(feretui, session, options)

    def get_transition_url(
        self: "View",
        feretui: "FeretUI",
        options: dict,
        **kwargs: dict[str, str],
    ) -> str:
        """Return the query string of a transition.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param options: the main query string
        :type options: dict
        :param kwargs: the new entries
        :type kwargs: dict
        :return: The querystring
        :rtype: str.
        """
        options = options.copy()
        options['action'] = 'goto'
        for key, value in kwargs.items():
            if value is None:
                options.pop(key, None)
            elif isinstance(value, list):
                options[key] = value
            else:
                options[key] = [value]

        return (
            f'{ feretui.base_url }/action/resource?'
            f'{urllib.parse.urlencode(options, doseq=True)}'
        )

    @view_action_validator(methods=Request.GET)
    def goto(self: "View", feretui: "FeretUI", request: Request) -> Response:
        """Change the view type and renderer it.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param request: The request
        :type request: :class:`feretui.request.Request`
        :return: The page to display
        :rtype: :class:`feretui.response.Response`
        """
        options = request.query.copy()
        options.pop('action', None)
        view = options.get('view')
        if isinstance(view, list):
            view = view[0]

        base_url = request.get_base_url_from_current_url()
        url = request.get_url_from_dict(base_url, options)

        if view not in self.resource.views:
            body = page_404(feretui, request.session, options)
        else:
            body = self.resource.views[view].render(
                feretui,
                request.session,
                options,
            )

        return Response(
            body,
            headers={
                'HX-Push-Url': url,
            },
        )

    def get_transition_url(
        self: "View",
        feretui: "FeretUI",
        options: dict,
        **kwargs: dict[str, str],
    ) -> str:
        """Return the query string of a transition.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param options: the main query string
        :type options: dict
        :param kwargs: the new entries
        :type kwargs: dict
        :return: The querystring
        :rtype: str
        """
        options = options.copy()
        options['action'] = 'goto'
        for key, value in kwargs.items():
            if value is None:
                options.pop(key, None)
            elif isinstance(value, list):
                options[key] = value
            else:
                options[key] = [value]

        return (
            f'{ feretui.base_url }/action/resource?'
            f'{urllib.parse.urlencode(options, doseq=True)}'
        )

    def goto(self, feretui, request):
        # TODO get validator
        options = request.query.copy()
        options.pop('action', None)
        view = options.get('view')
        if isinstance(view, list):
            view = view[0]

        base_url = request.get_base_url_from_current_url()
        url = request.get_url_from_dict(base_url, options)

        return Response(
            self.resource.views[view].render(feretui, request.session, options),
            headers={
                'HX-Push-Url': url,
            },
        )

    def get_form_cls(self: "View") -> FeretUIForm:
        """Return the Form for the view."""
        res = type(
            f'Form_{self.resource.code}_{self.code}',
            (self.Form, self.resource.Form, ViewForm, FeretUIForm),
            {'view': self},
        )
        if not hasattr(res, 'pk'):
            raise ViewFormError(f'The form {res} has no pk')

        return res
