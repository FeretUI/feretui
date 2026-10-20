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
from polib import POFile
from wtforms import StringField

from feretui.exceptions import ViewActionError, ViewError
from feretui.form import FeretUIForm, onchange
from feretui.request import Request
from feretui.resources.actions import (
    Actionset,
    GotoViewAction,
    SelectedRowsAction,
)
from feretui.resources.common import (
    ActionsMixinForView,
    MultiView,
    TemplateMixinForView,
)
from feretui.resources.resource import Resource
from feretui.resources.view import View


class MyViewWithAction(ActionsMixinForView, View):

    class Form:
        pk = StringField()

    actions = [
        Actionset(
            'Test',
            [
                SelectedRowsAction('foo', 'foo', description='Bar'),
                GotoViewAction('Bar', 'bar'),
            ],
            description='Other',
        ),
    ]


class MultiResource(Resource):

    def filtered_reads(self, form_cls, filters, offset, limit):
        return {'total': 0, 'forms': []}


class TestMultiView:

    def test_init_1(self) -> None:

        class MyView(MultiView, View):
            create_button_redirect_to = 'other'
            delete_button_redirect_to = 'other'
            do_click_on_entry_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = MultiResource()
        resource.context = 'test'
        with pytest.raises(ViewError):
            MyView(resource)

    def test_init_2(self) -> None:

        class MyView(MultiView, View):
            limit = 15
            delete_button_redirect_to = 'other'
            do_click_on_entry_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = MultiResource()
        resource.context = 'test'
        with pytest.raises(ViewError):
            MyView(resource)

    def test_init_3(self) -> None:

        class MyView(MultiView, View):
            limit = 15
            create_button_redirect_to = 'other'
            delete_button_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = MultiResource()
        resource.context = 'test'
        with pytest.raises(ViewError):
            MyView(resource)

    def test_init_4(self) -> None:

        class MyView(MultiView, View):
            limit = 15
            do_click_on_entry_redirect_to = 'other'
            create_button_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = MultiResource()
        resource.context = 'test'
        with pytest.raises(ViewError):
            MyView(resource)

    def test_init_5(self) -> None:

        class MyView(MultiView, View):
            limit = 15
            create_button_redirect_to = 'other'
            delete_button_redirect_to = 'other'
            do_click_on_entry_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = Resource()
        resource.context = 'test'
        with pytest.raises(ViewError):
            MyView(resource)

    def test_get_header_buttons(self, snapshot, feretui, session) -> None:

        class MyView(MultiView, View):
            limit = 15
            create_button_redirect_to = 'other'
            delete_button_redirect_to = 'other'
            do_click_on_entry_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = MultiResource()
        resource.context = 'test'
        view = MyView(resource)
        snapshot.assert_match(
            view.get_header_buttons(feretui, session, {})[0],
            'snapshot.html',
        )

    def test_render_kwargs(self, feretui, session, frequest) -> None:

        class MyView(MultiView, View):
            limit = 15
            create_button_redirect_to = 'other'
            delete_button_redirect_to = 'other'
            do_click_on_entry_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = MultiResource()
        resource.context = 'test'
        view = MyView(resource)

        assert view.render_kwargs(feretui, session, {'offset': [0]})

    def test_call_pagination(self, feretui, session) -> None:
        request = Request(
            method=Request.GET,
            querystring='offset=0',
            session=session,
            headers={'Hx-Current-Url': '/test?resource=test'},
        )

        class MyView(MultiView, View):
            limit = 15
            create_button_redirect_to = 'other'
            delete_button_redirect_to = 'other'
            do_click_on_entry_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = MultiResource()
        resource.context = 'test'
        view = MyView(resource)
        assert view.pagination(feretui, request).body is not None

    def test_call_filters_post(self, feretui, session) -> None:
        request = Request(
            method=Request.POST,
            params={'foo': ['Bar'], 'action': ['filters']},
            session=session,
            headers={'Hx-Current-Url': '/test?resource=test'},
        )

        class MyView(MultiView, View):
            limit = 15
            create_button_redirect_to = 'other'
            delete_button_redirect_to = 'other'
            do_click_on_entry_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = MultiResource()
        resource.context = 'test'
        view = MyView(resource)
        res = view.filters(feretui, request)
        assert res.body is not None
        assert (
            res.headers['HX-Push-Url']
            == '/test?resource=test&offset=0&filter%5Bfoo%5D=Bar'
        )

    def test_call_filters_delete(self, feretui, session) -> None:
        request = Request(
            method=Request.DELETE,
            params={'foo': ['Bar']},
            session=session,
            headers={
                'Hx-Current-Url': '/test?resource=test&filter%5Bfoo%5D=Bar',
            },
        )

        class MyView(MultiView, View):
            limit = 15
            create_button_redirect_to = 'other'
            delete_button_redirect_to = 'other'
            do_click_on_entry_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = MultiResource()
        resource.context = 'test'
        view = MyView(resource)
        res = view.filters(feretui, request)
        assert res.body is not None
        assert res.headers['HX-Push-Url'] == '/test?resource=test&offset=0'

    def test_call_filters_multidict_and_brackets(
        self, feretui, session,
    ) -> None:
        md = MultiDict([
            ('action', 'filters'),
            ('filter[theme]', 'minthy'),
            ('lang', 'fr'),
        ])
        request = Request(
            method=Request.POST,
            params=md,
            session=session,
            headers={'Hx-Current-Url': '/test?resource=test'},
        )

        class MyView(MultiView, View):
            limit = 15
            create_button_redirect_to = 'other'
            delete_button_redirect_to = 'other'
            do_click_on_entry_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = MultiResource()
        resource.context = 'test'
        view = MyView(resource)
        res = view.filters(feretui, request)
        assert res.body is not None
        assert 'filter%5Btheme%5D=minthy' in res.headers['HX-Push-Url']
        assert 'filter%5Blang%5D=fr' in res.headers['HX-Push-Url']

        # Now delete using MultiDict
        del_md = MultiDict([
            ('filter[theme]', 'minthy'),
        ])
        del_request = Request(
            method=Request.DELETE,
            params=del_md,
            session=session,
            headers={'Hx-Current-Url': res.headers['HX-Push-Url']},
        )
        del_res = view.filters(feretui, del_request)
        assert 'filter%5Btheme%5D' not in del_res.headers['HX-Push-Url']
        assert 'filter%5Blang%5D=fr' in del_res.headers['HX-Push-Url']

    def test_call_filters_query_fallback_and_scalar(
        self, feretui, session,
    ) -> None:
        request = Request(
            method=Request.DELETE,
            params={'theme': 'minthy'},
            querystring='action=filters&theme=minthy',
            session=session,
            headers={
                'Hx-Current-Url': '/test?resource=test&filter%5Btheme%5D=minthy',
            },
        )

        class MyView(MultiView, View):
            limit = 15
            create_button_redirect_to = 'other'
            delete_button_redirect_to = 'other'
            do_click_on_entry_redirect_to = 'other'

            class Form:
                pk = StringField()

        resource = MultiResource()
        resource.context = 'test'
        view = MyView(resource)
        res = view.filters(feretui, request)
        assert res.headers['HX-Push-Url'] == '/test?resource=test&offset=0'

        # When params is None, fallback to request.query
        request_query = Request(
            method=Request.DELETE,
            querystring='action=filters&theme=minthy',
            session=session,
            headers={
                'Hx-Current-Url': '/test?resource=test&filter%5Btheme%5D=minthy',
            },
        )
        res2 = view.filters(feretui, request_query)
        assert res2.headers['HX-Push-Url'] == '/test?resource=test&offset=0'

    def test_goto_delete(self, feretui, session) -> None:
        request = Request(
            method=Request.POST,
            session=session,
            headers={'Hx-Current-Url': '/test?resource=test'},
        )

        class MyView(MultiView, View):
            limit = 15
            create_button_redirect_to = 'other'
            delete_button_redirect_to = 'other'
            do_click_on_entry_redirect_to = 'other'

            class Form:
                pk = StringField()

            def get_call_kwargs(self, request):
                return {'pks': ['foo', 'bar']}

        resource = MultiResource()
        resource.context = 'test'
        view = MyView(resource)
        resource.views['other'] = view
        res = view.goto_delete(feretui, request)
        assert res.body is not None
        assert (
            res.headers['HX-Push-Url']
            == '/test?resource=test&view=other&pk=foo&pk=bar'
        )

    def test_export_catalog(self, feretui, frequest) -> None:

        class MyView(MultiView, View):
            limit = 15
            create_button_redirect_to = 'other'
            delete_button_redirect_to = 'other'
            do_click_on_entry_redirect_to = 'other'

            class Form:
                pk = StringField()

            class Filter:
                other = StringField()

        po = POFile()
        resource = MultiResource()
        resource.context = 'test'
        view = MyView(resource)
        view.export_catalog(feretui.translation, po)
        assert len(po) == 3


class TestCommonActionsMixinForView:

    def test_get_actions(self, snapshot, feretui, session) -> None:
        resource = Resource()
        resource.context = 'test'
        view = MyViewWithAction(resource)
        snapshot.assert_match(
            view.get_actions(feretui, session, {})[0],
            'snapshot.html',
        )

    def test_get_call_kwargs(self, snapshot) -> None:
        resource = Resource()
        resource.context = 'test'
        view = MyViewWithAction(resource)
        assert view.get_call_kwargs({}) == {}

    def test_export_catalog(self, feretui, frequest) -> None:
        po = POFile()
        resource = Resource()
        resource.context = 'test'
        view = MyViewWithAction(resource)
        view.export_catalog(feretui.translation, po)
        assert len(po) == 6

    def test_call_1(self, feretui, session) -> None:
        request = Request(method=Request.GET, session=session)
        resource = Resource()
        resource.context = 'test'
        view = MyViewWithAction(resource)
        with pytest.raises(ViewActionError):
            view.call(feretui, request)

    def test_call_2(self, feretui, session) -> None:
        request = Request(
            method=Request.POST,
            params={},
            session=session,
        )
        resource = Resource()
        resource.context = 'test'
        view = MyViewWithAction(resource)
        with pytest.raises(ViewActionError):
            view.call(feretui, request)

    def test_call_3(self, feretui, session) -> None:
        request = Request(
            method=Request.POST,
            params={'method': ['foo']},
            session=session,
        )

        class MyResource(Resource):

            def foo(self, *a, **kw) -> str:
                return 'bar'

        resource = MyResource()
        resource.context = 'test'
        view = MyViewWithAction(resource)
        assert view.call(feretui, request).body == 'bar'

    def test_call_4(self, feretui, session) -> None:
        request = Request(
            method=Request.POST,
            params={'method': ['foo']},
            session=session,
            headers={'Hx-Current-Url': '/test?resource=test'},
        )

        class MyResource(Resource):

            def foo(self, *a, **kw) -> None:
                return None

        resource = MyResource()
        resource.context = 'test'
        view = MyViewWithAction(resource)
        assert view.call(feretui, request).body is not None


class TestTemplateMixinForView:

    def test_render_1(self, snapshot, feretui, session, frequest) -> None:

        class MyResource(Resource):
            code = 'foo'

            class Form:
                pk = StringField()

        class MyView(TemplateMixinForView, View):
            code = 'bar'

        resource = MyResource()
        resource.context = 'test'
        view = MyView(resource)

        snapshot.assert_match(
            view.render(feretui, session, {}),
            'snapshot.html',
        )

    def test_render_2(self, snapshot, feretui, session, frequest) -> None:

        class MyResource(Resource):
            code = 'foo'

            class Form:
                pk = StringField()

        class MyView(TemplateMixinForView, View):
            code = 'bar'
            header_template = "<div>Header</div>"
            body_template = "<div>Body</div>"
            footer_template = "<div>Footer</div>"

        resource = MyResource()
        resource.context = 'test'
        view = MyView(resource)

        snapshot.assert_match(
            view.render(feretui, session, {}),
            'snapshot.html',
        )

    def test_export_catalog_1(self, feretui, frequest) -> None:
        class MyResource(Resource):
            code = 'foo'

            class Form:
                pk = StringField()

        class MyView(TemplateMixinForView, View):
            code = 'bar'

        po = POFile()
        resource = MyResource()
        resource.context = 'test'
        view = MyView(resource)
        view.export_catalog(feretui.translation, po)
        assert len(po) == 1

    def test_export_catalog_2(self, feretui, frequest) -> None:
        class MyResource(Resource):
            code = 'foo'

            class Form:
                pk = StringField()

        class MyView(TemplateMixinForView, View):
            code = 'bar'
            header_template = "<div>Header</div>"
            body_template = "<div>Body</div>"
            footer_template = "<div>Footer</div>"

        po = POFile()
        resource = MyResource()
        resource.context = 'test'
        view = MyView(resource)
        view.export_catalog(feretui.translation, po)
        assert len(po) == 4

    def test_onchange_missing_form_cls_raises(self, feretui, session) -> None:
        class DummyForm(FeretUIForm):
            pk = StringField()

        class DummyView(TemplateMixinForView, View):
            code = "dummy"
            Form = DummyForm

        class DummyResource(Resource):
            code = "dummy_res"

        res = DummyResource()
        res.context = "test"
        view = DummyView(res)
        view.form_cls = None
        request = Request(session=session, method=Request.POST, form=MultiDict())
        with pytest.raises(ViewActionError, match="has no form_cls"):
            view.onchange(feretui, request)

    def test_onchange_executes_handlers(self, feretui, session) -> None:
        class OrderForm(FeretUIForm):
            pk = StringField()
            price = StringField()
            qty = StringField()
            total = StringField()

            @onchange("qty", "price")
            def _calc(self) -> None:
                p = int(self.price.data or 0)
                q = int(self.qty.data or 0)
                self.total.data = str(p * q)

        class OrderView(TemplateMixinForView, View):
            code = "order_view"
            Form = OrderForm

        class OrderResource(Resource):
            code = "order"

        res = OrderResource()
        res.context = "test"
        view = OrderView(res)
        request = Request(
            session=session,
            method=Request.POST,
            querystring="field=qty",
            form=MultiDict([("price", "15"), ("qty", "3"), ("total", "0")]),
        )
        response = view.onchange(feretui, request)
        assert response.status_code == 200
        assert 'id="field-total-wrapper"' in response.body
        assert 'hx-swap-oob="true"' in response.body
        assert 'value="45"' in response.body
        assert '<div id="feretui-onchange-alert" hx-swap-oob="true"></div>' in response.body

    def test_onchange_with_warning_and_params(self, feretui, session) -> None:
        class WarningForm(FeretUIForm):
            pk = StringField()
            discount = StringField()

            @onchange("discount")
            def _check_discount(self) -> None:
                val = int(self.discount.data or 0)
                if val > 50:
                    self.onchange_warning = "High discount applied!"

        class WarningView(TemplateMixinForView, View):
            code = "warn_view"
            Form = WarningForm

        class WarningResource(Resource):
            code = "warn_res"

        res = WarningResource()
        res.context = "test"
        view = WarningView(res)
        # Pass field in params as a list
        request = Request(
            session=session,
            method=Request.POST,
            params={"field": ["discount"]},
            form=MultiDict([("discount", "70")]),
        )
        response = view.onchange(feretui, request)
        assert response.status_code == 200
        assert 'id="feretui-onchange-alert"' in response.body
        assert "High discount applied!" in response.body

        # Pass field in params as single string
        request2 = Request(
            session=session,
            method=Request.POST,
            params={"field": "discount"},
            form=MultiDict([("discount", "10")]),
        )
        response2 = view.onchange(feretui, request2)
        assert '<div id="feretui-onchange-alert" hx-swap-oob="true"></div>' in response2.body

    def test_quick_filters(self, feretui, session) -> None:
        from feretui.resources import QuickFilter
        from feretui.resources.common import MultiView

        class DummyMultiView(MultiView, View):
            code = "multi_test"
            limit = 20
            do_click_on_entry_redirect_to = "read"
            create_button_redirect_to = "create"
            delete_button_redirect_to = "delete"

            class Form:
                pk = StringField()
                status = StringField()

            quick_filters = [
                QuickFilter("In Progress", "status", "in_progress", icon="ti ti-clock"),
                ("Done", "status", "done", "ti ti-check"),
                {"label": "Draft", "field": "status", "value": "draft", "icon": "ti ti-pencil"},
            ]

        class DummyResource(Resource):
            code = "dummy"

            def filtered_reads(self, form_cls, filters, offset, limit):
                return {"forms": [], "total": 0}

        res = DummyResource()
        res.context = "test"
        view = DummyMultiView(res)

        # Test inactive filters
        qf_items = view.get_quick_filters(feretui, session, {})
        assert len(qf_items) == 3
        qf_prog = qf_items[0]
        assert qf_prog["label"] == "In Progress"
        assert qf_prog["is_active"] is False
        assert qf_prog["method"] == "post"
        assert "filter[status]=in_progress" in qf_prog["url"]

        # Test active filter
        qf_items_active = view.get_quick_filters(
            feretui, session, {"filter[status]": ["in_progress"]}
        )
        assert qf_items_active[0]["is_active"] is True
        assert qf_items_active[0]["method"] == "delete"
        assert qf_items_active[1]["is_active"] is False
        assert qf_items_active[1]["method"] == "post"

    def test_render_kwargs_search_and_group_by(self, feretui, session) -> None:
        """Test MultiView.render_kwargs with search and group_by options."""
        class DummyForm(FeretUIForm):
            pk = StringField("PK")
            status = StringField("Status")
            category = StringField("Category")

        f1 = DummyForm(data={"pk": "1", "status": "open", "category": "A"})
        f2 = DummyForm(data={"pk": "2", "status": "closed", "category": "A"})
        f3 = DummyForm(data={"pk": "3", "status": "open", "category": "B"})

        captured_filters = []

        class DummyResource(Resource):
            code = "item"

            def filtered_reads(self, form_cls, filters, offset, limit):
                nonlocal captured_filters
                captured_filters = list(filters)
                return {"forms": [f1, f2, f3], "total": 3}

        class DummyMultiView(MultiView, View):
            code = "multi"
            limit = 20
            do_click_on_entry_redirect_to = "read"
            create_button_redirect_to = "create"
            delete_button_redirect_to = "delete"
            Form = DummyForm
            group_by_fields = [("status", "Status"), ("category", "Category")]

        res = DummyResource()
        res.context = "resource:item"
        view = DummyMultiView(res)

        # 1. Search option
        options_search = {"search": ["test"]}
        kwargs = view.render_kwargs(feretui, session, options_search)
        assert kwargs["search_query"] == "test"
        assert ("search", ["test"]) in captured_filters
        assert kwargs["grouped_forms"] is None

        # 2. Group by option
        options_gb = {"group_by": ["status"]}
        kwargs_gb = view.render_kwargs(feretui, session, options_gb)
        assert kwargs_gb["group_by"] == "status"
        assert kwargs_gb["grouped_forms"] is not None
        assert "open" in kwargs_gb["grouped_forms"]
        assert len(kwargs_gb["grouped_forms"]["open"]) == 2
        assert len(kwargs_gb["grouped_forms"]["closed"]) == 1

        # 3. Render view-multi-header template with search & group_by
        html = feretui.render_template(
            session,
            "view-multi-header",
            label="Items",
            dataset={"total": 3},
            search_query="Widget",
            group_by="status",
            group_by_options=[("status", "Status")],
            quick_filters=[],
            filters=[],
            rcode="item",
            vcode="multi",
        )
        assert 'name="search"' in html
        assert 'value="Widget"' in html
        assert 'name="group_by"' in html
        assert "selected" in html



