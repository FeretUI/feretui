# This file is a part of the FeretUI project
#
#    Copyright (C) 2026 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Unit tests for Django adapter."""

import pytest

try:
    import django
    from django.conf import settings
    from django.test import Client, RequestFactory
    from feretui.ext.django import (
        _get_request_params,
        feretui_session,
        get_urlpatterns_for_feretui_client,
        make_django_response,
    )
except ImportError:
    django = None

from feretui.feretui import FeretUI
from feretui.response import Response
from feretui.session import Session

test_feret = FeretUI()


@test_feret.register_action
def my_action(feret, request):
    return Response(body="django-ok")


urlpatterns = []
if django:
    urlpatterns = get_urlpatterns_for_feretui_client(test_feret)
    if not settings.configured:
        settings.configure(
            DEBUG=False,
            SECRET_KEY="test-secret-key-django",
            ROOT_URLCONF="feretui.ext.tests.test_django",
            ALLOWED_HOSTS=["*"],
            SESSION_ENGINE="django.contrib.sessions.backends.signed_cookies",
            MIDDLEWARE=[
                "django.contrib.sessions.middleware.SessionMiddleware",
            ],
        )
        django.setup()


@pytest.fixture(scope="class")
def django_client():
    """Create Django test client."""
    return Client(raise_request_exception=False)


class TestDjango:
    """Test suite for feretui.ext.django."""

    @pytest.mark.skipif(django is None, reason="No django found")
    def test_index(self, django_client) -> None:
        """Test GET index route."""
        res = django_client.get("/")
        assert res.status_code == 200
        assert "<!DOCTYPE html" in res.content.decode("utf-8")
        assert "FeretUI" in res.content.decode("utf-8")

    @pytest.mark.skipif(django is None, reason="No django found")
    def test_static(self, django_client) -> None:
        """Test GET static file route."""
        res = django_client.get("/feretui/static/logo.png")
        assert res.status_code == 200
        content = b"".join(res.streaming_content)
        assert len(content) > 0

    @pytest.mark.skipif(django is None, reason="No django found")
    def test_static_404(self, django_client) -> None:
        """Test GET missing static file returns 404."""
        res = django_client.get("/feretui/static/nonexistent_file.png")
        assert res.status_code == 404

    @pytest.mark.skipif(django is None, reason="No django found")
    def test_call_action_get(self, django_client) -> None:
        """Test GET action call."""
        res = django_client.get(
            "/feretui/action/goto?page=login",
            HTTP_HX_CURRENT_URL="/",
        )
        assert res.status_code == 200

    @pytest.mark.skipif(django is None, reason="No django found")
    def test_call_action_post(self, django_client) -> None:
        """Test POST action call with form data."""
        res = django_client.post(
            "/feretui/action/my_action?query_opt=1",
            data={"login": "admin", "password": "wrong"},
            HTTP_HX_CURRENT_URL="/",
        )
        assert res.status_code == 200
        assert res.content.decode("utf-8") == "django-ok"

    @pytest.mark.skipif(django is None, reason="No django found")
    def test_call_action_error(self, django_client) -> None:
        """Test action call with unexisting action returns 500."""
        res = django_client.get(
            "/feretui/action/unexisting_action",
            HTTP_HX_CURRENT_URL="/",
        )
        assert res.status_code == 500

    @pytest.mark.skipif(django is None, reason="No django found")
    def test_get_urlpatterns_custom_index_path(self) -> None:
        """Test get_urlpatterns_for_feretui_client with custom index path."""
        myferet = FeretUI()
        patterns = get_urlpatterns_for_feretui_client(
            myferet,
            index_path="admin/",
        )
        assert len(patterns) == 3

    @pytest.mark.skipif(django is None, reason="No django found")
    def test_make_django_response(self) -> None:
        """Test make_django_response helper."""
        fres = Response(body="<h1>Hello</h1>", headers={"X-Custom": "test"})
        dres = make_django_response(fres)
        assert dres.content == b"<h1>Hello</h1>"
        assert dres["X-Custom"] == "test"

    @pytest.mark.skipif(django is None, reason="No django found")
    def test_get_request_params_overlapping(self) -> None:
        """Test _get_request_params with overlapping query and post params."""
        factory = RequestFactory()
        req = factory.post("/test?tag=1", data={"tag": "2", "extra": "3"})
        params = _get_request_params(req)
        assert params["tag"] == ["1", "2"]
        assert params["extra"] == ["3"]

    @pytest.mark.skipif(django is None, reason="No django found")
    def test_feretui_session_no_session_attribute(self) -> None:
        """Test feretui_session when request object does not have session."""
        factory = RequestFactory()
        req = factory.get("/")
        with feretui_session(req, Session) as s:
            assert isinstance(s, Session)
