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
from feretui.exceptions import ViewFormError


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

    def test_export_catalog(self):
        local.feretui = myferet = FeretUI()
        po = POFile()
        resource = MyResource.build()
        resource.export_catalog(myferet.translation, po)
        assert len(po) == 2
        form = resource.views['test'].form_cls()
        assert form.pk.label.text == 'Pk'

    def test_without_pk(self) -> None:
        with pytest.raises(ViewFormError):
            resource = MyResource()
            resource.context = 'test'
            View(resource)
