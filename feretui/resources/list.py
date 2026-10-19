# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Module feretui.resources.list.

The List resource represent data under html table.

* :class:`.ListView`
* :class:`.LResource`

::

    myferet.register_resource(
    )
    class MyResource(LResource, Resource):
        code = 'code of the resource',
        label = 'label',

        class MetaViewList:
            pass
"""

import csv
import io
import urllib.parse
from typing import TYPE_CHECKING

from markupsafe import Markup
from wtforms.fields import Field

from feretui.exceptions import ResourceError
from feretui.form import FeretUIForm
from feretui.request import Request
from feretui.resources.common import LabelMixinForView, MultiView
from feretui.resources.view import View, view_action_validator
from feretui.response import Response
from feretui.session import Session

from .resource import Resource

if TYPE_CHECKING:
    from feretui.feretui import FeretUI


def span_widget(field: Field) -> Markup:
    """Render a field in the td node.

    :param field: The field of the form to render.
    :type: Field_
    :return: The html
    :rtype: Markup_
    """
    data = field.data
    if hasattr(field, "choices"):
        for choice in field.choices:
            if choice[0] == data:
                data = choice[1]
                break

    return Markup("<span>{}</span>").format(data)


class DefaultViewList:
    """Default value for the view list."""

    label: str = None
    limit: int = 20
    create_button_redirect_to: str = None
    delete_button_redirect_to: str = None
    do_click_on_entry_redirect_to: str = None
    enable_export: bool = False
    export_formats: list[str] = ["csv", "xlsx"]


class ListView(MultiView, LabelMixinForView, View):
    """List view."""

    code: str = "list"
    WIDGETS: dict[str, Field] = {}
    enable_export: bool = False
    export_formats: list[str] = ["csv", "xlsx"]

    def widget(self: "ListView", field: Field, **kwargs: dict) -> Markup:
        """Render the field for the view list."""
        return self.WIDGETS.get(field.__class__, span_widget)(field, **kwargs)

    def get_call_kwargs(self: "ListView", request: Request) -> dict:
        """Return the kwargs of the call method."""
        res = super().get_call_kwargs(request)
        key = f"selected-rows-resource-{self.resource.code}-view-{self.code}"
        if key in request.params:
            res["pks"] = request.params[key]

        return res

    def get_header_buttons(
        self: "ListView",
        feretui: "FeretUI",
        session: Session,
        options: dict,
    ) -> list[Markup]:
        """Return the buttons for the list view."""
        res = super().get_header_buttons(feretui, session, options)
        if getattr(self, "enable_export", False):
            formats = getattr(self, "export_formats", ["csv", "xlsx"])
            base_url = f"{feretui.base_url}/action/resource"
            filter_qs = {
                k: v
                for k, v in options.items()
                if k.startswith("filter[") and k.endswith("]")
            }
            for fmt in formats:
                params = {
                    "action": "export",
                    "format": fmt,
                    "resource": self.resource.code,
                    "view": self.code,
                }
                params.update(filter_qs)
                export_url = (
                    f"{base_url}?{urllib.parse.urlencode(params, doseq=True)}"
                )
                res.append(
                    Markup(
                        feretui.render_template(
                            session,
                            "view-export-button",
                            url=export_url,
                            format=fmt,
                        ),
                    ),
                )

        return res

    @view_action_validator(methods=[Request.GET])
    def export(
        self: "ListView",
        feretui: "FeretUI",  # noqa: ARG002
        request: Request,
    ) -> Response:
        """Export list data to CSV or XLSX format.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param request: The request
        :type request: :class:`feretui.request.Request`
        :return: Response containing exported file
        :rtype: :class:`feretui.response.Response`
        """
        if not getattr(self, "enable_export", False):
            raise ResourceError("Export is disabled for this view")

        fmt = request.query.get("format", ["csv"])[0].lower()
        allowed_formats = getattr(self, "export_formats", ["csv", "xlsx"])
        if fmt not in allowed_formats:
            raise ResourceError(f"Unsupported export format: {fmt}")

        filters = [
            (key[7:-1], values)
            for key, values in request.query.items()
            if key.startswith("filter[") and key.endswith("]")
        ]

        if hasattr(self.resource, "export_data"):
            headers, rows = self.resource.export_data(
                self,
                filters=filters,
                request=request,
            )
        else:
            dataset = self.resource.filtered_reads(
                self.form_cls,
                filters,
                offset=0,
                limit=100000,
            )
            form = self.form_cls()
            fields = [field for field in form if field.name != "csrf_token"]
            headers = [
                str(f.label.text if f.label and f.label.text else f.name)
                for f in fields
            ]
            field_names = [f.name for f in fields]
            rows = [
                [row_form[name].data for name in field_names]
                for row_form in dataset.get("forms", [])
            ]

        filename = f"{self.resource.code}_{self.code}.{fmt}"
        if fmt == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(headers)
            for row in rows:
                writer.writerow(row)

            body = output.getvalue().encode("utf-8")
            content_type = "text/csv; charset=utf-8"
        else:
            import openpyxl

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Export"
            ws.append(headers)
            for row in rows:
                ws.append([str(v) if v is not None else "" for v in row])

            b_output = io.BytesIO()
            wb.save(b_output)
            body = b_output.getvalue()
            content_type = (
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )

        return Response(
            body=body,
            headers={
                "Content-Type": content_type,
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )

    def render(
        self: "ListView",
        feretui: "FeretUI",
        session: Session,
        options: dict,
    ) -> str:
        """Render the view.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The Session
        :type session: :class:`feretui.session.Session`
        :param options: The options come from the body or the query string
        :type options: dict
        :return: The html page in
        :rtype: str.
        """
        return Markup(
            feretui.render_template(
                session,
                "feretui-resource-list",
                widget=self.widget,
                **self.render_kwargs(feretui, session, options),
            ),
        )


class LResource:
    """LResource class."""

    default_view: str = "list"

    MetaViewList = DefaultViewList

    def build_view(
        self: "LResource",
        view_cls_name: str,
    ) -> Resource:
        """Return the view instance in fonction of the MetaView attributes.

        :param view_cls_name: name of the meta attribute
        :type view_cls_name: str
        :return: An instance of the view
        :rtype: :class:`feretui.resources.view.View`
        """
        if view_cls_name.startswith("MetaViewList"):
            meta_view_cls = self.get_meta_view_class(view_cls_name)
            meta_view_cls.append(ListView)
            view_cls = type(
                "ListView",
                tuple(meta_view_cls),
                {},
            )
            if not self.default_view:
                self.default_view = view_cls.code

            return view_cls(self)

        return super().build_view(view_cls_name)

    def filtered_reads(
        self: "LResource",
        form_cls: FeretUIForm,
        filters: list[tuple[str, list[str]]],
        offset: int,
        limit: int,
    ) -> dict:
        """Return the dataset of the list.

        should return a dict with 2 key
        * forms: list of instance of form_cls
        * total: number of the exisinting entries without offset and limit

        .. warning:: must be overwriting

        :param form_cls: Form of the list view
        :type form_cls: :class:`feretui.form.FeretUIForm`
        :param filters: The filters choosen in the list
        :type filters: list[tuple[str, list[str]]]
        :param offset: The start of the plage of the dataset
        :type offset: int
        :param limit: The size of the plage of the dataset
        :type limit: int
        :return: the dataset
        :rtype: dict
        """
