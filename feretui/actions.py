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

from feretui.exceptions import ActionError, ResourceError
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
    if "page" not in options:
        raise ActionError("page in the query string is missing")

    page = options["page"][0]
    # WARN: options can be modified by the page
    body = feretui.get_page(page)(feretui, request.session, options)
    base_url = request.get_base_url_from_current_url()
    if options.get("in-aside"):
        options.update(
            {
                "in-aside": [],
                "page": ["aside-menu"],
                "aside": options["in-aside"],
                "aside_page": [page],
            },
        )
    url = request.get_url_from_dict(base_url=base_url, querystring=options)
    headers = {
        "HX-Push-Url": url,
    }
    title = feretui.get_title(request)
    if title:
        headers["HX-Title"] = title

    return Response(
        body,
        headers=headers,
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
            return Response(
                login(
                    feretui,
                    request.session,
                    {"form": form, "error": str(e)},
                ),
            )
        qs = request.get_query_string_from_current_url()
        if qs.get("page") == ["login"]:
            base_url = request.get_base_url_from_current_url()
            headers = {
                "HX-Redirect": f"{base_url}?page=homepage",
            }
        else:
            headers = {
                "HX-Refresh": "true",
            }

        return Response("", headers=headers)

    return Response(login(feretui, request.session, {"form": form}))


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
            return Response(
                signup(
                    feretui,
                    request.session,
                    {"form": form, "error": str(e)},
                ),
            )
        if redirect:
            qs = request.get_query_string_from_current_url()
            if qs.get("page") == ["signup"]:
                base_url = request.get_base_url_from_current_url()
                headers = {
                    "HX-Redirect": f"{base_url}?page=homepage",
                }
            else:
                headers = {
                    "HX-Refresh": "true",
                }

            return Response("", headers=headers)

    return Response(signup(feretui, request.session, {"form": form}))


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
    return Response("", headers={"HX-Redirect": url})


@action_validator()
def resource(
    feretui: "FeretUI",
    request: Request,
) -> str:
    """Resource entry point actions.

    Used the SignUpForm passed in the request.session.

    :param feretui: The feretui client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param request: The request
    :type request: :class:`feretui.request.Request`
    :return: The page to display
    :rtype: :class:`feretui.response.Response`
    """
    qs = request.get_query_string_from_current_url()
    code = qs.get("resource", [None])[0]
    if not code:
        raise ResourceError("No resource in the query string")

    resource = feretui.get_resource(code)
    return resource.router(feretui, request)


@action_validator(methods=[Request.GET])
def modal(
    feretui: "FeretUI",
    request: Request,
) -> Response:
    """Render a resource view inside a stackable modal dialog.

    :param feretui: The feretui client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param request: The request
    :type request: :class:`feretui.request.Request`
    :return: The modal dialog html fragment
    :rtype: :class:`feretui.response.Response`
    """
    import uuid

    from markupsafe import Markup

    options = request.query.copy()
    code = (
        options.get("resource", [None])[0]
        if isinstance(options.get("resource"), list)
        else options.get("resource")
    )
    if not code:
        raise ActionError("No resource in the query string")

    resource_obj = feretui.get_resource(code)
    view_code = (
        options.get("view", ["create"])[0]
        if isinstance(options.get("view"), list)
        else options.get("view", "create")
    )
    if view_code not in resource_obj.views:
        raise ActionError(f"View {view_code} not found for resource {code}")

    title = (
        options.get("title", [None])[0]
        if isinstance(options.get("title"), list)
        else options.get("title")
    )
    if not title:
        title = f"{resource_obj.label} - {view_code.capitalize()}"

    modal_size = (
        options.get("modal_size", ["normal"])[0]
        if isinstance(options.get("modal_size"), list)
        else options.get("modal_size", "normal")
    )
    target_field = (
        options.get("target_field", [""])[0]
        if isinstance(options.get("target_field"), list)
        else options.get("target_field", "")
    )

    clean_options = {
        k: v[0] if isinstance(v, list) else v for k, v in options.items()
    }
    clean_options["in_modal"] = "1"
    content = resource_obj.views[view_code].render(
        feretui, request.session, clean_options
    )

    modal_id = uuid.uuid4().hex[:8]
    html = feretui.render_template(
        request.session,
        "feretui-modal-dialog",
        modal_id=modal_id,
        title=title,
        content=Markup(content),
        modal_size=modal_size,
        target_field=target_field,
    )
    return Response(html)


@action_validator(methods=[Request.GET, Request.POST])
def close_modal(
    feretui: "FeretUI",  # noqa: ARG001
    request: Request,  # noqa: ARG001
) -> Response:
    """Close the top modal dialog.

    :param feretui: The feretui client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param request: The request
    :type request: :class:`feretui.request.Request`
    :return: Response with closeModal trigger header
    :rtype: :class:`feretui.response.Response`
    """
    return Response("", status_code=200, headers={"HX-Trigger": "closeModal"})


def _extract_active_ids(options: dict[str, object]) -> list[str]:
    """Extract active record IDs from request options."""
    if "active_ids" in options:
        val = options["active_ids"]
        return val if isinstance(val, list) else [str(val)]
    if "pk" in options:
        val = options["pk"]
        return val if isinstance(val, list) else [str(val)]

    active: list[str] = []
    for k, v in options.items():
        if k.startswith("selected-rows-"):
            active.extend(v if isinstance(v, list) else [str(v)])
    return active


@action_validator(methods=[Request.GET, Request.POST])
def wizard(
    feretui: "FeretUI",
    request: Request,
) -> Response:
    """Render a wizard resource inside a stackable modal dialog."""
    import uuid

    from markupsafe import Markup

    options = (
        request.params.copy()
        if (request.method == Request.POST and request.params is not None)
        else (request.query.copy() if request.query is not None else {})
    )
    code = (
        options.get("wizard", [None])[0]
        if isinstance(options.get("wizard"), list)
        else options.get("wizard")
    )
    if not code:
        code = (
            options.get("resource", [None])[0]
            if isinstance(options.get("resource"), list)
            else options.get("resource")
        )
    if not code:
        raise ActionError("No wizard or resource specified in query string")

    wizard_obj = feretui.get_resource(code)
    active_ids = _extract_active_ids(options)

    modal_size = (
        options.get("modal_size", [wizard_obj.modal_size])[0]
        if isinstance(options.get("modal_size"), list)
        else options.get("modal_size", wizard_obj.modal_size)
    )
    title = (
        options.get("title", [wizard_obj.title or wizard_obj.label])[0]
        if isinstance(options.get("title"), list)
        else options.get("title", wizard_obj.title or wizard_obj.label)
    )

    content = wizard_obj.render_modal_content(
        feretui, request.session, active_ids
    )

    modal_id = uuid.uuid4().hex[:8]
    html = feretui.render_template(
        request.session,
        "feretui-modal-dialog",
        modal_id=modal_id,
        title=title,
        content=Markup(content),
        modal_size=modal_size,
        target_field="",
    )
    return Response(html)
