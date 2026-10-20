# This file is a part of the FeretUI project
#
#    Copyright (C) 2026 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Unit tests for WizardResource and OpenWizardAction."""

from multidict import MultiDict
import pytest
from wtforms import StringField
from wtforms.validators import DataRequired

from feretui.exceptions import ActionError
from feretui.form import FeretUIForm
from feretui.request import Request
from feretui.resources.actions import (
    OpenModalSelectedRowsAction,
    OpenWizardAction,
)
from feretui.resources.wizard import WizardResource
from feretui.response import Response


class CancelOrderForm(FeretUIForm):
    reason = StringField("Reason", validators=[DataRequired()])


class CancelOrderWizard(WizardResource):
    code = "cancel_wizard"
    label = "Cancel Orders"
    title = "Cancel Confirmation"
    Form = CancelOrderForm
    modal_size = "small"

    def get_defaults(self, session, active_ids):
        return {"reason": f"Bulk cancellation of {len(active_ids)} orders"}

    def execute(self, form, session, active_ids):
        if form.reason.data == "custom_response":
            return Response("Cancelled successfully", status_code=200)
        return None


class SimpleWizard(WizardResource):
    code = "simple_wizard"
    label = "Simple"
    Form = CancelOrderForm


class TestWizardResource:
    """Test suite for WizardResource."""

    def test_wizard_defaults_and_execute(self, session) -> None:
        """Test default get_defaults and execute methods."""
        wiz = SimpleWizard()
        assert wiz.get_defaults(session, ["1", "2"]) == {}
        form = CancelOrderForm(data={"reason": "test"})
        assert wiz.execute(form, session, ["1", "2"]) is None

    def test_build_form(self) -> None:
        """Test build_form with and without data."""
        wiz = CancelOrderWizard()
        form_empty = wiz.build_form()
        assert form_empty.reason.data is None

        form_defaults = wiz.build_form(defaults={"reason": "prefilled"})
        assert form_defaults.reason.data == "prefilled"

        form_data = wiz.build_form(form_data=MultiDict([("reason", "submitted")]))
        assert form_data.reason.data == "submitted"

    def test_render_modal_content(self, feretui, session, frequest) -> None:  # noqa: ARG002
        """Test render_modal_content produces form HTML."""
        wiz = CancelOrderWizard()
        html = wiz.render_modal_content(feretui, session, ["1", "2"])
        assert "feretui-wizard-container" in html
        assert 'name="active_ids"' in html
        assert 'value="1"' in html
        assert 'value="2"' in html
        assert "Bulk cancellation of 2 orders" in html
        assert "Confirm" in html
        assert "Cancel" in html

        # Providing existing form
        f = CancelOrderForm(data={"reason": "Manual reason"})
        html_manual = wiz.render_modal_content(
            feretui, session, ["3"], form=f
        )
        assert "Manual reason" in html_manual

    def test_wizard_execute_success_default_response(
        self, feretui, session, frequest  # noqa: ARG002
    ) -> None:
        """Test wizard_execute with valid data returning default close response."""
        wiz = CancelOrderWizard()
        params = MultiDict([
            ("active_ids", "10"),
            ("active_ids", "20"),
            ("reason", "Out of stock"),
        ])
        req = Request(session, method=Request.POST, params=params)
        resp = wiz.wizard_execute(feretui, req)
        assert resp.status_code == 200
        assert resp.headers.get("HX-Trigger") == "closeModal"
        assert "<!-- modal-closed -->" in resp.body

    def test_wizard_execute_success_custom_response(
        self, feretui, session, frequest  # noqa: ARG002
    ) -> None:
        """Test wizard_execute when execute returns a custom Response."""
        wiz = CancelOrderWizard()
        params = MultiDict([
            ("active_ids", "10"),
            ("reason", "custom_response"),
        ])
        req = Request(session, method=Request.POST, params=params)
        resp = wiz.wizard_execute(feretui, req)
        assert resp.status_code == 200
        assert "Cancelled successfully" in resp.body

    def test_wizard_execute_active_ids_fallback(
        self, feretui, session, frequest  # noqa: ARG002
    ) -> None:
        """Test wizard_execute parsing active_ids when not a getall object."""
        wiz = CancelOrderWizard()
        req = Request(session, method=Request.POST)
        req.params = {"active_ids": "42", "reason": "Standard"}
        resp = wiz.wizard_execute(feretui, req)
        assert resp.status_code == 200

    def test_wizard_execute_validation_failure(
        self, feretui, session, frequest  # noqa: ARG002
    ) -> None:
        """Test wizard_execute with missing required field returns 422 with errors."""
        wiz = CancelOrderWizard()
        params = MultiDict([("active_ids", "5"), ("reason", "")])
        req = Request(session, method=Request.POST, params=params)
        resp = wiz.wizard_execute(feretui, req)
        assert resp.status_code == 422
        assert "feretui-modal" in resp.body
        assert "This field is required." in resp.body or "required" in resp.body


class TestOpenWizardAction:
    """Test suite for OpenWizardAction and OpenModalSelectedRowsAction."""

    def test_open_wizard_action_for_selected_rows(self) -> None:
        """Test OpenWizardAction attributes for selected rows mode."""
        act = OpenWizardAction(
            "Cancel Selected",
            wizard="cancel_wizard",
            title="Cancel Orders",
            modal_size="large",
            icon="ti ti-ban",
            description="Cancel all selected orders",
            for_selected_rows=True,
        )
        assert (
            act.template_id
            == "feretui-page-resource-action-open-modal-for-selected-rows"
        )
        assert act.wizard == "cancel_wizard"
        assert act.for_selected_rows is True

    def test_open_wizard_action_for_single_row(self) -> None:
        """Test OpenWizardAction attributes for single record mode."""
        act = OpenWizardAction(
            "Cancel Order",
            wizard="cancel_wizard",
            for_selected_rows=False,
        )
        assert act.template_id == "feretui-page-resource-action-open-modal"
        assert act.for_selected_rows is False

    def test_open_wizard_action_get_url(self, feretui, session) -> None:
        """Test OpenWizardAction URL generation."""
        act = OpenWizardAction(
            "Cancel",
            wizard="cancel_wizard",
            title="Cancel Modal",
            modal_size="small",
        )
        url = act.get_url(feretui, session, {"pk": ["101"]})
        assert "/action/wizard?" in url
        assert "wizard=cancel_wizard" in url
        assert "modal_size=small" in url
        assert "title=Cancel+Modal" in url
        assert "pk=101" in url

    def test_open_modal_selected_rows_action(self) -> None:
        """Test OpenModalSelectedRowsAction template id."""
        act = OpenModalSelectedRowsAction("Open", resource="res")
        assert (
            act.template_id
            == "feretui-page-resource-action-open-modal-for-selected-rows"
        )


class TestWizardActionEndpoint:
    """Test suite for /action/wizard endpoint in feretui.actions."""

    def test_action_wizard_missing_code(self, feretui, session) -> None:
        """Test /action/wizard raises ActionError when wizard code is missing."""
        from feretui.actions import wizard

        req = Request(session, method=Request.GET, querystring="")
        with pytest.raises(ActionError, match="No wizard or resource specified"):
            wizard(feretui, req)

    def test_action_wizard_get_open(self, feretui, session, frequest) -> None:  # noqa: ARG002
        """Test /action/wizard opens modal dialog via GET request."""
        from feretui.actions import wizard

        wiz = CancelOrderWizard.build()
        feretui.register_resource()(CancelOrderWizard)

        req = Request(
            session,
            method=Request.GET,
            querystring="wizard=cancel_wizard&active_ids=1&active_ids=2",
        )
        resp = wizard(feretui, req)
        assert resp.status_code == 200
        assert "feretui-modal" in resp.body
        assert "Cancel Confirmation" in resp.body
        assert "Bulk cancellation of 2 orders" in resp.body

    def test_action_wizard_post_with_selected_rows(
        self, feretui, session, frequest  # noqa: ARG002
    ) -> None:
        """Test /action/wizard opens modal with selected-rows-* params from form inclusion."""
        from feretui.actions import wizard

        wiz = CancelOrderWizard.build()
        feretui.register_resource()(CancelOrderWizard)

        params = MultiDict([
            ("wizard", "cancel_wizard"),
            ("selected-rows-orders-view-list", "101"),
            ("selected-rows-orders-view-list", "102"),
        ])
        req = Request(session, method=Request.POST, params=params)
        resp = wizard(feretui, req)
        assert resp.status_code == 200
        assert "Bulk cancellation of 2 orders" in resp.body

    def test_action_wizard_with_pk_and_defaults(
        self, feretui, session, frequest  # noqa: ARG002
    ) -> None:
        """Test /action/wizard with pk parameter and default title."""
        from feretui.actions import wizard

        SimpleWizard.build()
        feretui.register_resource()(SimpleWizard)

        req = Request(
            session,
            method=Request.GET,
            querystring="resource=simple_wizard&pk=99",
        )
        resp = wizard(feretui, req)
        assert resp.status_code == 200
        assert "Simple" in resp.body
        assert 'name="active_ids"' in resp.body
        assert 'value="99"' in resp.body
