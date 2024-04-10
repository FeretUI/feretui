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
from feretui.resources import UResource, Resource
from feretui.session import Session
from feretui.thread import local


class MyResource(UResource, Resource):
    code = 'foo'
    label = 'Foo'

    class Form:
        pk = StringField()

    class MetaViewTest:
        pass

    class MetaViewUpdate:

        class Form:
            foo = StringField()
            test = SelectField(choices=[('test1', 'Test 1')])

    def update(self, forms):
        pass

    def read(self, form_cls, pk):
        return form_cls(MultiDict(pk=pk))


class TestEditView:

    def test_render_1(self, snapshot) -> None:

        resource = MyResource.build()
        local.feretui = feretui = FeretUI()
        session = Session()
        local.request = Request(session=session)

        snapshot.assert_match(
            resource.views['edit'].render(
                feretui, session, {'pk': ['foo'], 'error': 'With error'},
            ),
            'snapshot.html',
        )

    def test_render_2(self, snapshot) -> None:

        resource = MyResource.build()
        local.feretui = feretui = FeretUI()
        session = Session()
        local.request = Request(session=session)

        resource.views['edit'].cancel_button_redirect_to = 'other'
        form = resource.views['edit'].form_cls(pk=1)
        form.validate()
        snapshot.assert_match(
            resource.views['edit'].render(
                feretui, session, {'form': form},
            ),
            'snapshot.html',
        )

    def test_save_empty(self, snapshot) -> None:
        local.feretui = feretui = FeretUI()
        resource = MyResource.build()
        session = Session()
        local.request = request = Request(
            session=session,
            form=MultiDict(),
            headers={'Hx-Current-Url': '/?pk=foo'},
        )
        snapshot.assert_match(
            resource.views['edit'].save(feretui, request).body,
            'snapshot.html',
        )

    def test_save(self, snapshot) -> None:
        class MyResource2(MyResource):
            class MetaViewUpdate:
                after_update_redirect_to = 'edit'

        local.feretui = feretui = FeretUI()
        resource = MyResource2.build()
        session = Session()
        local.request = request = Request(
            session=session,
            form=MultiDict(pk=1, foo='bar', test='test1'),
            headers={'Hx-Current-Url': '/?'},
        )
        snapshot.assert_match(
            resource.views['edit'].save(feretui, request).body,
            'snapshot.html',
        )

    def test_save_error(self, snapshot) -> None:
        class MyResource2(MyResource):

            def update(self, *a) -> NoReturn:
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
            resource.views['edit'].save(feretui, request).body,
            'snapshot.html',
        )
