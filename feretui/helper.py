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
"""
from functools import wraps
from typing import TYPE_CHECKING

from feretui.exceptions import ActionValidatorError
from feretui.request import RequestMethod
from feretui.response import Response

if TYPE_CHECKING:
    from feretui.feretui import FeretUI


def action_validator(
    methods: list[RequestMethod] = None,
) -> Response:
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

    def wrapper_function(func):
        @wraps(func)
        def wrapper_call(
            feret: "FeretUI",
            request: Response,
        ):
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
