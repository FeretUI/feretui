# This file is a part of the FeretUI project
#
#    Copyright (C) 2026 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Unit tests for Starlette adapter."""

import pytest

try:
    from starlette.applications import Starlette
    from starlette.middleware import Middleware
    from starlette.middleware.sessions import SessionMiddleware
    from starlette.testclient import TestClient
    from feretui.ext.starlette import (
        declare_routes_for_feretui_client,
        get_routes_for_feretui_client,
        make_starlette_response,
    )
except ImportError:
    Starlette = None

from feretui.feretui import FeretUI
from feretui.response import Response


@pytest.fixture(scope="class")
def starlette_client():
    """Create a Starlette test client with FeretUI routes and SessionMiddleware."""
    app = Starlette(
        middleware=[
            Middleware(SessionMiddleware, secret_key="test-secret-key"),
        ],
    )
    myferet = FeretUI()

    @myferet.register_action
    def my_action(feret, request):
        return Response(body="ok")

    declare_routes_for_feretui_client(app, myferet)
    return TestClient(app, raise_server_exceptions=False)


class TestStarlette:
    """Test suite for feretui.ext.starlette."""

    @pytest.mark.skipif(Starlette is None, reason="No starlette found")
    def test_index(self, starlette_client) -> None:
        """Test GET index route."""
        res = starlette_client.get("/")
        assert res.status_code == 200
        assert "<!DOCTYPE html" in res.text
        assert "FeretUI" in res.text

    @pytest.mark.skipif(Starlette is None, reason="No starlette found")
    def test_static(self, starlette_client) -> None:
        """Test GET static file route."""
        res = starlette_client.get("/feretui/static/logo.png")
        assert res.status_code == 200
        assert res.headers["content-type"] == "image/png"
        assert len(res.content) > 0

    @pytest.mark.skipif(Starlette is None, reason="No starlette found")
    def test_static_404(self, starlette_client) -> None:
        """Test GET missing static file returns 404."""
        res = starlette_client.get("/feretui/static/nonexistent_file.png")
        assert res.status_code == 404

    @pytest.mark.skipif(Starlette is None, reason="No starlette found")
    def test_call_action_get(self, starlette_client) -> None:
        """Test GET action call."""
        res = starlette_client.get(
            "/feretui/action/goto?page=login",
            headers={"Hx-Current-Url": "/"},
        )
        assert res.status_code == 200

    @pytest.mark.skipif(Starlette is None, reason="No starlette found")
    def test_call_action_post(self, starlette_client) -> None:
        """Test POST action call with form data."""
        res = starlette_client.post(
            "/feretui/action/my_action?query_opt=1",
            data={"login": "admin", "password": "wrong"},
            headers={"Hx-Current-Url": "/"},
        )
        assert res.status_code == 200
        assert res.text == "ok"

    @pytest.mark.skipif(Starlette is None, reason="No starlette found")
    def test_call_action_error(self, starlette_client) -> None:
        """Test action call with unexisting action returns 500."""
        res = starlette_client.get(
            "/feretui/action/unexisting_action",
            headers={"Hx-Current-Url": "/"},
        )
        assert res.status_code == 500

    @pytest.mark.skipif(Starlette is None, reason="No starlette found")
    def test_get_routes_and_declare(self) -> None:
        """Test get_routes_for_feretui_client directly."""
        myferet = FeretUI()
        routes = get_routes_for_feretui_client(myferet, index_path="/admin")
        assert len(routes) == 3
        assert routes[0].path == "/admin"

    @pytest.mark.skipif(Starlette is None, reason="No starlette found")
    def test_make_starlette_response(self) -> None:
        """Test make_starlette_response helper."""
        fres = Response(body="<h1>Hello</h1>", headers={"X-Custom": "test"})
        sres = make_starlette_response(fres)
        assert sres.body == b"<h1>Hello</h1>"
        assert sres.headers["X-Custom"] == "test"

        fres_csv = Response(
            body="a,b\n1,2",
            headers={"Content-Type": "text/csv; charset=utf-8"},
        )
        sres_csv = make_starlette_response(fres_csv)
        assert sres_csv.body == b"a,b\n1,2"
        assert "text/csv" in sres_csv.headers["content-type"]
