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
from wtforms import StringField

from feretui.request import Request
from feretui.resources import DResource, LResource, Resource
from feretui.context import cvar_request


class MyResource(DResource, Resource):
    code = 'foo'
    label = 'Foo'

    class Form:
        pk = StringField()

    class MetaViewTest:
        pass

    def delete(self, pks) -> None:
        pass


class TestDeleteView:

    def test_render_1(self, snapshot, feretui, session) -> None:
        resource = MyResource.build()
        request = Request(
            method=Request.GET,
            session=session,
            headers={'Hx-Current-Url': '/?'},
        )
        cvar_request.set(request)

        snapshot.assert_match(
            resource.views['delete'].render(
                feretui,
                session,
                {'pk': ['foo', 'bar'], 'error': 'With error'},
            ),
            'snapshot.html',
        )

    def test_render_2(self, snapshot, feretui, session) -> None:
        resource = MyResource.build()
        request = Request(
            method=Request.GET,
            session=session,
            headers={'Hx-Current-Url': '/?'},
        )
        cvar_request.set(request)

        snapshot.assert_match(
            resource.views['delete'].render(
                feretui, session, {'pk': 'foo'},
            ),
            'snapshot.html',
        )

    def test_delete(self, snapshot, feretui, session) -> None:
        class MyResource2(LResource, MyResource):
            class MetaViewDelete:
                after_delete_redirect_to = 'list'

            def filtered_reads(self, *a, **kw):
                return {
                    'total': 0,
                    'forms': [],
                }

        resource = MyResource2.build()
        request = request = Request(
            method=Request.DELETE,
            session=session,
            headers={'Hx-Current-Url': '/?pk=foo&pk=bar'},
        )
        cvar_request.set(request)
        snapshot.assert_match(
            resource.views['delete'].delete(feretui, request).body,
            'snapshot.html',
        )

    def test_delete_raise(self, snapshot, feretui, session) -> None:
        class MyResource2(LResource, MyResource):
            class MetaViewDelete:
                after_delete_redirect_to = 'list'

            def filtered_reads(self, *a, **kw):
                return {
                    'total': 0,
                    'forms': [],
                }

            def delete(self, *a) -> NoReturn:
                raise Exception

        resource = MyResource2.build()
        request = request = Request(
            method=Request.DELETE,
            session=session,
            headers={'Hx-Current-Url': '/?pk=foo&pk=bar'},
        )
        cvar_request.set(request)
        snapshot.assert_match(
            resource.views['delete'].delete(feretui, request).body,
            'snapshot.html',
        )
