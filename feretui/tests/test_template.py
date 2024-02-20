# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Unittest for templating."""
from io import StringIO

import pytest
from lxml import html

from feretui.exceptions import TemplateError
from feretui.template import Template
from feretui.translation import Translation


class TestTemplate:
    """TestTemplate."""

    @pytest.fixture(autouse=True)
    def init_template(self, request):
        """Fixture to get an empty Template instance."""
        self.Template = Template(Translation())

    def format_element(self, element):
        """Convert string."""
        return self.Template.tostring(element, "unicode")

    def test_load_file(self):
        """Test load a file."""
        f = StringIO()
        t1 = """<template id='test'><a><b1/><b2/></a></template>"""
        f.write(t1)
        f.seek(0)
        self.Template.load_file(f)
        assert (
            self.format_element(self.Template.known['test']['tmpl'][0]) ==
            '<template id="test">\n'
            ' <a>\n'
            '  <b1>\n'
            '  </b1>\n'
            '  <b2>\n'
            '  </b2>\n'
            ' </a>\n'
            '</template>\n'
        )

    def test_load_file_2(self):
        """Test load a file with comment."""
        f = StringIO()
        t1 = (
            "<templates><!-- a comment --><template id='test'><a><b1/><b2/>"
            "</a></template></templates>"
        )
        f.write(t1)
        f.seek(0)
        self.Template.load_file(f)
        assert (
            self.format_element(self.Template.known['test']['tmpl'][0]) ==
            '<template id="test">\n'
            ' <a>\n'
            '  <b1>\n'
            '  </b1>\n'
            '  <b2>\n'
            '  </b2>\n'
            ' </a>\n'
            '</template>\n'
        )

    def test_load_file_3(self):
        """Test load a file with wrong tag."""
        f = StringIO()
        t1 = "<templates><div/></templates>"
        f.write(t1)
        f.seek(0)
        with pytest.raises(TemplateError):
            self.Template.load_file(f)

    def test_load_file_4(self):
        """Test load a file with wrong root tag."""
        f = StringIO()
        t1 = "<div/>"
        f.write(t1)
        f.seek(0)
        with pytest.raises(TemplateError):
            self.Template.load_file(f)

    def test_template_from_str(self):
        """Test load a template in string mode."""
        t1 = """<template id='test'><a><b1/><b2/></a></template>"""
        self.Template.load_template_from_str(t1)
        assert (
            self.format_element(self.Template.known['test']['tmpl'][0]) ==
            '<template id="test">\n'
            ' <a>\n'
            '  <b1>\n'
            '  </b1>\n'
            '  <b2>\n'
            '  </b2>\n'
            ' </a>\n'
            '</template>\n'
        )

    def test_load_template(self):
        """Test load a template in etree.Element node."""
        et = html.fromstring(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.load_template(et)
        assert (
            self.format_element(self.Template.known['test']['tmpl'][0]) ==
            '<template id="test">\n'
            ' <a>\n'
            '  <b1>\n'
            '  </b1>\n'
            '  <b2>\n'
            '  </b2>\n'
            ' </a>\n'
            '</template>\n'
        )

    def test_load_template_without_id_and_without_extend(self):
        """Test load a template without id or extend."""
        et = html.fromstring(
            '<template><a><b1/><b2/></a></template>')
        with pytest.raises(TemplateError):
            self.Template.load_template(et)

    def test_load_template_for_extend(self):
        """Test load a template with extend."""
        et = html.fromstring(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.load_template(et)
        et = html.fromstring("""
            <template extend="test">
                <xpath expression="//b2" action="insertAfter">
                    <b3/>
                </xpath>
            </template>""")
        self.Template.load_template(et)
        assert len(self.Template.known['test']['tmpl']) == 2

    def test_load_template_for_extend_ignore_missing(self):
        """Test load a template with extend and ignore missing."""
        et = html.fromstring(
            '<template extend="missing"><a><b1/><b2/></a></template>')
        self.Template.load_template(et, ignore_missing_extend=True)
        assert len(self.Template.known['missing']['tmpl']) == 1

    def test_load_template_for_extend_unexisting_template(self):
        """Test load a template with extend a missing template id."""
        et = html.fromstring("""
            <template extend="test">
                <xpath expression="//b2" action="insertAfter">
                    <b3/>
                </xpath>
            </template>""")
        with pytest.raises(TemplateError):
            self.Template.load_template(et)

    def test_load_template_for_replace_existing_template_ko(self):
        """Test load a template for replace it without extend."""
        et = html.fromstring(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.load_template(et)
        et = html.fromstring(
            '<template id="test"><a><c1/><c2/></a></template>')
        with pytest.raises(TemplateError):
            self.Template.load_template(et)

    def test_load_template_for_replace_existing_template_ok(self):
        """Test force load a template for replace it without extend."""
        et = html.fromstring(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.load_template(et)
        et = html.fromstring(
            '<template id="test" rewrite="1"><a><c1/><c2/></a></template>')
        self.Template.load_template(et)
        assert (
            self.format_element(self.Template.known['test']['tmpl'][0]) ==
            (
                '<template id="test" rewrite="1">\n'
                ' <a>\n'
                '  <c1>\n'
                '  </c1>\n'
                '  <c2>\n'
                '  </c2>\n'
                ' </a>\n'
                '</template>\n'
            )
        )

    def test_get_xpath(self):
        """Test get xpath."""
        et = html.fromstring("""
            <template>
                <xpath expression="//a1" action="replace"><b/></xpath>
                <xpath expression="//a2" action="insertBefore"><c/></xpath>
                <xpath expression="//a3" action="insertAfter"><d/></xpath>
            </template>""")
        xpaths = self.Template.get_xpath(et)
        assert len(xpaths) == 3

        def check_xpath(xpath, result):
            assert xpath.expression == result['expression']
            assert xpath.action == result['action']
            els = [html.tostring(el) for el in xpath.elements]
            assert els == result['elements']

        check_xpath(xpaths[0], {'expression': '//a1',
                                'action': 'replace',
                                'elements': [b'<b></b>']})
        check_xpath(xpaths[1], {'expression': '//a2',
                                'action': 'insertBefore',
                                'elements': [b'<c></c>']})
        check_xpath(xpaths[2], {'expression': '//a3',
                                'action': 'insertAfter',
                                'elements': [b'<d></d>']})

    def test_xpath_insertBefore(self):
        """Test xpath insertBefore."""
        self.Template.compiled['en'] = {}
        self.Template.compiled['en']['test'] = html.fromstring(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.xpath_insert_before(
            'en', 'test', './/b1', True, [html.fromstring('<b0/>')])
        assert (
            self.format_element(self.Template.compiled['en']['test']) ==
            (
                '<template id="test">\n'
                ' <a>\n'
                '  <b0>\n'
                '  </b0>\n'
                '  <b1>\n'
                '  </b1>\n'
                '  <b2>\n'
                '  </b2>\n'
                ' </a>\n'
                '</template>\n'
            )
        )

    def test_xpath_insertBefore2(self):
        """Test xpath insertBefore from tag xpath."""
        self.Template.load_template_from_str(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.load_template_from_str(
            '<template extend="test">'
            '<xpath expression=".//b1" action="insertBefore"><b0/></xpath>'
            '</template>'
        )
        self.Template.compile()
        assert (
            self.format_element(self.Template.compiled['en']['test']) ==
            (
                '<template id="test">\n'
                ' <a>\n'
                '  <b0>\n'
                '  </b0>\n'
                '  <b1>\n'
                '  </b1>\n'
                '  <b2>\n'
                '  </b2>\n'
                ' </a>\n'
                '</template>\n'
            )
        )

    def test_xpath_insertAfter(self):
        """Test xpath insertAfter."""
        self.Template.compiled['en'] = {}
        self.Template.compiled['en']['test'] = html.fromstring(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.xpath_insert_after(
            'en', 'test', './/b2', True, [html.fromstring('<b3/>')])
        assert (
            self.format_element(self.Template.compiled['en']['test']) ==
            (
                '<template id="test">\n'
                ' <a>\n'
                '  <b1>\n'
                '  </b1>\n'
                '  <b2>\n'
                '  </b2>\n'
                '  <b3>\n'
                '  </b3>\n'
                ' </a>\n'
                '</template>\n'
            )
        )

    def test_xpath_insertAfter2(self):
        """Test xpath insertAfter from tag xpath."""
        self.Template.load_template_from_str(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.load_template_from_str(
            '<template extend="test">'
            '<xpath expression=".//b2" action="insertAfter"><b3/></xpath>'
            '</template>'
        )
        self.Template.compile()
        assert (
            self.format_element(self.Template.compiled['en']['test']) ==
            (
                '<template id="test">\n'
                ' <a>\n'
                '  <b1>\n'
                '  </b1>\n'
                '  <b2>\n'
                '  </b2>\n'
                '  <b3>\n'
                '  </b3>\n'
                ' </a>\n'
                '</template>\n'
            )
        )

    def test_xpath_insert(self):
        """Test xpath insert."""
        self.Template.compiled['en'] = {}
        self.Template.compiled['en']['test'] = html.fromstring(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.xpath_insert_inside(
            'en', 'test', './/b2', True, [html.fromstring('<c/>')])
        assert (
            self.format_element(self.Template.compiled['en']['test']) ==
            (
                '<template id="test">\n'
                ' <a>\n'
                '  <b1>\n'
                '  </b1>\n'
                '  <b2>\n'
                '   <c>\n'
                '   </c>\n'
                '  </b2>\n'
                ' </a>\n'
                '</template>\n'
            )
        )

    def test_xpath_replace(self):
        """Test xpath replace."""
        self.Template.compiled['en'] = {}
        self.Template.compiled['en']['test'] = html.fromstring(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.xpath_replace(
            'en', 'test', './/b2', True, [html.fromstring('<c/>')])
        assert (
            self.format_element(self.Template.compiled['en']['test']) ==
            '<template id="test">\n'
            ' <a>\n'
            '  <b1>\n'
            '  </b1>\n'
            '  <c>\n'
            '  </c>\n'
            ' </a>\n'
            '</template>\n'
        )

    def test_xpath_replace2(self):
        """Test xpath replace from xpath tag."""
        self.Template.load_template_from_str(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.load_template_from_str(
            '<template extend="test">'
            '<xpath expression=".//b2" action="replace"><c/></xpath>'
            '</template>'
        )
        self.Template.compile()
        assert (
            self.format_element(self.Template.compiled['en']['test']) ==
            '<template id="test">\n'
            ' <a>\n'
            '  <b1>\n'
            '  </b1>\n'
            '  <c>\n'
            '  </c>\n'
            ' </a>\n'
            '</template>\n'
        )

    def test_xpath_remove(self):
        """Test xpath remove."""
        self.Template.compiled['en'] = {}
        self.Template.compiled['en']['test'] = html.fromstring(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.xpath_remove('en', 'test', './/b2', True)
        assert (
            self.format_element(self.Template.compiled['en']['test']) ==
            '<template id="test">\n'
            ' <a>\n'
            '  <b1>\n'
            '  </b1>\n'
            ' </a>\n'
            '</template>\n'
        )

    def test_xpath_remove2(self):
        """Test xpath remove from xpath tag."""
        self.Template.load_template_from_str(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.load_template_from_str(
            '<template extend="test">'
            '<xpath expression=".//b2" action="remove" />'
            '</template>'
        )
        self.Template.compile()
        assert (
            self.format_element(self.Template.compiled['en']['test']) ==
            '<template id="test">\n'
            ' <a>\n'
            '  <b1>\n'
            '  </b1>\n'
            ' </a>\n'
            '</template>\n'
        )

    def test_get_xpath_attributes(self):
        """Test xpath attributes."""
        ets = [
            html.fromstring("""<attribute name="test" test="name"/>"""),
            html.fromstring("""<attribute a="b" c="d"/>"""),
        ]
        attributes = self.Template.get_xpath_attributes(ets)
        assert len(attributes) == 2

        assert attributes[0] == {'name': 'test', 'test': 'name'}
        assert attributes[1] == {'a': 'b', 'c': 'd'}

    def test_xpath_attributes(self):
        """Test xpath attributes."""
        self.Template.compiled['en'] = {}
        self.Template.compiled['en']['test'] = html.fromstring(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.xpath_attributes(
            'en', 'test', './/b2', True, {'name': "test"})
        assert (
            self.format_element(self.Template.compiled['en']['test']) ==
            (
                '<template id="test">\n'
                ' <a>\n'
                '  <b1>\n'
                '  </b1>\n'
                '  <b2 name="test">\n'
                '  </b2>\n'
                ' </a>\n'
                '</template>\n'
            )
        )

    def test_xpath_attributes2(self):
        """Test xpath attributes from template."""
        self.Template.load_template_from_str(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.load_template_from_str(
            '<template extend="test">'
            '<xpath expression=".//b2" action="attributes" >'
            '<attribute name="test" />'
            '</xpath>'
            '</template>'
        )
        self.Template.compile()
        assert (
            self.format_element(self.Template.compiled['en']['test']) ==
            (
                '<template id="test">\n'
                ' <a>\n'
                '  <b1>\n'
                '  </b1>\n'
                '  <b2 name="test">\n'
                '  </b2>\n'
                ' </a>\n'
                '</template>\n'
            )
        )

    def test_xpath_attributes3(self):
        """Test xpath attributes with wrong tag."""
        self.Template.load_template_from_str(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.load_template_from_str(
            '<template extend="test">'
            '<xpath expression=".//b2" action="attributes" >'
            '<other name="test" />'
            '</xpath>'
            '</template>'
        )
        with pytest.raises(TemplateError):
            self.Template.compile()

    def test_xpath_other(self):
        """Test xpath with wrong tag."""
        self.Template.load_template_from_str(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.load_template_from_str(
            '<template extend="test">'
            '<xpath expression=".//b2" action="other" />'
            '</template>'
        )
        with pytest.raises(TemplateError):
            self.Template.compile()

    def test_include(self):
        """Test with include tag."""
        self.Template.load_template_from_str(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.load_template_from_str(
            '<template id="test2">'
            '<c><include template="test"/></c>'
            '</template>'
        )
        self.Template.compile()
        assert (
            self.format_element(self.Template.compiled['en']['test']) ==
            '<template id="test">\n'
            ' <a>\n'
            '  <b1>\n'
            '  </b1>\n'
            '  <b2>\n'
            '  </b2>\n'
            ' </a>\n'
            '</template>\n'
        )
        assert (
            self.format_element(self.Template.compiled['en']['test2']) ==
            '<template id="test2">\n'
            ' <c>\n'
            '  <a>\n'
            '   <b1>\n'
            '   </b1>\n'
            '   <b2>\n'
            '   </b2>\n'
            '  </a>\n'
            ' </c>\n'
            '</template>\n'
        )

    def test_get_template(self):
        """Test get template."""
        template = '<a><b1></b1><b2></b2></a>'
        self.Template.known = {
            'test': {'encoding': 'unicode'},
        }
        self.Template.compiled['en'] = {}
        self.Template.compiled['en']['test'] = html.fromstring(
            f'<template>{template}</template>')
        assert (
            self.Template.get_template('test') ==
            '<a>\n'
            ' <b1>\n'
            ' </b1>\n'
            ' <b2>\n'
            ' </b2>\n'
            '</a>\n'
        )
        assert self.Template.compiled_str["en"]["unicode"]["test"]
        assert (
            self.Template.get_template('test') ==
            '<a>\n'
            ' <b1>\n'
            ' </b1>\n'
            ' <b2>\n'
            ' </b2>\n'
            '</a>\n'
        )

    def test_get_template_with_translation(self):
        """Test get template with translation."""
        template = '<template id="test"><b1 label="test">test</b1></template>'
        self.Template.load_template_from_str(template)
        assert (
            self.Template.get_template('test') ==
            '<b1 label="test">\n'
            ' test\n'
            '</b1>\n'
        )

    def test_get_template_tostring_is_False(self):
        """Test get template with tostring is False."""
        template = '<a><b1></b1><b2></b2></a>'
        self.Template.compiled['en'] = {}
        self.Template.compiled['en']['test'] = html.fromstring(template)
        assert self.Template.get_template('test', tostring=False) is not None

    def test_compile_the_same_template(self):
        """Test compile the template in two id."""
        et = html.fromstring(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.load_template(et)
        et = html.fromstring("""
            <template extend="test">
                <xpath expression='.//b1' action="insertInside"><c/></xpath>
            </template>""")
        self.Template.load_template(et)
        self.Template.compile()
        assert (
            self.format_element(self.Template.compiled['en']['test']) ==
            '<template id="test">\n'
            ' <a>\n'
            '  <b1>\n'
            '   <c>\n'
            '   </c>\n'
            '  </b1>\n'
            '  <b2>\n'
            '  </b2>\n'
            ' </a>\n'
            '</template>\n'
        )

    def test_compile_with_extend_another_template(self):
        """Test compile the template with extend."""
        et = html.fromstring(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.load_template(et)
        et = html.fromstring("""
            <template extend="test" id="test2">
                <xpath expression='.//b1' action="insertInside"><c/></xpath>
            </template>""")
        self.Template.load_template(et)
        self.Template.compile()
        assert (
            self.format_element(self.Template.compiled['en']['test']) ==
            '<template id="test">\n'
            ' <a>\n'
            '  <b1>\n'
            '  </b1>\n'
            '  <b2>\n'
            '  </b2>\n'
            ' </a>\n'
            '</template>\n'
        )
        assert (
            self.format_element(self.Template.compiled['en']['test2']) ==
            '<template id="test2">\n'
            ' <a>\n'
            '  <b1>\n'
            '   <c>\n'
            '   </c>\n'
            '  </b1>\n'
            '  <b2>\n'
            '  </b2>\n'
            ' </a>\n'
            '</template>\n'
        )

    def test_compile_the_same_template_and_extend_it(self):
        """Test compile the template with extend."""
        et = html.fromstring(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.load_template(et)
        et = html.fromstring("""
            <template extend="test" id="test2">
                <xpath expression='.//b1' action="insertInside"><c/></xpath>
            </template>""")
        self.Template.load_template(et)
        et = html.fromstring("""
            <template extend="test">
                <xpath expression='.//b2' action="insertInside"><c/></xpath>
            </template>""")
        self.Template.load_template(et)
        self.Template.compile()
        assert (
            self.format_element(self.Template.compiled['en']['test']) ==
            '<template id="test">\n'
            ' <a>\n'
            '  <b1>\n'
            '  </b1>\n'
            '  <b2>\n'
            '   <c>\n'
            '   </c>\n'
            '  </b2>\n'
            ' </a>\n'
            '</template>\n'
        )
        assert (
            self.format_element(self.Template.compiled['en']['test2']) ==
            (
                '<template id="test2">\n'
                ' <a>\n'
                '  <b1>\n'
                '   <c>\n'
                '   </c>\n'
                '  </b1>\n'
                '  <b2>\n'
                '   <c>\n'
                '   </c>\n'
                '  </b2>\n'
                ' </a>\n'
                '</template>\n'
            )
        )

    def test_html_attribute(self):
        """Test keep the html attribute."""
        et = html.fromstring(
            '<template id="test" test><a><b1/><b2/></a></template>')
        self.Template.load_template(et)
        assert (
            self.format_element(self.Template.known['test']['tmpl'][0]) ==
            '<template id="test" test>\n'
            ' <a>\n'
            '  <b1>\n'
            '  </b1>\n'
            '  <b2>\n'
            '  </b2>\n'
            ' </a>\n'
            '</template>\n'
        )

    def test_html_no_ending_tag(self):
        """Test with not ending tag."""
        et = html.fromstring(
            '<template id="test"><a><b1></a></template>')
        self.Template.load_template(et)
        assert (
            self.format_element(self.Template.known['test']['tmpl'][0]) == (
                '<template id="test">\n'
                ' <a>\n'
                '  <b1>\n'
                '  </b1>\n'
                ' </a>\n'
                '</template>\n'
            )
        )

    def test_copy(self):
        """Test copy."""
        et = html.fromstring(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.load_template(et)
        et = html.fromstring("""
            <template id="test2" extend="test">
                <xpath expression='.//b1' action="insertInside"><c/></xpath>
            </template>""")
        self.Template.load_template(et)
        template2 = self.Template.copy()
        self.Template.compile()
        template2.compile()
        assert (
            self.format_element(self.Template.compiled['en']['test']) ==
            self.format_element(template2.compiled['en']['test'])
        )
        assert (
            self.format_element(self.Template.compiled['en']['test2']) ==
            self.format_element(template2.compiled['en']['test2'])
        )
