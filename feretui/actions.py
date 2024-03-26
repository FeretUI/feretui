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

* :func:`.goto`.
* :func:`.login_password`.
* :func:`.login_signup`.
* :func:`.logout`.
"""
from typing import TYPE_CHECKING

from feretui.exceptions import ActionError
from feretui.helper import (
    action_for_authenticated_user,
    action_for_unauthenticated_user,
    action_validator,
)
from feretui.pages import login, signup
from feretui.request import Request
from feretui.response import Response

if TYPE_CHECKING:
    from feretui.feretui import FeretUI


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
@action_for_unauthenticated_user
def login_password(
    feretui: "FeretUI",
    request: Request,
) -> str:
    """Login the user.

    Used the LoginForm passed in the request.session.

    :param feretui: The feretui client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param request: The request
    :type request: :class:`feretui.request.Request`
    :return: The page to display
    :rtype: :class:`feretui.response.Response`
    """
    form = request.session.LoginForm(request.form)
    if form.validate():
        try:
            request.session.login(form)
        except Exception as e:
            return Response(login(
                feretui,
                request.session,
                {'form': form, 'error': str(e)},
            ))

        qs = request.get_query_string_from_current_url()
        if qs.get('page') == ['login']:
            base_url = request.get_base_url_from_current_url()
            headers = {
                'HX-Redirect': f'{base_url}?page=homepage',
            }
        else:
            headers = {
                'HX-Refresh': 'true',
            }

        return Response('', headers=headers)

    return Response(login(feretui, request.session, {'form': form}))


@action_validator(methods=[Request.POST])
@action_for_unauthenticated_user
def login_signup(
    feretui: "FeretUI",
    request: Request,
) -> str:
    """Signup actions.

    Used the SignUpForm passed in the request.session.

    :param feretui: The feretui client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param request: The request
    :type request: :class:`feretui.request.Request`
    :return: The page to display
    :rtype: :class:`feretui.response.Response`
    """
    form = request.session.SignUpForm(request.form)
    if form.validate():
        try:
            redirect = request.session.signup(form)
        except Exception as e:
            return Response(signup(
                feretui,
                request.session,
                {'form': form, 'error': str(e)},
            ))
        if redirect:
            qs = request.get_query_string_from_current_url()
            if qs.get('page') == ['signup']:
                base_url = request.get_base_url_from_current_url()
                headers = {
                    'HX-Redirect': f'{base_url}?page=homepage',
                }
            else:
                headers = {
                    'HX-Refresh': 'true',
                }

            return Response('', headers=headers)

    return Response(signup(feretui, request.session, {'form': form}))


@action_validator(methods=[Request.POST])
@action_for_authenticated_user
def logout(
    feretui: "FeretUI",  # noqa: ARG001
    request: Request,
) -> str:
    """Logout actions.

    Used the SignUpForm passed in the request.session.

    :param feretui: The feretui client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param request: The request
    :type request: :class:`feretui.request.Request`
    :return: The page to display
    :rtype: :class:`feretui.response.Response`
    """
    request.session.logout()
    base_url = request.get_base_url_from_current_url()
    url = request.get_url_from_dict(base_url=base_url, querystring={})
    return Response('', headers={'HX-Redirect': url})


@action_validator()
def resource(
    feret: "FeretUI",
    request: Request,
) -> str:
    qs = request.get_query_string_from_current_url()
    resource = qs.get('resource', [None])[0]
    if not resource:
        raise Exception('No resource')

    Resource = feret.get_resource(resource)

    if request.method in (Request.GET,):
        action = request.query.get('action', [None])[0]
    else:
        action = request.params.get('action', [None])

    if not action:
        raise Exception('No action')

    attr = f'router_{action}'
    if not hasattr(Resource, attr):
        raise Exception(f"No router found for : {action}")

    return getattr(Resource, attr)(feret, request)
