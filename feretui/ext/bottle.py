# This file is a part of the FeretUI project
#
#    Copyright (C) 2025 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Helper for bottle web server."""
from contextlib import contextmanager
from os import path
from typing import TYPE_CHECKING

from multidict import MultiDict

from feretui.request import Request
from feretui.session import Session

try:
    from bottle import abort, request, response, route, static_file
except ImportError as err:  # pragma: no cover
    raise ImportError(
        "bottle is missing => pip install feretui[bottle]",
    ) from err

if TYPE_CHECKING:
    from feretui.feretui import FeretUI


@contextmanager
def feretui_session(session_cls: type[Session]) -> Session:
    """Context manager to link bottle session and feretui session.

    ::

        from feretui.Session import Session

        with feretui_session(Session) as session:
            ...

    :param session_cls: Feretui Session class
    :type session_cls: type[:class:`feretui.session.Session`]
    :return: the session instance
    :rtype: :class:`session_cls`
    """
    session = None
    try:
        session = session_cls(**request.session)
        yield session
    finally:
        if session:
            request.session.update(session.to_dict())


def add_response_headers(headers: dict) -> None:
    """Register headers in the bottle response.

    ::

        res = ...  # feretui.response.Response
        add_response_headers(res.headers)

    :param headers: the headers to save
    :type headers: dict
    """
    for k, v in headers.items():
        response.set_header(k, v)


def declare_routes_for_feretui_client(
    feretui: "FeretUI",
    index_path: str = '/',
    session_cls: type[Session] = Session,
) -> None:
    """Declare a bottle route for a feretui client.

    ::

        myferet = FeretUI()

        class MySession(Session):
            pass

        declare_routes_for_feretui_client(
            myferet,
            index_path='/',  # path of the main page for the client
            session_cls=MySession,
        )

    :param feretui: the client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param index_path: the path of the main page of the client
    :type index_path: str
    :param session_cls: Feretui Session class
    :type session_cls: type[:class:`feretui.session.Session`]
    """

    @route(index_path)
    def index() -> str:
        with feretui_session(session_cls) as session:
            frequest = Request(
                method=Request.GET,
                querystring=request.query_string,
                headers=dict(request.headers),
                session=session,
            )
            res = feretui.render(frequest)
            add_response_headers(res.headers)
            return res.body

    @route(f'{feretui.base_url}/static/<filepath:path>')
    def feretui_static_file(filepath: str) -> str:
        filepath = feretui.get_static_file_path(filepath)
        if filepath:
            root, name = path.split(filepath)
            return static_file(name, root)

        return abort(404)

    @route(
        f'{feretui.base_url}/action/<action>',
        method=['DELETE', 'GET', 'POST'],
    )
    def call_action(action: str) -> str:
        with feretui_session(session_cls) as session:
            frequest = Request(
                method=getattr(Request, request.method),
                querystring=request.query_string,
                form=MultiDict(request.forms),
                params=MultiDict(request.params),
                headers=dict(request.headers),
                session=session,
            )
            res = feretui.execute_action(frequest, action)
            add_response_headers(res.headers)
            return res.body
