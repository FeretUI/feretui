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
from multidict import MultiDict

from feretui.exceptions import (
    RequestFormError,
    RequestNoSessionError,
    RequestWrongSessionError,
)
from feretui.request import Request
from feretui.session import Session


class TestRequest:
    """Test Request."""

    def test_request(self) -> None:
        """Test simple request."""
        session = Session()
        request = Request(
            session,
            method=Request.POST,
            form=MultiDict({'foo': 'bar'}),
            querystring="a=b",
        )
        assert request.session is session
        assert request.method is Request.POST
        assert request.query == {'a': ['b']}

    def test_request_wrong_form(self) -> None:
        """Test simple request."""
        session = Session()
        with pytest.raises(RequestFormError):
            Request(
                session,
                method=Request.POST,
                form={'foo': 'bar'},
            )

    def test_request_with_no_session(self) -> None:
        """Test request with none session."""
        with pytest.raises(RequestNoSessionError):
            Request(None)

    def test_request_wrong_session(self) -> None:
        """Test request with wrong session type."""
        with pytest.raises(RequestWrongSessionError):
            Request("session", querystring="a=b")

    def test_get_url_from_dict(self) -> None:
        """Test get_url_from_dict with querystring."""
        session = Session()
        request = Request(session)
        assert request.get_url_from_dict(querystring={'a': 1}) == '/?a=1'

    def test_get_url_from_dict_2(self) -> None:
        """Test get_url_from_dict without querystring."""
        session = Session()
        request = Request(session)
        assert request.get_url_from_dict() == '/'

    def test_get_query_string_from_current_url(self) -> None:
        """Test get_query_string_from_current_url."""
        session = Session()
        request = Request(session, headers={'Hx-Current-Url': '/?a=b'})
        assert request.get_query_string_from_current_url()
