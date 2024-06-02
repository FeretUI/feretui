# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Module feretui.helper.

The helper is function to help the integration of the client in an another
project.

* :func:`.action_validator`: Decorator to validate the call of the action
  callback
* :func:`.action_for_authenticated_user`: The action can be call only
  by the authenticated user
* :func:`.action_for_unauthenticated_user`: The action can be call only
  by the unauthenticated user
* :func:`.page_for_authenticated_user_or_goto`: Decorator to protect the
  accebility of one page, and allow this page only for a user.
* :func:`.page_for_unauthenticated_user_or_goto`: Decorator to protect the
  accebility of one page, and allow this page only if the user is not
  authenticated.
* :func:`.menu_for_authenticated_user`: Callback to return
  if the user is authenticated.
* :func:`.menu_for_unauthenticated_user`: Callback to return
  if the user is authenticated.
* :func:`.menu_for_all_users`: No restriction
  if the user is authenticated.
"""
from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING

from feretui.exceptions import (
    ActionUserIsAuthenticatedError,
    ActionUserIsNotAuthenticatedError,
    ActionValidatorError,
)
from feretui.request import RequestMethod
from feretui.response import Response
from feretui.session import Session

if TYPE_CHECKING:
    from feretui.feretui import FeretUI


def action_validator(
    methods: list[RequestMethod] = None,
) -> Callable:
    """Validate the action callback.

    ::

        @myferet.register_action
        @action_validator(methods=[RequestMethod.POST])
        def my_action(feretui, request):
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
            feret: "FeretUI",
            request: Response,
        ) -> Response:
            if methods is not None and request.method not in methods:
                raise ActionValidatorError(
                    f"The received method is {request.method} "
                    f"but waiting method {methods}",
                )

            response = func(feret, request)
            if not isinstance(response, Response):
                raise ActionValidatorError(
                    f"The response '{response}' is not an instance of Response",
                )

            return response

        return wrapper_call

    return wrapper_function


def action_for_authenticated_user(func: Callable) -> Callable:
    """Raise an exception if the user is not authenticated.

    It is a decorator

    ::

        @myferet.register_action
        @action_for_authenticated_user
        def my_action(feretui, request):
            return Response(...)

    :return: a wrapper function:
    :rtype: Callable
    :exception: ActionUserIsNotAuthenticatedError
    """
    @wraps(func)
    def wrapper_call(
        feret: "FeretUI",
        request: Response,
    ) -> Response:
        if request.session.user is None:
            raise ActionUserIsNotAuthenticatedError(
                "The action is called by an unauthenticated user",
            )

        return func(feret, request)

    return wrapper_call


def action_for_unauthenticated_user(func: Callable) -> Callable:
    """Raise an exception if the user is authenticated.

    It is a decorator

    ::

        @myferet.register_action
        @action_for_unauthenticated_user
        def my_action(feretui, request):
            return Response(...)

    :return: a wrapper function:
    :rtype: Callable
    :exception: ActionUserIsAuthenticatedError
    """
    @wraps(func)
    def wrapper_call(
        feret: "FeretUI",
        request: Response,
    ) -> Response:
        if request.session.user:
            raise ActionUserIsAuthenticatedError(
                "The action is called by an authenticated user",
            )

        return func(feret, request)

    return wrapper_call


def page_for_authenticated_user_or_goto(
    fallback_page: str | Callable,
) -> Callable:
    """Display the decorated page if the user is authenticated.

    In the case or the user is not autenticated. The returned page
    is the fallback page.

    ::

        @page_for_authenticated_user_or_goto('404')
        def my_page(myferet, session, options):
            ...

    :param fallback_page: The page if the user is not authenticated
    :type fallback_page: str or the callable page
    :return: a decorator
    :rtype: Callable
    """

    def wrap_func(func: Callable) -> Callable:

        @wraps(func)
        def wrap_call(
            feretui: "FeretUI",
            session: Session,
            options: dict,
        ) -> str:
            if session.user:
                return func(feretui, session, options)

            page = fallback_page
            if isinstance(fallback_page, str):
                page = feretui.get_page(fallback_page)

            return page(feretui, session, options)

        return wrap_call

    return wrap_func


def page_for_unauthenticated_user_or_goto(
    fallback_page: str | Callable,
) -> Callable:
    """Display the decorated page if the user is not authenticated.

    In the case or the user is autenticated. The returned page
    is the fallback page.

    ::

        @page_for_unauthenticated_user_or_goto('forbidden')
        def my_page(myferet, session, options):
            ...

    :param fallback_page: The page if the user is authenticated
    :type fallback_page: str or the callable page
    :return: a decorator
    :rtype: Callable
    """

    def wrap_func(func: Callable) -> Callable:

        @wraps(func)
        def wrap_call(
            feretui: "FeretUI",
            session: Session,
            options: dict,
        ) -> str:
            if session.user is None:
                return func(feretui, session, options)

            page = fallback_page
            if isinstance(fallback_page, str):
                page = feretui.get_page(fallback_page)

            return page(feretui, session, options)

        return wrap_call

    return wrap_func


def menu_for_authenticated_user(session: Session) -> bool:
    """Return True if the user is authenticated.

    See the :class:`feretui.menus.Menu`

    :param session: The user session
    :type session: :class:`feretui.session.Session`
    :return: True if the user is authenticated
    :rtype: bool
    """
    return bool(session.user)


def menu_for_unauthenticated_user(session: Session) -> bool:
    """Return True if the user is not authenticated.

    See the :class:`feretui.menus.Menu`

    :param session: The user session
    :type session: :class:`feretui.session.Session`
    :return: True if the user is not authenticated
    :rtype: bool
    """
    return not session.user


def menu_for_all_users(session: Session) -> bool:  # noqa: ARG001
    """Return always True.

    See the :class:`feretui.menus.Menu`

    :param session: The user session
    :type session: :class:`feretui.session.Session`
    :return: True if the user is not authenticated
    :rtype: bool
    """
    return True
