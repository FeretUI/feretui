# This file is a part of the FeretUI project
#
#    Copyright (C) 2025 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Helper for flask web server."""
import urllib
from contextlib import contextmanager
from importlib import import_module
from typing import TYPE_CHECKING

from flask import Flask, abort, make_response, request, send_file
from flask import Response as FlaskResponse
from multidict import MultiDict

from feretui.request import Request
from feretui.response import Response
from feretui.session import Session

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
    session = import_module('flask').session
    fsession = None
    try:
        fsession = session_cls(**session)
        yield fsession
    finally:
        if fsession:
            session.update(fsession.to_dict())


def make_flask_response(fresponse: Response) -> FlaskResponse:
    """Make the flask response.

    ::

        res = ...  # feretui.response.Response
        response = make_flask_response(res)

    :param response: the response come from FeretUI
    :type reponse: :class:`feretui.response:Response`
    """
    resp = make_response(fresponse.body)
    resp.headers.update(fresponse.headers)
    return resp


def declare_routes_for_feretui_client(
    app: Flask,
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

    :param app: Flask application
    :type app: :class:`flask.Flask`
    :param feretui: the client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param index_path: the path of the main page of the client
    :type index_path: str
    :param session_cls: Feretui Session class
    :type session_cls: type[:class:`feretui.session.Session`]
    """
    @app.route(index_path)
    def index() -> str:
        with feretui_session(session_cls) as session:
            frequest = Request(
                method=Request.GET,
                querystring=request.query_string.decode('utf-8'),
                headers=dict(request.headers),
                session=session,
            )
            return make_flask_response(feretui.render(frequest))

    @app.route(f'{feretui.base_url}/static/<path:filepath>')
    def feretui_static_file(filepath: str) -> str:
        filepath = feretui.get_static_file_path(filepath)
        if filepath:
            return send_file(filepath.resolve())

        abort(404)
        return None  # pragma: no cover

    @app.route(
        f'{feretui.base_url}/action/<action>',
        methods=['DELETE', 'GET', 'POST'],
    )
    def call_action(action: str) -> str:
        params = {}
        if request.method in ['DELETE', 'POST']:
            params = {
                x: request.form.getlist(x)
                for x in request.form
            }
            params.update(urllib.parse.parse_qs(
                request.query_string.decode('utf-8'),
            ))

        with feretui_session(session_cls) as session:
            frequest = Request(
                method=getattr(Request, request.method),
                querystring=request.query_string.decode('utf-8'),
                form=MultiDict(request.form),
                params=params,
                headers=dict(request.headers),
                session=session,
            )
            return make_flask_response(feretui.execute_action(frequest, action))
