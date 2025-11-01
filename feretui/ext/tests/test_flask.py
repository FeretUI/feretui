# This file is a part of the FeretUI project
#
#    Copyright (C) 2023-2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest
try:
    import flask
    from feretui.ext.flask import declare_routes_for_feretui_client
except ImportError:
    flask = None

from webtest import TestApp
from feretui.feretui import FeretUI


@pytest.fixture(scope="class")
def flask_server():
    app = flask.Flask('test')
    app.secret_key = b'secret'
    declare_routes_for_feretui_client(app, FeretUI())
    return TestApp(app)


class TestFlask:

    @pytest.mark.skipif(flask is None, reason="No flask found")
    def test_index(self, snapshot, flask_server) -> None:
        snapshot.assert_match(flask_server.get('/').body, 'index.html')

    @pytest.mark.skipif(flask is None, reason="No flask found")
    def test_static(self, snapshot, flask_server) -> None:
        snapshot.assert_match(
            flask_server.get('/feretui/static/logo.png').body, 'logo.png')

    @pytest.mark.skipif(flask is None, reason="No flask found")
    def test_static_2(self, snapshot, flask_server) -> None:
        flask_server.get('/feretui/static/wrong.png', status=404)

    @pytest.mark.skipif(flask is None, reason="No flask found")
    def test_action(self, snapshot, flask_server) -> None:
        snapshot.assert_match(
            flask_server.get(
                '/feretui/action/goto?page=login',
                headers={'Hx-Current-Url': '/'},
            ).body,
            "page_404.html")

    @pytest.mark.skipif(flask is None, reason="No flask found")
    def test_action_2(self, flask_server) -> None:
        flask_server.post(
            '/feretui/action/login',
            {},
            headers={'Hx-Current-Url': '/'},
            status=500,
        )
