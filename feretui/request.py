# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Module feretui.request.

It is the request object used by feretui. FeretUI can't decode any request
from any web-server.

The adapter to connect the web-server with this request must be write by
another libray or by the developper.

Example with bottle::

    from bottle import request, route
    from feretui import FeretUI, Request, Session

    myferet = FeretUI()
    session = Session()

    @route('/feretui/action/<action>', method=['POST'])
    def post_action(action):
        frequest = Request(
            session=session,
            method=Request.POST,
            body=request.body.read(),
            headers=dict(request.headers),
        )
        ...
"""
import json
import urllib
from typing import Any

from multidict import MultiDict

from feretui.exceptions import (
    RequestFormError,
    RequestNoSessionError,
    RequestWrongSessionError,
)
from feretui.session import Session


class RequestMethod:
    """RequestMethod."""


class Request:
    """Description of the request.

    This object is just a description of the web-server request.

    :param session: User session
    :type session: Session
    :param method: [Request.POST], the request method
    :type method: RequestMethod
    :param body: [None]
    :type body: str
    :param form: [None]
    :type form: MultiDict_
    :param querystring: [None]
    :type querystring: str
    :param headers: [None]
    :type headers: dict[str, str]
    :exception: :class:`feretui.exceptions.RequestFormError`
    :exception: :class:`feretui.exceptions.RequestNoSessionError`
    :exception: :class:`feretui.exceptions.RequestWrongSessionError`
    """

    DELETE = RequestMethod()
    """DELETE request method"""
    GET = RequestMethod()
    """GET request method"""
    PATCH = RequestMethod()
    """PATCH request method"""
    POST = RequestMethod()
    """Post request method"""
    PUT = RequestMethod()
    """PUT request method"""

    def __init__(
        self: "Request",
        session: Session,
        method: RequestMethod = POST,
        form: MultiDict = None,
        body: str = None,
        params: MultiDict = None,
        querystring: str = None,
        headers: dict[str, str] = None,
    ) -> "Request":
        """Request object."""
        if headers is None:
            headers = {}

        self.session = session
        self.method = method
        self.form = form
        self.body = body
        self.params = params
        self.raw_querystring = querystring
        self.headers = headers

        self.query = {}
        if querystring:
            self.query = urllib.parse.parse_qs(querystring)

        if form and not isinstance(form, MultiDict):
            raise RequestFormError('The form must be a MultiDict')

        if session is None:
            raise RequestNoSessionError('the session is required')

        if not isinstance(session, Session):
            raise RequestWrongSessionError(
                'the session must be an instance of FeretUI Session')

    @property
    def json(self: "Request") -> MultiDict:
        """Return the body as a dict."""
        if self.body:
            return MultiDict(json.loads(self.body))

        return {}

    def get_url_from_dict(
        self: "Request",
        base_url: str = '/',
        querystring: dict[str, Any] = None,
    ) -> str:
        """Return an url.

        The url is built in function the ain_url and the querystring.

        :param base_url: [/], the base url before the querystring.
        :type base_url: str
        :param querystring: [None], the querystring.
        :type querystring: dict[str, Any]
        :return: Return the URL.
        :rtype: str
        """
        if not querystring:
            return base_url

        return f'{base_url}?{urllib.parse.urlencode(querystring, doseq=True)}'

    def get_query_string_from_current_url(
        self: "Request",
    ) -> dict[str, list[str]]:
        """Get the querystring from the current client URL.

        :return: The converted querystring.
        :rtype: dict[str, list[str]]
        """
        url = self.headers['Hx-Current-Url']
        url = urllib.parse.urlparse(url)
        return urllib.parse.parse_qs(url.query)

    def get_base_url_from_current_url(self: "Request") -> dict[str, list[str]]:
        """Get the querystring from the current client URL.

        :return: The converted querystring.
        :rtype: dict[str, list[str]]
        """
        url = self.headers['Hx-Current-Url']
        url = urllib.parse.urlparse(url)
        return url.path
