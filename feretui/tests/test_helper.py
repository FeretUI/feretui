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

from feretui.exceptions import (
    ActionUserIsAuthenticatedError,
    ActionUserIsNotAuthenticatedError,
    ActionValidatorError,
)
from feretui.feretui import FeretUI
from feretui.helper import (
    action_for_authenticated_user,
    action_for_unauthenticated_user,
    action_validator,
    menu_for_authenticated_user,
    menu_for_unauthenticated_user,
    page_for_authenticated_user_or_goto,
    page_for_unauthenticated_user_or_goto,
)
from feretui.pages import page_404
from feretui.request import Request
from feretui.response import Response
from feretui.session import Session


class TestActionValidator:
    """TestActionValidator."""

    def test_method_None(self) -> None:
        """Test session."""
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)

        @myferet.register_action
        @action_validator()
        def my_action(feretui, request):
            return Response('True')

        assert myferet.execute_action(request, 'my_action')

    def test_method_ok(self) -> None:
        """Test session."""
        myferet = FeretUI()
        session = Session()
        request = Request(method=Request.POST, session=session)

        @myferet.register_action
        @action_validator(methods=Request.POST)
        def my_action(feretui, request):
            return Response('True')

        assert myferet.execute_action(request, 'my_action')

    def test_method_ko(self) -> None:
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

    def test_not_return_response(self) -> None:
        """Test session."""
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)

        @myferet.register_action
        @action_validator()
        def my_action(feretui, request) -> bool:
            return True

        with pytest.raises(ActionValidatorError):
            myferet.execute_action(request, 'my_action')

    def test_page_for_authenticated_user_or_goto_1(self) -> None:
        myferet = FeretUI()
        session = Session()

        @page_for_authenticated_user_or_goto('404')
        def my_page(feretui, session, options) -> str:
            return '<div>Test</div>'

        assert my_page(myferet, session, {}) == page_404(myferet, session, {})

    def test_page_for_authenticated_user_or_goto_2(self) -> None:
        myferet = FeretUI()
        session = Session()

        @page_for_authenticated_user_or_goto(page_404)
        def my_page(feretui, session, options) -> str:
            return '<div>Test</div>'

        assert my_page(myferet, session, {}) == page_404(myferet, session, {})

    def test_page_for_authenticated_user_or_goto_3(self) -> None:
        myferet = FeretUI()
        session = Session(user='test')

        @page_for_authenticated_user_or_goto(page_404)
        def my_page(feretui, session, options) -> str:
            return '<div>Test</div>'

        assert my_page(myferet, session, {}) == '<div>Test</div>'

    def test_page_for_unauthenticated_user_or_goto_1(self) -> None:
        myferet = FeretUI()
        session = Session()

        @page_for_unauthenticated_user_or_goto('404')
        def my_page(feretui, session, options) -> str:
            return '<div>Test</div>'

        assert my_page(myferet, session, {}) == '<div>Test</div>'

    def test_page_for_unauthenticated_user_or_goto_2(self) -> None:
        myferet = FeretUI()
        session = Session(user='test')

        @page_for_unauthenticated_user_or_goto('404')
        def my_page(feretui, session, options) -> str:
            return '<div>Test</div>'

        assert my_page(myferet, session, {}) == page_404(myferet, session, {})

    def test_page_for_unauthenticated_user_or_goto_3(self) -> None:
        myferet = FeretUI()
        session = Session(user='test')

        @page_for_unauthenticated_user_or_goto(page_404)
        def my_page(feretui, session, options) -> str:
            return '<div>Test</div>'

        assert my_page(myferet, session, {}) == page_404(myferet, session, {})

    def test_menu_for_authenticated_user_1(self) -> None:
        assert menu_for_authenticated_user(Session()) is False

    def test_menu_for_authenticated_user_2(self) -> None:
        assert menu_for_authenticated_user(Session(user="test")) is True

    def test_menu_for_unauthenticated_user_1(self) -> None:
        assert menu_for_unauthenticated_user(Session()) is True

    def test_menu_for_unauthenticated_user_2(self) -> None:
        assert menu_for_unauthenticated_user(Session(user="test")) is False

    def test_action_for_authenticated_user_1(self) -> None:
        myferet = FeretUI()
        session = Session()
        request = Request(session)

        @action_for_authenticated_user
        def my_action(feretui, request) -> bool:
            return True

        with pytest.raises(ActionUserIsNotAuthenticatedError):
            my_action(myferet, request)

    def test_action_for_authenticated_user_2(self) -> None:
        myferet = FeretUI()
        session = Session(user='test')
        request = Request(session)

        @action_for_authenticated_user
        def my_action(feretui, request) -> bool:
            return True

        assert my_action(myferet, request) is True

    def test_action_for_unauthenticated_user_1(self) -> None:
        myferet = FeretUI()
        session = Session()
        request = Request(session)

        @action_for_unauthenticated_user
        def my_action(feretui, request) -> bool:
            return True

        assert my_action(myferet, request) is True

    def test_action_for_unauthenticated_user_2(self) -> None:
        myferet = FeretUI()
        session = Session(user='test')
        request = Request(session)

        @action_for_unauthenticated_user
        def my_action(feretui, request) -> bool:
            return True

        with pytest.raises(ActionUserIsAuthenticatedError):
            my_action(myferet, request)
