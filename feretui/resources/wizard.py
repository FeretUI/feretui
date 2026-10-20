# This file is a part of the FeretUI project
#
#    Copyright (C) 2026 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Wizard module.

Wizards are transient resources that open in modal dialogs to collect input
and perform interactive operations (e.g., batch cancellation, partial payment,
state transition confirmations).
"""

import uuid
from typing import TYPE_CHECKING, Any

from markupsafe import Markup

from feretui.form import FeretUIForm
from feretui.resources.resource import Resource
from feretui.response import Response
from feretui.session import Session

if TYPE_CHECKING:
    from feretui.feretui import FeretUI
    from feretui.request import Request


class WizardResource(Resource):
    """WizardResource for transient interactive forms and batch operations."""

    default_view: str = "form"

    modal_size: str = "normal"
    confirm_label: str = "Confirm"
    cancel_label: str = "Cancel"
    confirm_icon: str = "ti ti-check"
    title: str | None = None

    def get_defaults(
        self: "WizardResource",
        session: Session,  # noqa: ARG002
        active_ids: list[str],  # noqa: ARG002
    ) -> dict[str, Any]:
        """Return initial default form values."""
        return {}

    def execute(
        self: "WizardResource",
        form: FeretUIForm,  # noqa: ARG002
        session: Session,  # noqa: ARG002
        active_ids: list[str],  # noqa: ARG002
    ) -> Response | None:
        """Execute the wizard logic upon submission."""
        return None

    def build_form(
        self: "WizardResource",
        form_data: object = None,
        defaults: dict[str, object] | None = None,
    ) -> FeretUIForm:
        """Instantiate and populate the wizard form."""
        form_cls = getattr(self, "Form", FeretUIForm)
        if form_data is not None:
            return form_cls(form_data)
        return form_cls(data=defaults or {})

    def render_modal_content(
        self: "WizardResource",
        feretui: "FeretUI",
        session: Session,
        active_ids: list[str],
        form: FeretUIForm | None = None,
    ) -> str:
        """Render the inner wizard form HTML."""
        if form is None:
            defaults = self.get_defaults(session, active_ids)
            form = self.build_form(defaults=defaults)

        submit_url = (
            f"{feretui.base_url}/action/resource?"
            f"resource={self.code}&action=wizard_execute"
        )
        return feretui.render_template(
            session,
            "feretui-wizard-form",
            wizard=self,
            form=form,
            active_ids=active_ids,
            submit_url=submit_url,
            confirm_label=self.confirm_label,
            cancel_label=self.cancel_label,
            confirm_icon=self.confirm_icon,
        )

    def wizard_execute(
        self: "WizardResource",
        feretui: "FeretUI",
        request: "Request",
    ) -> Response:
        """Handle wizard submission and trigger callback execution."""
        active_ids: list[str] = []

        if request.params:
            if hasattr(request.params, "getall"):
                active_ids = request.params.getall("active_ids")
            elif "active_ids" in request.params:
                val = request.params["active_ids"]
                active_ids = val if isinstance(val, list) else [str(val)]

        form = self.build_form(form_data=request.params)
        if form.validate():
            custom_resp = self.execute(form, request.session, active_ids)
            if isinstance(custom_resp, Response):
                return custom_resp
            return Response(
                "<!-- modal-closed -->",
                status_code=200,
                headers={"HX-Trigger": "closeModal"},
            )

        content = self.render_modal_content(
            feretui, request.session, active_ids, form=form
        )
        modal_id = uuid.uuid4().hex[:8]
        html = feretui.render_template(
            request.session,
            "feretui-modal-dialog",
            modal_id=modal_id,
            title=self.title or self.label,
            content=Markup(content),
            modal_size=self.modal_size,
            target_field="",
        )
        return Response(html, status_code=422)
