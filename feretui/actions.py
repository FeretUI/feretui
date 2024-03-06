# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Module feretui.actions.

The actions is called by the :meth:`feretui.feretui.FeretUI.execute_action`.

The availlable actions are:

* :func:`.render`.
* :func:`.goto`.
"""
from typing import TYPE_CHECKING

from feretui.exceptions import ActionError
from feretui.helper import action_validator
from feretui.request import Request
from feretui.response import Response
from feretui.pages import login
from multidict import MultiDict

if TYPE_CHECKING:
    from feretui.feretui import FeretUI


@action_validator(methods=[Request.GET])
def render(
    feretui: "FeretUI",
    request: Request,
) -> str:
    """Render the page.

    the page is an entry in the query string of the request.

    :param feretui: The feretui client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param request: The request
    :type request: :class:`feretui.request.Request`
    :return: The page to display
    :rtype: :class:`feretui.response.Response`
    """
    page = request.query.get('page', ['homepage'])[0]
    return Response(
        feretui.get_page(page)(feretui, request.session, request.query),
    )


@action_validator(methods=[Request.GET])
def goto(
    feretui: "FeretUI",
    request: Request,
) -> str:
    """Render the page and change the url in the browser.

    the page is an entry in the query string of the request.

    If *in-aside* is in the querystring, It is mean that the page
    is rendering inside the page aside-menu and the url to push have to
    keep this information.

    :param feretui: The feretui client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param request: The request
    :type request: :class:`feretui.request.Request`
    :return: The page to display
    :rtype: :class:`feretui.response.Response`
    """
    options = request.query.copy()
    if 'page' not in options:
        raise ActionError('page in the query string is missing')

    page = options['page'][0]
    # WARN: options can be modified by the page
    body = feretui.get_page(page)(feretui, request.session, options)
    base_url = request.get_base_url_from_current_url()
    if options.get('in-aside'):
        options.update({
            'in-aside': [],
            'page': ['aside-menu'],
            'aside': options['in-aside'],
            'aside_page': [page],
        })
    url = request.get_url_from_dict(base_url=base_url, querystring=options)
    return Response(
        body,
        headers={
            'HX-Push-Url': url,
        },
    )


@action_validator(methods=[Request.POST])
def login_password(
    feret: "FeretUI",
    request: Request
) -> str:
    form = request.session.LoginForm(MultiDict(**request.body))
    if form.validate():
        request.session.login(**form.data)
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

    return Response(login(feret, request.session, {'form': form}))


@action_validator(methods=[Request.POST])
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


@action_validator(methods=[Request.POST])
def action_logout(feret: "FeretUI", request: Request) -> str:
    request.session.logout()
    url = request.get_url_from_dict({})
    return Response('', headers={'HX-Redirect': url})
