.. This file is a part of the FeretUI project
..
..    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

Serve FeretUI with flask
------------------------

Flask is a lightweight WSGI web application framework. It is designed to make 
getting started quick and easy, with the ability to scale up to complex 
applications. It began as a simple wrapper around Werkzeug and Jinja, and has become 
one of the most popular Python web application frameworks.

See the `flask documentation <https://flask.palletsprojects.com/en/3.0.x/>`_.

For this example you need  to install some additional package

::

    pip install flask

::

    import logging
    import urllib
    from contextlib import contextmanager
    from wsgiref.simple_server import make_server

    from flask import Flask, abort, make_response, request, send_file
    from multidict import MultiDict

    from feretui import FeretUI, Request, Session

    logging.basicConfig(level=logging.DEBUG)

    app = Flask(__name__)
    app.secret_key = b'secret'


    @contextmanager
    def feretui_session(cls):
        from flask import session
        fsession = None
        try:
            fsession = cls(**session)
            yield fsession
        finally:
            if fsession:
                session.update(fsession.to_dict())


    def response(fresponse):
        resp = make_response(fresponse.body)
        resp.headers.update(fresponse.headers)
        return resp


    myferet = FeretUI()

    # Here define your feretui stuff.


    @app.route('/')
    def index():
        with feretui_session(Session) as session:
            frequest = Request(
                method=Request.GET,
                querystring=request.query_string.decode('utf-8'),
                headers=dict(request.headers),
                session=session,
            )
            return response(myferet.render(frequest))


    @app.route('/feretui/static/<path:filepath>')
    def feretui_static_file(filepath):
        filepath = myferet.get_static_file_path(filepath)
        if filepath:
            return send_file(filepath)

        abort(404)
        return None


    @app.route('/feretui/action/<action>', methods=['DELETE', 'GET', 'POST'])
    def call_action(action):
        params = {}
        if request.method in ['DELETE', 'POST']:
            params = {
                x: request.form.getlist(x)
                for x in request.form
            }
            params.update(urllib.parse.parse_qs(
                request.query_string.decode('utf-8'),
            ))

        with feretui_session(Session) as session:
            frequest = Request(
                method=getattr(Request, request.method),
                querystring=request.query_string.decode('utf-8'),
                form=MultiDict(request.form),
                params=params,
                headers=dict(request.headers),
                session=session,
            )
            return response(myferet.execute_action(frequest, action))


    if __name__ == "__main__":
        with make_server('', 8080, app) as httpd:
            logging.info("Serving on port 8080...")
            httpd.serve_forever()
