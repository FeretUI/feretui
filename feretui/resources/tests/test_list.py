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

from feretui.exceptions import ResourceError
from feretui.request import Request
from feretui.resources.actions import Action, Actionset, SelectedRowsAction
from feretui.resources.list import LResource
from feretui.resources.resource import Resource


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

    def test_view_render(self, snapshot, feretui, session, frequest) -> None:
        session.user = 'Test'
        resource = MyResource.build()
        snapshot.assert_match(
            resource.views['list'].render(
                feretui, session, {'filter[foo]': ['Foo']},
            ),
            'snapshot.html',
        )

    def test_export_catalog_1(self, feretui) -> None:
        po = POFile()
        resource = MyResource.build()
        resource.context = 'test'
        resource.views['list'].export_catalog(feretui.translation, po)
        assert len(po) == 12

    def test_export_catalog_2(self, feretui) -> None:
        po = POFile()
        resource = MyResource2.build()
        resource.context = 'test'
        resource.views['list'].export_catalog(feretui.translation, po)
        assert len(po) == 13

    def test_get_label(self, feretui, session) -> None:
        resource = MyResource2.build()
        resource.context = 'test'
        assert resource.views['list'].get_label(
            feretui, session
        ) == 'other label'

    def test_get_call_kwargs(self, session) -> None:
        resource = MyResource2.build()
        resource.context = 'test'
        view = resource.views['list']
        request = Request(
            session=session,
            params={'selected-rows-resource-foo-view-list': ['foo', 'bar']},
        )
        assert view.get_call_kwargs(request) == {'pks': ['foo', 'bar']}

    def test_export_buttons_disabled(self, feretui, session) -> None:
        resource = MyResource.build()
        view = resource.views['list']
        buttons = view.get_header_buttons(feretui, session, {})
        assert not any('Export' in str(b) for b in buttons)

    def test_export_buttons_enabled(self, feretui, session) -> None:
        class ExportableResource(MyResource):
            class MetaViewList(MyResource.MetaViewList):
                enable_export = True
                export_formats = ['csv', 'xlsx']

        resource = ExportableResource.build()
        view = resource.views['list']
        buttons = view.get_header_buttons(feretui, session, {'filter[foo]': ['val1']})
        assert len(buttons) >= 2
        btn_str = ''.join(str(b) for b in buttons)
        assert 'Export CSV' in btn_str
        assert 'Export XLSX' in btn_str
        assert 'format=csv' in btn_str
        assert 'format=xlsx' in btn_str
        assert 'filter%5Bfoo%5D=val1' in btn_str

    def test_export_disabled_raises(self, feretui, session) -> None:
        resource = MyResource.build()
        view = resource.views['list']
        request = Request(
            session=session,
            method=Request.GET,
            querystring='action=export&format=csv&resource=foo&view=list',
        )
        with pytest.raises(ResourceError, match="Export is disabled for this view"):
            view.export(feretui, request)

    def test_export_unsupported_format_raises(self, feretui, session) -> None:
        class ExportableResource(MyResource):
            class MetaViewList(MyResource.MetaViewList):
                enable_export = True

        resource = ExportableResource.build()
        view = resource.views['list']
        request = Request(
            session=session,
            method=Request.GET,
            querystring='action=export&format=json&resource=foo&view=list',
        )
        with pytest.raises(ResourceError, match="Unsupported export format: json"):
            view.export(feretui, request)

    def test_export_csv_default(self, feretui, session) -> None:
        class ExportableResource(MyResource):
            class MetaViewList(MyResource.MetaViewList):
                enable_export = True

        resource = ExportableResource.build()
        view = resource.views['list']
        request = Request(
            session=session,
            method=Request.GET,
            querystring='action=export&format=csv&resource=foo&view=list',
        )
        response = view.export(feretui, request)
        assert response.headers['Content-Type'] == 'text/csv; charset=utf-8'
        assert 'attachment; filename="foo_list.csv"' in response.headers['Content-Disposition']
        content = response.body.decode('utf-8')
        lines = content.strip().split('\r\n')
        assert 'Foo' in lines[0]
        assert 'Test' in lines[0]
        assert len(lines) == 11  # header + 10 rows

    def test_export_xlsx_default(self, feretui, session) -> None:
        import io
        import openpyxl

        class ExportableResource(MyResource):
            class MetaViewList(MyResource.MetaViewList):
                enable_export = True

        resource = ExportableResource.build()
        view = resource.views['list']
        request = Request(
            session=session,
            method=Request.GET,
            querystring='action=export&format=xlsx&resource=foo&view=list',
        )
        response = view.export(feretui, request)
        assert response.headers['Content-Type'] == (
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        assert 'attachment; filename="foo_list.xlsx"' in response.headers['Content-Disposition']
        wb = openpyxl.load_workbook(io.BytesIO(response.body))
        ws = wb.active
        assert ws.title == 'Export'
        rows = list(ws.iter_rows(values_only=True))
        assert len(rows) == 11
        assert 'Foo' in rows[0]

    def test_export_custom_resource_method(self, feretui, session) -> None:
        class CustomExportResource(MyResource):
            class MetaViewList(MyResource.MetaViewList):
                enable_export = True
                export_formats = ['csv']

            def export_data(self, view, filters=None, request=None):
                return ['ID', 'Name'], [['1', 'Alice'], ['2', 'Bob']]

        resource = CustomExportResource.build()
        view = resource.views['list']
        request = Request(
            session=session,
            method=Request.GET,
            querystring='action=export&format=csv&resource=foo&view=list',
        )
        response = view.export(feretui, request)
        content = response.body.decode('utf-8')
        assert 'ID,Name' in content
        assert '1,Alice' in content
        assert '2,Bob' in content

