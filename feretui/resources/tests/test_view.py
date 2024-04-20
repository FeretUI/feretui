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

from feretui.exceptions import ViewActionError, ViewFormError
from feretui.request import Request
from feretui.resources.resource import Resource
from feretui.resources.view import View, view_action_validator
from feretui.context import cvar_request


class TView(View):
    code = 'test'

    class Form:
        pk = StringField()


class TResource:

    class MetaViewTest:
        pass

    def build_view(self, name):
        if name.startswith('MetaViewTest'):
            meta_view_cls = self.get_meta_view_class(name)
            meta_view_cls.append(TView)
            view_cls = type(
                'TView',
                tuple(meta_view_cls),
                {},
            )
            return view_cls(self)

        return super().build_view(self, name)


class MyResource(TResource, Resource):
    code = 'foo'
    label = 'Bar'


class TestResourceView:

    def test_view_render(self, feretui, session) -> None:
        resource = MyResource.build()
        assert resource.views['test'].render(feretui, session, {})

    def test_view_get_label(self, feretui, session, frequest) -> None:
        resource = MyResource.build()
        assert resource.views['test'].get_label(feretui, session)

    def test_get_transition_url_1(self, feretui) -> None:
        resource = MyResource.build()
        assert resource.views['test'].get_transition_url(
            feretui,
            {'foo': 'bar'},
            foo=None,
        ) == '/feretui/action/resource?action=goto'

    def test_get_transition_url_2(self, feretui) -> None:
        resource = MyResource.build()
        assert resource.views['test'].get_transition_url(
            feretui,
            {'foo': 'bar'},
            bar='bar',
        ) == '/feretui/action/resource?foo=bar&action=goto&bar=bar'

    def test_get_transition_url_3(self, feretui) -> None:
        resource = MyResource.build()
        assert resource.views['test'].get_transition_url(
            feretui,
            {'foo': 'bar'},
            bar=['bar'],
        ) == '/feretui/action/resource?foo=bar&action=goto&bar=bar'

    def test_export_catalog(self, feretui, frequest) -> None:
        po = POFile()
        resource = MyResource.build()
        resource.export_catalog(feretui.translation, po)
        assert len(po) == 2
        form = resource.views['test'].form_cls()
        assert form.pk.label.text == 'Pk'

    def test_without_pk(self) -> None:
        with pytest.raises(ViewFormError):
            resource = MyResource()
            resource.context = 'test'
            View(resource)

    def test_goto_without_view(self, snapshot, feretui, session) -> None:
        request = Request(
            session=session,
            method=Request.GET,
            headers={'Hx-Current-Url': '/test?'},
        )
        cvar_request.set(request)

        class MyView(View):
            class Form:
                pk = StringField()

        resource = Resource()
        resource.context = 'test'
        view = MyView(resource)
        snapshot.assert_match(
            view.goto(feretui, request).body,
            'snapshot.html',
        )

    def test_goto_with_view(self, snapshot, feretui, session) -> None:
        request = Request(
            method=Request.GET,
            querystring='view=test',
            session=session,
            headers={'Hx-Current-Url': '/test?'},
        )
        cvar_request.set(request)

        class MyView(View):
            class Form:
                pk = StringField()

        resource = Resource()
        resource.context = 'test'
        view = MyView(resource)
        resource.views = {'test': view}
        snapshot.assert_match(
            view.goto(feretui, request).body,
            'snapshot.html',
        )

    def test_decorator(self, snapshot, feretui, frequest) -> None:

        class MyView(View):
            class Form:
                pk = StringField()

            @view_action_validator()
            def foo(self, *a, **kw) -> str:
                return 'bar'

        resource = Resource()
        resource.context = 'test'
        view = MyView(resource)
        with pytest.raises(ViewActionError):
            view.foo(feretui, frequest)
