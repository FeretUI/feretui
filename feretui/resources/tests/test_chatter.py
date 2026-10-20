"""Unit tests for HasChatterMixin and Chatter component."""

import pytest
from multidict import MultiDict
from wtforms import StringField

from feretui.context import cvar_feretui, cvar_request
from feretui.form import FeretUIForm
from feretui.request import Request
from feretui.resources import HasChatterMixin, LCRUD, Resource
from feretui.session import Session


class TestChatter:
    """Test suite for Chatter component."""

    def test_chatter_store_operations(self) -> None:
        """Verify adding and retrieving chatter messages."""

        class ChattyResource(HasChatterMixin, Resource):
            code = "chatty"
            label = "Chatty"

        res = ChattyResource()
        assert res.get_chatter_messages(None) == []
        assert res.get_chatter_messages("10") == []

        msg1 = res.add_chatter_message("10", "First internal note", author="Alice", msg_type="note")
        assert msg1["pk"] == "10"
        assert msg1["author"] == "Alice"
        assert msg1["body"] == "First internal note"
        assert msg1["type"] == "note"
        assert "date" in msg1

        msg2 = res.add_chatter_message("10", "Customer replied via email", author="Bob", msg_type="comment")
        messages = res.get_chatter_messages("10")
        assert len(messages) == 2
        assert messages[0]["body"] == "First internal note"
        assert messages[1]["body"] == "Customer replied via email"

        # Record 20 has no messages
        assert res.get_chatter_messages("20") == []

        # Test recovery if _chatter_store attribute is absent
        del res._chatter_store
        assert res.get_chatter_messages("10") == []
        del res._chatter_store
        res.add_chatter_message("10", "recreated note")
        assert len(res.get_chatter_messages("10")) == 1

    def test_chatter_post_action(self, feretui, session) -> None:
        """Verify chatter_post action endpoint."""
        cvar_feretui.set(feretui)
        cvar_request.set(Request(session=session))

        class OrderResource(HasChatterMixin, Resource):
            code = "orders"
            label = "Orders"

        res = OrderResource()

        # Missing pk -> 400
        req_no_pk = Request(
            session=session,
            method=Request.POST,
            querystring="action=chatter_post",
            headers={"Hx-Current-Url": "/?resource=orders"},
        )
        resp_no_pk = res.chatter_post(feretui, req_no_pk)
        assert resp_no_pk.status_code == 400

        # Empty body -> 204
        req_empty = Request(
            session=session,
            method=Request.POST,
            querystring="action=chatter_post&pk=42",
            headers={"Hx-Current-Url": "/?resource=orders&pk=42"},
            form=MultiDict([("chatter_body", "   ")]),
        )
        resp_empty = res.chatter_post(feretui, req_empty)
        assert resp_empty.status_code == 204

        # Valid note post
        req_valid = Request(
            session=session,
            method=Request.POST,
            querystring="action=chatter_post&pk=42",
            headers={"Hx-Current-Url": "/?resource=orders&pk=42"},
            form=MultiDict([("chatter_body", "Order approved by manager"), ("msg_type", "note")]),
        )
        resp_valid = res.chatter_post(feretui, req_valid)
        assert resp_valid.status_code == 200
        assert "feretui-chatter-item" in resp_valid.body
        assert "Order approved by manager" in resp_valid.body
        assert "Administrator" in resp_valid.body

        # Post via query parameter list
        req_query_body = Request(
            session=session,
            method=Request.POST,
            querystring="action=chatter_post&pk=42&body=Query+note+body",
            headers={"Hx-Current-Url": "/?resource=orders&pk=42"},
        )
        resp_qb = res.chatter_post(feretui, req_query_body)
        assert resp_qb.status_code == 200
        assert "Query note body" in resp_qb.body

    def test_chatter_rendering_in_sheet(self, feretui, session) -> None:
        """Verify chatter container renders in readonly and readwrite sheet views."""
        cvar_feretui.set(feretui)
        cvar_request.set(Request(session=session))

        class ProjectForm(FeretUIForm):
            pk = StringField()
            name = StringField()

        class ProjectResource(HasChatterMixin, LCRUD, Resource):
            code = "projects"
            label = "Projects"
            Form = ProjectForm
            chatter = True

            class MetaViewRead:
                body_template_id = "view-sheet-readonly-form"

            def read(self, form_cls, pk):
                f = form_cls()
                f.pk.data = str(pk)
                f.name.data = "Apollo Project"
                return f

        res = ProjectResource.build()
        res.add_chatter_message("99", "Kickoff meeting held", author="Sarah")

        read_view = res.views["read"]
        html = read_view.render(feretui, session, {"pk": "99"})
        assert "feretui-chatter-container" in html
        assert "Activity" in html
        assert "Notes" in html
        assert "Kickoff meeting held" in html
        assert "Sarah" in html
