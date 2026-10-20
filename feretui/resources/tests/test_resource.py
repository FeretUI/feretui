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

        from feretui.context import cvar_feretui, cvar_request
        from feretui.form import FeretUIForm
        from feretui.request import Request

        cvar_feretui.set(feretui)
        cvar_request.set(Request(session=session))

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

    def test_view_switchers(self, feretui, session) -> None:
        from wtforms import StringField
        from feretui.resources import KResource, LResource

        class SingleViewResource(LResource, Resource):
            code = "single"
            label = "Single View"

            class Form:
                pk = StringField()

            def filtered_reads(self, form_cls, filters, offset, limit):
                return {"forms": [], "total": 0}

        single = SingleViewResource.build()
        # Only 1 collection view -> no switcher
        assert single.get_view_switchers(feretui, session, {"view": "list"}) == []

        class MultiViewResource(KResource, LResource, Resource):
            code = "multi"
            label = "Multi View"

            class Form:
                pk = StringField()
                status = StringField()

            def filtered_reads(self, form_cls, filters, offset, limit):
                return {"forms": [], "total": 0}

        multi = MultiViewResource.build()
        switchers = multi.get_view_switchers(feretui, session, {"view": "list"})
        assert len(switchers) == 2
        view_codes = [s["view"] for s in switchers]
        assert "list" in view_codes
        assert "kanban" in view_codes

        list_sw = next(s for s in switchers if s["view"] == "list")
        kanban_sw = next(s for s in switchers if s["view"] == "kanban")
        assert list_sw["is_active"] is True
        assert kanban_sw["is_active"] is False
        assert "page=resource" in list_sw["url"]
        assert "view=list" in list_sw["url"]
        assert "action/goto" in kanban_sw["goto_url"]

        # View where is_visible returns False is skipped
        orig_is_visible = getattr(multi.views["kanban"], "is_visible", None)
        multi.views["kanban"].is_visible = lambda s: False
        switchers_hidden = multi.get_view_switchers(feretui, session, {"view": "list"})
        assert switchers_hidden == []
        if orig_is_visible:
            multi.views["kanban"].is_visible = orig_is_visible
        else:
            del multi.views["kanban"].is_visible

        # Switch to kanban active
        switchers_k = multi.get_view_switchers(feretui, session, {"view": "kanban"})
        list_sw_k = next(s for s in switchers_k if s["view"] == "list")
        kanban_sw_k = next(s for s in switchers_k if s["view"] == "kanban")
        assert list_sw_k["is_active"] is False
        assert kanban_sw_k["is_active"] is True

    def test_resource_router_errors(self, feretui, session) -> None:
        from wtforms import StringField
        from feretui.exceptions import ResourceError
        from feretui.request import Request
        from feretui.resources import LResource

        class SimpleResource(LResource, Resource):
            code = "simple"
            label = "Simple"

            class Form:
                pk = StringField()

            def filtered_reads(self, form_cls, filters, offset, limit):
                return {"forms": [], "total": 0}

        res = SimpleResource.build()

        # Action is not on resource, and no view defined
        req_no_view = Request(
            session=session,
            method=Request.GET,
            querystring="action=custom_view_action",
            headers={"Hx-Current-Url": "/?page=resource&resource=simple"},
        )
        with pytest.raises(ResourceError, match="No view defined in the query string"):
            res.router(feretui, req_no_view)

        # Action is not on resource, and view does not exist
        req_invalid_view = Request(
            session=session,
            method=Request.GET,
            querystring="action=custom_view_action&view=nonexistent",
            headers={"Hx-Current-Url": "/?page=resource&resource=simple&view=nonexistent"},
        )
        with pytest.raises(ResourceError, match="No view nonexistent defined"):
            res.router(feretui, req_invalid_view)

    def test_update_edit_aliasing_and_save_fallback(self, feretui, session) -> None:
        from wtforms import StringField
        from feretui.request import Request
        from multidict import MultiDict
        from feretui.response import Response
        from feretui.resources import CResource, UResource

        class CrudResource(CResource, UResource, Resource):
            code = "crud"
            label = "CRUD"
            action_security = None
            page_visibility = None

            class Form:
                pk = StringField()
                name = StringField()

            def create(self, form):
                return "1"

            def read(self, form_cls, pk):
                return form_cls()

            def update(self, forms):
                pass

        res = CrudResource.build()
        assert "edit" in res.views
        assert "create" in res.views

        # 1. Resource.render with view='update' aliases to 'edit'
        html_update = res.render(feretui, session, {"view": "update", "pk": "1"})
        assert "crud" in html_update

        # 2. Resource.router with view='update' aliases to 'edit'
        req_update = Request(
            session=session,
            method=Request.POST,
            querystring="action=save&view=update&pk=1",
            headers={"Hx-Current-Url": "/?page=resource&resource=crud&view=update&pk=1"},
        )
        resp = res.router(feretui, req_update)
        assert isinstance(resp, Response)

        # 3. Resource.router fallback without view when action='save' with pk (resolves to edit)
        req_save_pk = Request(
            session=session,
            method=Request.POST,
            querystring="action=save&pk=1",
            form=MultiDict({"pk": "1"}),
            headers={"Hx-Current-Url": "/?page=resource&resource=crud&pk=1"},
        )
        resp_save = res.router(feretui, req_save_pk)
        assert isinstance(resp_save, Response)

        # 4. Resource.router fallback without view when action='save' without pk (resolves to create)
        req_save_new = Request(
            session=session,
            method=Request.POST,
            querystring="action=save",
            form=MultiDict({"name": "New Item"}),
            headers={"Hx-Current-Url": "/?page=resource&resource=crud"},
        )
        resp_new = res.router(feretui, req_save_new)
        assert isinstance(resp_new, Response)

        # 5. Reverse alias: view='edit' when only 'update' exists in views
        class MockUpdateView:
            def render(self, f, s, opt):
                return "<div>Custom Update</div>"
            def custom_action(self, f, r):
                return Response("custom_update")

        res.views["update"] = MockUpdateView()
        del res.views["edit"]

        html_edit = res.render(feretui, session, {"view": "edit"})
        assert "Custom Update" in html_edit

        req_edit = Request(
            session=session,
            method=Request.GET,
            querystring="action=custom_action&view=edit",
        )
        resp_edit = res.router(feretui, req_edit)
        assert resp_edit.body == "custom_update"



