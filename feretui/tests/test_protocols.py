# This file is a part of the FeretUI project
#
#    Copyright (C) 2024-2026 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Tests for FeretUI structural typing protocols."""

from typing import Any

from wtforms import StringField

from feretui.form import FeretUIForm
from feretui.protocols import (
    FormProtocol,
    RequestProtocol,
    ResourceProtocol,
    ResponseProtocol,
    SessionProtocol,
    ViewProtocol,
)
from feretui.request import Request
from feretui.resources.list import LResource
from feretui.resources.resource import Resource
from feretui.response import Response
from feretui.session import Session


class SampleForm(FeretUIForm):
    """Sample form implementing FormProtocol."""

    title = StringField("Title")


class SampleResource(LResource, Resource):
    """Sample resource implementing ResourceProtocol."""

    code = "sample"
    label = "Sample"
    default_view = "list"

    class Form:
        pk = StringField("PK")
        title = StringField("Title")

    def filtered_reads(
        self: "SampleResource",
        *args: tuple,  # noqa: ARG002
        **kwargs: dict,  # noqa: ARG002
    ) -> dict[str, Any]:
        """Mock filtered reads."""
        return {"total": 0, "forms": []}


def test_protocols_runtime_checkable() -> None:
    """Verify runtime conformance of FeretUI objects to protocols."""
    sess = Session()
    assert isinstance(sess, SessionProtocol)

    req = Request(sess, method=Request.GET, querystring="a=1")
    assert isinstance(req, RequestProtocol)

    resp = Response("OK", status_code=200)
    assert isinstance(resp, ResponseProtocol)

    form = SampleForm()
    assert isinstance(form, FormProtocol)

    res = SampleResource.build()
    assert isinstance(res, ResourceProtocol)

    view = res.views["list"]
    assert isinstance(view, ViewProtocol)





def test_custom_objects_satisfy_protocols() -> None:
    """Verify duck-typed custom objects satisfy protocols."""
    class CustomSession:
        user = "admin"
        lang = "en"
        theme = "default"
        color_scheme = None

        def to_dict(self) -> dict[str, Any]:
            return {"user": self.user}

    assert isinstance(CustomSession(), SessionProtocol)

    class CustomResponse:
        body = "custom"
        status_code = 200
        headers = {}

    assert isinstance(CustomResponse(), ResponseProtocol)

