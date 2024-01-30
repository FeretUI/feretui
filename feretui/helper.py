from functools import wraps
from typing import TYPE_CHECKING

from pydantic import BaseModel

from feretui.exceptions import ActionValidatorError
from feretui.request import RequestMethod
from feretui.response import Response

if TYPE_CHECKING:
    from feretui.feretui import FeretUI


def action_validator(
    method: RequestMethod = None,
    body_validator: BaseModel = None,
    query_string_validator: BaseModel = None,
) -> Response:
    def wrapper_function(func):
        @wraps(func)
        def wrapper_call(
            feret: "FeretUI",
            request: Response,
            *a
        ):
            if method is not None and request.method != method:
                raise ActionValidatorError(
                    f"The received method is {request.method} "
                    f"but waiting method {method}"
                )

            request.body_validator = body_validator
            request.query_string_validator = query_string_validator
            return func(feret, request, *a)

        return wrapper_call

    return wrapper_function
