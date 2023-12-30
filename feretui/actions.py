from typing import TYPE_CHECKING

from pydantic import ValidationError

from feretui.exceptions import ResourceRouterError
from feretui.helper import action_validator, session_validator
from feretui.request import Request
from feretui.response import Response
from feretui.schema import format_errors

if TYPE_CHECKING:
    from feretui.feretui import FeretUI


@action_validator(method=Request.GET)
def action_goto_page(
    feret: "FeretUI",
    request: Request,
    page: str,
) -> str:
    options = request.query.copy()
    options.update({'page': page})
    # WARN: options can be modified by the page
    body = feret.get_page(page)(feret, request.session, options)
    url = request.get_url_from_dict(options)
    return Response(
        body,
        headers={
            'HX-Push-Url': url,
        }
    )


@action_validator(method=Request.GET)
def action_render_page(
    feret: "FeretUI",
    request: Request
) -> str:
    page = request.query.get('page', ['homepage'])[0]
    return Response(
        feret.get_page(page)(feret, request.session, request.query),
    )


@action_validator()
def action_resource_router(
    feret: "FeretUI",
    request: Request,
    router: str,
) -> str:
    resourcecode = request.query['resource'][0]
    Resource = feret.get_resource(resourcecode)
    attr = f'_router_{router}'
    if not hasattr(Resource, attr):
        raise ResourceRouterError(f"No router found for : {router}")

    return getattr(Resource, attr)(feret, request)


@action_validator(
    method=Request.POST,
    body_validator=session_validator('LoginValidator'),
)
def action_login_password(
    feret: "FeretUI",
    request: Request
) -> str:
    try:
        request.session.login(**dict(request.deserialized_body))
        qs = request.get_query_string_from_current_url()
        if qs.get('page') == ['login']:
            headers = {
                'HX-Redirect': '/?page=homepage',
            }
        else:
            headers = {
                'HX-Refresh': 'true',
            }

        return Response('', headers=headers)
    except ValidationError as e:
        return Response(
            feret.load_page_template(
                request.session,
                'feretui-page-pydantic-failed',
                errors=format_errors(e.errors()),
            )
        )
    except Exception:
        return Response(
            feret.load_page_template(
                request.session,
                'feretui-page-login-failed'
            )
        )


@action_validator(
    method=Request.POST,
    body_validator=session_validator('SignupValidator'),
)
def action_login_signup(
    feret: "FeretUI",
    request: Request
) -> str:
    try:
        redirect = request.session.signup(**dict(request.deserialized_body))
        if redirect:
            qs = request.get_query_string_from_current_url()
            if qs.get('page') == ['login']:
                headers = {
                    'HX-Redirect': '/?page=homepage',
                }
            else:
                headers = {
                    'HX-Refresh': 'true',
                }
        else:
            headers = {}

        return Response(
            feret.load_page_template(
                request.session,
                'feretui-page-signup-success',
            ),
            headers=headers
        )
    except ValidationError as e:
        return Response(
            feret.load_page_template(
                request.session,
                'feretui-page-pydantic-failed',
                errors=format_errors(e.errors()),
            )
        )
    except Exception:
        return Response(
            feret.load_page_template(
                request.session,
                'feretui-page-error-500'
            )
        )


@action_validator(method=Request.POST)
def action_logout(feret: "FeretUI", request: Request) -> str:
    request.session.logout()
    url = request.get_url_from_dict({})
    return Response('', headers={'HX-Redirect': url})
