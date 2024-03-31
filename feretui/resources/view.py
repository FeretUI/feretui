# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Module feretui.responses.view.

The main class to construct a view
"""
import urllib
from typing import TYPE_CHECKING

from feretui.pages import page_404
from feretui.session import Session

if TYPE_CHECKING:
    from feretui.feretui import FeretUI
    from feretui.resources.resource import Resource


class View:
    """View class."""

    code: str = None

    def __init__(self: "View", resource: "Resource") -> None:
        """View class.

        :param resource: The resource instance
        :type resource: :class:`feretui.resources.resource.Resource`
        """
        self.resource = resource

    def get_label(self: "View") -> str:
        """Return the translated label."""
        return self.resource.get_label()

    def render(
        self: "View",
        feretui: "FeretUI",
        session: Session,
        options: dict,
    ) -> str:
        """Render the view.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The Session
        :type session: :class:`feretui.session.Session`
        :param options: The options come from the body or the query string
        :type options: dict
        :return: The html page in
        :rtype: str.
        """
        return page_404(feretui, session, options)

    def get_transition_querystring(
        self: "View",
        options: dict,
        **kwargs: dict[str, str],
    ) -> str:
        """Return the query string of a transition.

        :param options: the main query string
        :type options: dict
        :param kwargs: the new entries
        :type kwargs: dict
        :return: The querystring
        :rtype: str
        """
        options = options.copy()
        for key, value in kwargs.items():
            if value is None:
                options.pop(key, None)
            elif isinstance(value, list):
                options[key] = value
            else:
                options[key] = [value]

        return urllib.parse.urlencode(options, doseq=True)
