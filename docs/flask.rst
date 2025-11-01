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
    from wsgiref.simple_server import make_server

    from flask import Flask, abort, make_response, request, send_file
    from multidict import MultiDict

    from feretui import FeretUI
    from feretui.ext.flask import declare_routes_for_feretui_client

    logging.basicConfig(level=logging.DEBUG)

    app = Flask(__name__)
    app.secret_key = b'secret'


    myferet = FeretUI()

    # Here define your feretui stuff.

    declare_routes_for_feretui_client(app, myferet)

    if __name__ == "__main__":
        with make_server('', 8080, app) as httpd:
            logging.info("Serving on port 8080...")
            httpd.serve_forever()
