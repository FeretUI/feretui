# This file is a part of the FeretUI project
#
#    Copyright (C) 2023-2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Unittest.

with pytest.
"""
from tempfile import NamedTemporaryFile

import pytest  # noqa: F401

from feretui.feretui import FeretUI
from feretui.translation import (
    TranslatedTemplate,
    Translation,
    translated_message,
)


class TestTranslation:
    """Test Translation."""

    def test_translated_message_without_args(self):
        """Test translated_message without args."""
        mytranslation = translated_message('My translation')
        assert str(mytranslation) == "My translation"

    def test_translated_message_with_args(self):
        """Test translated_message without args."""
        mytranslation = translated_message('My translation {foo}')
        assert str(mytranslation) == "My translation {foo}"
        assert mytranslation.format(foo='bar') == "My translation bar"

    def test_has_langs(self):
        """Test has_lang."""
        assert Translation.has_lang('a_lang') is False
        Translation.langs.add('a_lang')
        assert Translation.has_lang('a_lang') is True

    def test_lang_setter_and_getter(self):
        """Test setter and getter for the langs."""
        assert Translation.get_lang() == 'en'
        Translation.set_lang(lang='fr')
        assert Translation.get_lang() == 'fr'
        Translation.set_lang(lang='en')

    def test_export_load_catalog(self):
        """Test export and Load catalog. from FeretUI."""
        translated_message('My translation')
        t1 = b"""
            <template id='test'>
                <div>
                    test text
                    <div>{{ test }}</div>
                    test tail
                </div>
                <div label="test label" />
                <div hx-confirm="test hx-confirm" />
            </template>
        """

        with NamedTemporaryFile() as fpt:
            fpt.write(t1)
            fpt.seek(0)
            tt = TranslatedTemplate(fpt.name, addons='feretui')
            Translation.add_translated_template(tt)

            with NamedTemporaryFile() as fp:
                FeretUI.export_catalog(fp.name, '0.0.1', 'feretui')
                FeretUI.load_catalog(fp.name, 'fr')
