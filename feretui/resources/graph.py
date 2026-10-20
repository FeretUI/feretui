# This file is a part of the FeretUI project
#
#    Copyright (C) 2024-2026 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Module feretui.resources.graph.

The Graph resource displays data visually using SVG charts (bar, line, pie)
and a summary pivot table for reporting and business intelligence.

* :class:`.GraphView`
* :class:`.GResource`
"""

import math
from typing import TYPE_CHECKING

from markupsafe import Markup

from feretui.form import FeretUIForm
from feretui.resources.common import LabelMixinForView, MultiView
from feretui.resources.view import View
from feretui.session import Session

from .resource import Resource

if TYPE_CHECKING:
    from feretui.feretui import FeretUI

PALETTE = [
    "#3b82f6",
    "#10b981",
    "#f59e0b",
    "#ef4444",
    "#8b5cf6",
    "#ec4899",
    "#06b6d4",
    "#84cc16",
    "#f97316",
    "#6366f1",
]


class DefaultViewGraph:
    """Default values for graph view."""

    label: str | None = None
    limit: int = 1000
    create_button_redirect_to: str | None = None
    delete_button_redirect_to: str | None = None
    do_click_on_entry_redirect_to: str | None = None
    graph_type: str = "bar"
    group_by: str = ""
    measure: str = ""
    measure_operator: str = "sum"
    group_by_fields: list[tuple[str, str]] = []
    quick_filters: list = []


class GraphView(MultiView, LabelMixinForView, View):
    """Graph view for business reporting, analytics, and metrics."""

    code: str = "graph"
    limit: int = 1000
    create_button_redirect_to: str | None = None
    delete_button_redirect_to: str | None = None
    do_click_on_entry_redirect_to: str | None = None
    graph_type: str = "bar"
    group_by_field: str = ""
    measure_field: str = ""
    measure_operator: str = "sum"

    def _extract_group_val(
        self: "GraphView", form: FeretUIForm, group_by: str
    ) -> str:
        """Extract a readable string group label from form."""
        if not group_by or not hasattr(form, group_by):
            return "All"
        field = getattr(form, group_by)
        val = field.data
        if hasattr(field, "choices") and field.choices:
            for c_val, c_lbl in field.choices:
                if str(c_val) == str(val):
                    return str(c_lbl)
        return str(val) if val is not None else "Undefined"

    def _extract_measure_num(
        self: "GraphView", form: FeretUIForm, measure: str
    ) -> float:
        """Extract a float measure value from form."""
        if not measure or not hasattr(form, measure):
            return 1.0
        val = getattr(form, measure).data
        if val is None:
            return 0.0
        try:
            return float(val)
        except (ValueError, TypeError):
            return 0.0

    def aggregate_data(
        self: "GraphView",
        forms: list[FeretUIForm],
        group_by: str,
        measure: str,
        operator: str,
    ) -> list[dict[str, object]]:
        """Group and aggregate forms into structured metrics."""
        groups: dict[str, list[float]] = {}
        for form in forms:
            g_lbl = self._extract_group_val(form, group_by)
            val = self._extract_measure_num(form, measure)
            groups.setdefault(g_lbl, []).append(val)

        results: list[dict[str, object]] = []
        for g_lbl, vals in groups.items():
            count = len(vals)
            if operator == "count" or not measure:
                agg = float(count)
            elif operator == "avg":
                agg = sum(vals) / count if count else 0.0
            else:
                agg = sum(vals)

            results.append(
                {
                    "label": g_lbl,
                    "value": round(agg, 2),
                    "count": count,
                }
            )

        return results

    def _build_bar_svg(
        self: "GraphView",
        data: list[dict[str, object]],
        width: int,
        height: int,
    ) -> str:
        """Generate SVG for bar chart."""
        max_val = max([float(d["value"]) for d in data], default=1.0)
        if max_val <= 0:
            max_val = 1.0

        n = len(data)
        bar_w = max(24, int((width - 120) / max(n, 1)) - 16)
        svg_parts = [
            f'<svg viewBox="0 0 {width} {height}" class="feretui-chart-svg" '
            'style="width: 100%; max-height: 400px;">',
            f'<line x1="60" y1="{height - 50}" x2="{width - 20}" '
            f'y2="{height - 50}" stroke="currentColor" stroke-opacity="0.3" />',
        ]

        for i, d in enumerate(data):
            val = float(d["value"])
            color = PALETTE[i % len(PALETTE)]
            b_h = max(4, int((val / max_val) * (height - 100)))
            x = 70 + i * (bar_w + 16)
            y = height - 50 - b_h
            lbl = str(d["label"])
            svg_parts.append(
                f'<rect x="{x}" y="{y}" width="{bar_w}" height="{b_h}" '
                f'rx="4" fill="{color}"><title>{lbl}: {val}</title></rect>'
            )
            svg_parts.append(
                f'<text x="{x + bar_w / 2}" y="{y - 8}" text-anchor="middle" '
                f'font-size="11" font-weight="600" fill="currentColor">'
                f"{val:g}</text>"
            )
            svg_parts.append(
                f'<text x="{x + bar_w / 2}" y="{height - 30}" '
                f'text-anchor="middle" font-size="11" fill="currentColor" '
                f'opacity="0.8">{lbl[:10]}</text>'
            )

        svg_parts.append("</svg>")
        return "".join(svg_parts)

    def _build_line_svg(
        self: "GraphView",
        data: list[dict[str, object]],
        width: int,
        height: int,
    ) -> str:
        """Generate SVG for line chart."""
        max_val = max([float(d["value"]) for d in data], default=1.0)
        if max_val <= 0:
            max_val = 1.0

        pts: list[tuple[float, float, str, float]] = []
        n = len(data)
        step = (width - 140) / max(n - 1, 1)

        for i, d in enumerate(data):
            val = float(d["value"])
            x = 70 + i * step
            y = height - 50 - ((val / max_val) * (height - 100))
            pts.append((x, y, str(d["label"]), val))

        poly_pts = " ".join([f"{x},{y}" for x, y, _, _ in pts])
        svg_parts = [
            f'<svg viewBox="0 0 {width} {height}" class="feretui-chart-svg" '
            'style="width: 100%; max-height: 400px;">',
            f'<line x1="60" y1="{height - 50}" x2="{width - 20}" '
            f'y2="{height - 50}" stroke="currentColor" stroke-opacity="0.3" />',
            f'<polyline fill="none" stroke="{PALETTE[0]}" stroke-width="3" '
            f'points="{poly_pts}" />',
        ]

        for x, y, lbl, val in pts:
            svg_parts.append(
                f'<circle cx="{x}" cy="{y}" r="5" fill="{PALETTE[0]}">'
                f"<title>{lbl}: {val}</title></circle>"
            )
            svg_parts.append(
                f'<text x="{x}" y="{y - 10}" text-anchor="middle" '
                f'font-size="11" font-weight="600" fill="currentColor">'
                f"{val:g}</text>"
            )
            svg_parts.append(
                f'<text x="{x}" y="{height - 30}" text-anchor="middle" '
                f'font-size="11" fill="currentColor" opacity="0.8">'
                f"{lbl[:10]}</text>"
            )

        svg_parts.append("</svg>")
        return "".join(svg_parts)

    def _build_pie_slice(
        self: "GraphView",
        cx: float,
        cy: float,
        r: float,
        start_angle: float,
        angle: float,
        color: str,
        lbl: str,
        val: float,
    ) -> str:
        """Render a single pie/donut slice path."""
        end_angle = start_angle + angle
        x1 = cx + r * math.cos(start_angle)
        y1 = cy + r * math.sin(start_angle)
        x2 = cx + r * math.cos(end_angle)
        y2 = cy + r * math.sin(end_angle)
        large = 1 if angle > math.pi else 0
        path_d = (
            f"M {cx},{cy} L {x1:.2f},{y1:.2f} "
            f"A {r},{r} 0 {large},1 {x2:.2f},{y2:.2f} Z"
        )
        return (
            f'<path d="{path_d}" fill="{color}">'
            f"<title>{lbl}: {val}</title></path>"
        )

    def _build_pie_svg(
        self: "GraphView",
        data: list[dict[str, object]],
        width: int,
        height: int,
    ) -> str:
        """Generate SVG for pie chart."""
        total = sum([float(d["value"]) for d in data])
        cx, cy, r = width / 3, height / 2, min(width / 3, height / 2) - 30

        if total <= 0 or not data:
            return (
                f'<svg viewBox="0 0 {width} {height}" '
                'class="feretui-chart-svg">'
                f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#e5e7eb" />'
                "</svg>"
            )

        svg_parts = [
            f'<svg viewBox="0 0 {width} {height}" class="feretui-chart-svg" '
            'style="width: 100%; max-height: 400px;">'
        ]

        if len(data) == 1:
            val = float(data[0]["value"])
            svg_parts.append(
                f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{PALETTE[0]}">'
                f'<title>{data[0]["label"]}: {val}</title></circle>'
            )
        else:
            curr_angle = -math.pi / 2
            for i, d in enumerate(data):
                val = float(d["value"])
                angle = (val / total) * 2 * math.pi
                color = PALETTE[i % len(PALETTE)]
                svg_parts.append(
                    self._build_pie_slice(
                        cx,
                        cy,
                        r,
                        curr_angle,
                        angle,
                        color,
                        str(d["label"]),
                        val,
                    )
                )
                curr_angle += angle

        leg_x = width * 0.65
        for i, d in enumerate(data):
            color = PALETTE[i % len(PALETTE)]
            ly = 40 + i * 24
            pct = (float(d["value"]) / total * 100) if total else 0
            svg_parts.append(
                f'<rect x="{leg_x}" y="{ly}" width="14" height="14" rx="3" '
                f'fill="{color}" />'
                f'<text x="{leg_x + 22}" y="{ly + 11}" font-size="12" '
                f'fill="currentColor">{d["label"]} ({pct:.1f}%)</text>'
            )

        svg_parts.append("</svg>")
        return "".join(svg_parts)

    def generate_chart_svg(
        self: "GraphView",
        data: list[dict[str, object]],
        graph_type: str,
        width: int = 680,
        height: int = 320,
    ) -> str:
        """Generate SVG for the requested chart type."""
        if not data:
            return (
                f'<svg viewBox="0 0 {width} {height}" '
                'class="feretui-chart-svg">'
                f'<text x="{width / 2}" y="{height / 2}" text-anchor="middle" '
                'fill="currentColor" opacity="0.6">'
                "No data available for chart</text>"
                "</svg>"
            )

        if graph_type == "pie":
            return self._build_pie_svg(data, width, height)
        if graph_type == "line":
            return self._build_line_svg(data, width, height)
        return self._build_bar_svg(data, width, height)

    def render(
        self: "GraphView",
        feretui: "FeretUI",
        session: Session,
        options: dict,
    ) -> str:
        """Render the graph reporting view."""
        kwargs = self.render_kwargs(feretui, session, options)
        dataset = kwargs.get("dataset", {})
        forms = dataset.get("forms", [])

        g_type = options.get("graph_type", [self.graph_type])
        active_type = g_type[0] if isinstance(g_type, list) else g_type

        gb_field = kwargs.get("group_by") or self.group_by_field
        ms_field = options.get("measure", [self.measure_field])
        active_measure = ms_field[0] if isinstance(ms_field, list) else ms_field

        op = options.get("operator", [self.measure_operator])
        active_op = op[0] if isinstance(op, list) else op

        chart_data = self.aggregate_data(
            forms, gb_field, active_measure, active_op
        )
        chart_svg = self.generate_chart_svg(chart_data, active_type)

        total_val = sum([float(d["value"]) for d in chart_data])
        total_count = sum([int(d["count"]) for d in chart_data])

        return Markup(
            feretui.render_template(
                session,
                "feretui-resource-graph",
                chart_data=chart_data,
                chart_svg=chart_svg,
                active_graph_type=active_type,
                active_measure=active_measure,
                active_operator=active_op,
                total_val=round(total_val, 2),
                total_count=total_count,
                **kwargs,
            )
        )


class GResource:
    """GResource mixin class for Graph / Analytics views."""

    default_view: str = "graph"
    MetaViewGraph = DefaultViewGraph

    def build_view(
        self: "GResource",
        view_cls_name: str,
    ) -> Resource:
        """Return view instance for MetaViewGraph."""
        if view_cls_name.startswith("MetaViewGraph"):
            meta_view_cls = self.get_meta_view_class(view_cls_name)
            meta_view_cls.append(GraphView)
            view_cls = type(
                "GraphView",
                tuple(meta_view_cls),
                {},
            )
            if not self.default_view:
                self.default_view = view_cls.code

            return view_cls(self)

        return super().build_view(view_cls_name)
