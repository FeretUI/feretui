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

from feretui.exceptions import ResourceError
from feretui.resources.resource import Resource


class TestResource:

    def test_without_code(self) -> None:

        class MyResource(Resource):
            label = 'Test'

        with pytest.raises(ResourceError):
            MyResource.build()

    def test_without_label(self) -> None:

        class MyResource(Resource):
            code = 'test'

        with pytest.raises(ResourceError):
            MyResource.build()

    def test_crud_mixins(self) -> None:
        from feretui.resources import (
            CalCRUD,
            CalCRUDResource,
            GCRUD,
            GCRUDResource,
            KCRUD,
            KCRUDResource,
            LCRUD,
            LCRUDResource,
            LKCRUD,
            LKCRUDResource,
        )

        assert LCRUD is LCRUDResource
        assert KCRUD is KCRUDResource
        assert LKCRUD is LKCRUDResource
        assert CalCRUD is CalCRUDResource
        assert GCRUD is GCRUDResource

        assert LCRUD.default_view == "list"
        assert KCRUD.default_view == "kanban"
        assert LKCRUD.default_view == "list"
        assert CalCRUD.default_view == "calendar"
        assert GCRUD.default_view == "graph"

        from wtforms import StringField

        class BaseStub:
            def filtered_reads(self, form_cls, filters, offset, limit):
                return {"total": 0, "forms": []}

            def create(self, form):
                pass

            def read(self, pk):
                return None

            def update(self, forms):
                pass

            def delete(self, pks):
                pass

        class MyKResource(KCRUD, BaseStub, Resource):
            code = "test_kcrud"
            label = "Test KCRUD"

            class Form:
                pk = StringField()

        MyKResource.build()
        assert MyKResource.default_view == "kanban"

        class MyLKResource(LKCRUD, BaseStub, Resource):
            code = "test_lkcrud"
            label = "Test LKCRUD"

            class Form:
                pk = StringField()

        MyLKResource.build()
        assert MyLKResource.default_view == "list"

        class MyCalResource(CalCRUD, BaseStub, Resource):
            code = "test_calcrud"
            label = "Test CalCRUD"

            class Form:
                pk = StringField()

        MyCalResource.build()
        assert MyCalResource.default_view == "calendar"

        class MyGResource(GCRUD, BaseStub, Resource):
            code = "test_gcrud"
            label = "Test GCRUD"

            class Form:
                pk = StringField()

        MyGResource.build()
        assert MyGResource.default_view == "graph"

    def test_security_harmonization(self) -> None:
        from feretui.helper import action_for_authenticated_user

        class PublicResource(Resource):
            code = "public_res"
            label = "Public"
            page_visibility = None

        res = PublicResource.build()
        assert res.action_security is None

        class CustomSecResource(Resource):
            code = "custom_sec_res"
            label = "Custom"
            page_visibility = None
            action_security = staticmethod(action_for_authenticated_user)

        res2 = CustomSecResource.build()
        assert res2.action_security is not None

    def test_meta_view_edit_alias(self) -> None:
        from wtforms import StringField

        from feretui.resources import UResource

        class EditStubResource(UResource, Resource):
            code = "edit_stub"
            label = "Edit Stub"

            class Form:
                pk = StringField()

            class MetaViewEdit:
                class Form:
                    name = StringField()

            def update(self, forms):
                pass

            def read(self, form_cls, pk):
                pass

        res = EditStubResource.build()
        assert "edit" in res.views
        assert res.views["edit"].code == "edit"

    def test_xss_protection_in_render(self, feretui, session) -> None:
        from wtforms import StringField

        from feretui.form import FeretUIForm

        class VulnerableForm(FeretUIForm):
            comment = StringField()

        xss_payload = '<script>alert("xss")</script><img src=x onerror=alert(1)>'
        form = VulnerableForm(comment=xss_payload)
        rendered = form.comment()
        # Verify user HTML is escaped, not executed or unescaped
        assert '<script>' not in rendered
        assert '<img src=x onerror=alert(1)>' not in rendered
        assert '&lt;script&gt;' in rendered
        assert '&lt;img src=x onerror=alert(1)&gt;' in rendered
