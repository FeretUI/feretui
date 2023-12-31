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

    from bottle import HTTPResponse, route
    from feretui import FeretUI

    myferet = FeretUI()

    @route('/feretui/action/<action>', method=['POST'])
    def post_action(action):
        ...
        response = myferet.do_action(frequest, action)
        return HTTPResponse(
            body=response.body,
            status=response.status_code,
            headers=response.headers
        )

"""
from typing import Any


class Response:
    """Description of the response.

    This object is just a description to inform the web-server library
    the return of FeretUI

    ::

        from feretui import Response


        response = Response('<div>This is a template</div>')

    :param body: [''], response return to the web-serving.
    :type body: Any
    :param content_type: ['text/html'], The web-serving content type.
    :type content_type: str
    :param status_code: [200], the status code of the response.
    :type status_code: int
    :param headers: Optionnal, additionnal headers.
    :type headers: dict[str, str]
    """

    def __init__(
        self,
        body: Any = '',
        content_type: str = 'text/html',
        status_code: int = 200,
        headers: dict[str, str] = None
    ):
        """FeretUI response.

        :param body: [''], response return to the web-serving.
        :type body: Any
        :param content_type: ['text/html'], The web-serving content type.
        :type content_type: str
        :param status_code: [200], the status code of the response.
        :type status_code: int
        :param headers: Optionnal, additionnal headers.
        :type headers: dict[str, str]
        """
        if headers is None:
            headers = {}

        self.body = body
        self.content_type = content_type
        self.status_code = status_code
        self.headers = headers
