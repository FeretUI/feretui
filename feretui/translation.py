# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Module feretui.translation.

The translation mechanism is used to translate the user interface.

The translation files is store in po file. To translate the pot in each
language with `PoEdit <https://poedit.net/>`_.

The translated object are:

* :class:`feretui.translation.TranslatedMessage`
* :class:`feretui.translation.TranslatedTemplate`

The Translation class have two methods to manipulate the catalogs:

* :meth:`.Translation.export_catalog` : Export the catalog at a path
  for a specific addons
* :meth:`.Translation.load_catalog` : Load catalog for a specific lang


.. _POEntry: https://polib.readthedocs.io/en/latest/api.html#the-poentry-class
"""
import inspect
from datetime import datetime
from logging import getLogger
from os import path
from typing import Any

from polib import POEntry, POFile, pofile

from feretui.exceptions import TranslationError
from feretui.thread import local

logger = getLogger(__name__)


class TranslatedMessage:
    """TranslatedMessage class.

    Declare a string as translatable. The instance is used to be exported
    or to be translated in the render.

    ::

        mytranslation = TranslatedMessage(
            'My translation', 'my.module', 'my.addons')

        Translation.add_translated_message(mytranslation)

    To declare a TranslatedMessage more easily, a helper exist
    :func:`.translated_message`.

    Attributes
    ----------
    * [msgid:str] : the translated string
    * [context:str] : the context in the catalog
    * [addons:str] : the addons of the message

    :param message: the translated string
    :type message: str
    :param module: the module name where the message come from
    :type module: str
    :param addons: The addons where the message come from
    :type addons: str

    """

    def __init__(
        self,
        message: str,
        module: str,
        addons: str,
    ) -> "TranslatedMessage":
        """TranslatedMessage class."""
        self.msgid: str = message
        self.context: str = f'message:{module}'
        self.addons: str = addons

    def __str__(self) -> str:
        """Return the translated message.

        the message depend of the language defined in the Translation class.
        If not language is defined then the raw string is returned.
        """
        if local.feretui is None:
            raise TranslationError('No feretui instance in local thread')

        translation = local.feretui.translation
        lang = translation.get_lang()
        msg = translation.get(lang, self.context, self.msgid)
        return msg

    def format(self, **kwargs: dict[str, Any]) -> str:
        """Return the translated message with some arguments.

        ::

            mytranslation = TranslatedMessage(
                'My message {foo}',
                'my.module',
                'my.addons',
            )
            mytranslation.format(foo='bar')
        """
        return str(self).format(**kwargs)


class TranslatedTemplate:
    """TranslatedTemplate class.

    Declare a template file as translatable. The instance is used
    to defined the template files where take the entries to export
    in the catalog

    ::

        mytranslation = TranslatedTemplate(
            'path/of/template.tmpl', 'my.addons')

        Translation.add_translated_template(mytranslation)

    To declare a TranslatedTemplate more easily, a helper exist on FeretUI
    :meth:`feretui.feretui.FeretUI.import_templates_file`.

    Attributes
    ----------
    * [path:str] : the template file path
    * [addons:str] : the addons of the template file

    :param template_path: the template file path
    :type template_path: str
    :param addons: The addons where the message come from
    :type addons: str

    """

    def __init__(
        self,
        template_path: str,
        addons: str = 'feretui',
    ) -> "TranslatedTemplate":
        """TranslatedMessage class."""
        self.path: str = template_path
        self.addons: str = addons

    def __str__(self) -> str:
        """Return the instance as a string."""
        return f'<TranslatedTemplate {self.path} addons={self.addons}>'


class Translation:
    """Translation class.

    This class is used to manipulate translation.

    ::

        myferet = FeretUI()
        local.feretui = myferet

        mytranslation = TranslatedMessage('My translation')
        Translation.add_translated_message(mytranslation)

        assert myferet.translation.get_lang() == 'en'
        assert str(mytranslation) == 'My translation'
        myferet.translation.set_lang('fr')
        assert str(mytranslation) == 'Ma traduction'

    .. warning::

        The behaviour work with thread local
    """

    messages: list[TranslatedMessage] = []
    """Translated messages"""

    def __init__(self):
        """Instance of the Translation class."""
        self.langs: set = set()
        self.translations: dict[tuple[str, str, str], str] = {}
        self.templates: list[TranslatedTemplate] = []
        """Translated templates"""

    def has_lang(self, lang: str) -> bool:
        """Return True the lang is declared.

        :param lang: The language tested
        :type lang: str
        :return: The verification
        :rtype: bool
        """
        return lang in self.langs

    def set_lang(self, lang: str = 'en') -> None:
        """Define the lang as the default language of this thread.

        :param lang: [en], The language code
        :type lang: str
        """
        if lang not in self.langs:
            logger.warning(f"{lang} does not defined in {self.langs}")

        local.lang = lang

    def get_lang(self) -> str:
        """Return the default language code from local thread.

        :return: Language code.
        :rtype: str
        """
        return local.lang

    def set(self, lang: str, poentry: POEntry) -> None:
        """Add a new translation in translations.

        :param lang: The language code
        :type lang: str
        :param poentry: The poentry defined
        :type poentry: POEntry_
        """
        self.langs.add(lang)
        self.translations[
            (lang, poentry.msgctxt, poentry.msgid)
        ] = poentry.msgstr if poentry.msgstr else poentry.msgid

    def get(self, lang: str, context: str, message: str) -> str:
        """Get the translated message from translations.

        :param lang: The language code
        :type lang: str
        :param context: The context in the catalog
        :type context: str
        :param message: The original message
        :type message: str
        :return: The translated message
        :rtype: str
        """
        return self.translations.get((lang, context, message), message)

    def define(self, context: str, message: str) -> POEntry:
        """Create a POEntry for a message.

        :param context: The context in the catalog
        :type context: str
        :param message: The original message
        :type message: str
        :return: The poentry
        :rtype: POEntry_
        """
        logger.debug('msgctxt : %r, msgid: %r', context, message)
        return POEntry(
            msgctxt=context,
            msgid=message,
            msgstr='',
        )

    @classmethod
    def add_translated_message(
        cls, translated_message: TranslatedMessage,
    ) -> None:
        """Add in messages a TranslatedMessage.

        :param translated_message: A message.
        :type translated_message: :class:`TranslatedMessage`
        """
        Translation.messages.append(translated_message)
        logger.debug(
            f'Translation : Added new message: {translated_message.msgid}',
        )

    def add_translated_template(self, template: TranslatedTemplate):
        """Add in templates a TranslatedTemplate.

        :param template: The template.
        :type translated_message: :class:`TranslatedMessage`
        """
        self.templates.append(template)
        logger.debug(f'Translation : Added new template : {template}')

    def export_catalog(
        self,
        output_path: str,
        version: str,
        addons: str = None,
    ) -> None:
        """Export a catalog template.

        :param output_path: The path where write the catalog
        :type output_path: str
        :param version: The version of the catalog
        :type version: str
        :param addons: The addons where the message come from
        :type addons: str
        """
        from feretui.template import Template

        abspath = path.abspath(output_path)
        dirname = path.dirname(abspath)
        basename = path.basename(abspath)
        po = POFile()
        po.metadata = {
            'Project-Id-Version': version,
            'POT-Creation-Date': datetime.now().isoformat(),
            'MIME-Version': '1.0',
            'Content-Type': 'text/plain; charset=utf-8',
            'Content-Transfer-Encoding': '8bit',
        }
        messages = Translation.messages
        templates = self.templates
        if addons is not None:
            messages = filter(lambda x: x.addons == addons, messages)
            templates = filter(lambda x: x.addons == addons, templates)

        for message in messages:
            po.append(self.define(message.context, message.msgid))

        tmpls = Template(Translation())
        for template in templates:
            with open(template.path) as fp:
                tmpls.load_file(fp, ignore_missing_extend=True)

        tmpls.export_catalog(po)

        po.save(path.join(dirname, basename))

    def load_catalog(self, catalog_path: str, lang: str) -> None:
        """Load a catalog in translations.

        :param catalog_path: Path of the catalog
        :type catalog_path: str
        :param lang: Language code
        :type lang: str
        """
        po = pofile(catalog_path)
        for entry in po:
            self.set(lang, entry)


def translated_message(
    message: str,
    addons: str = 'feretui',
) -> TranslatedMessage:
    """Help to define TranslatedMessage.

    ::

        mytranslation = translated_message('My Translation')

    :param message: the translated string
    :type message: str
    :param addons: The addons where the message come from
    :type addons: str
    :return: the message
    :rtype: :class:`.TranslatedMessage`
    """
    frm = inspect.stack()[1]
    mod = inspect.getmodule(frm[0])
    translated_message = TranslatedMessage(message, mod.__name__, addons)
    Translation.add_translated_message(translated_message)
    return translated_message
