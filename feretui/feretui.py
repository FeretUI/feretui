# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Module feretui.feretui.

A FeretUI instance represent one client. Each instance is a specific clent.
Each client are isolated.

::

    from feretui import FeretUI

    myferet = FeretUI()

"""
from feretui.translation import Translation


class FeretUI:
    """Feretui class.

    Attributes
    ----------
    * ...

    """

    # ---------- Translation ----------
    @classmethod
    def export_catalog(
        cls,
        output_path: str,
        version: str,
        addons: str = None
    ) -> None:
        """Export the catalog at the POT format.

        ::

            FeretUI.export_catalog(
                'feretui/locale/feretui.pot', addons='feretui')

        :param output_path: The path where write the catalog
        :type output_path: str
        :param version: The version of the catalog
        :type version: str
        :param addons: The addons where the message come from
        :type addons: str
        """
        Translation.export_catalog(output_path, version, addons=addons)

    @classmethod
    def load_catalog(cls, catalog_path: str, lang: str):
        """Load a specific catalog for a language.

        ::
            FeretUI.load_catalog('feretui/locale/fr.po', 'fr')

        :param catalog_path: Path of the catalog
        :type catalog_path: str
        :param lang: Language code
        :type lang: str
        """
        Translation.load_catalog(catalog_path, lang)
