from functools import wraps
from typing import TYPE_CHECKING

from pydantic import BaseModel

from feretui.exceptions import ActionValidatorError
from feretui.request import Request, RequestMethod
from feretui.response import Response
from feretui.session import Session

if TYPE_CHECKING:
    from feretui.feretui import FeretUI


def authenticated_or_404(func):
    @wraps(func)
    def wrap(feret: "FeretUI", session: Session, options: dict):
        if session.user:
            return func(feret, session, options)

        return feret.get_page('404')(feret, session, options)

    return wrap


def authenticated_or_login(func):
    @wraps(func)
    def wrap(feret: "FeretUI", session: Session, options: dict):
        if session.user:
            return func(feret, session, options)

        page = feret.get_callback('feretui_default_authentication')()
        return feret.get_page(page)(feret, session, options)

    return wrap


def authenticated_or_forbidden(func):
    @wraps(func)
    def wrap(feret: "FeretUI", session: Session, options: dict):
        if session.user:
            return func(feret, session, options)

        return feret.get_page('forbidden')(feret, session, options)

    return wrap


def unauthenticated_or_forbidden(func):
    @wraps(func)
    def wrap(feret: "FeretUI", session: Session, options: dict):
        if not session.user:
            return func(feret, session, options)

        return feret.get_page('forbidden')(feret, session, options)

    return wrap


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


def session_validator(validator: str):
    def wrapper(request: Request):
        if not hasattr(request.session, validator):
            raise ActionValidatorError(
                f"No Schema {validator} found on the session"
            )

        return getattr(request.session, validator)

    return wrapper
