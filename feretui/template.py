# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Template behaviours.

The goal of this Templating is to give the templating modulare, overwritable,
translable and cachable without complex behaviours.

The complex behaviours is given by jinja.

Each FeretUI instance have his own instance of Template class. The stored
templates could be deferents.

The templates are declared in file and imported with
:meth:`.Template.load_file`.

::

    <templates>
        <template id="my-template-1">
            <div>My template</div>
        </template>
        <template id="my-template-2">
            <div>My other template</div>
        </template>
    </templates>


It is possible to extend an existing template.

::

    <template extend="my-template>
      <!-- ... -->
    </template>


It is possible to create a new template from an existing template.

::

    <template id="my-new-template" extend="my-template>
      <!-- ... -->
    </template>

To modify a template with extend, use the tags include and xpath.

* include : Include another template at this location

  ::

      <template id="tmpl-a">
        <!-- ... -->
             <include template="tmpl-b"></include>
        <!-- ... -->
      </template>

* xpath insert: Insert in a tag path

  ::

      <template extend="my-template">
        <xpath expression=".//my-tag" type="insert">
          <!-- ... -->
        </xpath>
      </template>

* xpath insertBefore: Insert before the tag path

  ::

      <template extend="my-template">
        <xpath expression=".//my-tag" type="insertBefore">
          <!-- ... -->
        </xpath>
      </template>

* xpath insertAfter: Insert after the tag path

  ::

      <template extend="my-template">
        <xpath expression=".//my-tag" type="insertAfter">
          <!-- ... -->
        </xpath>
      </template>

* xpath replace: Replace the tag path

  ::

      <template extend="my-template">
        <xpath expression=".//my-tag" type="replace">
          <!-- ... -->
        </xpath>
      </template>

* xpath remove: Remove the tag path

  ::

      <template extend="my-template">
        <xpath expression=".//my-tag" type="remove">
        </xpath>
      </template>


For the xpath the expression attribute use
`xpath of lxml <https://lxml.de/xpathxslt.html>`_.

.. warning::

    The parser used to manipulate the html is lxml, the html
    must be parsed. So the jinja command must not break the parser.

.. _HtmlElement: https://lxml.de/api/lxml.html.HtmlElement-class.html
.. _PoFile: https://polib.readthedocs.io/en/latest/api.html#polib.POFile
"""
import re
from collections.abc import Callable
from copy import deepcopy
from logging import getLogger
from typing import IO

from bs4 import BeautifulSoup, UnicodeDammit
from lxml import etree, html
from polib import POFile

from feretui.exceptions import TemplateError
from feretui.translation import Translation

logger = getLogger(__name__)


JINJA_REGEXES = [
    "\{\{ [a-zA-Z0-9_()\.|, ']* \}\}",  # noqa W605
    "\{% set [a-zA-Z0-9_\[\]]* = [a-zA-Z0-9_()\.,']* %\}",  # noqa W605
    "\{% if [a-zA-Z0-9_()\., =<>!'\[\]]* %\}",  # noqa W605
    "\{% elif [a-zA-Z0-9_()\., =<>!'\[\]]* %\}",  # noqa W605
    "\{% else %\}",  # noqa W605
    "\{% endif %\}",  # noqa W605
    "\{% for [a-zA-Z0-9_(), ]* in [a-zA-Z0-9_()\.'\[\]]* recursive %\}",  # noqa W605
    "\{% for [a-zA-Z0-9_(), ]* in [a-zA-Z0-9_()\.'\[\]]* %\}",  # noqa W605
    "\{% endfor %\}",  # noqa W605
]
"""Regex to indicate if the text is a command jinja"""


def decode_html(html_string: str) -> str:
    """Convert html string to html string markup.

    :param html_string: The html to convert
    :type html: str
    :return: The converted html
    :rtype: str[unicode]
    :exception: UnicodeDecodeError
    """
    converted = UnicodeDammit(html_string)
    if not converted.unicode_markup:
        raise UnicodeDecodeError(  # pragma: no cover
            "Failed to detect encoding, tried [%s]",
            ', '.join(converted.tried_encodings))

    return converted.unicode_markup


def _minify_text_and_tail(el: etree.Element) -> None:
    """Minimify the text and the tail of an etree.Element.

    ::

        _minify_text_and_tail(
            etree.fromstring('''
                <div>
                    Minimify
                    <strong> Me </strong>
                    !
                </div>
            )
        ''')
        == Etree.fromstring(
            '<div>Minimify<strong>Me</strong>!</div>'
        )

    :param el: The node to minimify.
    :type el: etree.Element
    """
    for name in ('text', 'tail'):
        text = getattr(el, name)
        if text is None:
            continue

        text = text.strip()
        setattr(el, name, text)


def get_translated_message(text: str | None) -> str | None:
    """Return the text to translate.

    If the text if link with a jinja command or whatever int the
    :func:`.JINJA_REGEXES`.

    :param text: The initiale text or jinja commande
    :type el: str
    :return: The text to translate
    :rtype: str
    """
    if not text:
        return text

    text = text.replace('\n', '').replace('\n', '').strip()
    for regex in JINJA_REGEXES:
        if re.findall(regex, text):
            return None

    return text


class XPathDescription:
    """Xpath description object.

    Attributes
    ----------
    * expression: str, the xpath expression
    * mult: bool, If False, take only the first
    * action: str, The action to do in the xpath
    * elements: list[HtmlElement_], the node in the xpath

    :param expression: the xpath expression
    :type expression: str
    :param mult: If False, take only the first
    :type mult: bool
    :param action: The action to do in the xpath
    :type action: str
    :param elements: the list of the node from the xpath
    :type elements: list[HtmlElement_]

    """

    def __init__(
        self,
        expression: str = None,
        mult: bool = None,
        action: str = None,
        elements: list[html.HtmlElement] = None,
    ):
        """Xpath description object.

        :param expression: the xpath expression
        :type expression: str
        :param mult: If False, take only the first
        :type mult: bool
        :param action: The action to do in the xpath
        :type action: str
        :param elements: the list of the node from the xpath
        :type elements: list[HtmlElement_]
        """
        self.expression: str = expression
        self.mult: bool = mult
        self.action: str = action
        self.elements: list[html.HtmlElement] = elements


class Template:
    """html templating framework, the need is to manipulate web template.

    ::

        tmpl = Template()
        tmpl.load_file(file_pointer_1)
        tmpl.load_file(file_pointer_2)
        tmpl.load_file(file_pointer_3)
        tmpl.load_file(file_pointer_N)
        tmpl.compîle()


    Attributes
    ----------
    * known [dict]:
        internal store of the raw templates and inherits.
    * compiled [dict[lang: dict[id: HtmlElement_]]]:
        The compiled template, ready to use and store by lang.
    * compiled_str [dict[lang: dict[encoding: dict[id: HtmlElement_]]]]:
        The compiled encoded template, ready to use and store by lang.
    * translation [:class:`feretui.translation.Translation`]:
        instance of the translation for this instance of Template

    """

    def __init__(self, translation: Translation):
        """Template class.

        :param translation: instance of the translation mechanism
        :type translation: :class:`feretui.translation.Translation`
        """
        self.compiled: dict = {}
        self.compiled_str: dict = {}
        self.known: dict[str, dict[str, html.HtmlElement]] = {}
        self.translation: Translation = translation

    def get_template(
        self,
        name: str,
        lang: str = 'en',
        tostring: bool = True,
        encoding: str = "unicode",
    ) -> html.HtmlElement | str:
        """Return a specific template.

        :param name: name of the template to export
        :type name: str
        :param lang: [en] The template lang
        :type name: str
        :param tostring: [True] If True the template will be returned as a
                         string.
        :type tostring: bool
        :param encoding: [unicode] The default encoding of the template when
                         **tostring** is True
        :type encoding: str
        :return: The compiled template in the defined **lang**.
        :rtype: HtmlElement_ or str
        """
        if (
            tostring
            and lang in self.compiled_str
            and encoding in self.compiled_str[lang]
            and name in self.compiled_str[lang][encoding]
        ):
            return self.compiled_str[lang][encoding][name]

        if lang not in self.compiled:
            self.compile(lang=lang)

        tmpl = deepcopy(self.compiled[lang][name])[0]

        if tostring:
            tmpl_str = self.tostring(tmpl, encoding)
            compiled_str_lang = self.compiled_str.setdefault(lang, {})
            compiled_str_lang_encoding = compiled_str_lang.setdefault(
                encoding, {})
            compiled_str_lang_encoding[name] = tmpl_str
            return tmpl_str

        return tmpl

    def tostring(
        self,
        template: html.HtmlElement,
        encoding: str,
    ) -> str | bytes:
        """Return the template as a string.

        :param template: The template to convert to string
        :type template: HtmlElement_
        :param encoding: The encoding use for the string
        :type encoding: str
        :return: the template in string mode
        :rtype: bytes or str
        """
        soup = BeautifulSoup(
            etree.tostring(template, encoding=encoding),
            "html.parser",
        )
        return soup.prettify(formatter="html5")

    def load_file(
        self,
        openedfile: IO,
        ignore_missing_extend: bool = False,
    ) -> None:
        """Load a file from the file descriptor.

        File format ::

            <templates>
                <template id="...">
                    ...
                </template>
            </templates>

        :param openedfile: file descriptor
        :type openedfile: typing.IO
        :param ignore_missing_extend: [False] use in the case of the export the
            catalog. If True the missing extends are ignored.
        :type ignore_missing_extend: bool
        :exception: :class:`feretui.exceptions.TemplateError`
        """
        try:
            el = openedfile.read()
            # the operator ?= are cut, then I replace them before
            # to save the operator in get_template
            element = html.fromstring(decode_html(el))
        except Exception:  # pragma: no cover
            logger.error('error durring load of %r', openedfile)
            raise

        if element.tag.lower() == 'template':
            self.load_template(
                element, ignore_missing_extend=ignore_missing_extend)
        elif element.tag.lower() == 'templates':
            for _element in element.getchildren():
                if _element.tag in (etree.Comment, html.HtmlComment):
                    continue
                elif _element.tag.lower() == 'template':
                    self.load_template(
                        _element, ignore_missing_extend=ignore_missing_extend)
                else:
                    raise TemplateError(
                        f"Only 'template' can be loaded not {_element.tag} "
                        f"in the file {openedfile}",
                    )

        else:
            raise TemplateError(
                "Only 'template' or 'templates' can be loaded not "
                f"{element.tag} in the file {openedfile}",
            )

    def load_template(
        self,
        element: html.HtmlElement,
        ignore_missing_extend: bool = False,
    ) -> None:
        """Load one specific template.

        :param element: The element node to load.
        :type element: HtmlElement_
        :param ignore_missing_extend: [False] use in the case of the export the
            catalog. If True the missing extends are ignored.
        :type ignore_missing_extend: bool
        :exception: :class:`feretui.exceptions.TemplateError`
        """
        name = element.attrib.get('id')
        extend = element.attrib.pop('extend', None)
        rewrite = bool(eval(element.attrib.get('rewrite', "False")))

        if name:
            if self.known.get(name) and not rewrite:
                raise TemplateError(f"Alredy existing template {name}")

            self.known[name] = {
                'tmpl': [],
            }

        if extend:
            if name:
                self.known[name]['extend'] = extend
            else:
                if extend not in self.known:
                    if ignore_missing_extend:
                        self.known[extend] = {'tmpl': []}
                    else:
                        raise TemplateError(
                            "Extend an unexisting template "
                            f"{html.tostring(element)}",
                        )

                name = extend

        if not name:
            raise TemplateError(
                "No template id or extend attrinute found %r"
                f"{html.tostring(element)}",
            )

        els = [element] + element.findall('.//*')
        for el in els:
            _minify_text_and_tail(el)

        self.known[name]['tmpl'].append(element)

    def load_template_from_str(self, template: str) -> None:
        """Load a template from string.

        :param template: The template to load.
        :type template: str
        """
        el = html.fromstring(decode_html(template))
        self.load_template(el)

    def get_xpath(self, element: html.HtmlElement) -> list[XPathDescription]:
        """Find and return the xpath found in the template.

        :param element: The root node of the template
        :type element: HtmlElement_
        :return: The xpath nodes description
        :rtype: list[XPathDescription]
        """
        res = []
        for el in element.findall('xpath'):
            res.append(XPathDescription(
                expression=el.attrib.get('expression', '/'),
                mult=bool(eval(el.attrib.get('mult', 'False'))),
                action=el.attrib.get('action', 'insert'),
                elements=el.getchildren(),
            ))

        return res

    def xpath(
        self,
        lang: str,
        name: str,
        expression: str,
        mult: bool,
    ) -> list[html.HtmlElement]:
        """Apply the xpath on template id and get nodes.

        :param lang: lang for the translation
        :type lang: str
        :param name: The id of the template
        :type name: str
        :param expression: xpath regex to find the good node
        :type expression: str
        :param mult: if True the return will take only the first element in
            the list.
        :type mult: bool
        :return: the nodes from xpath expression
        :rtype: list[HtmlElement_]
        """
        tmpl = self.compiled[lang][name]
        if mult:
            return tmpl.findall(expression)
        else:
            return [tmpl.find(expression)]

    def xpath_insertInside(
        self,
        lang: str,
        name: str,
        expression: str,
        mult: bool,
        elements: list[html.HtmlElement],
    ) -> None:
        """Apply a xpath with action="insertInside".

        ::

            <template id="..." extend="other template">
                <xpath expression="..." action="insert">
                    ...
                </xpath>
            </template>

        :param lang: lang for the translation
        :type lang: str
        :param name: The id of the template
        :type name: str
        :param expression: xpath regex to find the good node
        :type expression: str
        :param mult: If true, xpath can apply on all the element found
        :type mult: bool
        :param elements: children of the xpath to insert
        :type elements: list[HtmlElement_]
        """
        els = self.xpath(lang, name, expression, mult)
        for el in els:
            nbchildren = len(el.getchildren())
            for i, subel in enumerate(elements):
                el.insert(i + nbchildren, subel)

    def xpath_insertBefore(
        self,
        lang: str,
        name: str,
        expression: str,
        mult: bool,
        elements: list[html.HtmlElement],
    ) -> None:
        """Apply a xpath with action="insertBefore".

        ::

            <template id="..." extend="other template">
                <xpath expression="..." action="insertBefore">
                    ...
                </xpath>
            </template>

        :param lang: lang for the translation
        :type lang: str
        :param name: The id of the template
        :type name: str
        :param expression: xpath regex to find the good node
        :type expression: str
        :param mult: If true, xpath can apply on all the element found
        :type mult: bool
        :param elements: children of the xpath to insert
        :type elements: list[HtmlElement_]
        """
        els = self.xpath(lang, name, expression, mult)
        parent_els = self.xpath(lang, name, expression + '/..', mult)
        for parent in parent_els:
            for i, cel in enumerate(parent.getchildren()):
                if cel in els:
                    for j, subel in enumerate(elements):
                        parent.insert(i + j, subel)

    def xpath_insertAfter(
        self,
        lang: str,
        name: str,
        expression: str,
        mult: bool,
        elements: list[html.HtmlElement],
    ) -> None:
        """Apply a xpath with action="insertAfter".

        ::

            <template id="..." extend="other template">
                <xpath expression="..." action="insertAfter">
                    ...
                </xpath>
            </template>

        :param lang: lang for the translation
        :type lang: str
        :param name: The id of the template
        :type name: str
        :param expression: xpath regex to find the good node
        :type expression: str
        :param mult: If true, xpath can apply on all the element found
        :type mult: bool
        :param elements: children of the xpath to insert
        :type elements: list[HtmlElement_]
        """
        els = self.xpath(lang, name, expression, mult)
        parent_els = self.xpath(lang, name, expression + '/..', mult)
        for parent in parent_els:
            for i, cel in enumerate(parent.getchildren()):
                if cel in els:
                    for j, subel in enumerate(elements):
                        parent.insert(i + j + 1, subel)

    def xpath_remove(
        self,
        lang: str,
        name: str,
        expression: str,
        mult: bool,
    ) -> None:
        """Apply a xpath with action="remove".

        ::

            <template id="..." extend="other template">
                <xpath expression="..." action="remove"/>
            </template>

        :param lang: lang for the translation
        :type lang: str
        :param name: The id of the template
        :type name: str
        :param expression: xpath regex to find the good node
        :type expression: str
        :param mult: If true, xpath can apply on all the element found
        :type mult: bool
        """
        els = self.xpath(lang, name, expression, mult)
        for el in els:
            el.drop_tree()

    def xpath_replace(
        self,
        lang: str,
        name: str,
        expression: str,
        mult: bool,
        elements: list[html.HtmlElement],
    ) -> None:
        """Apply a xpath with action="replace".

        ::

            <template id="..." extend="other template">
                <xpath expression="..." action="replace">
                    ...
                </xpath>
            </template>

        :param lang: lang for the translation
        :type lang: str
        :param name: The id of the template
        :type name: str
        :param expression: xpath regex to find the good node
        :type expression: str
        :param mult: If true, xpath can apply on all the element found
        :type mult: bool
        :param elements: children of the xpath to insert
        :type elements: list[HtmlElement_]
        """
        els = self.xpath(lang, name, expression, mult)
        parent_els = self.xpath(lang, name, expression + '/..', mult)
        for parent in parent_els:
            for i, cel in enumerate(parent.getchildren()):
                if cel in els:
                    parent.remove(cel)
                    for j, subel in enumerate(elements):
                        parent.insert(i + j, subel)

    def xpath_attributes(
        self,
        lang: str,
        name: str,
        expression: str,
        mult: bool,
        attributes: dict[str, str],
    ) -> None:
        """Apply a xpath with action="attributes".

        ::

            <template id="..." extend="other template">
                <xpath expression="..." action="attributes">
                    <attribute key="value"/>
                    <attribute foo="bar"/>
                </xpath>
            </template>

        :param lang: lang for the translation
        :type lang: str
        :param name: The id of the template
        :type name: str
        :param expression: xpath regex to find the good node
        :type expression: str
        :param mult: If true, xpath can apply on all the element found
        :type mult: bool
        :param attributes: attributes to apply
        :type attributes: dict[str, str]
        """
        els = self.xpath(lang, name, expression, mult)
        for el in els:
            for k, v in attributes.items():
                el.set(k, v)

    def get_xpath_attributes(
        self,
        elements: list[html.HtmlElement],
    ) -> list[dict[str, str]]:
        """Find and return the attibutes in the xpath.

        :param elements: The node where are the attribute node
        :type elements: list[HtmlElement_]
        :return: The list of the attibutes.
        :rtype: list[dict[str, str]]
        :exception: :class:`feretui.exceptions.TemplateError`
        """
        res = []
        for el in elements:
            if el.tag != 'attribute':
                raise TemplateError(
                    "get %r node, waiting 'attribute' node" % el.tag)

            res.append(dict(el.items()))

        return res

    def get_elements(self, lang: str, name: str) -> list[html.HtmlElement]:
        """Return the store templates for one id, and apply *include* on them.

        :param lang: The langage use for the include.
        :type lang: str
        :param name: The id of the template.
        :type name: str
        :return: The list of the templates
        :rtype: list[HtmlElement_]
        """
        elements = [deepcopy(x) for x in self.known[name]['tmpl']]
        for el in elements:
            for el_include in el.findall('.//include'):
                tmpl = self.compile_template(
                    lang, el_include.attrib['template'])
                for index, child in enumerate(tmpl.getchildren()):
                    el_include.insert(index, deepcopy(child))

                el_include.drop_tag()

        return elements

    def apply_xpath(
        self,
        description: XPathDescription,
        lang: str,
        name: str,
    ) -> None:
        """Apply the xpath from XPathDescription.

        :param description: The xpath description
        :type description: :class:`.XPathDescription`
        :param lang: The langage use for the include.
        :type lang: str
        :param name: The id of the template.
        :type name: str
        :exception: :class:`feretui.exceptions.TemplateError`
        """
        action = description.action
        expression = description.expression
        mult = description.mult
        els = description.elements
        if action in (
            'insertInside',
            'insertBefore',
            'insertAfter',
            'replace',
        ):
            getattr(self, f"xpath_{action}")(lang, name, expression, mult, els)
        elif action == 'remove':
            self.xpath_remove(lang, name, expression, mult)
        elif action == 'attributes':
            for attributes in self.get_xpath_attributes(els):
                self.xpath_attributes(
                    lang, name, expression, mult, attributes)
        else:
            raise TemplateError("Unknown action %r" % action)

    def compile_template(self, lang: str, name: str) -> html.HtmlElement:
        """Compile a specific template in function of the lang.

        The compiled template is stored to get it quuickly at the next
        call.

        :param lang: The langage use for the include.
        :type lang: str
        :param name: The id of the template.
        :type name: str
        :return: The compiled template
        :rtype: HtmlElement_
        """
        if lang not in self.compiled:
            self.compiled[lang] = {}

        if name in self.compiled[lang]:
            return self.compiled[lang][name]

        extend = self.known[name].get('extend')
        elements = self.get_elements(lang, name)

        if extend:
            tmpl = deepcopy(self.compile_template(lang, extend))
            tmpl.set('id', name)
        else:
            tmpl = elements[0]
            elements = elements[1:]

        self.compiled[lang][name] = tmpl

        for el in elements:
            for val in self.get_xpath(el):
                self.apply_xpath(val, lang, name)

        def callback(text, suffix=''):
            return self.get_translation(lang, name, text, suffix)

        self.compile_template_i18n(self.compiled[lang][name], callback)
        return self.compiled[lang][name]

    def export_catalog(self, po: POFile) -> None:
        """Export the template translation in the catalog.

        :param po: The catalog from the
            :class:`feretui.translation.Translation`.
        :type po: PoFile_
        """

        def callback(name):
            def _callback(text, suffix=''):
                context = f'template:{name}'
                if suffix:
                    context += ':' + suffix

                entry = self.translation.define(context, text)
                po.append(entry)

            return _callback

        for name in self.known:
            for tmpl in self.known[name]['tmpl']:
                self.compile_template_i18n(tmpl, callback(name))

    def compile_template_i18n(
        self,
        tmpl: html.HtmlElement,
        action_callback: Callable[[str, str], None],
    ) -> None:
        """Compile the translation for a node.

        :param tmpl: The node to translate.
        :type tmpl: HtmlElement_
        :param action_callback: The callback use to translate
            or to store in the catalog
        :type action_callback: Callback[[str, str], None]
        """
        text = get_translated_message(tmpl.text)
        tail = get_translated_message(tmpl.tail)
        if text:
            tmpl.text = action_callback(text)

        if tail:
            tmpl.tail = action_callback(tail)

        for key in (set(tmpl.attrib.keys()).intersection(
            {"label", "hx-confirm"})
        ):
            tmpl.attrib[key] = action_callback(
                tmpl.attrib[key], suffix=f'{tmpl.tag}:{key}')

        for child in tmpl.getchildren():
            self.compile_template_i18n(child, action_callback)

    def get_translation(
        self,
        lang: str,
        name: str,
        text: str,
        suffix: str,
    ) -> str:
        """Get the translation.

        :param lang: The langage use for the include.
        :type lang: str
        :param name: The id of the template.
        :type name: str
        :param text: The default text to translate.
        :type text: str
        :param suffix: suffix to put in the context
        :type suffix: str
        :return: The translated message
        :rtype: str
        """
        context = f'template:{name}'
        if suffix:
            context += ':' + suffix

        return self.translation.get(lang, context, text)

    def compile(self, lang='en') -> None:
        """Compile all the templates for a specific lang.

        :param lang: [en], The langage use for the include.
        :type lang: str
        """
        for tmpl in self.known:
            self.compile_template(lang, tmpl)

    def copy(self) -> "Template":
        """Copy all the known templates."""
        self_copy = Template(Translation())
        for tmpl_name in self.known:
            self_copy.known[tmpl_name] = {
                'tmpl': [x for x in self.known[tmpl_name]['tmpl']],
            }
            if 'extend' in self.known[tmpl_name]:
                self_copy.known[tmpl_name]['extend'] = self.known[tmpl_name][
                    'extend']

        return self_copy
