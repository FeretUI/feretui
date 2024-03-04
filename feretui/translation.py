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
* :class:`feretui.translation.TranslatedFileTemplate`
* :class:`feretui.translation.TranslatedStringTemplate`
* :class:`feretui.translation.TranslatedMenu`

The Translation class have two methods to manipulate the catalogs:

* :meth:`.Translation.export_catalog` : Export the catalog at a path
  for a specific addons
* :meth:`.Translation.load_catalog` : Load catalog for a specific lang


.. _POEntry: https://polib.readthedocs.io/en/latest/api.html#the-poentry-class
"""
import inspect
from datetime import datetime
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING, Any

from polib import POEntry, POFile, pofile

from feretui.exceptions import TranslationError
from feretui.menus import Menu
from feretui.thread import local

if TYPE_CHECKING:
    from feretui.template import Template

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
        self: "TranslatedMessage",
        message: str,
        module: str,
        addons: str,
    ) -> "TranslatedMessage":
        """TranslatedMessage class."""
        self.msgid: str = message
        self.context: str = f'message:{module}'
        self.addons: str = addons

    def __str__(self: "TranslatedMessage") -> str:
        """Return the translated message.

        the message depend of the language defined in the Translation class.
        If not language is defined then the raw string is returned.
        """
        if local.feretui is None:
            raise TranslationError('No feretui instance in local thread')

        translation = local.feretui.translation
        lang = translation.get_lang()
        return translation.get(lang, self.context, self.msgid)

    def format(self: "TranslatedMessage", **kwargs: dict[str, Any]) -> str:
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

    Declare a template. The instance is used to defined the template files
    where take the entries to export in the catalog

    ::

        mytranslation = TranslatedTemplate('my.addons')
        Translation.add_translated_template(mytranslation)

    Attributes
    ----------
    * [addons:str] : the addons of the template file

    :param addons: The addons where the message come from
    :type addons: str

    """

    def __init__(
        self: "TranslatedTemplate",
        addons: str = 'feretui',
    ) -> "TranslatedTemplate":
        """TranslatedMessage class."""
        self.addons: str = addons

    def __str__(self: "TranslatedTemplate") -> str:
        """Return the instance as a string."""
        return (
            f'<{self.__class__.__name__} {getattr(self, "path", "")} '
            f'addons={self.addons}>'
        )

    def load(
        self: "TranslatedFileTemplate",
        template: "Template",  # noqa: ARG002
    ) -> None:  # pragma: no cover
        """Load the template in the template instance.

        :param template: template instance
        :type template: :class:`feretui.template.Template`
        :exceptions: TranslationError
        """
        raise TranslationError("This method must be overwriting")


class TranslatedFileTemplate(TranslatedTemplate):
    """TranslatedFileTemplate class.

    Declare a template file as translatable. The instance is used
    to defined the template files where take the entries to export
    in the catalog

    ::

        mytranslation = TranslatedFileTemplate(
            'path/of/the/teplate',
            'my.addons'
        )

        translation.add_translated_template(mytranslation)

    To declare a TranslatedFileTemplate more easily, a helper exist on
    FeretUI :meth:`feretui.feretui.FeretUI.import_templates_file`.

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
        self: "TranslatedFileTemplate",
        template_path: str,
        addons: str = 'feretui',
    ) -> "TranslatedFileTemplate":
        """TranslatedFileTemplate class."""
        super().__init__(addons=addons)
        self.path: str = template_path

    def load(self: "TranslatedFileTemplate", template: "Template") -> None:
        """Load the template in the template instance.

        :param template: template instance
        :type template: :class:`feretui.template.Template`
        """
        with Path(self.path).open() as fp:
            template.load_file(fp, ignore_missing_extend=True)


class TranslatedStringTemplate(TranslatedTemplate):
    """TranslatedStringTemplate class.

    Declare a template str as translatable. The instance is used
    to defined the template str where take the entries to export
    in the catalog

    ::

        mytranslation = TranslatedStringTemplate(
            '''
              <template id="my-teplate">
                 ...
              </template>
            ''',
            'my.addons'
        )

        translation.add_translated_template(mytranslation)

    To declare a TranslatedStringTemplate more easily, a helper exist on
    FeretUI :meth:`feretui.feretui.FeretUI.register_page`.

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
        self: "TranslatedStringTemplate",
        template: str,
        addons: str = 'feretui',
    ) -> "TranslatedStringTemplate":
        """TranslatedStringTemplate class."""
        super().__init__(addons=addons)
        self.template: str = template

    def load(self: "TranslatedStringTemplate", template: "Template") -> None:
        """Load the template in the template instance.

        :param template: template instance
        :type template: :class:`feretui.template.Template`
        """
        template.load_template_from_str(self.template)


class TranslatedMenu:
    """TranslatedMenu class.

    Declare a menu as translatable. The instance is used
    to defined the menu targeted to be exported in the catalog

    ::

        mytranslatedmenu = TranslatedMenu(mymenu, 'my.addons')
        translation.add_translated_menu(mytranslation)

    To declare a TranslatedMenu more easily, The helpers exist on
    FeretUI :

    * :meth:`feretui.feretui.FeretUI.register_toolbar_left_menus`.
    * :meth:`feretui.feretui.FeretUI.register_toolbar_right_menus`.
    * :meth:`feretui.feretui.FeretUI.register_aside_menus`.

    Attributes
    ----------
    * [menu:Menu] : the menu to translated
    * [addons:str] : the addons of the template file

    :param menu: the menu to translate
    :type menu: :class:`feretui.menus.Menu`
    :param addons: The addons where the message come from
    :type addons: str

    """

    def __init__(
        self: "TranslatedMenu",
        menu: Menu,
        addons: str = 'feretui',
    ) -> "TranslatedMenu":
        """TranslatedMenu class."""
        self.menu: Menu = menu
        self.addons: str = addons

    def __str__(self: "TranslatedTemplate") -> str:
        """Return the instance as a string."""
        return f'<TranslatedMenu {self.menu} addons={self.addons}>'

    def export_catalog(
        self: "TranslatedMenu",
        translation: "Translation",
        po: POFile,
    ) -> None:
        """Export the menu translation in the catalog.

        :param translation: The translation instance to add also inside it.
        :type translation: :class:`.Translation`
        :param po: The catalog instance
        :type po: PoFile_
        """
        po.append(translation.define(
            f'{self.menu.context}:label', self.menu.label))
        if self.menu.tooltip:
            po.append(translation.define(
                f'{self.menu.context}:tooltip', self.menu.tooltip))


class Translation:
    """Translation class.

    This class is used to manipulate translation.

    example with TranslatedMessage::

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

    def __init__(self: "Translation") -> "Translation":
        """Instance of the Translation class."""
        self.langs: set = set()
        self.translations: dict[tuple[str, str, str], str] = {}
        self.templates: list[TranslatedTemplate] = []
        self.menus: list[TranslatedMenu] = []

    def has_lang(self: "Translation", lang: str) -> bool:
        """Return True the lang is declared.

        :param lang: The language tested
        :type lang: str
        :return: The verification
        :rtype: bool
        """
        return lang in self.langs

    def set_lang(self: "Translation", lang: str = 'en') -> None:
        """Define the lang as the default language of this thread.

        :param lang: [en], The language code
        :type lang: str
        """
        if lang not in self.langs:
            logger.warning("%s does not defined in %s", lang, self.langs)

        local.lang = lang

    def get_lang(self: "Translation") -> str:
        """Return the default language code from local thread.

        :return: Language code.
        :rtype: str
        """
        return local.lang

    def set(self: "Translation", lang: str, poentry: POEntry) -> None:
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

    def get(self: "Translation", lang: str, context: str, message: str) -> str:
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

    def define(self: "Translation", context: str, message: str) -> POEntry:
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
        cls: "Translation", translated_message: TranslatedMessage,
    ) -> None:
        """Add in messages a TranslatedMessage.

        :param translated_message: A message.
        :type translated_message: :class:`TranslatedMessage`
        """
        Translation.messages.append(translated_message)
        logger.debug(
            'Translation : Added new message: %s',
            translated_message.msgid,
        )

    def add_translated_template(
        self: "Translation",
        template: TranslatedTemplate,
    ) -> None:
        """Add in templates a TranslatedTemplate.

        :param template: The template.
        :type template: :class:`TranslatedMessage`
        """
        self.templates.append(template)
        logger.debug('Translation : Added new template : %s', template)

    def add_translated_menu(
        self: "Translation",
        menu: TranslatedMenu,
    ) -> None:
        """Add in menus a TranslatedMenu.

        :param menu: The menu.
        :type menu: :class:`TranslatedMenu`
        """
        self.menus.append(menu)
        logger.debug('Translation : Added new menu : %s', menu)

    def export_catalog(
        self: "Translation",
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
        menus = self.menus

        if addons is not None:
            messages = filter(lambda x: x.addons == addons, messages)
            templates = filter(lambda x: x.addons == addons, templates)
            menus = filter(lambda x: x.addons == addons, menus)

        for message in messages:
            po.append(self.define(message.context, message.msgid))

        tmpls = Template(Translation())
        for template in templates:
            template.load(tmpls)

        tmpls.export_catalog(po)

        for menu in menus:
            menu.export_catalog(self, po)

        po.save(Path(output_path).resolve())

    def load_catalog(
        self: "Translation",
        catalog_path: str,
        lang: str,
    ) -> None:
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
