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

.. _pydantic: https://docs.pydantic.dev/latest/
.. _BaseModel: https://docs.pydantic.dev/latest/api/base_model/
"""
import inspect
import json
import urllib
from typing import Any

from pydantic import BaseModel

from feretui.exceptions import (
    RequestBodyDeserializationError,
    RequestNoSessionError,
    RequestQueryStringDeserializationError,
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
    :param querystring: [None]
    :type querystring: str
    :param headers: [None]
    :type headers: dict[str, str]
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
        self,
        session: Session,
        method: RequestMethod = POST,
        body: str = None,
        querystring: str = None,
        headers: dict[str, str] = None,
    ):
        """Request object."""
        if headers is None:
            headers = {}

        self.session = session
        self.method = method
        self.raw_body = body
        self.raw_querystring = querystring
        self.headers = headers

        self.pydantic_body_validator = None
        self.pydantic_querystring_validator = None

        self.query = {}
        if querystring:
            self.query = urllib.parse.parse_qs(querystring)

        if self.raw_body:
            try:
                self.body = json.loads(self.raw_body)
            except Exception:
                self.body = {}

        if session is None:
            raise RequestNoSessionError('the session is required')

        if not isinstance(session, Session):
            raise RequestWrongSessionError(
                'the session must be an instance of FeretUI Session')

    @property
    def deserialized_body(self) -> BaseModel:
        """Get The body deserialized by pydantic_.

        ::

            class MyValidator(BaseModel):
                foo: str

            myrequest.pydantic_body_validator = MyValidator

        .. note::

            The validator is filled by the helper
            :func:`feretui.helper.action_validator`

        :return: Deserialized body
        :rtype: BaseModel_
        :exception: :class:`feretui.exceptions.RequestBodyDeserializationError`
        """
        if not self.pydantic_body_validator:
            raise RequestBodyDeserializationError(
                'No schema validator defined for deserialize the body'
            )

        if inspect.isfunction(self.pydantic_body_validator):
            schema = self.pydantic_body_validator(self)
        else:
            schema = self.pydantic_body_validator

        return schema(**self.body)

    @property
    def deserialized_querystring(self) -> dict:
        """Get The query string deserialized by pydantic_.

        ::

            class MyValidator(BaseModel):
                foo: str

            myrequest.pydantic_querystring_validator = MyValidator

        .. note::

            The validator is filled by the helper
            :func:`feretui.helper.action_validator`

        :return: Deserialized query string
        :rtype: BaseModel_
        :exception:
            :class:`feretui.exceptions.RequestQueryStringDeserializationError`
        """
        if not self.pydantic_querystring_validator:
            raise RequestQueryStringDeserializationError(
                'No schema validator defined for deserialize the querystring'
            )

        if inspect.isfunction(self.pydantic_querystring_validator):
            schema = self.pydantic_querystring_validator(self)
        else:
            schema = self.pydantic_querystring_validator

        return schema(**self.query)

    def get_url_from_dict(
        self,
        base_url: str = '/',
        querystring: dict[str, Any] = None
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

    def get_query_string_from_current_url(self) -> dict[str, list[str]]:
        """Get the querystring from the current client URL.

        :return: The converted querystring.
        :rtype: dict[str, list[str]]
        """
        url = self.headers['Hx-Current-Url']
        url = urllib.parse.urlparse(url)
        return urllib.parse.parse_qs(url.query)
