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

from feretui.request import Request
from feretui.resources import CResource, Resource


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

    def test_render_1(self, snapshot, feretui, session, frequest) -> None:
        resource = MyResource.build()
        snapshot.assert_match(
            resource.views['create'].render(
                feretui, session, {'error': 'With error'},
            ),
            'snapshot.html',
        )

    def test_render_2(self, snapshot, feretui, session, frequest) -> None:
        resource = MyResource.build()
        form = resource.views['create'].form_cls(pk=1)
        form.validate()
        snapshot.assert_match(
            resource.views['create'].render(
                feretui, session, {'form': form},
            ),
            'snapshot.html',
        )

    def test_render_3(self, snapshot, feretui, session, frequest) -> None:
        resource = MyResource.build()
        resource.views['create'].label = 'Test'
        snapshot.assert_match(
            resource.views['create'].render(
                feretui, session, {},
            ),
            'snapshot.html',
        )

    def test_export_catalog(self, feretui) -> None:
        po = POFile()
        resource = MyResource.build()
        resource.context = 'test'
        resource.views['create'].export_catalog(feretui.translation, po)
        assert len(po) == 5

    def test_save_empty(self, snapshot, feretui, session) -> None:
        resource = MyResource.build()
        request = Request(
            session=session,
            form=MultiDict(),
            headers={'Hx-Current-Url': '/?'},
        )
        snapshot.assert_match(
            resource.views['create'].save(feretui, request).body,
            'snapshot.html',
        )

    def test_save(self, snapshot, feretui, session) -> None:
        class MyResource2(MyResource):
            class MetaViewCreate:
                after_create_redirect_to = 'create'

        resource = MyResource2.build()
        request = Request(
            session=session,
            form=MultiDict(pk=1, foo='bar', test='test1'),
            headers={'Hx-Current-Url': '/?'},
        )
        snapshot.assert_match(
            resource.views['create'].save(feretui, request).body,
            'snapshot.html',
        )

    def test_save_error(self, snapshot, feretui, session) -> None:
        class MyResource2(MyResource):

            def create(self, *a) -> NoReturn:
                raise Exception

        resource = MyResource2.build()
        request = Request(
            session=session,
            form=MultiDict(pk=1, foo='bar', test='test1'),
            headers={'Hx-Current-Url': '/?'},
        )
        snapshot.assert_match(
            resource.views['create'].save(feretui, request).body,
            'snapshot.html',
        )
