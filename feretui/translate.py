# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2022 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import inspect
from datetime import datetime
from logging import getLogger
from os import path
from threading import local
from typing import Any

import polib

logger = getLogger(__name__)


class TranslatedMessage:

    def __init__(
        self,
        msg: str,
        module: str,
        addons: str,
    ) -> "TranslatedMessage":
        self.msgid = msg
        self.context = f'message:{module}'

    def __str__(self) -> str:
        lang = Translation.get_lang()
        msg = Translation.get(lang, self.context, self.msgid)
        return msg

    def get(self, **kwargs: dict[str, Any]) -> str:
        return str(self).format(**kwargs)


class TranslatedTemplate:
    def __init__(self, template_path: str, addons: str = 'feretui'):
        self.path = template_path
        self.addons = addons

    def __str__(self):
        return f'<TranslatedTemplate {self.path} addons={self.addons}>'


class TranslatedResource:
    def __init__(self, resource, addons: str):
        self.klass = resource
        self.addons = addons

    def __str__(self):
        return f'<TranslatedResource {self.klass} addons={self.addons}>'


class TranslationLocal(local):
    lang: str = 'en'


class Translation:

    translation: dict = {}
    messages: list[TranslatedMessage] = []
    templates: list[TranslatedTemplate] = []
    resources: list[TranslatedResource] = []
    langs: set = set()
    local = TranslationLocal()  # thread safe

    @classmethod
    def has_lang(cls, lang: str) -> bool:
        return True if lang in cls.langs else False

    @classmethod
    def set_lang(cls, lang: str = 'en'):
        if lang not in cls.langs:
            logger.warning(f"{lang} does not defined in {cls.langs}")

        cls.local.lang = lang

    @classmethod
    def get_lang(cls):
        return cls.local.lang

    @classmethod
    def set(cls, lang: str, poentry: polib.POEntry) -> None:
        cls.langs.add(lang)
        cls.translation[
            (lang, poentry.msgctxt, poentry.msgid)
        ] = poentry.msgstr

    @classmethod
    def get(cls, lang: str, context: str, text: str) -> str:
        res = cls.translation.get((lang, context, text))
        if not res:
            return text

        return res

    @classmethod
    def define(cls, msgctxt: str, msgid: str) -> polib.POEntry:
        logger.debug('msgctxt : %r, msgid: %r', msgctxt, msgid)
        return polib.POEntry(
            msgctxt=msgctxt,
            msgid=msgid,
            msgstr='',
        )

    @classmethod
    def add_translated_message(cls, message: TranslatedMessage):
        Translation.messages.append(message)
        logger.debug(f'Translation : Added new message: {message}')

    @classmethod
    def add_translated_template(cls, template: TranslatedTemplate):
        Translation.templates.append(template)
        logger.debug(f'Translation : Added new template : {template}')

    @classmethod
    def add_translated_resource(cls, resource: TranslatedResource):
        Translation.resources.append(resource)
        logger.debug(f'Translation : Added new resource : {resource}')

    @classmethod
    def export_catalog(cls, output_path: str, addons: str = None):
        from feretui.template import Template

        abspath = path.abspath(output_path)
        dirname = path.dirname(abspath)
        basename = path.basename(abspath)
        po = polib.POFile()
        po.metadata = {
            'Project-Id-Version': '0.0.1',
            'POT-Creation-Date': datetime.now().isoformat(),
            'MIME-Version': '1.0',
            'Content-Type': 'text/plain; charset=utf-8',
            'Content-Transfer-Encoding': '8bit',
        }
        messages = cls.messages
        templates = cls.templates
        resources = cls.resources
        if addons is not None:
            messages = filter(messages, lambda x: x.addons == addons)
            templates = filter(templates, lambda x: x.addons == addons)
            resource = filter(resources, lambda x: x.addons == addons)

        for message in messages:
            entry = cls.define(message.context, message.msgid)
            po.append(entry)

        for resource in resources:
            resource.klass.export_catalog(po)

        tmpls = Template()
        for template in templates:
            with open(template.path, 'r') as fp:
                tmpls.load_file(fp, ignore_missing_extend=True)

        tmpls.export_i18n(po)

        po.save(path.join(dirname, basename))

    @classmethod
    def load_catalog(cls, catalog_path: str, lang: str):
        po = polib.pofile(catalog_path)
        for entry in po:
            cls.set(lang, entry)


def translated_message(msg: str, addons: str = 'feretui') -> TranslatedMessage:
    frm = inspect.stack()[1]
    mod = inspect.getmodule(frm[0])
    tmsg = TranslatedMessage(msg, mod.__name__, addons)
    Translation.add_translated_message(tmsg)
    return tmsg
