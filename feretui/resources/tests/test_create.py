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
from typing import NoReturn

import pytest  # noqa: F401
from multidict import MultiDict
from polib import POFile
from wtforms import SelectField, StringField

from feretui.feretui import FeretUI
from feretui.request import Request
from feretui.resources import CResource, Resource
from feretui.session import Session
from feretui.thread import local


class MyResource(CResource, Resource):
    code = 'foo'
    label = 'Foo'

    class Form:
        pk = StringField()

    class MetaViewTest:
        pass

    class MetaViewCreate:
        pass

        class Form:
            foo = StringField()
            test = SelectField(choices=[('test1', 'Test 1')])

    def create(self, form):
        return form.pk.data


class TestCreateView:

    def test_render_1(self, snapshot) -> None:

        resource = MyResource.build()
        local.feretui = feretui = FeretUI()
        session = Session()
        local.request = Request(session=session)

        snapshot.assert_match(
            resource.views['create'].render(
                feretui, session, {'error': 'With error'},
            ),
            'snapshot.html',
        )

    def test_render_2(self, snapshot) -> None:

        resource = MyResource.build()
        local.feretui = feretui = FeretUI()
        session = Session()
        local.request = Request(session=session)

        form = resource.views['create'].form_cls(pk=1)
        form.validate()
        snapshot.assert_match(
            resource.views['create'].render(
                feretui, session, {'form': form},
            ),
            'snapshot.html',
        )

    def test_render_3(self, snapshot) -> None:

        resource = MyResource.build()
        local.feretui = feretui = FeretUI()
        session = Session()
        local.request = Request(session=session)

        resource.views['create'].label = 'Test'
        snapshot.assert_match(
            resource.views['create'].render(
                feretui, session, {},
            ),
            'snapshot.html',
        )

    def test_export_catalog_1(self) -> None:
        local.feretui = myferet = FeretUI()
        po = POFile()
        resource = MyResource.build()
        resource.context = 'test'
        resource.views['create'].export_catalog(myferet.translation, po)
        assert len(po) == 4

    def test_export_catalog_2(self) -> None:
        local.feretui = myferet = FeretUI()
        po = POFile()
        resource = MyResource.build()
        resource.context = 'test'
        resource.views['create'].label = 'Test'
        resource.views['create'].export_catalog(myferet.translation, po)
        assert len(po) == 5

    def test_save_empty(self, snapshot) -> None:
        local.feretui = feretui = FeretUI()
        resource = MyResource.build()
        session = Session()
        local.request = request = Request(
            session=session,
            form=MultiDict(),
            headers={'Hx-Current-Url': '/?'},
        )
        snapshot.assert_match(
            resource.views['create'].save(feretui, request).body,
            'snapshot.html',
        )

    def test_save(self, snapshot) -> None:
        class MyResource2(MyResource):
            class MetaViewCreate:
                after_create_redirect_to = 'create'

        local.feretui = feretui = FeretUI()
        resource = MyResource2.build()
        session = Session()
        local.request = request = Request(
            session=session,
            form=MultiDict(pk=1, foo='bar', test='test1'),
            headers={'Hx-Current-Url': '/?'},
        )
        snapshot.assert_match(
            resource.views['create'].save(feretui, request).body,
            'snapshot.html',
        )

    def test_save_error(self, snapshot) -> None:
        class MyResource2(MyResource):

            def create(self, *a) -> NoReturn:
                raise Exception

        local.feretui = feretui = FeretUI()
        resource = MyResource2.build()
        session = Session()
        local.request = request = Request(
            session=session,
            form=MultiDict(pk=1, foo='bar', test='test1'),
            headers={'Hx-Current-Url': '/?'},
        )
        snapshot.assert_match(
            resource.views['create'].save(feretui, request).body,
            'snapshot.html',
        )
