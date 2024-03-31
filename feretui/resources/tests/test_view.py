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


class TView(View):
    code = 'test'


class TResource:

    class MetaViewTest:
        pass

    def build_view(resource, name, cls):
        if name.startswith('MetaViewTest'):
            view_cls = type(
                'TView',
                (cls, TView),
                {},
            )
            return view_cls(resource)

        return super().build_view(resource, name, cls)


class MyResource(TResource, Resource):
    code = 'foo'
    label = 'Bar'


class TestResourceView:

    def test_view_render(self):
        local.feretui = feretui = FeretUI()
        session = Session()
        resource = MyResource.build()
        assert resource.views['test'].render(feretui, session, {})

    def test_view_get_label(self):
        local.feretui = FeretUI()
        resource = MyResource.build()
        assert resource.views['test'].get_label()

    def test_get_transition_querystring_1(self):
        resource = MyResource.build()
        assert resource.views['test'].get_transition_querystring(
            {'foo': 'bar'},
            foo=None,
        ) == ''

    def test_get_transition_querystring_2(self):
        resource = MyResource.build()
        assert resource.views['test'].get_transition_querystring(
            {'foo': 'bar'},
            bar='bar',
        ) == 'foo=bar&bar=bar'

    def test_get_transition_querystring_3(self):
        resource = MyResource.build()
        assert resource.views['test'].get_transition_querystring(
            {'foo': 'bar'},
            bar=['bar'],
        ) == 'foo=bar&bar=bar'
