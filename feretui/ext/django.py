# This file is a part of the FeretUI project
#
#    Copyright (C) 2026 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Helper for Django web framework."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING

from multidict import MultiDict

from feretui.request import Request
from feretui.response import Response
from feretui.session import Session

try:
    from django.http import (
        FileResponse,
        HttpRequest,
        HttpResponse,
        HttpResponseNotFound,
    )
    from django.urls import URLPattern, path
except ImportError as err:  # pragma: no cover
    raise ImportError(
        "django is missing => pip install feretui[django]",
    ) from err

if TYPE_CHECKING:
    from feretui.feretui import FeretUI


@contextmanager
def feretui_session(
    request: HttpRequest,
    session_cls: type[Session] = Session,
) -> Iterator[Session]:
    """Context manager to link Django session and FeretUI session.

    ::

        from feretui.session import Session

        with feretui_session(request, Session) as session:
            ...

    :param request: Django HTTP request
    :type request: :class:`django.http.HttpRequest`
    :param session_cls: Feretui Session class
    :type session_cls: type[:class:`feretui.session.Session`]
    :return: The session instance
    :rtype: :class:`session_cls`
    """
    session_data = dict(getattr(request, "session", {}))
    fsession = None
    try:
        fsession = session_cls(**session_data)
        yield fsession
    finally:
        if fsession and hasattr(request, "session"):
            request.session.update(fsession.to_dict())
            if hasattr(request.session, "modified"):
                request.session.modified = True


def make_django_response(fresponse: Response) -> HttpResponse:
    """Make a Django HttpResponse from a FeretUI Response.

    ::

        res = ...  # feretui.response.Response
        response = make_django_response(res)

    :param fresponse: The response from FeretUI
    :type fresponse: :class:`feretui.response.Response`
    :return: Django HttpResponse
    :rtype: :class:`django.http.HttpResponse`
    """
    response = HttpResponse(
        content=fresponse.body,
        status=fresponse.status_code,
    )
    for k, v in fresponse.headers.items():
        response[k] = v

    return response


def _get_request_params(request: HttpRequest) -> dict[str, list[str]]:
    """Extract and normalize all query and form parameters."""
    res: dict[str, list[str]] = {}
    if request.GET:
        for key in request.GET:
            res[key] = request.GET.getlist(key)

    if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
        for key in request.POST:
            val = request.POST.getlist(key)
            if key in res:
                res[key].extend(val)
            else:
                res[key] = val

    return res


def get_urlpatterns_for_feretui_client(
    feretui: "FeretUI",
    index_path: str = "",
    session_cls: type[Session] = Session,
) -> list[URLPattern]:
    """Build a list of Django URLPattern objects for a FeretUI client.

    ::

        from feretui.ext.django import get_urlpatterns_for_feretui_client

        urlpatterns = [
            ...
        ] + get_urlpatterns_for_feretui_client(myferet)

    :param feretui: The FeretUI client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param index_path: The path of the main client page (default: "")
    :type index_path: str
    :param session_cls: FeretUI Session class
    :type session_cls: type[:class:`feretui.session.Session`]
    :return: List of Django URLPattern objects
    :rtype: list[:class:`django.urls.URLPattern`]
    """

    def index(request: HttpRequest) -> HttpResponse:
        with feretui_session(request, session_cls) as session:
            frequest = Request(
                method=Request.GET,
                querystring=request.META.get("QUERY_STRING", ""),
                headers=dict(request.headers),
                session=session,
            )
            return make_django_response(feretui.render(frequest))

    def feretui_static_file(
        request: HttpRequest,  # noqa: ARG001
        filepath: str,
    ) -> HttpResponse:
        target_path = feretui.get_static_file_path(filepath)
        if target_path and target_path.is_file():
            return FileResponse(target_path.open("rb"))

        return HttpResponseNotFound()

    def call_action(request: HttpRequest, action: str) -> HttpResponse:
        params = _get_request_params(request)

        form_data: MultiDict = MultiDict()
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            for k in request.POST:
                for v in request.POST.getlist(k):
                    form_data.add(k, str(v))

        with feretui_session(request, session_cls) as session:
            frequest = Request(
                method=getattr(Request, request.method),
                querystring=request.META.get("QUERY_STRING", ""),
                form=form_data,
                params=params,
                headers=dict(request.headers),
                session=session,
            )
            return make_django_response(
                feretui.execute_action(frequest, action),
            )

    base = feretui.base_url.strip("/")
    base_prefix = f"{base}/" if base else ""

    norm_index = index_path.strip("/")
    index_route = f"{norm_index}/" if norm_index else ""

    return [
        path(index_route, index, name="feretui_index"),
        path(
            f"{base_prefix}static/<path:filepath>",
            feretui_static_file,
            name="feretui_static",
        ),
        path(
            f"{base_prefix}action/<str:action>",
            call_action,
            name="feretui_action",
        ),
    ]
