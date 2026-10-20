# This file is a part of the FeretUI project
#
#    Copyright (C) 2023-2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Unittest.

with pytest.
"""
import pytest  # noqa: F401

from feretui.response import Response


def test_response() -> None:
    """Test Response."""
    response = Response('<div>Response</div>')
    assert response.body == '<div>Response</div>'
    assert response.status_code == 200
    assert response.headers == {}


def test_response_redirect_hx() -> None:
    """Test Response.redirect with HX header."""
    resp = Response.redirect("/next-page")
    assert resp.status_code == 200
    assert resp.headers == {"HX-Redirect": "/next-page"}


def test_response_redirect_standard() -> None:
    """Test Response.redirect without HX header (302)."""
    resp = Response.redirect("/login", hx=False)
    assert resp.status_code == 302
    assert resp.headers == {"Location": "/login"}


def test_response_refresh() -> None:
    """Test Response.refresh helper."""
    resp = Response.refresh()
    assert resp.status_code == 200
    assert resp.headers == {"HX-Refresh": "true"}


def test_response_with_trigger() -> None:
    """Test Response.with_trigger helper variations."""
    resp1 = Response("ok").with_trigger("itemSaved")
    assert resp1.headers["HX-Trigger"] == "itemSaved"

    resp2 = Response("ok").with_trigger("showToast", "success")
    assert resp2.headers["HX-Trigger"] == "showToast:success"

    resp3 = Response("ok").with_trigger("cartUpdated", {"count": 3})
    assert 'cartUpdated' in resp3.headers["HX-Trigger"]
    assert '"count": 3' in resp3.headers["HX-Trigger"]

