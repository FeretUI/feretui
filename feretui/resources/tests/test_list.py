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
from wtforms import SelectField, StringField

from feretui.feretui import FeretUI
from feretui.request import Request
from feretui.resources.actions import Action, Actionset, SelectedRowsAction
from feretui.resources.list import LResource
from feretui.resources.resource import Resource
from feretui.session import Session
from feretui.thread import local


class MyResource(LResource, Resource):
    code = 'foo'
    label = 'Bar'

    class Form:
        pk = StringField()

    class MetaViewOther:
        pass

    class MetaViewList:

        class Form:
            foo = StringField()
            test = SelectField(choices=[('test1', 'Test 1')])

        class Filter:
            bar = StringField()

        actions = [
            Actionset('Print', [
                Action('Print 1', 'print_1'),
                SelectedRowsAction('Print 10', 'print_10'),
            ]),
        ]

    def filtered_reads(self, form_cls, filters, offset, limit):
        total = 10
        forms = [
            form_cls(pk=str(x), foo='Foo', test='test1')
            for x in range(total)
        ]
        return {
            'total': total,
            'forms': forms,
        }


class MyResource2(MyResource):
    default_view = None

    class MetaViewList:
        label = 'other label'


class TestLResource:

    def test_view_render(self, snapshot) -> None:
        local.feretui = feretui = FeretUI()
        session = Session(user='Test')
        local.request = Request(session=session)
        resource = MyResource.build()
        snapshot.assert_match(
            resource.views['list'].render(
                feretui, session, {'filter[foo]': ['Foo']},
            ),
            'snapshot.html',
        )

    def test_export_catalog_1(self) -> None:
        local.feretui = myferet = FeretUI()
        po = POFile()
        resource = MyResource.build()
        resource.context = 'test'
        resource.views['list'].export_catalog(myferet.translation, po)
        assert len(po) == 12

    def test_export_catalog_2(self) -> None:
        local.feretui = myferet = FeretUI()
        po = POFile()
        resource = MyResource2.build()
        resource.context = 'test'
        resource.views['list'].export_catalog(myferet.translation, po)
        assert len(po) == 13

    def test_get_label(self) -> None:
        local.feretui = FeretUI()
        resource = MyResource2.build()
        resource.context = 'test'
        assert resource.views['list'].get_label() == 'other label'

    def test_get_call_kwargs(self) -> None:
        resource = MyResource2.build()
        resource.context = 'test'
        view = resource.views['list']
        assert view.get_call_kwargs(
            {'selected-rows-resource-foo-view-list': ['foo', 'bar']},
        ) == {'pks': ['foo', 'bar']}
