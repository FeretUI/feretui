# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Module feretui.resources.chatter.

Provides HasChatterMixin for social collaboration, internal notes,
and activity timeline.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any

from feretui.request import Request
from feretui.resources.view import view_action_validator
from feretui.response import Response

if TYPE_CHECKING:
    from feretui.feretui import FeretUI


class HasChatterMixin:
    """Mixin to enable Chatter / Activity Timeline on a Resource."""

    chatter: bool = True

    def __init__(self, *args: tuple, **kwargs: dict) -> None:
        """Initialize Chatter mixin."""
        super().__init__(*args, **kwargs)

        if not hasattr(self, "_chatter_store"):
            self._chatter_store: dict[str, list[dict[str, Any]]] = {}

    def get_chatter_messages(self, pk: str | None) -> list[dict[str, Any]]:
        """Return list of chatter message entries for given record pk."""
        if not pk:
            return []
        if not hasattr(self, "_chatter_store"):
            self._chatter_store = {}
        return list(self._chatter_store.get(str(pk), []))

    def add_chatter_message(
        self,
        pk: str,
        body: str,
        author: str = "User",
        msg_type: str = "note",
    ) -> dict[str, Any]:
        """Record a new message or note in the chatter."""
        if not hasattr(self, "_chatter_store"):
            self._chatter_store = {}

        str_pk = str(pk)
        if str_pk not in self._chatter_store:
            self._chatter_store[str_pk] = []

        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        msg = {
            "id": str(len(self._chatter_store[str_pk]) + 1),
            "pk": str_pk,
            "author": author,
            "body": body,
            "date": now,
            "type": msg_type,
        }
        self._chatter_store[str_pk].append(msg)
        return msg

    @view_action_validator(methods=[Request.POST])
    def chatter_post(
        self,
        feretui: "FeretUI",
        request: Request,
    ) -> Response:
        """Handle posting a new note or message to chatter."""
        options = request.get_query_string_from_current_url()
        pk = (
            options.get("pk", [None])[0]
            if isinstance(options.get("pk"), list)
            else options.get("pk")
        )
        if not pk:
            return Response("Missing pk", status_code=400)

        body = ""
        if request.form and "chatter_body" in request.form:
            body = request.form["chatter_body"]
        elif "body" in request.query:
            body = request.query["body"]
        if isinstance(body, list):
            body = body[0] if body else ""

        body = (body or "").strip()
        if not body:
            return Response("", status_code=204)

        msg_type = "note"
        if request.form and "msg_type" in request.form:
            msg_type = request.form["msg_type"]

        author = getattr(request.session, "user", None) or "Administrator"

        self.add_chatter_message(pk, body, author=author, msg_type=msg_type)
        messages = self.get_chatter_messages(pk)

        html = feretui.render_template(
            request.session,
            "feretui-resource-chatter-thread",
            pk=pk,
            resource=self,
            messages=messages,
        )
        return Response(html, status_code=200)
