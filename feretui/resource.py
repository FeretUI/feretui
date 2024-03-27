# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Module feretui.resource.

The resource is a set of View to représente one data.

* :class:`.Resource`

::

    myferet.register_resource(
        'code of the resource',
        'label',
    )
    class MyResource(Resource):
        pass
"""
from collections.abc import Callable
from typing import TYPE_CHECKING

from polib import POFile

if TYPE_CHECKING:
    from feretui.translation import Translation


class Resource:
    """Resource class."""

    def __init__(
        self: "Resource",
        code: str,
        label: str,
        icon: str = None,
        description: str = None,
        visible_callback: Callable = None,
    ) -> None:
        """Resource class.

        :param code: The id of the resource in feretui instance
        :type code: str
        :param label: The main label of the resource
        :type label: str
        :param icon: The icon html class used in the render
        :type icon: str
        :param description: The tooltip, it is a helper to understand the
                            role of the menu
        :type description: str
        :param visible_callback: Callback to determine with the session,
                                 if the menu is visible or not.
        :type visible_callback: Callback[:class:`feretui.session.Session`,
                                bool]
        """
        self.context = f'resource:{code}'
        self.code = code
        self.label = label
        self.icon = icon
        self.description = description
        self.visible_callback = visible_callback

    def __str__(self: "Resource") -> str:
        """Return the resource as a string."""
        return f'<{self.__class__.__name__} code={self.code}>'

    def export_catalog(
        self: "Resource",
        translation: "Translation",
        po: POFile,
    ) -> None:
        """Export the translations in the catalog.

        :param translation: The translation instance to add also inside it.
        :type translation: :class:`.Translation`
        :param po: The catalog instance
        :type po: PoFile_
        """
        po.append(translation.define(f'{self.context}:label', self.label))

    @classmethod
    def build(cls: "Resource") -> None:
        """Build the additional part of the resource."""
