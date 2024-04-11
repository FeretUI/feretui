.. This file is a part of the FeretUI project
..
..    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

Serve FeretUI with bottle
-------------------------

Bottle is a fast, simple and lightweight WSGI micro web-framework for Python.
It is distributed as a single file module and has no dependencies other than the 
Python Standard Library.

See the `bottle documentation <https://bottlepy.org/docs/dev/>`_.

For this example you need  to install some additional package

::

    pip install bottle BottleSessions

::

    import logging
    from contextlib import contextmanager
    from os import path

    from bottle import abort, app, request, response, route, run, static_file
    from BottleSessions import BottleSessions
    from multidict import MultiDict

    from feretui import FeretUI, Request, Session

    logging.basicConfig(level=logging.DEBUG)


    @contextmanager
    def feretui_session(cls):
        session = None
        try:
            session = cls(**request.session)
            yield session
        finally:
            if session:
                request.session.update(session.to_dict())


    def add_response_headers(headers) -> None:
        for k, v in headers.items():
            response.set_header(k, v)


    myferet = FeretUI()

    # Here define your feretui stuff.


    @route('/')
    def index():
        with feretui_session(Session) as session:
            frequest = Request(
                method=Request.GET,
                querystring=request.query_string,
                headers=dict(request.headers),
                session=session,
            )
            res = myferet.render(frequest)
            add_response_headers(res.headers)
            return res.body


    @route('/feretui/static/<filepath:path>')
    def feretui_static_file(filepath):
        filepath = myferet.get_static_file_path(filepath)
        if filepath:
            root, name = path.split(filepath)
            return static_file(name, root)

        abort(404)


    @route('/feretui/action/<action>', method=['DELETE', 'GET', 'POST'])
    def call_action(action):
        with feretui_session(Session) as session:
            frequest = Request(
                method=getattr(Request, request.method),
                querystring=request.query_string,
                form=MultiDict(request.forms),
                params=MultiDict(request.params),
                headers=dict(request.headers),
                session=session,
            )
            res = myferet.execute_action(frequest, action)
            add_response_headers(res.headers)
            return res.body


    if __name__ == "__main__":
        app = app()
        cache_config = {
            'cache_type': 'FileSystem',
            'cache_dir': './sess_dir',
            'threshold': 2000,
        }
        BottleSessions(
            app, session_backing=cache_config, session_cookie='appcookie')
        run(host="localhost", port=8080, debug=True, reloader=1)
