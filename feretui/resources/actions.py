# This file is a part of the FeretUI project
#
#    Copyright (C) 2023-2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""feretui.resources.actions's module.

Declare the actions.

"""

import urllib
from collections.abc import Callable
from typing import TYPE_CHECKING

from markupsafe import Markup
from polib import POFile

from feretui.context import ContextProperties
from feretui.session import Session

if TYPE_CHECKING:
    from feretui.feretui import FeretUI
    from feretui.resources.view import View
    from feretui.translation import Translation


class ActionI18nMixin(ContextProperties):
    """Mixin to declare and get the translation."""

    def get_label(self: "Action") -> str:
        """Return the translated label.

        :return: The label translated in the user lang
        :rtype: str
        """
        return self.feretui.translation.get(
            self.request.session.lang,
            f"{self.context}:label",
            self.label,
        )

    def get_description(self: "Action") -> str:
        """Return the translated description.

        :return: The label translated in the user lang
        :rtype: str
        """
        return self.feretui.translation.get(
            self.request.session.lang,
            f"{self.context}:description",
            self.description,
        )

    def export_catalog(
        self: "Action",
        translation: "Translation",
        po: POFile,
    ) -> None:
        """Export the menu translation in the catalog.

        :param translation: The translation instance to add also inside it.
        :type translation: :class:`.Translation`
        :param po: The catalog instance
        :type po: PoFile_
        """
        po.append(translation.define(f"{self.context}:label", self.label))
        if self.description:
            po.append(
                translation.define(
                    f"{self.context}:description", self.description
                )
            )


class Action(ActionI18nMixin):
    """Action class.

    Define an action in actionset in the view meta.
    """

    template_id: str = "feretui-page-resource-action"

    def __init__(
        self: "Action",
        label: str,
        method: str,
        icon: str = None,
        description: str = None,
        visible_callback: Callable = None,
    ) -> None:
        """Construct the Action class.

        :param label: The label of the menu
        :type label: str
        :param method: The method name to call on the resource
        :type method: str
        :param icon: The icon html class used in the render
        :type icon: str
        :param description: The tooltip, it is a helper to understand the
                            role of the menu
        :type description: str
        :param visible_callback: Callback to determine with the session,
                                 if the menu is visible or not.
        :type visible_callback: Callback[:class:`feretui.session.Session`, bool]
        """
        self.label = label
        self.method = method
        self.icon = icon
        self.description = description
        self.visible_callback = visible_callback

    def get_url(
        self: "Action",
        feretui: "FeretUI",  # noqa: ARG002
        session: Session,  # noqa: ARG002
        options: dict,  # noqa: ARG002
    ) -> str:
        """Return the hx-post url.

        :param feretui: The feretui client instance.
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The session of the user
        :type session: :class:`feretui.session.Session`
        :param options: The querystring
        :type options: dict
        :return: The html
        :rtype: Markup
        """
        return (
            f"{feretui.base_url}/action/resource?"
            f"action=call&method={self.method}"
        )

    def render(
        self: "Action",
        feretui: "FeretUI",
        session: Session,
        options: dict,
        resource_code: str,
        view_code: str,
    ) -> Markup:
        """Return the html of the action.

        :param feretui: The feretui client instance.
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The session of the user
        :type session: :class:`feretui.session.Session`
        :param options: The querystring
        :type options: dict
        :return: The html
        :rtype: Markup
        """
        return Markup(
            feretui.render_template(
                session,
                self.template_id,
                url=self.get_url(feretui, session, options),
                label=self.get_label(),
                description=self.get_description(),
                icon=self.icon,
                rcode=resource_code,
                vcode=view_code,
            )
        )

    def is_visible(
        self: "Action",
        session: Session,  # noqa: ARG002
    ) -> bool:
        """Return True is the action should be displayed.

        :param session: The session of the user
        :type session: :class:`feretui.session.Session`
        :rtype: bool
        """
        return True


class GotoViewAction(Action):
    """Action class.

    Define an action in actionset in the view meta.
    """

    def __init__(
        self: "GotoViewAction",
        label: str,
        view: str,
        icon: str = None,
        description: str = None,
        visible_callback: Callable = None,
    ) -> None:
        """GotoViewAction class.

        :param label: The label of the menu
        :type label: str
        :param view: The view to render
        :type view: str
        :param icon: The icon html class used in the render
        :type icon: str
        :param description: The tooltip, it is a helper to understand the
                            role of the menu
        :type description: str
        :param visible_callback: Callback to determine with the session,
                                 if the menu is visible or not.
        :type visible_callback: Callback[:class:`feretui.session.Session`, bool]
        """
        super().__init__(
            label,
            view,
            icon=icon,
            description=description,
            visible_callback=visible_callback,
        )

    def get_url(
        self: "Action",
        feretui: "FeretUI",  # noqa: ARG002
        session: Session,  # noqa: ARG002
        options: dict,
    ) -> str:
        """Return the hx-post url.

        :param feretui: The feretui client instance.
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The session of the user
        :type session: :class:`feretui.session.Session`
        :param options: The querystring
        :type options: dict
        :return: The html
        :rtype: Markup
        """
        options = options.copy()
        options.update(
            {
                "action": "goto",
                "view": self.method,
            }
        )
        return (
            f"{feretui.base_url}/action/resource?"
            f"{urllib.parse.urlencode(options, doseq=True)}"
        )


class SelectedRowsAction(Action):
    """SelectedRowsAction class.

    This action is not disabled when an entry is selected.
    """

    template_id: str = "feretui-page-resource-action-for-selected-rows"


class Actionset(ActionI18nMixin):
    """Actionset class.

    The Actionset is a set of action with a label.

    This need to group the action in the same place
    """

    def __init__(
        self: "Actionset",
        label: str,
        actions: list[Action],
        icon: str = None,
        description: str = None,
    ) -> None:
        """Actionset constructor.

        :param label: The label of the menu
        :type label: str
        :param actions: The actions in this set
        :type actions: list[Action]
        :param icon: The icon html class used in the render
        :type icon: str
        :param description: The tooltip, it is a helper to understand the
                            role of the menu
        :type description: str
        """
        self.label = label
        self.actions = actions
        self.icon = icon
        self.description = description

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
        super().export_catalog(translation, po)
        for action in self.actions:
            action.export_catalog(translation, po)

    def render(
        self: "Actionset",
        feretui: "FeretUI",
        session: Session,
        options: dict,
        resource_code: str,
        view_code: str,
    ) -> Markup:
        """Return the html of the action.

        :param feretui: The feretui client instance.
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The session of the user
        :type session: :class:`feretui.session.Session`
        :param options: The querystring
        :type options: dict
        :param resource_code: the code of the resource
        :type resource_code: str
        :param view_code: the code of the view
        :type view_code: str
        :return: The html
        :rtype: Markup
        """
        return Markup(
            feretui.render_template(
                session,
                "feretui-page-resource-action-set",
                label=self.get_label(),
                actions=[
                    action.render(
                        feretui,
                        session,
                        options,
                        resource_code,
                        view_code,
                    )
                    for action in self.actions
                    if action.is_visible(session)
                ],
                description=self.description,
            )
        )

    def is_visible(
        self: "Actionset",
        session: Session,
    ) -> bool:
        """Return True is the action should be displayed.

        :param session: The session of the user
        :type session: :class:`feretui.session.Session`
        :rtype: bool
        """
        return all(action.is_visible(session) for action in self.actions)
