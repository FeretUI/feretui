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
from polib import POFile
from wtforms import StringField

from feretui.exceptions import ViewActionError, ViewError
from feretui.feretui import FeretUI
from feretui.request import Request
from feretui.resources.actions import (
    Actionset,
    GotoViewAction,
    SelectedRowsAction,
)
from feretui.resources.common import (
    ActionsMixinForView,
    MultiView,
    TemplateMixinForView,
)
from feretui.resources.resource import Resource
from feretui.resources.view import View
from feretui.session import Session
from feretui.thread import local


class MyViewWithAction(ActionsMixinForView, View):

    class Form:
        pk = StringField()

    actions = [
        Actionset(
            'Test',
            [
                SelectedRowsAction('foo', 'foo', description='Bar'),
                GotoViewAction('Bar', 'bar'),
            ],
            description='Other',
        ),
    ]


class MultiResource(Resource):

    def filtered_reads(self, form_cls, filters, offset, limit):
        return {'total': 0, 'forms': []}


class TestMultiView:

    def test_init_1(self) -> None:

        class MyView(MultiView, View):
            create_button_redirect_to = 'other'
            delete_button_redirect_to = 'other'
            do_click_on_entry_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = MultiResource()
        resource.context = 'test'
        with pytest.raises(ViewError):
            MyView(resource)

    def test_init_2(self) -> None:

        class MyView(MultiView, View):
            limit = 15
            delete_button_redirect_to = 'other'
            do_click_on_entry_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = MultiResource()
        resource.context = 'test'
        with pytest.raises(ViewError):
            MyView(resource)

    def test_init_3(self) -> None:

        class MyView(MultiView, View):
            limit = 15
            create_button_redirect_to = 'other'
            delete_button_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = MultiResource()
        resource.context = 'test'
        with pytest.raises(ViewError):
            MyView(resource)

    def test_init_4(self) -> None:

        class MyView(MultiView, View):
            limit = 15
            do_click_on_entry_redirect_to = 'other'
            create_button_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = MultiResource()
        resource.context = 'test'
        with pytest.raises(ViewError):
            MyView(resource)

    def test_init_5(self) -> None:

        class MyView(MultiView, View):
            limit = 15
            create_button_redirect_to = 'other'
            delete_button_redirect_to = 'other'
            do_click_on_entry_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = Resource()
        resource.context = 'test'
        with pytest.raises(ViewError):
            MyView(resource)

    def test_get_header_buttons(self, snapshot) -> None:

        class MyView(MultiView, View):
            limit = 15
            create_button_redirect_to = 'other'
            delete_button_redirect_to = 'other'
            do_click_on_entry_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = MultiResource()
        resource.context = 'test'
        view = MyView(resource)
        local.feretui = feretui = FeretUI()
        session = Session()
        snapshot.assert_match(
            view.get_header_buttons(feretui, session, {})[0],
            'snapshot.html',
        )

    def test_render_kwargs(self) -> None:

        class MyView(MultiView, View):
            limit = 15
            create_button_redirect_to = 'other'
            delete_button_redirect_to = 'other'
            do_click_on_entry_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = MultiResource()
        resource.context = 'test'
        view = MyView(resource)
        local.feretui = feretui = FeretUI()
        session = Session()
        local.request = Request(session=session)

        assert view.render_kwargs(feretui, session, {'offset': [0]})

    def test_call_pagination(self) -> None:
        local.feretui = myferet = FeretUI()
        session = Session()
        request = Request(
            method=Request.GET,
            querystring='offset=0',
            session=session,
            headers={'Hx-Current-Url': '/test?resource=test'},
        )

        class MyView(MultiView, View):
            limit = 15
            create_button_redirect_to = 'other'
            delete_button_redirect_to = 'other'
            do_click_on_entry_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = MultiResource()
        resource.context = 'test'
        view = MyView(resource)
        assert view.pagination(myferet, request).body is not None

    def test_call_filters_post(self) -> None:
        local.feretui = myferet = FeretUI()
        session = Session()
        request = Request(
            method=Request.POST,
            params={'foo': ['Bar'], 'action': ['filters']},
            session=session,
            headers={'Hx-Current-Url': '/test?resource=test'},
        )

        class MyView(MultiView, View):
            limit = 15
            create_button_redirect_to = 'other'
            delete_button_redirect_to = 'other'
            do_click_on_entry_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = MultiResource()
        resource.context = 'test'
        view = MyView(resource)
        res = view.filters(myferet, request)
        assert res.body is not None
        assert (
            res.headers['HX-Push-Url']
            == '/test?resource=test&offset=0&filter%5Bfoo%5D=Bar'
        )

    def test_call_filters_delete(self) -> None:
        local.feretui = myferet = FeretUI()
        session = Session()
        request = Request(
            method=Request.DELETE,
            params={'foo': ['Bar']},
            session=session,
            headers={
                'Hx-Current-Url': '/test?resource=test&filter%5Bfoo%5D=Bar',
            },
        )

        class MyView(MultiView, View):
            limit = 15
            create_button_redirect_to = 'other'
            delete_button_redirect_to = 'other'
            do_click_on_entry_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = MultiResource()
        resource.context = 'test'
        view = MyView(resource)
        res = view.filters(myferet, request)
        assert res.body is not None
        assert res.headers['HX-Push-Url'] == '/test?resource=test&offset=0'

    def test_goto_delete(self) -> None:
        local.feretui = myferet = FeretUI()
        session = Session()
        request = Request(
            method=Request.POST,
            session=session,
            headers={'Hx-Current-Url': '/test?resource=test'},
        )

        class MyView(MultiView, View):
            limit = 15
            create_button_redirect_to = 'other'
            delete_button_redirect_to = 'other'
            do_click_on_entry_redirect_to = 'other'

            class Form:
                pk = StringField()

            def get_call_kwargs(self, request):
                return {'pks': ['foo', 'bar']}

        resource = MultiResource()
        resource.context = 'test'
        view = MyView(resource)
        resource.views['other'] = view
        res = view.goto_delete(myferet, request)
        assert res.body is not None
        assert (
            res.headers['HX-Push-Url']
            == '/test?resource=test&view=other&pk=foo&pk=bar'
        )

    def test_export_catalog(self) -> None:

        class MyView(MultiView, View):
            limit = 15
            create_button_redirect_to = 'other'
            delete_button_redirect_to = 'other'
            do_click_on_entry_redirect_to = 'other'

            class Form:
                pk = StringField()

            class Filter:
                other = StringField()

        local.feretui = myferet = FeretUI()
        po = POFile()
        resource = MultiResource()
        resource.context = 'test'
        view = MyView(resource)
        view.export_catalog(myferet.translation, po)
        assert len(po) == 3


class TestCommonActionsMixinForView:

    def test_get_actions(self, snapshot) -> None:
        resource = Resource()
        resource.context = 'test'
        view = MyViewWithAction(resource)
        local.feretui = feretui = FeretUI()
        session = Session()
        snapshot.assert_match(
            view.get_actions(feretui, session, {})[0],
            'snapshot.html',
        )

    def test_get_call_kwargs(self, snapshot) -> None:
        resource = Resource()
        resource.context = 'test'
        view = MyViewWithAction(resource)
        assert view.get_call_kwargs({}) == {}

    def test_export_catalog(self) -> None:
        local.feretui = myferet = FeretUI()
        po = POFile()
        resource = Resource()
        resource.context = 'test'
        view = MyViewWithAction(resource)
        view.export_catalog(myferet.translation, po)
        assert len(po) == 6

    def test_call_1(self) -> None:
        local.feretui = myferet = FeretUI()
        session = Session()
        request = Request(method=Request.GET, session=session)
        resource = Resource()
        resource.context = 'test'
        view = MyViewWithAction(resource)
        with pytest.raises(ViewActionError):
            view.call(myferet, request)

    def test_call_2(self) -> None:
        local.feretui = myferet = FeretUI()
        session = Session()
        request = Request(
            method=Request.POST,
            params={},
            session=session,
        )
        resource = Resource()
        resource.context = 'test'
        view = MyViewWithAction(resource)
        with pytest.raises(ViewActionError):
            view.call(myferet, request)

    def test_call_3(self) -> None:
        local.feretui = myferet = FeretUI()
        session = Session()
        request = Request(
            method=Request.POST,
            params={'method': ['foo']},
            session=session,
        )

        class MyResource(Resource):

            def foo(self, *a, **kw) -> str:
                return 'bar'

        resource = MyResource()
        resource.context = 'test'
        view = MyViewWithAction(resource)
        assert view.call(myferet, request).body == 'bar'

    def test_call_4(self) -> None:
        local.feretui = myferet = FeretUI()
        session = Session()
        request = Request(
            method=Request.POST,
            params={'method': ['foo']},
            session=session,
            headers={'Hx-Current-Url': '/test?resource=test'},
        )

        class MyResource(Resource):

            def foo(self, *a, **kw) -> None:
                return None

        resource = MyResource()
        resource.context = 'test'
        view = MyViewWithAction(resource)
        assert view.call(myferet, request).body is not None


class TestTemplateMixinForView:

    def test_render_1(self, snapshot) -> None:

        class MyResource(Resource):
            code = 'foo'

            class Form:
                pk = StringField()

        class MyView(TemplateMixinForView, View):
            code = 'bar'

        resource = MyResource()
        resource.context = 'test'
        view = MyView(resource)
        local.feretui = feretui = FeretUI()
        session = Session()
        local.request = Request(session=session)

        snapshot.assert_match(
            view.render(feretui, session, {}),
            'snapshot.html',
        )

    def test_render_2(self, snapshot) -> None:

        class MyResource(Resource):
            code = 'foo'

            class Form:
                pk = StringField()

        class MyView(TemplateMixinForView, View):
            code = 'bar'
            header_template = "<div>Header</div>"
            body_template = "<div>Body</div>"
            footer_template = "<div>Footer</div>"

        resource = MyResource()
        resource.context = 'test'
        view = MyView(resource)
        local.feretui = feretui = FeretUI()
        session = Session()
        local.request = Request(session=session)

        snapshot.assert_match(
            view.render(feretui, session, {}),
            'snapshot.html',
        )

    def test_export_catalog_1(self) -> None:
        class MyResource(Resource):
            code = 'foo'

            class Form:
                pk = StringField()

        class MyView(TemplateMixinForView, View):
            code = 'bar'

        local.feretui = myferet = FeretUI()
        po = POFile()
        resource = MyResource()
        resource.context = 'test'
        view = MyView(resource)
        view.export_catalog(myferet.translation, po)
        assert len(po) == 1

    def test_export_catalog_2(self) -> None:
        class MyResource(Resource):
            code = 'foo'

            class Form:
                pk = StringField()

        class MyView(TemplateMixinForView, View):
            code = 'bar'
            header_template = "<div>Header</div>"
            body_template = "<div>Body</div>"
            footer_template = "<div>Footer</div>"

        local.feretui = myferet = FeretUI()
        po = POFile()
        resource = MyResource()
        resource.context = 'test'
        view = MyView(resource)
        view.export_catalog(myferet.translation, po)
        assert len(po) == 4
