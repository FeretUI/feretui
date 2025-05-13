# This file is a part of the FeretUI project
#
#    Copyright (C) 2023-2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest
try:
    import bottle
    from BottleSessions import BottleSessions
    from feretui.ext.bottle import declare_routes_for_feretui_client
except ImportError:
    bottle = None

from webtest import TestApp
from feretui.feretui import FeretUI


@pytest.fixture(scope="class")
def bottle_server():
    declare_routes_for_feretui_client(FeretUI())
    cache_config = {
    }
    app = bottle.app()
    BottleSessions(
        app, session_backing=cache_config, session_cookie='appcookie')
    return TestApp(app)


class TestBottle:

    @pytest.mark.skipif(bottle is None, reason="No bottle found")
    def test_index(self, snapshot, bottle_server) -> None:
        snapshot.assert_match(bottle_server.get('/').body, 'index.html')

    @pytest.mark.skipif(bottle is None, reason="No bottle found")
    def test_static(self, snapshot, bottle_server) -> None:
        snapshot.assert_match(
            bottle_server.get('/feretui/static/logo.png').body, 'logo.png')

    @pytest.mark.skipif(bottle is None, reason="No bottle found")
    def test_static_2(self, snapshot, bottle_server) -> None:
        bottle_server.get('/feretui/static/wrong.png', status=404)

    @pytest.mark.skipif(bottle is None, reason="No bottle found")
    def test_action(self, snapshot, bottle_server) -> None:
        snapshot.assert_match(
            bottle_server.get(
                '/feretui/action/goto?page=login',
                headers={'Hx-Current-Url': '/'},
            ).body,
            "page_404.html")
