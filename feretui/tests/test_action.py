from typing import NoReturn

import pytest
from multidict import MultiDict

from feretui.actions import goto, login_password, login_signup, logout
from feretui.exceptions import (
    ActionError,
    ActionUserIsAuthenticatedError,
    ActionUserIsNotAuthenticatedError,
    ActionValidatorError,
)
from feretui.feretui import FeretUI
from feretui.pages import homepage
from feretui.request import Request
from feretui.session import Session
from feretui.thread import local


class TestAction:

    def test_goto(self) -> None:
        myferet = FeretUI()
        session = Session()
        request = Request(
            method=Request.GET,
            session=session,
            querystring="page=homepage",
            headers={
                'Hx-Current-Url': '/',
            },
        )
        res = goto(myferet, request)
        assert res.body == homepage(myferet, session, {})
        assert res.headers['HX-Push-Url'] == "/?page=homepage"

    def test_goto_without_page(self) -> None:
        myferet = FeretUI()
        session = Session()
        request = Request(method=Request.GET, session=session)
        with pytest.raises(ActionError):
            goto(myferet, request)

    def test_goto_with_in_aside(self) -> None:
        myferet = FeretUI()
        session = Session()
        request = Request(
            method=Request.GET,
            session=session,
            querystring="in-aside=test&page=homepage",
            headers={
                'Hx-Current-Url': '/',
            },
        )
        res = goto(myferet, request)
        assert res.body == homepage(myferet, session, {})
        assert (
            res.headers['HX-Push-Url']
            == "/?page=aside-menu&aside=test&aside_page=homepage"
        )

    def test_login_password_1(self) -> None:
        myferet = FeretUI()
        session = Session()
        request = Request(method=Request.GET, session=session)

        with pytest.raises(ActionValidatorError):
            login_password(myferet, request)

    def test_login_password_2(self) -> None:
        myferet = FeretUI()
        session = Session(user="Test")
        request = Request(method=Request.POST, session=session)

        with pytest.raises(ActionUserIsAuthenticatedError):
            login_password(myferet, request)

    def test_login_password_3(self, snapshot) -> None:
        local.feretui = myferet = FeretUI()
        session = Session()
        local.request = request = Request(
            method=Request.POST, session=session)
        local.lang = 'fr'

        snapshot.assert_match(
            login_password(myferet, request).body,
            'snapshot.html',
        )

    def test_login_password_4(self) -> None:
        local.feretui = myferet = FeretUI()
        session = Session()
        local.request = request = Request(
            method=Request.POST,
            form=MultiDict({'login': 'test', 'password': 'test'}),
            session=session,
            headers={'Hx-Current-Url': '/'},
        )
        res = login_password(myferet, request)
        assert res.body == ''
        assert res.headers['HX-Refresh'] == 'true'

    def test_login_password_5(self) -> None:
        local.feretui = myferet = FeretUI()
        session = Session()
        local.request = request = Request(
            method=Request.POST,
            form=MultiDict({'login': 'test', 'password': 'test'}),
            session=session,
            headers={'Hx-Current-Url': '/test?page=login'},
        )
        res = login_password(myferet, request)
        assert res.body == ''
        assert res.headers['HX-Redirect'] == '/test?page=homepage'

    def test_login_password_6(self, snapshot) -> None:
        class MySession(Session):
            def login(self, form) -> NoReturn:
                raise Exception('Test')

        local.feretui = myferet = FeretUI()
        session = MySession()
        local.request = request = Request(
            method=Request.POST,
            form=MultiDict({'login': 'test', 'password': 'test'}),
            session=session,
            headers={'Hx-Current-Url': '/test?page=login'},
        )
        snapshot.assert_match(
            login_password(myferet, request).body,
            'snapshot.html',
        )

    def test_login_signup_1(self) -> None:
        myferet = FeretUI()
        session = Session()
        request = Request(method=Request.GET, session=session)

        with pytest.raises(ActionValidatorError):
            login_signup(myferet, request)

    def test_login_signup_2(self) -> None:
        myferet = FeretUI()
        session = Session(user="Test")
        request = Request(method=Request.POST, session=session)

        with pytest.raises(ActionUserIsAuthenticatedError):
            login_signup(myferet, request)

    def test_login_signup_3(self, snapshot) -> None:
        local.feretui = myferet = FeretUI()
        session = Session()
        local.request = request = Request(
            method=Request.POST, session=session)
        local.lang = 'fr'

        snapshot.assert_match(
            login_signup(myferet, request).body,
            'snapshot.html',
        )

    def test_login_signup_4(self) -> None:
        local.feretui = myferet = FeretUI()
        session = Session()
        local.request = request = Request(
            method=Request.POST,
            form=MultiDict({
                'login': 'test',
                'lang': 'en',
                'password': 'Testtest123!',
                'password_confirm': 'Testtest123!',
            }),
            session=session,
            headers={'Hx-Current-Url': '/'},
        )
        res = login_signup(myferet, request)
        assert res.body == ''
        assert res.headers['HX-Refresh'] == 'true'

    def test_login_signup_5(self) -> None:
        local.feretui = myferet = FeretUI()
        session = Session()
        local.request = request = Request(
            method=Request.POST,
            form=MultiDict({
                'login': 'test',
                'lang': 'en',
                'password': 'Testtest123!',
                'password_confirm': 'Testtest123!',
            }),
            session=session,
            headers={'Hx-Current-Url': '/test?page=signup'},
        )
        res = login_signup(myferet, request)
        assert res.body == ''
        assert res.headers['HX-Redirect'] == '/test?page=homepage'

    def test_login_signup_6(self, snapshot) -> None:
        class MySession(Session):
            def signup(self, form) -> NoReturn:
                raise Exception('Test')

        local.feretui = myferet = FeretUI()
        session = MySession()
        local.request = request = Request(
            method=Request.POST,
            form=MultiDict({
                'login': 'test',
                'lang': 'en',
                'password': 'Testtest123!',
                'password_confirm': 'Testtest123!',
            }),
            session=session,
            headers={'Hx-Current-Url': '/test?page=signup'},
        )
        snapshot.assert_match(
            login_signup(myferet, request).body,
            'snapshot.html',
        )

    def test_logout_1(self) -> None:
        myferet = FeretUI()
        session = Session(user="Test")
        request = Request(method=Request.GET, session=session)

        with pytest.raises(ActionValidatorError):
            logout(myferet, request)

    def test_logout_2(self) -> None:
        myferet = FeretUI()
        session = Session()
        request = Request(method=Request.POST, session=session)

        with pytest.raises(ActionUserIsNotAuthenticatedError):
            logout(myferet, request)

    def test_logout_3(self, snapshot) -> None:
        local.feretui = myferet = FeretUI()
        session = Session(user="Test")
        local.request = request = Request(
            method=Request.POST,
            session=session,
            headers={'Hx-Current-Url': '/test?page=signup'},
        )
        local.lang = 'fr'
        res = logout(myferet, request)
        assert res.body == ''
        assert res.headers['HX-Redirect'] == '/test'
