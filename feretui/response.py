# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Module feretui.response.

It is the response object used by feretui to return any result quering by
the client.

This reponse can not be used directly by web serving. The adapter to connect
the web-serving with this response must be write by another libray or by the
developper.

Example with bottle::

    from bottle import response, route
    from feretui import FeretUI

    myferet = FeretUI()

    @route('/feretui/action/<action>', method=['GET', 'POST'])
    def post_action(action):
        ...
        res = myferet.do_action(frequest, action)
        for k, v in res.headers.items():
            response.set_header(k, v)

        return res.body,

"""


class Response:
    """Description of the response.

    This object is just a description to inform the web-server library
    the return of FeretUI

    ::

        from feretui import Response


        response = Response('<div>This is a template</div>')

    :param body: [''], response return to the web-serving.
    :type body: Any
    :param status_code: [200], the status code of the response.
    :type status_code: int
    :param headers: Optionnal, additionnal headers.
    :type headers: dict[str, str]
    """

    def __init__(
        self: "Response",
        body: str | None = "",
        status_code: int = 200,
        headers: dict[str, str] = None,
    ) -> "Response":
        """FeretUI response.

        :param body: [''], response return to the web-serving.
        :type body: Any
        :param status_code: [200], the status code of the response.
        :type status_code: int
        :param headers: Optionnal, additionnal headers.
        :type headers: dict[str, str]
        """
        if headers is None:
            headers = {}

        self.body = body
        self.status_code = status_code
        self.headers = headers

    @classmethod
    def redirect(
        cls: type["Response"],
        url: str,
        hx: bool = True,
        status_code: int = 200,
    ) -> "Response":
        """Return a redirect response using HX-Redirect or standard 302."""
        if hx:
            return cls(
                body="",
                status_code=status_code,
                headers={"HX-Redirect": url},
            )
        return cls(
            body="",
            status_code=302,
            headers={"Location": url},
        )

    @classmethod
    def refresh(cls: type["Response"]) -> "Response":
        """Return a response instructing client to refresh via HX-Refresh."""
        return cls(body="", status_code=200, headers={"HX-Refresh": "true"})

    def with_trigger(
        self: "Response",
        event_name: str,
        detail: str | dict | None = None,
    ) -> "Response":
        """Add an HX-Trigger event to response headers."""
        if detail is None:
            self.headers["HX-Trigger"] = event_name
        elif isinstance(detail, dict):
            import json

            self.headers["HX-Trigger"] = json.dumps({event_name: detail})
        else:
            self.headers["HX-Trigger"] = f"{event_name}:{detail}"
        return self
