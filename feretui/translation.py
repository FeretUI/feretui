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

The Translation class have two methods to manipulate the catalogs:

* :meth:`.Translation.export_catalog` : Export the catalog at a path
  for a specific addons
* :meth:`.Translation.load_catalog` : Load catalog for a specific lang
"""
import inspect
from datetime import datetime
from logging import getLogger
from os import path
from threading import local
from typing import Any

from polib import POEntry, POFile, pofile

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
    """

    def __init__(
        self,
        message: str,
        module: str,
        addons: str,
    ) -> "TranslatedMessage":
        """TranslatedMessage class.

        :param message: the translated string
        :type message: str
        :param module: the module name where the message come from
        :type module: str
        :param addons: The addons where the message come from
        :type addons: str
        """
        self.msgid: str = message
        self.context: str = f'message:{module}'
        self.addons: str = addons

    def __str__(self) -> str:
        """Return the translated message.

        the message depend of the language defined in the Translation class.
        If not language is defined then the raw string is returned.
        """
        lang = Translation.get_lang()
        msg = Translation.get(lang, self.context, self.msgid)
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


class TranslationLocal(local):
    """TranslationLocal class.

    It is a thread safe store point.
    """

    lang: str = 'en'
    """The language code of the thread"""


class Translation:
    """Translation class.

    This class is used to manipulate translation.
    """

    local = TranslationLocal()
    """A thread safe local store. [:class:`.TranslationLocal`]"""

    langs: set = set()
    """Language codes"""

    translations: dict[tuple[str, str, str], str] = {}
    """Local storage of the translation"""

    messages: list[TranslatedMessage] = []
    """Translated messages"""

    @classmethod
    def has_lang(cls, lang: str) -> bool:
        """Return True the lang is declared.

        :param lang: The language tested
        :type lang: str
        :return: The verification
        :rtype: bool
        """
        return lang in cls.langs

    @classmethod
    def set_lang(cls, lang: str = 'en') -> None:
        """Define the lang as the default language of this thread.

        :param lang: [en], The language code
        :type lang: str
        """
        if lang not in cls.langs:
            logger.warning(f"{lang} does not defined in {cls.langs}")

        cls.local.lang = lang

    @classmethod
    def get_lang(cls) -> str:
        """Return the default language code from local thread.

        :return: Language code.
        :rtype: str
        """
        return cls.local.lang

    @classmethod
    def set(cls, lang: str, poentry: POEntry) -> None:
        """Add a new translation in translations.

        :param lang: The language code
        :type lang: str
        :param poentry: The poentry defined
        :type poentry: POEntry
        """
        cls.langs.add(lang)
        cls.translations[
            (lang, poentry.msgctxt, poentry.msgid)
        ] = poentry.msgstr if poentry.msgstr else poentry.msgid

    @classmethod
    def get(cls, lang: str, context: str, message: str) -> str:
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
        return cls.translations.get((lang, context, message), message)

    @classmethod
    def define(cls, context: str, message: str) -> POEntry:
        """Create a POEntry for a message.

        :param context: The context in the catalog
        :type context: str
        :param message: The original message
        :type message: str
        :return: The poentry
        :rtype: POEntry
        """
        logger.debug('msgctxt : %r, msgid: %r', context, message)
        return POEntry(
            msgctxt=context,
            msgid=message,
            msgstr='',
        )

    @classmethod
    def add_translated_message(
        cls, translated_message: TranslatedMessage
    ) -> None:
        """Add in messages a TranslatedMessage.

        :param translated_message: A message.
        :type translated_message: :class:`TranslatedMessage`
        """
        Translation.messages.append(translated_message)
        logger.debug(f'Translation : Added new message: {translated_message}')

    @classmethod
    def export_catalog(
        cls,
        output_path: str,
        version: str,
        addons: str = None,
    ):
        """Export a catalog template.

        :param output_path: The path where write the catalog
        :type output_path: str
        :param version: The version of the catalog
        :type version: str
        :param addons: The addons where the message come from
        :type addons: str
        """
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
        messages = cls.messages
        if addons is not None:
            messages = filter(lambda x: x.addons == addons, messages)

        for message in messages:
            po.append(cls.define(message.context, message.msgid))

        po.save(path.join(dirname, basename))

    @classmethod
    def load_catalog(cls, catalog_path: str, lang: str) -> None:
        """Load a catalog in translations.

        :param catalog_path: Path of the catalog
        :type catalog_path: str
        :param lang: Language code
        :type lang: str
        """
        po = pofile(catalog_path)
        for entry in po:
            cls.set(lang, entry)


def translated_message(
    message: str,
    addons: str = 'feretui'
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
