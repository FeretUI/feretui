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

.. _BaseModel: https://docs.pydantic.dev/latest/api/base_model/
"""
from functools import wraps
from typing import TYPE_CHECKING

from pydantic import BaseModel

from feretui.exceptions import ActionValidatorError
from feretui.request import RequestMethod
from feretui.response import Response

if TYPE_CHECKING:
    from feretui.feretui import FeretUI


def action_validator(
    methods: list[RequestMethod] = None,
    pydantic_body_validator: BaseModel = None,
    pydantic_querystring_validator: BaseModel = None,
) -> Response:
    """Validate the action callback.

    This helper add a validation during the execution of the action. The
    validation could be done on the request method or with pydantic on
    the querystring or body.

    ::

        @myferet.register_action
        @action_validator(methods=[RequestMethod.POST])
        def my_action(feretui, request, *myargs):
            return Response(...)

    .. note::

        The response of the callback must be a
        :class:`feretui.response.Response`

    :param methods: The request methods of the action, if None the action can
                    be called with any request method, else allow only the
                    defined request methods.
    :type methods: list[:class:`feretui.request.RequestMethod`]
    :param pydantic_body_validator: A validator class to validate and
                                    format the body of the request.
    :type pydantic_body_validator: BaseModel_
    :param pydantic_querystring_validator: A validator class to validate and
                                           format the querystring from the
                                           request.
    :type pydantic_querystring_validator: BaseModel_
    :return: a wrapper function:
    :rtype: Callable
    """
    def wrapper_function(func):
        @wraps(func)
        def wrapper_call(
            feret: "FeretUI",
            request: Response,
            *a
        ):
            if (
                methods is not None
                and (
                    (
                        isinstance(methods, RequestMethod | str)
                        and request.method != methods
                    ) or (
                        request.method not in methods
                    )
                )
            ):
                raise ActionValidatorError(
                    f"The received method is {request.method} "
                    f"but waiting method {methods}"
                )

            request.pydantic_body_validator = pydantic_body_validator
            request.pydantic_querystring_validator = (
                pydantic_querystring_validator
            )
            return func(feret, request, *a)

        return wrapper_call

    return wrapper_function
