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
import urllib
from collections.abc import Callable
from typing import TYPE_CHECKING

from feretui.exceptions import PageError
from feretui.session import Session

from feretui.helper import unauthenticated_or_forbidden

if TYPE_CHECKING:
    from feretui.feretui import FeretUI


def page_404(feretui: "FeretUI", session: Session, options: dict) -> str:
    """Return the page 404.

    The page name is passed on the dict to display the good name to display.

    :param feretui: The feretui client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param session: The Session
    :type session: :class:`feretui.session.Session`
    :param options: The options come from the body or the query string
    :type options: dict
    :return: The html page
    :rtype: str
    """
    page = options.get('page', '')
    return feretui.render_template(session, 'feretui-page-404', page=page)


def page_forbidden(
    feretui: "FeretUI",
    session: Session,
    options: dict,
) -> str:
    """Return the page forbidden.

    The page name is passed on the dict to display the good name to display.

    :param feretui: The feretui client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param session: The Session
    :type session: :class:`feretui.session.Session`
    :param options: The options come from the body or the query string
    :type options: dict
    :return: The html page
    :rtype: str
    """
    page = options.get('page', '')
    return feretui.render_template(
        session, 'feretui-page-forbidden', page=page)


def homepage(
    feretui: "FeretUI",
    session: Session,
    options: dict,  # noqa: ARG001
) -> str:
    """Return the homepage.

    :param feretui: The feretui client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param session: The Session
    :type session: :class:`feretui.session.Session`
    :param options: The options come from the body or the query string
    :type options: dict
    :return: The html page in
    :rtype: str
    """
    return feretui.render_template(session, 'feretui-page-homepage')


def static_page(template_id: str) -> Callable:
    """Return the template linked the template_id.

    :param template_id: The template_id
    :type feretui: :str
    :return: The html page
    :rtype: Callable
    """
    def _static_page(
        feretui: "FeretUI",
        session: Session,
        options: dict,  # noqa: ARG001
    ) -> str:
        if template_id not in feretui.template.known:
            raise PageError(template_id)

        return feretui.render_template(session, template_id)

    return _static_page


def aside_menu(
    feretui: "FeretUI",
    session: Session,
    options: dict,  # noqa: ARG001
) -> str:
    """Return the aside_page in the aside_page.

    :param feretui: The feretui client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param session: The Session
    :type session: :class:`feretui.session.Session`
    :param options: The options come from the body or the query string
    :type options: dict
    :return: The html page in
    :rtype: str
    """
    if 'aside' not in options:
        raise PageError('The aside parameter is required in the querystring')

    options = options.copy()  # don't modify the main options
    menus = feretui.get_aside_menus(options['aside'][0])
    options['page'] = options.pop('aside_page', ['homepage'])[0]

    return feretui.render_template(
        session,
        'feretui-page-aside',
        menus=menus,
        querystring=urllib.parse.urlencode(options, doseq=True),
    )


@unauthenticated_or_forbidden
def login(feret: "FeretUI", session: Session, options: dict):
    form = options.get('form', session.LoginForm())
    return feret.render_template(session, 'feretui-page-login', form=form)


@unauthenticated_or_forbidden
def page_signup(feret: "FeretUI", session: Session, options: dict):
    return feret.load_page_template(session, 'feretui-page-signup')
