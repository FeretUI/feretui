from typing import TYPE_CHECKING

from feretui.helper import action_validator
from feretui.request import Request
from feretui.response import Response

if TYPE_CHECKING:
    from feretui.feretui import FeretUI


@action_validator(methods=[Request.GET])
def render(
    feret: "FeretUI",
    request: Request
) -> str:
    page = request.query.get('page', ['homepage'])[0]
    return Response(
        feret.get_page(page)(feret, request.session, request.query),
    )


@action_validator(methods=[Request.GET])
def goto(
    feret: "FeretUI",
    request: Request,
) -> str:
    options = request.query.copy()
    page = options['page'][0]
    # WARN: options can be modified by the page
    body = feret.get_page(page)(feret, request.session, options)
    base_url = request.get_base_url_from_current_url()
    url = request.get_url_from_dict(base_url=base_url, querystring=options)
    return Response(
        body,
        headers={
            'HX-Push-Url': url,
        }
    )
