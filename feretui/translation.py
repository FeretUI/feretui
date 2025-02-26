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

* :class:`feretui.translation.TranslatedForm`
* :class:`feretui.translation.TranslatedMenu`
* :class:`feretui.translation.TranslatedTemplate`
* :class:`feretui.translation.TranslatedFileTemplate`
* :class:`feretui.translation.TranslatedStringTemplate`
* :class:`feretui.translation.TranslatedResource`

The Translation class have two methods to manipulate the catalogs:

* :meth:`.Translation.export_catalog` : Export the catalog at a path
  for a specific addons
* :meth:`.Translation.load_catalog` : Load catalog for a specific lang


.. _POEntry: https://polib.readthedocs.io/en/latest/api.html#the-poentry-class
"""

from datetime import datetime
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING

from polib import POEntry, POFile, pofile

from feretui.exceptions import (
    TranslationError,
    TranslationFormError,
    TranslationMenuError,
    TranslationResourceError,
)
from feretui.form import FeretUIForm
from feretui.menus import Menu
from feretui.resources.resource import Resource
from feretui.session import Session

if TYPE_CHECKING:
    from feretui.feretui import FeretUI
    from feretui.template import Template

logger = getLogger(__name__)


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
        addons: str = "feretui",
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
        addons: str = "feretui",
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
        addons: str = "feretui",
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
        addons: str = "feretui",
    ) -> "TranslatedMenu":
        """TranslatedMenu class."""
        if not isinstance(menu, Menu):
            raise TranslationMenuError(f"{menu} must be an instance of Menu")

        self.menu: Menu = menu
        self.addons: str = addons

    def __str__(self: "TranslatedMenu") -> str:
        """Return the instance as a string."""
        return f"<TranslatedMenu {self.menu} addons={self.addons}>"

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
        po.append(
            translation.define(f"{self.menu.context}:label", self.menu.label),
        )
        if self.menu.description:
            po.append(
                translation.define(
                    f"{self.menu.context}:description", self.menu.description,
                ),
            )


class TranslatedForm:
    """TranslatedForm class.

    Declare a WTForm as translatable.

    ::

        mytranslatedmenu = TranslatedForm(MyForm, 'my.addons')
        translation.add_translated_form(mytranslation)

    To declare a TranslatedForm more easily, The helpers exist on
    FeretUI :

    * :meth:`feretui.feretui.FeretUI.register_form`.
    * :meth:`feretui.feretui.FeretUI.register_page`.

    Attributes
    ----------
    * [form:FeretUIForm] : the form to translated
    * [addons:str] : the addons of the template file

    :param form: the form class to translate
    :type form: :class:`feretui.form.FeretUIForm`
    :param addons: The addons where the message come from
    :type addons: str

    """

    def __init__(
        self: "TranslatedForm",
        form: FeretUIForm,
        addons: str = "feretui",
    ) -> None:
        """TranslatedForm class."""
        if not issubclass(form, FeretUIForm):
            raise TranslationFormError(f"{form} must be a sub class of FeretUI")

        self.form: FeretUIForm = form
        self.addons: str = addons

    def __str__(self: "TranslatedForm") -> str:
        """Return the instance as a string."""
        return f"<TranslatedForm {self.form} addons={self.addons}>"

    def export_catalog(
        self: "TranslatedForm",
        translation: "Translation",
        po: POFile,
    ) -> None:
        """Export the form translations in the catalog.

        :param translation: The translation instance to add also inside it.
        :type translation: :class:`.Translation`
        :param po: The catalog instance
        :type po: PoFile_
        """
        self.form.export_catalog(translation, po)


class TranslatedResource:
    """TranslatedForm class.

    Declare a resource as translatable.

    ::

        MyResource.build()
        myresource = MyResource('Code', 'The label')
        translation.add_translated_resource(myresource)


    To declare a TranslatedForm more easily, The helpers exist on
    FeretUI :

    * :meth:`feretui.feretui.FeretUI.register_resource`.

    Attributes
    ----------
    * [resource:Resource] : the resource to translated
    * [addons:str] : the addons of the template file

    :param resource: the resource instance to translate
    :type resource: :class:`feretui.resource.Resource`
    :param addons: The addons where the message come from
    :type addons: str

    """

    def __init__(
        self: "TranslatedResource",
        resource: Resource,
        addons: str = "feretui",
    ) -> None:
        """TranslatedForm class."""
        if not isinstance(resource, Resource):
            raise TranslationResourceError(
                f"{resource} must be an instance of Resource",
            )

        self.resource: Resource = resource
        self.addons: str = addons

    def __str__(self: "TranslatedResource") -> str:
        """Return the instance as a string."""
        return f"<TranslatedResource {self.resource} addons={self.addons}>"

    def export_catalog(
        self: "TranslatedResource",
        translation: "Translation",
        po: POFile,
    ) -> None:
        """Export the resource translations in the catalog.

        :param translation: The translation instance to add also inside it.
        :type translation: :class:`.Translation`
        :param po: The catalog instance
        :type po: PoFile_
        """
        self.resource.export_catalog(translation, po)


class Translation:
    """Translation class.

    This class is used to manipulate translation.

    .. warning::

        The behaviour work with thread local
    """

    def __init__(self: "Translation", feretui: "FeretUI") -> "Translation":
        """Instance of the Translation class."""
        self.feretui = feretui
        self.langs: set = set()
        self.translations: dict[tuple[str, str, str], str] = {}
        self.templates: list[TranslatedTemplate] = []
        self.menus: list[TranslatedMenu] = []
        self.forms: list[TranslatedForm] = []
        self.resources: list[TranslatedResource] = []

    def has_lang(self: "Translation", lang: str) -> bool:
        """Return True the lang is declared.

        :param lang: The language tested
        :type lang: str
        :return: The verification
        :rtype: bool
        """
        return lang in self.langs

    def set(self: "Translation", lang: str, poentry: POEntry) -> None:
        """Add a new translation in translations.

        :param lang: The language code
        :type lang: str
        :param poentry: The poentry defined
        :type poentry: POEntry_
        """
        self.langs.add(lang)
        self.translations[(lang, poentry.msgctxt, poentry.msgid)] = (
            poentry.msgstr if poentry.msgstr else poentry.msgid
        )

    def get(
        self: "Translation",
        lang: str,
        context: str,
        message: str,
        message_as_default: bool = True,
    ) -> str:
        """Get the translated message from translations.

        :param lang: The language code
        :type lang: str
        :param context: The context in the catalog
        :type context: str
        :param message: The original message
        :type message: str
        :param message_as_default: If True then when no translation is found
                                   it is return the message else return None
        :type message_as_default: bool
        :return: The translated message
        :rtype: str
        """
        return self.translations.get(
            (lang, context, message),
            message if message_as_default else None,
        )

    def define(self: "Translation", context: str, message: str) -> POEntry:
        """Create a POEntry for a message.

        :param context: The context in the catalog
        :type context: str
        :param message: The original message
        :type message: str
        :return: The poentry
        :rtype: POEntry_
        """
        logger.debug("msgctxt : %r, msgid: %r", context, message)
        return POEntry(
            msgctxt=context,
            msgid=message,
            msgstr="",
        )

    def add_translated_template(
        self: "Translation",
        template: TranslatedTemplate,
    ) -> None:
        """Add in templates a TranslatedTemplate.

        :param template: The template.
        :type template: :class:`TranslatedTemplate`
        """
        self.templates.append(template)
        logger.debug("Translation : Added new template : %s", template)

    def add_translated_menu(
        self: "Translation",
        menu: TranslatedMenu,
    ) -> None:
        """Add in menus a TranslatedMenu.

        :param menu: The menu.
        :type menu: :class:`TranslatedMenu`
        """
        self.menus.append(menu)
        logger.debug("Translation : Added new menu : %s", menu)

    def add_translated_form(
        self: "Translation",
        form: TranslatedForm,
    ) -> None:
        """Add in forms a TranslatedForm.

        :param form: The Form.
        :type form: :class:`.TranslatedForm`
        """
        self.forms.append(form)
        logger.debug("Translation : Added new form : %s", form)

    def add_translated_resource(
        self: "Translation",
        resource: TranslatedResource,
    ) -> None:
        """Add in forms a TranslatedResource.

        :param resource: The resource instance.
        :type resource: :class:`.TranslatedResource`
        """
        self.resources.append(resource)
        logger.debug("Translation : Added new resource : %s", resource)

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
            "Project-Id-Version": version,
            "POT-Creation-Date": datetime.now().isoformat(),
            "MIME-Version": "1.0",
            "Content-Type": "text/plain; charset=utf-8",
            "Content-Transfer-Encoding": "8bit",
        }
        templates = self.templates
        menus = self.menus
        forms = self.forms
        resources = self.resources

        self.add_translated_form(
            TranslatedForm(Session.LoginForm, addons="feretui"),
        )
        self.add_translated_form(
            TranslatedForm(Session.SignUpForm, addons="feretui"),
        )

        if addons is not None:
            templates = filter(lambda x: x.addons == addons, templates)
            menus = filter(lambda x: x.addons == addons, menus)
            forms = filter(lambda x: x.addons == addons, forms)
            resources = filter(lambda x: x.addons == addons, resources)

        for form_translated_message in FeretUIForm.TRANSLATED_MESSAGES:
            po.append(
                self.define(
                    FeretUIForm.get_context(),
                    form_translated_message,
                ),
            )

        tmpls = Template(Translation(self.feretui))
        for template in templates:
            template.load(tmpls)

        tmpls.export_catalog(po)

        for menu in menus:
            menu.export_catalog(self, po)

        for form in forms:
            form.export_catalog(self, po)

        for resource in resources:
            resource.export_catalog(self, po)

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
