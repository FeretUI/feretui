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
from multidict import MultiDict
from wtforms import SelectField, StringField

from feretui.exceptions import ViewActionError
from feretui.feretui import FeretUI
from feretui.request import Request
from feretui.resources import Resource, RResource
from feretui.resources.actions import Action, Actionset
from feretui.session import Session
from feretui.thread import local


class TestReadView:

    def test_render(self, snapshot) -> None:

        class MyResource(RResource, Resource):
            code = 'foo'
            label = 'Foo'

            class Form:
                pk = StringField()

            class MetaViewTest:
                pass

            class MetaViewRead:
                create_button_redirect_to = 'other'
                delete_button_redirect_to = 'other'
                edit_button_redirect_to = 'other'
                return_button_redirect_to = 'other'

                class Form:
                    foo = StringField()
                    test = SelectField(choices=[('test1', 'Test 1')])

                actions = [
                    Actionset('Print', [
                        Action('Print 1', 'print_1'),
                    ]),
                ]

            def read(self, form_cls, pk):
                return form_cls(MultiDict(pk=pk))

        resource = MyResource.build()
        local.feretui = feretui = FeretUI()
        session = Session()
        local.request = Request(session=session)

        snapshot.assert_match(
            resource.views['read'].render(feretui, session, {'pk': ['foo']}),
            'snapshot.html',
        )

    def test_get_call_kwargs_1(self) -> None:

        class MyResource(RResource, Resource):
            code = 'foo'
            label = 'Foo'

            class Form:
                pk = StringField()

        resource = MyResource.build()
        session = Session()
        local.request = request = Request(
            session=session,
            headers={'Hx-Current-Url': '/?pk=foo'},
        )
        assert resource.views['read'].get_call_kwargs(
            request,
        ) == {'pks': ['foo']}

    def test_get_call_kwargs_2(self) -> None:

        class MyResource(RResource, Resource):
            code = 'foo'
            label = 'Foo'

            class Form:
                pk = StringField()

        resource = MyResource.build()
        session = Session()
        local.request = request = Request(
            session=session,
            headers={'Hx-Current-Url': '/'},
        )
        with pytest.raises(ViewActionError):
            resource.views['read'].get_call_kwargs(request)
