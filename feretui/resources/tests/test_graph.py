# This file is a part of the FeretUI project
#
#    Copyright (C) 2026 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Unit tests for GraphView and GResource."""

import pytest  # noqa: F401
from wtforms import FloatField, SelectField, StringField

from feretui.form import FeretUIForm
from feretui.resources import GCRUD, GResource, Resource
from feretui.resources.graph import DefaultViewGraph, GraphView


class SalesOrderForm(FeretUIForm):
    pk = StringField("PK")
    salesperson = SelectField(
        "Salesperson",
        choices=[("sp1", "Alice"), ("sp2", "Bob")],
    )
    stage = StringField("Stage")
    amount = FloatField("Amount")
    invalid_num = StringField("Invalid")


class GraphTestResource(GResource, Resource):
    code = "sales"
    label = "Sales Analytics"
    Form = SalesOrderForm

    class MetaViewGraph:
        graph_type = "bar"
        group_by = "salesperson"
        measure = "amount"
        measure_operator = "sum"
        group_by_fields = [("salesperson", "Salesperson"), ("stage", "Stage")]

    def filtered_reads(self, form_cls, filters, offset, limit):
        f1 = form_cls()
        f1.pk.data = "1"
        f1.salesperson.data = "sp1"
        f1.stage.data = "won"
        f1.amount.data = 1500.0

        f2 = form_cls()
        f2.pk.data = "2"
        f2.salesperson.data = "sp2"
        f2.stage.data = "won"
        f2.amount.data = 2500.0

        f3 = form_cls()
        f3.pk.data = "3"
        f3.salesperson.data = "sp1"
        f3.stage.data = "lost"
        f3.amount.data = 500.0

        return {"forms": [f1, f2, f3], "total": 3}


def _get_test_view() -> GraphView:
    res = GraphTestResource.build()
    res.context = "resource:sales"
    return res.views["graph"]


class TestGraphView:
    """Test suite for GraphView."""

    def test_default_view_graph(self) -> None:
        """Test DefaultViewGraph attributes."""
        default = DefaultViewGraph()
        assert default.graph_type == "bar"
        assert default.limit == 1000
        assert default.measure_operator == "sum"

    def test_extract_group_val(self) -> None:
        """Test _extract_group_val helper."""
        view = _get_test_view()
        form = SalesOrderForm()

        # No group_by
        assert view._extract_group_val(form, "") == "All"
        assert view._extract_group_val(form, "non_existent") == "All"

        # Choice field matching
        form.salesperson.data = "sp1"
        assert view._extract_group_val(form, "salesperson") == "Alice"

        # Choice field not matching
        form.salesperson.data = "unknown"
        assert view._extract_group_val(form, "salesperson") == "unknown"

        # Normal field None
        form.stage.data = None
        assert view._extract_group_val(form, "stage") == "Undefined"

        # Normal field with value
        form.stage.data = "draft"
        assert view._extract_group_val(form, "stage") == "draft"

    def test_extract_measure_num(self) -> None:
        """Test _extract_measure_num helper."""
        view = _get_test_view()
        form = SalesOrderForm()

        # No measure or non-existent
        assert view._extract_measure_num(form, "") == 1.0
        assert view._extract_measure_num(form, "non_existent") == 1.0

        # None value
        form.amount.data = None
        assert view._extract_measure_num(form, "amount") == 0.0

        # Valid numeric value
        form.amount.data = 123.45
        assert view._extract_measure_num(form, "amount") == 123.45

        # Invalid numeric value string
        form.invalid_num.data = "not_a_number"
        assert view._extract_measure_num(form, "invalid_num") == 0.0

    def test_aggregate_data_operators(self) -> None:
        """Test aggregate_data with sum, avg, and count."""
        view = _get_test_view()
        f1 = SalesOrderForm()
        f1.stage.data = "won"
        f1.amount.data = 100.0

        f2 = SalesOrderForm()
        f2.stage.data = "won"
        f2.amount.data = 200.0

        f3 = SalesOrderForm()
        f3.stage.data = "lost"
        f3.amount.data = 50.0

        forms = [f1, f2, f3]

        # 1. Sum
        data_sum = view.aggregate_data(forms, "stage", "amount", "sum")
        by_label = {d["label"]: d for d in data_sum}
        assert by_label["won"]["value"] == 300.0
        assert by_label["won"]["count"] == 2
        assert by_label["lost"]["value"] == 50.0

        # 2. Avg
        data_avg = view.aggregate_data(forms, "stage", "amount", "avg")
        by_label_avg = {d["label"]: d for d in data_avg}
        assert by_label_avg["won"]["value"] == 150.0
        assert by_label_avg["lost"]["value"] == 50.0

        # 3. Count
        data_count = view.aggregate_data(forms, "stage", "amount", "count")
        by_label_cnt = {d["label"]: d for d in data_count}
        assert by_label_cnt["won"]["value"] == 2.0
        assert by_label_cnt["lost"]["value"] == 1.0

        # 4. Count without measure
        data_no_measure = view.aggregate_data(forms, "stage", "", "sum")
        by_label_nm = {d["label"]: d for d in data_no_measure}
        assert by_label_nm["won"]["value"] == 2.0

    def test_generate_chart_svg_empty(self) -> None:
        """Test generate_chart_svg when data is empty."""
        view = _get_test_view()
        svg = view.generate_chart_svg([], "bar")
        assert "No data available for chart" in svg

    def test_generate_bar_chart_svg(self) -> None:
        """Test bar chart SVG generation."""
        view = _get_test_view()
        data = [
            {"label": "Group A", "value": 100.0, "count": 2},
            {"label": "Group B", "value": 250.0, "count": 5},
        ]
        svg = view.generate_chart_svg(data, "bar")
        assert "<rect" in svg
        assert "Group A" in svg
        assert "Group B" in svg

        # Zero max_val fallback
        data_zero = [{"label": "Z", "value": 0.0, "count": 1}]
        svg_zero = view.generate_chart_svg(data_zero, "bar")
        assert "<rect" in svg_zero

    def test_generate_line_chart_svg(self) -> None:
        """Test line chart SVG generation."""
        view = _get_test_view()
        data = [
            {"label": "Jan", "value": 10.0, "count": 1},
            {"label": "Feb", "value": 25.0, "count": 2},
            {"label": "Mar", "value": 15.0, "count": 1},
        ]
        svg = view.generate_chart_svg(data, "line")
        assert "<polyline" in svg
        assert "<circle" in svg

        # Single point / zero max_val
        data_single = [{"label": "Solo", "value": 0.0, "count": 1}]
        svg_single = view.generate_chart_svg(data_single, "line")
        assert "<polyline" in svg_single

    def test_generate_pie_chart_svg(self) -> None:
        """Test pie chart SVG generation."""
        view = _get_test_view()

        # 1. Total zero
        data_zero = [{"label": "None", "value": 0.0, "count": 1}]
        svg_zero = view.generate_chart_svg(data_zero, "pie")
        assert "<circle" in svg_zero

        # 2. Single item (100%)
        data_one = [{"label": "Single", "value": 50.0, "count": 1}]
        svg_one = view.generate_chart_svg(data_one, "pie")
        assert "<circle" in svg_one
        assert "100.0%" in svg_one

        # 3. Multiple items including large slice (> 50%)
        data_multi = [
            {"label": "Dominant", "value": 75.0, "count": 3},
            {"label": "Minor", "value": 25.0, "count": 1},
        ]
        svg_multi = view.generate_chart_svg(data_multi, "pie")
        assert "<path" in svg_multi
        assert "Dominant" in svg_multi
        assert "75.0%" in svg_multi

    def test_render_graph_view(self, feretui, session, frequest) -> None:  # noqa: ARG002
        """Test full render of GraphView."""
        resource = GraphTestResource.build()
        resource.context = "sales"
        view = resource.views["graph"]

        # Default render
        html = view.render(feretui, session, {})
        assert "feretui-graph-view" in html
        assert "<svg" in html
        assert "feretui-pivot-table" in html
        assert "Alice" in html
        assert "Bob" in html

        # With query options (line, avg)
        html_line = view.render(
            feretui,
            session,
            {
                "graph_type": "line",
                "measure": "amount",
                "operator": "avg",
                "group_by": "stage",
            },
        )
        assert "<polyline" in html_line
        assert "Measure:" in html_line
        assert "amount" in html_line
        assert "(avg)" in html_line

    def test_gresource_build_view(self) -> None:
        """Test GResource.build_view and default_view."""
        class CustomGResource(GResource, Resource):
            code = "custom"
            label = "Custom"
            default_view = None
            Form = SalesOrderForm

            class MetaViewGraph:
                pass

            def filtered_reads(self, form_cls, filters, offset, limit):
                return {"forms": [], "total": 0}

        res = CustomGResource.build()
        assert res.default_view == "graph"
        assert "graph" in res.views

    def test_gcrud_composite(self) -> None:
        """Test GCRUDResource composite inheritance."""
        class MyGCRUD(GCRUD, Resource):
            code = "metrics"
            label = "Metrics"
            Form = SalesOrderForm

            def filtered_reads(self, form_cls, filters, offset, limit):
                return {"forms": [], "total": 0}

        res = MyGCRUD.build()
        assert res.default_view == "graph"
        assert "graph" in res.views
        assert "create" in res.views
        assert "read" in res.views
        assert "edit" in res.views
        assert "delete" in res.views
