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

from polib import POFile

from feretui.exceptions import ViewFormError
from feretui.form import FeretUIForm
from feretui.pages import page_404
from feretui.session import Session

if TYPE_CHECKING:
    from feretui.feretui import FeretUI
    from feretui.resources.resource import Resource
    from feretui.translation import Translation


class ViewForm:
    """View Form for translation."""

    @classmethod
    def get_context(cls: "ViewForm") -> str:
        """Return the context for the translation."""
        if hasattr(cls, 'view'):
            return f'{cls.view.context}:form'

        return ''


class View:
    """View class."""

    code: str = None

    class Form:
        """Form class."""

    def __init__(self: "View", resource: "Resource") -> None:
        """View class.

        :param resource: The resource instance
        :type resource: :class:`feretui.resources.resource.Resource`
        """
        self.resource = resource
        self.context = resource.context + f':view:{self.code}'
        self.form_cls = self.get_form_cls()

    def get_label(self: "View") -> str:
        """Return the translated label."""
        return self.resource.get_label()

    def export_catalog(
        self: "View",
        translation: "Translation",
        po: POFile,
    ) -> None:
        """Export the translations in the catalog.

        :param translation: The translation instance to add also inside it.
        :type translation: :class:`.Translation`
        :param po: The catalog instance
        :type po: PoFile_
        """
        self.form_cls.export_catalog(translation, po)

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

    def get_form_cls(self: "View") -> FeretUIForm:
        """Return the Form for the view."""
        res = type(
            f'Form_{self.resource.code}_{self.code}',
            (self.Form, self.resource.Form, ViewForm, FeretUIForm),
            {'view': self},
        )
        if not hasattr(res, 'pk'):
            raise ViewFormError(f'The form {res} has no pk')

        return res
