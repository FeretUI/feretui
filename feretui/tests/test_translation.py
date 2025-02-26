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
from wtforms import StringField

from feretui.exceptions import (
    TranslationFormError,
    TranslationMenuError,
    TranslationResourceError,
)
from feretui.feretui import FeretUI
from feretui.form import FeretUIForm
from feretui.menus import ToolBarMenu
from feretui.resources.resource import Resource
from feretui.translation import (
    TranslatedFileTemplate,
    TranslatedForm,
    TranslatedMenu,
    TranslatedResource,
    TranslatedStringTemplate,
    TranslatedTemplate,
    Translation,
)


class TestTranslation:
    """Test Translation."""

    def test_translated_template(self) -> None:
        """Test translated_message without feretui."""
        mytranslation = TranslatedTemplate()
        assert str(mytranslation)

    def test_translated_file_template(self) -> None:
        """Test translated_message without feretui."""
        mytranslation = TranslatedFileTemplate('/path/of/template')
        assert str(mytranslation)

    def test_translated_page_template(self) -> None:
        """Test translated_message without feretui."""
        mytranslation = TranslatedStringTemplate('template')
        assert str(mytranslation)

    def test_translated_menu(self) -> None:
        """Test translated_message without feretui."""
        mytranslation = TranslatedMenu(ToolBarMenu('Test', page='test'))
        assert str(mytranslation)

    def test_translated_menu_not_a_menu(self) -> None:
        """Test translated_message without feretui."""
        with pytest.raises(TranslationMenuError):
            TranslatedMenu(None)

    def test_translated_form(self) -> None:
        """Test translated_message without feretui."""
        mytranslation = TranslatedForm(FeretUIForm)
        assert str(mytranslation)

    def test_translated_form_not_a_form(self) -> None:
        """Test translated_message without feretui."""
        class A:
            pass

        with pytest.raises(TranslationFormError):
            TranslatedForm(A)

    def test_translated_resource(self) -> None:
        """Test translated_message without feretui."""
        mytranslation = TranslatedResource(Resource())
        assert str(mytranslation)

    def test_translated_resource_not_a_resource(self) -> None:
        class A:
            pass

        with pytest.raises(TranslationResourceError):
            TranslatedResource(A)

    def test_has_langs(self, feretui) -> None:
        """Test has_lang."""
        translation = Translation(feretui)
        assert translation.has_lang('a_lang') is False
        translation.langs.add('a_lang')
        assert translation.has_lang('a_lang') is True

    def test_export_load_catalog(self) -> None:
        """Test export and Load catalog. from FeretUI."""
        myferet = FeretUI()
        myferet.translation.add_translated_menu(
            TranslatedMenu(
                ToolBarMenu('Test', page='test', description='Test')),
        )
        myferet.translation.add_translated_menu(
            TranslatedMenu(ToolBarMenu('Test', page='test')),
        )
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

        class MyForm(FeretUIForm):
            name = StringField(description='My name')

        myferet.translation.add_translated_form(TranslatedForm(MyForm))

        class MyResource(Resource):
            code = 'test'
            label = 'Test'

        MyResource.build()
        myferet.translation.add_translated_resource(
            TranslatedResource(MyResource()))

        with NamedTemporaryFile() as fpt:
            fpt.write(t1)
            fpt.seek(0)
            myferet.translation.add_translated_template(
                TranslatedFileTemplate(fpt.name, addons='feretui'),
            )
            myferet.translation.add_translated_template(
                TranslatedStringTemplate(t2, addons='feretui'),
            )

            with NamedTemporaryFile() as fp:
                myferet.export_catalog(fp.name, '0.0.1', 'feretui')
                myferet.load_catalog(fp.name, 'fr')

    def test_load_internal_catalog_fr(self) -> None:
        myferet = FeretUI()
        myferet.load_internal_catalog('fr')
        assert myferet.translation.get(
            'fr', "template:feretui-input-label", 'required',
        ) == 'requis'
