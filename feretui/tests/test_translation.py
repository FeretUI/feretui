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

from feretui.exceptions import TranslationError
from feretui.feretui import FeretUI
from feretui.thread import local
from feretui.translation import (
    TranslatedPageTemplate,
    TranslatedFileTemplate,
    Translation,
    translated_message,
)


class TestTranslation:
    """Test Translation."""

    def test_translated_message_without_feretui(self):
        """Test translated_message without feretui."""
        local.feretui = None
        mytranslation = translated_message('My translation')
        with pytest.raises(TranslationError):
            str(mytranslation)

    def test_translated_message_without_args(self):
        """Test translated_message without args."""
        myferet = FeretUI()
        local.feretui = myferet

        mytranslation = translated_message('My translation')
        assert str(mytranslation) == "My translation"

    def test_translated_message_with_args(self):
        """Test translated_message without args."""
        myferet = FeretUI()
        local.feretui = myferet

        mytranslation = translated_message('My translation {foo}')
        assert str(mytranslation) == "My translation {foo}"
        assert mytranslation.format(foo='bar') == "My translation bar"

    def test_has_langs(self):
        """Test has_lang."""
        translation = Translation()
        assert translation.has_lang('a_lang') is False
        translation.langs.add('a_lang')
        assert translation.has_lang('a_lang') is True

    def test_lang_setter_and_getter(self):
        """Test setter and getter for the langs."""
        translation = Translation()
        assert translation.get_lang() == 'en'
        translation.set_lang(lang='fr')
        assert translation.get_lang() == 'fr'
        translation.set_lang(lang='en')

    def test_export_load_catalog(self):
        """Test export and Load catalog. from FeretUI."""
        myferet = FeretUI()
        local.feretui = myferet

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
        t2 = b"<template id='test2' extend='test'/>"

        with NamedTemporaryFile() as fpt:
            fpt.write(t1)
            fpt.seek(0)
            myferet.translation.add_translated_template(
                TranslatedFileTemplate(fpt.name, addons='feretui')
            )
            myferet.translation.add_translated_template(
                TranslatedPageTemplate(t2, addons='feretui')
            )

            with NamedTemporaryFile() as fp:
                myferet.export_catalog(fp.name, '0.0.1', 'feretui')
                myferet.load_catalog(fp.name, 'fr')
