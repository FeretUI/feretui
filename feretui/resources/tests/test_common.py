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

from feretui.resources.resource import Resource
from feretui.resources.view import View
from feretui.feretui import FeretUI
from feretui.session import Session
from feretui.thread import local
from polib import POFile
from wtforms import StringField
from feretui.exceptions import ViewActionError, ViewError
from feretui.resources.common import (ActionsMixinForView, MultiView)
from feretui.resources.actions import Actionset, SelectedRowsAction
from feretui.request import Request


class MyViewWithAction(ActionsMixinForView, View):

    class Form:
        pk = StringField()

    actions = [
        Actionset(
            'Test',
            [SelectedRowsAction('foo', 'foo', description='Bar')],
            description='Other'
        )
    ]


class MultiResource(Resource):

    def filtered_reads(self, form_cls, filters, offset, limit):
        return {'total': 0, 'forms': []}


class TestMultiView:

    def test_init_1(self):

        class MyView(MultiView, View):
            create_button_redirect_to = 'other'
            do_click_on_entry_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = MultiResource()
        resource.context = 'test'
        with pytest.raises(ViewError):
            MyView(resource)

    def test_init_2(self):

        class MyView(MultiView, View):
            limit = 15
            do_click_on_entry_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = MultiResource()
        resource.context = 'test'
        with pytest.raises(ViewError):
            MyView(resource)

    def test_init_3(self):

        class MyView(MultiView, View):
            limit = 15
            create_button_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = MultiResource()
        resource.context = 'test'
        with pytest.raises(ViewError):
            MyView(resource)

    def test_init_4(self):

        class MyView(MultiView, View):
            limit = 15
            create_button_redirect_to = 'other'
            do_click_on_entry_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = Resource()
        resource.context = 'test'
        with pytest.raises(ViewError):
            MyView(resource)

    def test_get_header_buttons(self, snapshot):

        class MyView(MultiView, View):
            limit = 15
            create_button_redirect_to = 'other'
            do_click_on_entry_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = MultiResource()
        resource.context = 'test'
        view = MyView(resource)
        local.feretui = feretui = FeretUI()
        session = Session()
        snapshot.assert_match(
            view.get_header_buttons(feretui, session, dict())[0],
            'snapshot.html',
        )

    def test_render_kwargs(self):

        class MyView(MultiView, View):
            limit = 15
            create_button_redirect_to = 'other'
            do_click_on_entry_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = MultiResource()
        resource.context = 'test'
        view = MyView(resource)
        local.feretui = feretui = FeretUI()
        session = Session()

        assert view.render_kwargs(feretui, session, {'offset': [0]})

    def test_call_pagination(self):
        local.feretui = myferet = FeretUI()
        session = Session()
        request = Request(
            method=Request.POST,
            querystring='offset=0',
            session=session,
            headers={'Hx-Current-Url': '/test?resource=test'},
        )

        class MyView(MultiView, View):
            limit = 15
            create_button_redirect_to = 'other'
            do_click_on_entry_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = MultiResource()
        resource.context = 'test'
        view = MyView(resource)
        assert view.pagination(myferet, request).body is not None


class TestCommonActionsMixinForView:

    def test_get_actions(self, snapshot):
        resource = Resource()
        resource.context = 'test'
        view = MyViewWithAction(resource)
        local.feretui = feretui = FeretUI()
        session = Session()
        snapshot.assert_match(
            view.get_actions(feretui, session)[0],
            'snapshot.html',
        )

    def test_get_call_kwargs(self, snapshot):
        resource = Resource()
        resource.context = 'test'
        view = MyViewWithAction(resource)
        assert view.get_call_kwargs({}) == {}

    def test_export_catalog(self):
        local.feretui = myferet = FeretUI()
        po = POFile()
        resource = Resource()
        resource.context = 'test'
        view = MyViewWithAction(resource)
        view.export_catalog(myferet.translation, po)
        assert len(po) == 5

    def test_call_1(self):
        local.feretui = myferet = FeretUI()
        session = Session()
        request = Request(method=Request.GET, session=session)
        resource = Resource()
        resource.context = 'test'
        view = MyViewWithAction(resource)
        with pytest.raises(ViewActionError):
            view.call(myferet, request)

    def test_call_2(self):
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

    def test_call_3(self):
        local.feretui = myferet = FeretUI()
        session = Session()
        request = Request(
            method=Request.POST,
            params={'method': ['foo']},
            session=session,
        )

        class MyResource(Resource):

            def foo(self, *a, **kw):
                return 'bar'

        resource = MyResource()
        resource.context = 'test'
        view = MyViewWithAction(resource)
        assert view.call(myferet, request).body == 'bar'

    def test_call_4(self):
        local.feretui = myferet = FeretUI()
        session = Session()
        request = Request(
            method=Request.POST,
            params={'method': ['foo']},
            session=session,
            headers={'Hx-Current-Url': '/test?resource=test'},
        )

        class MyResource(Resource):

            def foo(self, *a, **kw):
                return None

        resource = MyResource()
        resource.context = 'test'
        view = MyViewWithAction(resource)
        assert view.call(myferet, request).body is not None
