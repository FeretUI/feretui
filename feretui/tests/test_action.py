from typing import NoReturn

import pytest
from multidict import MultiDict
from wtforms import StringField

from feretui.actions import (
    close_modal,
    goto,
    login_password,
    login_signup,
    logout,
    modal,
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
from feretui.resources import OpenModalAction
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
        assert res.headers['HX-Title'] == "FeretUI"

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

    def test_modal_without_resource(self, feretui, session) -> None:
        request = Request(method=Request.GET, session=session)
        with pytest.raises(ActionError, match="No resource"):
            modal(feretui, request)

    def test_modal_with_unexisting_view(self, feretui, session) -> None:
        @feretui.register_resource()
        class MyResource(Resource):
            code = "test_modal_res"
            label = "Test Modal Res"

        request = Request(
            method=Request.GET,
            session=session,
            querystring="resource=test_modal_res&view=nonexistent",
        )
        with pytest.raises(ActionError, match="View nonexistent not found"):
            modal(feretui, request)

    def test_modal_render(self, feretui, session) -> None:
        @feretui.register_resource()
        class MyResource(Resource):
            code = "modal_record"
            label = "Modal Record"

            class Form:
                pk = StringField()

        class DummyView(View):
            code = "create"

            class Form:
                pk = StringField()

            def render(self, feretui, session, options):
                return "<form id='dummy-form'>Dummy Content</form>"

        feretui.resources["modal_record"].views["create"] = DummyView(
            feretui.resources["modal_record"]
        )

        request = Request(
            method=Request.GET,
            session=session,
            querystring="resource=modal_record&view=create&title=Quick+Create&modal_size=large",
        )
        res = modal(feretui, request)
        assert res.status_code == 200
        assert '<dialog class="feretui-modal"' in res.body
        assert "feretui-modal-large" in res.body
        assert "Quick Create" in res.body
        assert "Dummy Content" in res.body

    def test_close_modal(self, feretui, session) -> None:
        request = Request(method=Request.POST, session=session)
        res = close_modal(feretui, request)
        assert res.status_code == 200
        assert res.headers["HX-Trigger"] == "closeModal"

    def test_open_modal_action(self, feretui, session) -> None:
        from feretui.context import cvar_feretui, cvar_request

        cvar_feretui.set(feretui)
        cvar_request.set(Request(session=session))

        action = OpenModalAction(
            label="Add Subline",
            resource="lines",
            view="create",
            title="Add Order Line",
            modal_size="large",
            target_field="line_ids",
            icon="ti ti-plus",
            description="Create a new line in dialog",
        )
        action.context = "resource:orders:view:read:action:modal"
        url = action.get_url(feretui, session, {"resource": "orders", "pk": "123"})
        assert "/action/modal?" in url
        assert "resource=lines" in url
        assert "view=create" in url
        assert "title=Add+Order+Line" in url
        assert "target_field=line_ids" in url
        assert "modal_size=large" in url

        rendered = action.render(feretui, session, {}, "orders", "read")
        assert 'hx-target="#feretui-modal-stack"' in rendered
        assert 'hx-swap="beforeend"' in rendered
        assert "Add Subline" in rendered
        assert "ti ti-plus" in rendered
        assert 'data-tooltip="Create a new line in dialog"' in rendered
        assert "ti ti-info-circle" in rendered

        # Test OpenModalAction with pk and empty resource falling back to options
        action_with_pk = OpenModalAction(
            label="Edit Line",
            resource="",
            view="edit",
            pk="999",
        )
        url2 = action_with_pk.get_url(feretui, session, {"resource": "lines"})
        assert "resource=lines" in url2
        assert "pk=999" in url2

    def test_modal_render_default_title(self, feretui, session) -> None:
        @feretui.register_resource()
        class MyResource2(Resource):
            code = "modal_record2"
            label = "Modal Item"

            class Form:
                pk = StringField()

        class DummyView(View):
            code = "edit"

            class Form:
                pk = StringField()

            def render(self, feretui, session, options):
                return "<div>Edit Content</div>"

        feretui.resources["modal_record2"].views["edit"] = DummyView(
            feretui.resources["modal_record2"]
        )

        request = Request(
            method=Request.GET,
            session=session,
            querystring="resource=modal_record2&view=edit",
        )
        res = modal(feretui, request)
        assert res.status_code == 200
        assert "Modal Item - Edit" in res.body

