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
from pydantic import BaseModel

from feretui.exceptions import ActionValidatorError
from feretui.feretui import FeretUI
from feretui.helper import action_validator
from feretui.request import Request
from feretui.response import Response
from feretui.session import Session


class TestActionValidator:
    """TestActionValidator."""

    def test_method_None(self):
        """Test session."""
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)

        @myferet.register_action
        @action_validator()
        def my_action(feretui, request):
            return Response('True')

        assert myferet.execute_action(request, 'my_action')

    def test_method_ok(self):
        """Test session."""
        myferet = FeretUI()
        session = Session()
        request = Request(method=Request.POST, session=session)

        @myferet.register_action
        @action_validator(methods=Request.POST)
        def my_action(feretui, request):
            return Response('True')

        assert myferet.execute_action(request, 'my_action')

    def test_method_ko(self):
        """Test session."""
        myferet = FeretUI()
        session = Session()
        request = Request(method=Request.POST, session=session)

        @myferet.register_action
        @action_validator(methods=Request.GET)
        def my_action(feretui, request):
            return Response('True')

        with pytest.raises(ActionValidatorError):
            myferet.execute_action(request, 'my_action')

    def test_not_return_response(self):
        """Test session."""
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)

        @myferet.register_action
        @action_validator()
        def my_action(feretui, request):
            return True

        with pytest.raises(ActionValidatorError):
            myferet.execute_action(request, 'my_action')

    def test_pydantic_body_validator(self):
        """Test session."""
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)

        class MyValidator(BaseModel):
            test: str

        @myferet.register_action
        @action_validator(pydantic_body_validator=MyValidator)
        def my_action(feretui, request):
            assert request.pydantic_body_validator is MyValidator
            return Response('True')

        myferet.execute_action(request, 'my_action')

    def test_pydantic_querystring_validator(self):
        """Test session."""
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)

        class MyValidator(BaseModel):
            test: str

        @myferet.register_action
        @action_validator(pydantic_querystring_validator=MyValidator)
        def my_action(feretui, request):
            assert request.pydantic_querystring_validator is MyValidator
            return Response('True')

        myferet.execute_action(request, 'my_action')
