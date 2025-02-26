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
* :func:`.sitepage`.
* :func:`.static_page`.
* :func:`.aside_menu`.
* :func:`.login`.
* :func:`.signup`.
* :func:`.resource_page`.

To protect them in function of the user see:

* :func: `feretui.helper.page_for_authenticated_user_or_goto`
* :func: `feretui.helper.page_for_unauthenticated_user_or_goto`
"""

from collections.abc import Callable
from typing import TYPE_CHECKING

from markupsafe import Markup

from feretui.exceptions import PageError
from feretui.helper import page_for_unauthenticated_user_or_goto
from feretui.session import Session

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
    page = options.get("resource", options.get("page", ""))
    if isinstance(page, list):
        page = page[0]

    return feretui.render_template(session, "feretui-page-404", page=page)


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
    page = options.get("resource", options.get("page", ""))
    if isinstance(page, list):
        page = page[0]

    return feretui.render_template(session, "feretui-page-forbidden", page=page)


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
    return feretui.render_template(session, "feretui-page-homepage")


def sitemap(
    feretui: "FeretUI",
    session: Session,
    options: dict,  # noqa: ARG001
) -> str:
    """Return the sitemap.

    :param feretui: The feretui client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param session: The Session
    :type session: :class:`feretui.session.Session`
    :param options: The options come from the body or the query string
    :type options: dict
    :return: The html page in
    :rtype: str
    """
    menus = feretui.get_site_map_menus()
    return feretui.render_template(
        session,
        "feretui-page-sitemap",
        menus=menus,
    )


def static_page(template_id: str) -> Callable:
    """Return the template linked the template_id.

    :param template_id: The template_id
    :type feretui: :str
    :return: The html page
    :rtype: Callable
    :exception: :class:`feretui.exceptions.PageError`
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
    :exception: :class:`feretui.exceptions.PageError`
    """
    if "aside" not in options:
        raise PageError("The aside parameter is required in the querystring")

    menus = feretui.get_aside_menus(options["aside"][0])
    page = options.get("aside_page", ["homepage"])[0]

    return feretui.render_template(
        session,
        "feretui-page-aside",
        menus=menus,
        page=Markup(feretui.get_page(page)(feretui, session, options)),
    )


@page_for_unauthenticated_user_or_goto("forbidden")
def login(feretui: "FeretUI", session: Session, options: dict) -> str:
    """Return the login form page.

    If the user is already authenticated, the page will be mark
    as forbidden.

    :param feretui: The feretui client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param session: The Session
    :type session: :class:`feretui.session.Session`
    :param options: The options come from the body or the query string
    :type options: dict
    :return: The html page in
    :rtype: str
    """
    form = options.get("form", session.LoginForm())
    error = options.get("error")
    return feretui.render_template(
        session,
        "feretui-page-login",
        form=form,
        error=error,
    )


@page_for_unauthenticated_user_or_goto("forbidden")
def signup(feretui: "FeretUI", session: Session, options: dict) -> str:
    """Return the signup form page.

    If the user is already authenticated, the page will be mark
    as forbidden.

    :param feretui: The feretui client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param session: The Session
    :type session: :class:`feretui.session.Session`
    :param options: The options come from the body or the query string
    :type options: dict
    :return: The html page in
    :rtype: str
    """
    form = options.get("form", session.SignUpForm())
    error = options.get("error")
    return feretui.render_template(
        session,
        "feretui-page-signup",
        form=form,
        error=error,
    )


def resource_page(feretui: "FeretUI", session: Session, options: dict) -> str:
    """Return the resource page.

    :param feretui: The feretui client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param session: The Session
    :type session: :class:`feretui.session.Session`
    :param options: The options come from the body or the query string
    :type options: dict
    :return: The html page in
    :rtype: str
    :exception: :class:`feretui.exceptions.PageError`
    """
    code = options.get("resource")
    if isinstance(code, list):
        code = code[0]

    if not code:
        raise PageError("No resource in the query string")

    resource = feretui.get_resource(code)
    return resource.render(feretui, session, options)
