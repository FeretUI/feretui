from typing import NoReturn

import pytest
from multidict import MultiDict
from wtforms import StringField

from feretui.actions import (
    goto,
    login_password,
    login_signup,
    logout,
    resource,
)
from feretui.exceptions import (
    ActionError,
    ActionUserIsAuthenticatedError,
    ActionUserIsNotAuthenticatedError,
    ActionValidatorError,
    ResourceError,
)
from feretui.pages import homepage
from feretui.request import Request
from feretui.resources.resource import Resource
from feretui.resources.view import View
from feretui.response import Response
from feretui.context import cvar_request
from feretui.session import Session


class TestAction:

    def test_goto(self, feretui, session) -> None:
        request = Request(
            method=Request.GET,
            session=session,
            querystring="page=homepage",
            headers={
                'Hx-Current-Url': '/',
            },
        )
        res = goto(feretui, request)
        assert res.body == homepage(feretui, session, {})
        assert res.headers['HX-Push-Url'] == "/?page=homepage"

    def test_goto_without_page(self, feretui, session) -> None:
        request = Request(method=Request.GET, session=session)
        with pytest.raises(ActionError):
            goto(feretui, request)

    def test_goto_with_in_aside(self, feretui, session) -> None:
        request = Request(
            method=Request.GET,
            session=session,
            querystring="in-aside=test&page=homepage",
            headers={
                'Hx-Current-Url': '/',
            },
        )
        res = goto(feretui, request)
        assert res.body == homepage(feretui, session, {})
        assert (
            res.headers['HX-Push-Url']
            == "/?page=aside-menu&aside=test&aside_page=homepage"
        )

    def test_login_password_1(self, feretui, session) -> None:
        request = Request(method=Request.GET, session=session)

        with pytest.raises(ActionValidatorError):
            login_password(feretui, request)

    def test_login_password_2(self, feretui, authenticated_session) -> None:
        request = Request(method=Request.POST, session=authenticated_session)

        with pytest.raises(ActionUserIsAuthenticatedError):
            login_password(feretui, request)

    def test_login_password_3(self, snapshot, feretui, session) -> None:
        request = Request(
            method=Request.POST, session=session)
        session.lang = 'fr'
        cvar_request.set(request)
        snapshot.assert_match(
            login_password(feretui, request).body,
            'snapshot.html',
        )

    def test_login_password_4(self, feretui, session) -> None:
        request = Request(
            method=Request.POST,
            form=MultiDict({'login': 'test', 'password': 'test'}),
            session=session,
            headers={'Hx-Current-Url': '/'},
        )
        cvar_request.set(request)
        res = login_password(feretui, request)
        assert res.body == ''
        assert res.headers['HX-Refresh'] == 'true'

    def test_login_password_5(self, feretui, session) -> None:
        request = Request(
            method=Request.POST,
            form=MultiDict({'login': 'test', 'password': 'test'}),
            session=session,
            headers={'Hx-Current-Url': '/test?page=login'},
        )
        res = login_password(feretui, request)
        assert res.body == ''
        assert res.headers['HX-Redirect'] == '/test?page=homepage'

    def test_login_password_6(self, snapshot, feretui) -> None:
        class MySession(Session):
            def login(self, form) -> NoReturn:
                raise Exception('Test')

        session = MySession()
        request = Request(
            method=Request.POST,
            form=MultiDict({'login': 'test', 'password': 'test'}),
            session=session,
            headers={'Hx-Current-Url': '/test?page=login'},
        )
        snapshot.assert_match(
            login_password(feretui, request).body,
            'snapshot.html',
        )

    def test_login_signup_1(self, feretui, session) -> None:
        request = Request(method=Request.GET, session=session)
        with pytest.raises(ActionValidatorError):
            login_signup(feretui, request)

    def test_login_signup_2(self, feretui, authenticated_session) -> None:
        request = Request(method=Request.POST, session=authenticated_session)

        with pytest.raises(ActionUserIsAuthenticatedError):
            login_signup(feretui, request)

    def test_login_signup_3(self, snapshot, feretui, session) -> None:
        request = Request(
            method=Request.POST, session=session)
        session.lang = 'fr'
        cvar_request.set(request)

        snapshot.assert_match(
            login_signup(feretui, request).body,
            'snapshot.html',
        )

    def test_login_signup_4(self, feretui, session) -> None:
        request = Request(
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
        cvar_request.set(request)
        res = login_signup(feretui, request)
        assert res.body == ''
        assert res.headers['HX-Refresh'] == 'true'

    def test_login_signup_5(self, feretui, session) -> None:
        request = Request(
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
        res = login_signup(feretui, request)
        assert res.body == ''
        assert res.headers['HX-Redirect'] == '/test?page=homepage'

    def test_login_signup_6(self, snapshot, feretui) -> None:
        class MySession(Session):
            def signup(self, form) -> NoReturn:
                raise Exception('Test')

        session = MySession()
        request = Request(
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
            login_signup(feretui, request).body,
            'snapshot.html',
        )

    def test_logout_1(self, feretui, authenticated_session) -> None:
        request = Request(method=Request.GET, session=authenticated_session)

        with pytest.raises(ActionValidatorError):
            logout(feretui, request)

    def test_logout_2(self, feretui, session) -> None:
        request = Request(method=Request.POST, session=session)

        with pytest.raises(ActionUserIsNotAuthenticatedError):
            logout(feretui, request)

    def test_logout_3(self, snapshot, feretui, authenticated_session) -> None:
        request = Request(
            method=Request.POST,
            session=authenticated_session,
            headers={'Hx-Current-Url': '/test?page=signup'},
        )
        res = logout(feretui, request)
        assert res.body == ''
        assert res.headers['HX-Redirect'] == '/test'

    def test_resource_1(self, feretui, authenticated_session) -> None:
        request = Request(
            method=Request.POST,
            session=authenticated_session,
            headers={'Hx-Current-Url': '/test?page=signup'},
        )
        with pytest.raises(ResourceError):
            resource(feretui, request)

    def test_resource_2(self, feretui, authenticated_session) -> None:
        request = Request(
            method=Request.POST,
            session=authenticated_session,
            params=MultiDict({}),
            headers={'Hx-Current-Url': '/test?resource=test'},
        )

        @feretui.register_resource()
        class MyResource(Resource):
            code = 'test'
            label = 'Test'

        with pytest.raises(ResourceError):
            resource(feretui, request)

    def test_resource_3(self, feretui, authenticated_session) -> None:
        request = Request(
            method=Request.POST,
            session=authenticated_session,
            params=MultiDict({}),
            headers={'Hx-Current-Url': '/test?resource=test&view=test'},
        )

        @feretui.register_resource()
        class MyResource(Resource):
            code = 'test'
            label = 'Test'

        with pytest.raises(ResourceError):
            resource(feretui, request)

    def test_resource_4(self, feretui, authenticated_session) -> None:
        request = Request(
            method=Request.POST,
            session=authenticated_session,
            params=MultiDict({}),
            headers={'Hx-Current-Url': '/test?resource=test&view=test'},
        )

        @feretui.register_resource()
        class MyResource(Resource):
            code = 'test'
            label = 'Test'

            class Form:
                pk = StringField()

        feretui.resources['test'].views['test'] = View(
            feretui.resources['test'])

        with pytest.raises(ResourceError):
            resource(feretui, request)

    def test_resource_5(self, feretui, authenticated_session) -> None:
        request = Request(
            method=Request.POST,
            session=authenticated_session,
            params=MultiDict({'action': ['foo']}),
            headers={'Hx-Current-Url': '/test?resource=test&view=test'},
        )

        @feretui.register_resource()
        class MyResource(Resource):
            code = 'test'
            label = 'Test'

            class Form:
                pk = StringField()

        feretui.resources['test'].views['test'] = View(
            feretui.resources['test'])

        with pytest.raises(ResourceError):
            resource(feretui, request)

    def test_resource_6(self, feretui, authenticated_session) -> None:
        request = Request(
            method=Request.POST,
            session=authenticated_session,
            params=MultiDict({'action': ['foo']}),
            headers={'Hx-Current-Url': '/test?resource=test&view=test'},
        )

        @feretui.register_resource()
        class MyResource(Resource):
            code = 'test'
            label = 'Test'

        class MyView(View):

            class Form:
                pk = StringField()

            def foo(self, feretui, request):
                return Response('bar')

        feretui.resources['test'].views['test'] = MyView(
            feretui.resources['test'])

        assert resource(feretui, request).body == 'bar'

    def test_resource_7(self, feretui, authenticated_session) -> None:
        request = Request(
            method=Request.POST,
            session=authenticated_session,
            params=MultiDict({'action': ['foo']}),
            headers={'Hx-Current-Url': '/test?resource=test&view=test'},
        )

        @feretui.register_resource()
        class MyResource(Resource):
            code = 'test'
            label = 'Test'
            action_security = None

        class MyView(View):

            class Form:
                pk = StringField()

            def foo(self, feretui, request):
                return Response('bar')

        feretui.resources['test'].views['test'] = MyView(
            feretui.resources['test'])

        assert resource(feretui, request).body == 'bar'
