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
from wtforms import SelectField, StringField

from feretui.request import Request
from feretui.resources import UResource, Resource
from feretui.context import cvar_request


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

    def test_render_1(self, snapshot, feretui, session, frequest) -> None:
        resource = MyResource.build()
        snapshot.assert_match(
            resource.views['edit'].render(
                feretui, session, {'pk': ['foo'], 'error': 'With error'},
            ),
            'snapshot.html',
        )

    def test_render_2(self, snapshot, feretui, session, frequest) -> None:
        resource = MyResource.build()
        resource.views['edit'].cancel_button_redirect_to = 'other'
        form = resource.views['edit'].form_cls(pk=1)
        form.validate()
        snapshot.assert_match(
            resource.views['edit'].render(
                feretui, session, {'form': form},
            ),
            'snapshot.html',
        )

    def test_save_empty(self, snapshot, feretui, session) -> None:
        resource = MyResource.build()
        request = Request(
            session=session,
            form=MultiDict(),
            headers={'Hx-Current-Url': '/?pk=foo'},
        )
        cvar_request.set(request)

        snapshot.assert_match(
            resource.views['edit'].save(feretui, request).body,
            'snapshot.html',
        )

    def test_save(self, snapshot, feretui, session) -> None:
        class MyResource2(MyResource):
            class MetaViewUpdate:
                after_update_redirect_to = 'edit'

        resource = MyResource2.build()
        request = Request(
            session=session,
            form=MultiDict(pk=1, foo='bar', test='test1'),
            headers={'Hx-Current-Url': '/?'},
        )
        cvar_request.set(request)
        snapshot.assert_match(
            resource.views['edit'].save(feretui, request).body,
            'snapshot.html',
        )

    def test_save_error(self, snapshot, feretui, session) -> None:
        class MyResource2(MyResource):

            def update(self, *a) -> NoReturn:
                raise Exception

        resource = MyResource2.build()
        request = Request(
            session=session,
            form=MultiDict(pk=1, foo='bar', test='test1'),
            headers={'Hx-Current-Url': '/?'},
        )
        cvar_request.set(request)
        snapshot.assert_match(
            resource.views['edit'].save(feretui, request).body,
            'snapshot.html',
        )
