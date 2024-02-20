# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Module feretui.pages.

The page is the html inside the main in the html body.

::

    def my_page(feretui, session, options):
        vals = {
            ...
        }
        return feretui.render_template(session, 'my-page', **vals)


The availlable pages are:

* :func:`.page_404`.
* :func:`.page_forbidden`.
* :func:`.homepage`.
"""
from typing import TYPE_CHECKING

from feretui.response import Response
from feretui.session import Session

if TYPE_CHECKING:
    from feretui.feretui import FeretUI


def page_404(feretui: "FeretUI", session: Session, options: dict) -> Response:
    """Return the page 404.

    The page name is passed on the dict to display the good name to display.

    :param feretui: The feretui client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param session: The Session
    :type session: :class:`feretui.session.Session`
    :param options: The options come from the body or the query string
    :type options: dict
    :return: The html page in a response
    :rtype: :class:`feretui.response.Response`
    """
    page = options.get('page', '')
    return feretui.render_template(session, 'feretui-page-404', page=page)


def page_forbidden(
    feretui: "FeretUI",
    session: Session,
    options: dict,
) -> Response:
    """Return the page forbidden.

    The page name is passed on the dict to display the good name to display.

    :param feretui: The feretui client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param session: The Session
    :type session: :class:`feretui.session.Session`
    :param options: The options come from the body or the query string
    :type options: dict
    :return: The html page in a response
    :rtype: :class:`feretui.response.Response`
    """
    page = options.get('page', '')
    return feretui.render_template(
        session, 'feretui-page-forbidden', page=page)


def homepage(
    feretui: "FeretUI",
    session: Session,
    options: dict,  # noqa: ARG001
) -> Response:
    """Return the homepage.

    :param feretui: The feretui client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param session: The Session
    :type session: :class:`feretui.session.Session`
    :param options: The options come from the body or the query string
    :type options: dict
    :return: The html page in a response
    :rtype: :class:`feretui.response.Response`
    """
    return feretui.render_template(session, 'feretui-page-homepage')
