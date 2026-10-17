# This file is a part of the FeretUI project
#
#    Copyright (C) 2026 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Helper for Starlette and FastAPI web servers."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING

from multidict import MultiDict

from feretui.request import Request
from feretui.response import Response
from feretui.session import Session

try:
    from starlette.applications import Starlette
    from starlette.requests import Request as StarletteRequest
    from starlette.responses import FileResponse, HTMLResponse
    from starlette.responses import Response as StarletteResponse
    from starlette.routing import Route
except ImportError as err:  # pragma: no cover
    raise ImportError(
        "starlette is missing => pip install feretui[starlette]",
    ) from err

if TYPE_CHECKING:
    from feretui.feretui import FeretUI


@contextmanager
def feretui_session(
    request: StarletteRequest,
    session_cls: type[Session] = Session,
) -> Iterator[Session]:
    """Context manager to link Starlette session and feretui session.

    ::

        from feretui.session import Session

        with feretui_session(request, Session) as session:
            ...

    :param request: Starlette request
    :type request: :class:`starlette.requests.Request`
    :param session_cls: Feretui Session class
    :type session_cls: type[:class:`feretui.session.Session`]
    :return: the session instance
    :rtype: :class:`session_cls`
    """
    session_data = getattr(request, "session", {})
    fsession = None
    try:
        fsession = session_cls(**session_data)
        yield fsession
    finally:
        if fsession and hasattr(request, "session"):
            request.session.update(fsession.to_dict())


def make_starlette_response(fresponse: Response) -> StarletteResponse:
    """Make the Starlette response.

    ::

        res = ...  # feretui.response.Response
        response = make_starlette_response(res)

    :param fresponse: the response from FeretUI
    :type fresponse: :class:`feretui.response.Response`
    :return: Starlette response
    :rtype: :class:`starlette.responses.Response`
    """
    content_type = None
    for k, v in fresponse.headers.items():
        if k.lower() == "content-type":
            content_type = v
            break

    if content_type:
        return StarletteResponse(
            content=fresponse.body,
            status_code=fresponse.status_code,
            headers=fresponse.headers,
            media_type=content_type,
        )

    return HTMLResponse(
        content=fresponse.body,
        status_code=fresponse.status_code,
        headers=fresponse.headers,
    )


async def _get_request_params(
    request: StarletteRequest,
) -> dict[str, list[str]]:
    """Extract and normalize all query and form parameters."""
    res: dict[str, list[str]] = {}
    for key in request.query_params:
        val = request.query_params.getlist(key)
        if val:
            res[key] = val

    if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
        form = await request.form()
        for key in form:
            val = form.getlist(key)
            if val:
                # String conversion for non-file items
                res[key] = [str(v) for v in val]

    return res


def get_routes_for_feretui_client(
    feretui: "FeretUI",
    index_path: str = "/",
    session_cls: type[Session] = Session,
) -> list[Route]:
    """Build a list of Starlette Route objects for a FeretUI client.

    ::

        routes = get_routes_for_feretui_client(myferet)
        app = Starlette(routes=routes)

    :param feretui: The FeretUI client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param index_path: The path of the main client page
    :type index_path: str
    :param session_cls: Feretui Session class
    :type session_cls: type[:class:`feretui.session.Session`]
    :return: List of Starlette Route objects
    :rtype: list[:class:`starlette.routing.Route`]
    """

    async def index(request: StarletteRequest) -> HTMLResponse:
        with feretui_session(request, session_cls) as session:
            query_bytes = request.scope.get("query_string", b"")
            querystring = (
                query_bytes.decode("utf-8")
                if isinstance(query_bytes, bytes)
                else str(query_bytes)
            )
            frequest = Request(
                method=Request.GET,
                querystring=querystring,
                headers=dict(request.headers),
                session=session,
            )
            return make_starlette_response(feretui.render(frequest))

    async def feretui_static_file(
        request: StarletteRequest,
    ) -> StarletteResponse:
        filepath_param = request.path_params.get("filepath", "")
        filepath = feretui.get_static_file_path(filepath_param)
        if filepath and filepath.is_file():
            return FileResponse(filepath.resolve())

        return StarletteResponse(status_code=404)

    async def call_action(request: StarletteRequest) -> HTMLResponse:
        action = request.path_params.get("action", "")
        params = await _get_request_params(request)

        form_data: MultiDict = MultiDict()
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            raw_form = await request.form()
            for k, v in raw_form.multi_items():
                form_data.add(k, str(v))

        query_bytes = request.scope.get("query_string", b"")
        querystring = (
            query_bytes.decode("utf-8")
            if isinstance(query_bytes, bytes)
            else str(query_bytes)
        )

        with feretui_session(request, session_cls) as session:
            frequest = Request(
                method=getattr(Request, request.method),
                querystring=querystring,
                form=form_data,
                params=params,
                headers=dict(request.headers),
                session=session,
            )
            return make_starlette_response(
                feretui.execute_action(frequest, action)
            )

    return [
        Route(index_path, index, methods=["GET"]),
        Route(
            f"{feretui.base_url}/static/{{filepath:path}}",
            feretui_static_file,
            methods=["GET"],
        ),
        Route(
            f"{feretui.base_url}/action/{{action:str}}",
            call_action,
            methods=["GET", "POST", "DELETE"],
        ),
    ]


def declare_routes_for_feretui_client(
    app: Starlette,
    feretui: "FeretUI",
    index_path: str = "/",
    session_cls: type[Session] = Session,
) -> None:
    """Declare Starlette routes on an existing Starlette app.

    ::

        myferet = FeretUI()
        app = Starlette()
        declare_routes_for_feretui_client(app, myferet)

    :param app: Starlette application
    :type app: :class:`starlette.applications.Starlette`
    :param feretui: The FeretUI client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param index_path: Path of the main page
    :type index_path: str
    :param session_cls: Feretui Session class
    :type session_cls: type[:class:`feretui.session.Session`]
    """
    routes = get_routes_for_feretui_client(
        feretui,
        index_path=index_path,
        session_cls=session_cls,
    )
    for route in routes:
        app.routes.append(route)
