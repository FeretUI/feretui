# This file is a part of the FeretUI project
#
#    Copyright (C) 2023-2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from pathlib import Path

import pytest
from multidict import MultiDict
from wtforms import BooleanField, RadioField, SelectField, StringField
from wtforms.validators import InputRequired, Length, ValidationError

import feretui as fui
from feretui.form import (
    FeretUIForm,
    HiddenField,
    Many2ManyField,
    Many2OneField,
    One2ManyField,
    Password,
    get_field_translations,
    no_wrap,
    onchange,
    wrap_hidden,
    wrap_many2many,
    wrap_many2one,
    wrap_one2many,
)


class TestForm:

    def test_form(self, feretui, frequest) -> None:

        class MyForm(FeretUIForm):
            name = StringField()

        myform = MyForm(MultiDict(name='test'))
        assert myform.validate() is True

    def test_form_render_field(self, snapshot, feretui, frequest) -> None:

        class MyForm(FeretUIForm):
            name = StringField()

        myform = MyForm()
        snapshot.assert_match(
            myform.name(),
            'snapshot.html',
        )

    def test_form_render_field_translation(
        self, snapshot, feretui, session, frequest,
    ) -> None:
        session.lang = 'fr'

        class MyForm(FeretUIForm):
            name = StringField()

        feretui.translation.translations[(
            'fr',
            f'form:{MyForm.__module__}:{MyForm.__name__}:field:name:label',
            'Name',
        )] = 'Nom'
        myform = MyForm()
        snapshot.assert_match(
            myform.name(),
            'snapshot.html',
        )

    def test_form_render_field_render_kw(
        self, snapshot, feretui, frequest,
    ) -> None:

        class MyForm(FeretUIForm):
            name = StringField(render_kw={'foo': 'bar'})

        myform = MyForm()
        snapshot.assert_match(
            myform.name(),
            'snapshot.html',
        )

    def test_form_render_field_with_errors(
        self, snapshot, feretui, frequest,
    ) -> None:

        class MyForm(FeretUIForm):
            name = StringField(validators=[InputRequired()])

        myform = MyForm()
        myform.validate()
        snapshot.assert_match(
            myform.name(),
            'snapshot.html',
        )

    def test_form_render_field_required(
        self, snapshot, feretui, frequest,
    ) -> None:

        class MyForm(FeretUIForm):
            name = StringField(validators=[InputRequired()])

        myform = MyForm(MultiDict(name='test'))
        myform.validate()
        snapshot.assert_match(
            myform.name(),
            'snapshot.html',
        )

    def test_form_render_field_readonly(
        self, snapshot, feretui, frequest,
    ) -> None:

        class MyForm(FeretUIForm):
            name = StringField(validators=[InputRequired()])

        myform = MyForm(MultiDict(name='test'))
        myform.validate()
        snapshot.assert_match(
            myform.name(readonly=True),
            'snapshot.html',
        )

    def test_form_render_field_no_label(
        self, snapshot, feretui, frequest,
    ) -> None:

        class MyForm(FeretUIForm):
            name = StringField(validators=[InputRequired()])

        myform = MyForm(MultiDict(name='test'))
        myform.validate()
        snapshot.assert_match(
            myform.name(nolabel=True),
            'snapshot.html',
        )

    def test_get_field_choices_readonly(
        self,
        snapshot,
        feretui,
        frequest,
    ) -> None:

        class MyForm(FeretUIForm):
            name = SelectField(choices={'foo': 'Foo', 'bar': 'Bar'})

        myform = MyForm(MultiDict(name='foo'))
        myform.validate()
        snapshot.assert_match(
            myform.name(readonly=True),
            'snapshot.html',
        )

    def test_get_field_choices_readonly_2(
        self,
        snapshot,
        feretui,
        frequest,
    ) -> None:

        class MyForm(FeretUIForm):
            name = SelectField(choices={'foo': 'Foo', 'bar': 'Bar'})

        myform = MyForm()
        myform.validate()
        snapshot.assert_match(
            myform.name(readonly=True),
            'snapshot.html',
        )

    def test_get_field_choices_no_label(
        self,
        snapshot,
        feretui,
        frequest,
    ) -> None:

        class MyForm(FeretUIForm):
            name = SelectField(choices={'foo': 'Foo', 'bar': 'Bar'})

        myform = MyForm(MultiDict(name='foo'))
        myform.validate()
        snapshot.assert_match(
            myform.name(nolabel=True),
            'snapshot.html',
        )

    def test_get_field_choices_no_label_2(
        self,
        snapshot,
        feretui,
        frequest,
    ) -> None:

        class MyForm(FeretUIForm):
            name = SelectField(choices={'foo': 'Foo', 'bar': 'Bar'})

        myform = MyForm()
        myform.validate()
        snapshot.assert_match(
            myform.name(nolabel=True),
            'snapshot.html',
        )

    def test_form_render_field_password(
        self, snapshot, feretui, session, frequest,
    ) -> None:
        path = Path(fui.__file__).parent
        path = path / 'locale' / 'fr.po'
        feretui.load_catalog(path, 'fr')

        session.lang = 'fr'

        class MyForm(FeretUIForm):
            password = StringField(validators=[Password()])

        myform = MyForm()
        myform.validate()
        snapshot.assert_match(
            myform.password(),
            'snapshot.html',
        )

    def test_form_render_field_length_1(
        self, snapshot, feretui, frequest,
    ) -> None:

        class MyForm(FeretUIForm):
            name = StringField(validators=[Length(max=1)])

        myform = MyForm(MultiDict(name='test'))
        myform.validate()
        snapshot.assert_match(
            myform.name(),
            'snapshot.html',
        )

    def test_form_render_field_length_2(
        self, snapshot, feretui, frequest,
    ) -> None:

        class MyForm(FeretUIForm):
            name = StringField(validators=[Length(max=0)])

        myform = MyForm(MultiDict(name='test'))
        myform.validate()
        snapshot.assert_match(
            myform.name(),
            'snapshot.html',
        )

    def test_form_render_bool(
        self, snapshot, feretui, frequest,
    ) -> None:

        class MyForm(FeretUIForm):
            test = BooleanField()

        myform = MyForm()
        snapshot.assert_match(
            myform.test(),
            'snapshot.html',
        )

    def test_form_render_bool_readonly(
        self, snapshot, feretui, frequest,
    ) -> None:

        class MyForm(FeretUIForm):
            test = BooleanField()

        myform = MyForm()
        snapshot.assert_match(
            myform.test(readonly=True),
            'snapshot.html',
        )

    def test_form_render_bool_no_label(
        self, snapshot, feretui, frequest,
    ) -> None:

        class MyForm(FeretUIForm):
            test = BooleanField()

        myform = MyForm()
        snapshot.assert_match(
            myform.test(nolabel=True),
            'snapshot.html',
        )

    def test_form_render_bool_description(
        self, snapshot, feretui, frequest,
    ) -> None:

        class MyForm(FeretUIForm):
            test = BooleanField(description="Test")

        myform = MyForm()
        snapshot.assert_match(
            myform.test(),
            'snapshot.html',
        )

    def test_form_render_radio(self, snapshot, feretui, frequest) -> None:

        class MyForm(FeretUIForm):
            test = RadioField(choices=[('foo', 'Foo'), ('bar', 'Bar')])

        myform = MyForm()
        snapshot.assert_match(
            myform.test(),
            'snapshot.html',
        )

    def test_form_render_radio_readonly(
        self, snapshot, feretui, frequest,
    ) -> None:

        class MyForm(FeretUIForm):
            test = RadioField(choices=[('foo', 'Foo'), ('bar', 'Bar')])

        myform = MyForm()
        snapshot.assert_match(
            myform.test(readonly=True),
            'snapshot.html',
        )

    def test_form_render_radio_readonly_2(
        self, snapshot, feretui, frequest,
    ) -> None:

        class MyForm(FeretUIForm):
            test = RadioField(choices=[('foo', 'Foo'), ('bar', 'Bar')])

        myform = MyForm(MultiDict(test='foo'))
        snapshot.assert_match(
            myform.test(readonly=True),
            'snapshot.html',
        )

    def test_form_render_radio_no_label(
        self, snapshot, feretui, frequest,
    ) -> None:

        class MyForm(FeretUIForm):
            test = RadioField(choices=[('foo', 'Foo'), ('bar', 'Bar')])

        myform = MyForm()
        snapshot.assert_match(
            myform.test(nolabel=True),
            'snapshot.html',
        )

    def test_form_render_radio_nolabel_2(
        self, snapshot, feretui, frequest,
    ) -> None:

        class MyForm(FeretUIForm):
            test = RadioField(choices=[('foo', 'Foo'), ('bar', 'Bar')])

        myform = MyForm(MultiDict(test='foo'))
        snapshot.assert_match(
            myform.test(nolabel=True),
            'snapshot.html',
        )

    def test_form_render_radio_required(
        self, snapshot, feretui, frequest,
    ) -> None:

        class MyForm(FeretUIForm):
            test = RadioField(
                choices=[('foo', 'Foo'), ('bar', 'Bar')],
                validators=[InputRequired()])

        myform = MyForm()
        snapshot.assert_match(
            myform.test(),
            'snapshot.html',
        )

    def test_form_render_radio_description(
        self, snapshot, feretui, frequest,
    ) -> None:

        class MyForm(FeretUIForm):
            test = RadioField(
                choices=[('foo', 'Foo'), ('bar', 'Bar')], description="Test")

        myform = MyForm()
        snapshot.assert_match(
            myform.test(),
            'snapshot.html',
        )

    def test_form_render_radio_honrizontal(
        self, snapshot, feretui, frequest,
    ) -> None:

        class MyForm(FeretUIForm):
            test = RadioField(
                choices=[('foo', 'Foo'), ('bar', 'Bar')],
                render_kw={'vertical': False},
            )

        myform = MyForm()
        snapshot.assert_match(
            myform.test(),
            'snapshot.html',
        )

    def test_no_wrap(self, snapshot, feretui, session, frequest) -> None:

        class MyForm(FeretUIForm):
            test = StringField()

        form = MyForm()
        assert no_wrap(feretui, session, form.test) == (
            '<input id="test" name="test" type="text" value="">'
        )

    def test_add_translation(self) -> None:
        FeretUIForm.register_translation('One test')

    def test_password_validator(self, feretui) -> None:
        validator = Password()

        class MyForm(FeretUIForm):
            password = StringField()

        myform = MyForm(MultiDict(password='test'))
        with pytest.raises(ValidationError):
            validator(myform, myform.password)

    def test_password_validator_2(self, feretui, frequest) -> None:
        validator = Password(
            max_size=14,
            has_lowercase=False,
            has_uppercase=False,
            has_letters=False,
            has_digits=False,
            has_symbols=False,
            has_spaces=True,
        )

        class MyForm(FeretUIForm):
            password = StringField()

        myform = MyForm(MultiDict(password='test'))
        with pytest.raises(ValidationError):
            validator(myform, myform.password)

    def test_get_field_translation_label_1(self) -> None:

        calls = []

        def callback(f, label, context) -> None:
            calls.append((context, label))

        get_field_translations(
            FeretUIForm,
            StringField('Bar'),
            {'name': 'foo'},
            callback,
        )
        assert calls == [
            (':field:foo:label', 'Bar'),
        ]

    def test_get_field_translation_label_2(self) -> None:

        calls = []

        def callback(f, label, context) -> None:
            calls.append((context, label))

        get_field_translations(
            FeretUIForm,
            StringField(label='Bar'),
            {'name': 'foo'},
            callback,
        )
        assert calls == [
            (':field:foo:label', 'Bar'),
        ]

    def test_get_field_translation_description(self) -> None:

        calls = []

        def callback(f, label, context) -> None:
            calls.append((context, label))

        get_field_translations(
            FeretUIForm,
            StringField(description="Bar"),
            {'name': 'foo'},
            callback,
        )
        assert calls == [
            (':field:foo:label', 'Foo'), (':field:foo:description', 'Bar'),
        ]

    def test_get_field_translation_choices_1(self) -> None:

        calls = []

        def callback(f, label, context) -> None:
            calls.append((context, label))

        def choices():
            return {
                'foo': 'Foo',
                'bar': 'Bar',
            }

        get_field_translations(
            FeretUIForm,
            SelectField(choices=choices),
            {'name': 'foo'},
            callback,
        )
        assert calls == [
            (':field:foo:label', 'Foo'),
            (':field:foo:choice:foo:label', 'Foo'),
            (':field:foo:choice:bar:label', 'Bar'),
        ]

    def test_get_field_translation_choices_2(self) -> None:

        calls = []

        def callback(f, label, context) -> None:
            calls.append((context, label))

        def choices():
            return {
                'foo': 'Foo',
                'bar': 'Bar',
            }

        get_field_translations(
            FeretUIForm,
            RadioField(choices=[
                ('foo', 'Foo', {'description': 'Description of foo'}),
                ('bar', 'Bar', {'description': 'Description of bar'}),
            ]),
            {'name': 'foo'},
            callback,
        )
        assert calls == [
            (':field:foo:label', 'Foo'),
            (':field:foo:choice:foo:label', 'Foo'),
            (':field:foo:choice:foo:description', 'Description of foo'),
            (':field:foo:choice:bar:label', 'Bar'),
            (':field:foo:choice:bar:description', 'Description of bar'),
        ]

    def test_onchange_handlers(self) -> None:
        class CartForm(FeretUIForm):
            price = StringField()
            qty = StringField()
            total = StringField()

            @onchange("price", "qty")
            def _calc_total(self) -> None:
                p = int(self.price.data or 0)
                q = int(self.qty.data or 0)
                self.total.data = str(p * q)

        assert CartForm.has_onchange() is True
        handlers = CartForm.get_onchange_handlers()
        assert "price" in handlers
        assert "qty" in handlers
        assert "total" not in handlers

    def test_has_onchange_empty(self) -> None:
        class SimpleForm(FeretUIForm):
            name = StringField()

        assert SimpleForm.has_onchange() is False
        assert SimpleForm.get_onchange_handlers() == {}

    def test_process_onchange(self, feretui, frequest) -> None:
        class CartForm(FeretUIForm):
            price = StringField()
            qty = StringField()
            total = StringField()

            @onchange("price", "qty")
            def _calc_total(self) -> None:
                p = int(self.price.data or 0)
                q = int(self.qty.data or 0)
                self.total.data = str(p * q)

        form = CartForm(MultiDict(price="10", qty="3"))
        modified = form.process_onchange("qty")
        assert modified == ["total"]
        assert form.total.data == "30"

        # Field with no handlers returns empty list
        assert form.process_onchange("unrelated") == []

    def test_onchange_render_attributes(self, feretui, frequest) -> None:
        class CartForm(FeretUIForm):
            price = StringField()
            qty = StringField()
            total = StringField()

            @onchange("price")
            def _calc(self) -> None:
                pass

        form = CartForm()
        price_html = form.price()
        assert 'hx-post="/feretui/action/resource?action=onchange&amp;field=price"' in price_html
        assert 'id="field-price-wrapper"' in price_html
        assert 'id="field-total-wrapper"' in form.total()

    def test_onchange_wrappers_bool_radio_fieldset(
        self,
        feretui,
        frequest,
    ) -> None:
        from wtforms import BooleanField, FormField, RadioField

        from feretui.form import wrap_bool, wrap_fieldset, wrap_radio

        class SubForm(FeretUIForm):
            item = StringField()

        class ComplexForm(FeretUIForm):
            agree = BooleanField()
            choice = RadioField(choices=[("a", "A"), ("b", "B")])
            sub = FormField(SubForm)

            @onchange("agree")
            def _change_agree(self) -> None:
                pass

        form = ComplexForm()
        # Test wrap_bool with wrapper_id and oob
        b_html = wrap_bool(
            feretui,
            frequest.session,
            form.agree,
            wrapper_id="wrap-agree",
            oob=True,
        )
        assert 'id="wrap-agree"' in b_html
        assert 'hx-swap-oob="true"' in b_html

        # Test wrap_radio with wrapper_id and oob
        r_html = wrap_radio(
            feretui,
            frequest.session,
            form.choice,
            wrapper_id="wrap-choice",
            oob=False,
        )
        assert 'id="wrap-choice"' in r_html
        assert 'hx-swap-oob="true"' not in r_html

        # Test wrap_fieldset with wrapper_id and oob
        f_html = wrap_fieldset(
            feretui,
            frequest.session,
            form.sub,
            wrapper_id="wrap-sub",
            oob=True,
        )
        assert 'id="wrap-sub"' in f_html
        assert 'hx-swap-oob="true"' in f_html

    def test_hidden_field(self, feretui, frequest) -> None:
        """Test HiddenField and wrap_hidden without extra wrappers."""
        class HiddenForm(FeretUIForm):
            pk = HiddenField("ID")

        form = HiddenForm(MultiDict(pk="123"))
        html = form.pk()
        assert 'type="hidden"' in html
        assert 'value="123"' in html
        assert "<label" not in html

        direct_html = wrap_hidden(feretui, frequest.session, form.pk)
        assert 'type="hidden"' in direct_html

    def test_many2one_field(self, feretui, frequest) -> None:
        """Test Many2OneField in read and edit modes with choices and links."""
        class PartnerForm(FeretUIForm):
            partner_id = Many2OneField(
                "Partner",
                resource="partners",
                choices=[("1", "Alice"), ("2", "Bob")],
            )

        # Read mode with value
        form = PartnerForm(MultiDict(partner_id="1"))
        read_html = form.partner_id(readonly=True)
        assert "Alice" in read_html
        assert 'class="feretui-many2one-link"' in read_html
        assert "/?page=resource&amp;resource=partners&amp;view=read&amp;pk=1" in read_html
        assert "/feretui/action/goto?page=resource&amp;resource=partners&amp;view=read&amp;pk=1" in read_html
        assert 'hx-target="#feretui-body"' in read_html

        # Read mode without value
        empty_form = PartnerForm()
        empty_html = empty_form.partner_id(readonly=True)
        assert "feretui-many2one-empty" in empty_html
        assert "-" in empty_html

        # Edit mode with value
        edit_html = form.partner_id(readonly=False)
        assert "<select" in edit_html
        assert 'value="1"' in edit_html
        assert "Alice" in edit_html
        assert 'hx-target="#feretui-body"' in edit_html

        # Direct wrap_many2one without wrapper_id
        direct_html = wrap_many2one(feretui, frequest.session, form.partner_id)
        assert "feretui-many2one-wrapper" in direct_html
        assert "id=" not in direct_html or "wrap-" not in direct_html

        # Direct wrap_many2one with wrapper_id and oob
        oob_html = wrap_many2one(
            feretui,
            frequest.session,
            form.partner_id,
            wrapper_id="wrap-partner",
            oob=True,
        )
        assert 'id="wrap-partner"' in oob_html
        assert 'hx-swap-oob="true"' in oob_html

    def test_one2many_field(self, feretui, frequest) -> None:
        """Test One2ManyField process_data and rendering with dict and object rows."""
        class OrderForm(FeretUIForm):
            lines = One2ManyField(
                "Lines",
                columns=[("name", "Product"), ("qty", "Qty")],
                target_resource="products",
            )

        form = OrderForm()
        # Test process_data variations
        form.lines.process_data(None)
        assert form.lines.data == []

        form.lines.process_data([{"id": 1, "name": "Item A", "qty": 2}])
        assert len(form.lines.data) == 1

        form.lines.process_data(( {"id": 2, "name": "Item B", "qty": 3}, ))
        assert len(form.lines.data) == 1
        assert isinstance(form.lines.data, list)

        form.lines.process_data(999)  # Non-iterable fallback
        assert form.lines.data == []

        # Render with dict data
        form.lines.process_data([{"id": 10, "name": "Desk", "qty": 1}])
        dict_html = form.lines()
        assert "feretui-one2many-table" in dict_html
        assert "Desk" in dict_html
        assert "/?page=resource&amp;resource=products&amp;view=read&amp;pk=10" in dict_html
        assert "/feretui/action/goto?page=resource&amp;resource=products&amp;view=read&amp;pk=10" in dict_html
        assert "/?page=resource&amp;resource=products&amp;view=update&amp;pk=10" in dict_html
        assert "/?page=resource&amp;resource=products&amp;view=delete&amp;pk=10" in dict_html
        assert "/?page=resource&amp;resource=products&amp;view=create" in dict_html
        assert 'hx-target="#feretui-body"' in dict_html

        # Test flags can_create=False, can_edit=False, can_delete=False
        class RestrictedForm(FeretUIForm):
            lines = One2ManyField(
                "Lines",
                columns=[("name", "Product")],
                target_resource="products",
                can_create=False,
                can_edit=False,
                can_delete=False,
            )

        r_form = RestrictedForm()
        r_form.lines.process_data([{"id": 10, "name": "Desk"}])
        r_html = r_form.lines()
        assert "/?page=resource&amp;resource=products&amp;view=create" not in r_html
        assert "/?page=resource&amp;resource=products&amp;view=update&amp;pk=10" not in r_html
        assert "/?page=resource&amp;resource=products&amp;view=delete&amp;pk=10" not in r_html
        assert "/?page=resource&amp;resource=products&amp;view=read&amp;pk=10" in r_html

        # Test without target_resource: inline removal button
        class LocalForm(FeretUIForm):
            items = One2ManyField(
                "Local Items",
                columns=[("name", "Item")],
            )

        l_form = LocalForm()
        l_form.items.process_data([{"name": "Local Row"}])
        l_html = l_form.items()
        assert "this.closest('tr').remove()" in l_html

        # Render with object data
        class LineObj:
            id = 20
            name = "Chair"
            qty = 4

        form.lines.process_data([LineObj()])
        obj_html = form.lines()
        assert "Chair" in obj_html
        assert "/?page=resource&amp;resource=products&amp;view=read&amp;pk=20" in obj_html

        # Direct wrap_one2many without wrapper_id
        direct_html = wrap_one2many(feretui, frequest.session, form.lines)
        assert "feretui-one2many-wrapper" in direct_html

        # Direct wrap_one2many with wrapper_id and oob
        oob_html = wrap_one2many(
            feretui,
            frequest.session,
            form.lines,
            wrapper_id="wrap-lines",
            oob=True,
        )
        assert 'id="wrap-lines"' in oob_html
        assert 'hx-swap-oob="true"' in oob_html

    def test_many2many_field(self, feretui, frequest) -> None:
        """Test Many2ManyField process_data and rendering with dict and object rows."""
        class TaggedForm(FeretUIForm):
            tags = Many2ManyField(
                "Tags",
                columns=[("name", "Tag Name")],
                target_resource="tags",
            )

        form = TaggedForm()
        form.tags.process_data([{"id": 1, "name": "Python"}])
        html = form.tags()
        assert "feretui-one2many-table" in html
        assert "Python" in html
        assert "/?page=resource&amp;resource=tags&amp;view=read&amp;pk=1" in html
        assert "/feretui/action/goto?page=resource&amp;resource=tags&amp;view=read&amp;pk=1" in html
        assert 'hx-target="#feretui-body"' in html

        direct_html = wrap_many2many(feretui, frequest.session, form.tags)
        assert "feretui-one2many-wrapper" in direct_html

    def test_gettext_no_context(self) -> None:
        """Test gettext fallback when feretui or request context is missing."""
        from feretui.context import cvar_feretui
        from feretui.form import FeretUIForm, gettext

        class SimpleForm(FeretUIForm):
            pass

        token = cvar_feretui.set(None)
        try:
            assert gettext(SimpleForm, "Untranslated text") == "Untranslated text"
        finally:
            cvar_feretui.reset(token)

    def test_file_field(self, feretui, frequest) -> None:
        """Test FileField processing and rendering."""
        from feretui.form import FileField, FeretUIForm, wrap_file

        class DocumentForm(FeretUIForm):
            doc = FileField("Document", allowed_extensions=["pdf", "docx"], max_size=1024)

        form = DocumentForm()
        # Empty
        assert form.doc.data is None
        html_empty = form.doc()
        assert 'type="file"' in html_empty

        # Formdata processing
        form.doc.process_formdata(["invoice.pdf"])
        assert form.doc.data == "invoice.pdf"
        html_filled = form.doc()
        assert "invoice.pdf" in html_filled
        assert "Current file:" in html_filled

        # Readonly rendering with string data
        html_ro = form.doc(readonly=True)
        assert 'type="file"' not in html_ro
        assert "invoice.pdf" in html_ro

        # Readonly with object having filename
        class FileObj:
            filename = "report.docx"

        form.doc.data = FileObj()
        html_obj = form.doc(readonly=True)
        assert "report.docx" in html_obj

        # Readonly with dict having filename
        form.doc.data = {"filename": "sheet.xlsx"}
        html_dict = form.doc(readonly=True)
        assert "sheet.xlsx" in html_dict

        # Readonly with no file
        form.doc.data = None
        html_none = form.doc(readonly=True)
        assert "No file" in html_none

        # Empty formdata
        form.doc.process_formdata([])
        assert form.doc.data is None

        # Direct wrap with wrapper_id and oob
        wrapped = wrap_file(
            feretui,
            frequest.session,
            form.doc,
            wrapper_id="doc-wrap",
            oob=True,
        )
        assert 'id="doc-wrap"' in wrapped
        assert 'hx-swap-oob="true"' in wrapped

    def test_multi_file_field(self, feretui, frequest) -> None:
        """Test MultiFileField processing and rendering."""
        from feretui.form import MultiFileField, FeretUIForm, wrap_multi_file

        class AttachmentForm(FeretUIForm):
            files = MultiFileField("Attachments")

        form = AttachmentForm()
        assert form.files.data == []

        # Process formdata
        form.files.process_formdata(["f1.pdf", "f2.png"])
        assert form.files.data == ["f1.pdf", "f2.png"]
        html_rendered = form.files()
        assert "f1.pdf, f2.png" in html_rendered

        # Readonly with dict and object items
        class CustomFile:
            filename = "contract.pdf"

        form.files.data = ["plain.txt", CustomFile(), {"filename": "archive.zip"}]
        html_ro = form.files(readonly=True)
        assert "plain.txt, contract.pdf, archive.zip" in html_ro

        # Single item fallback
        form.files.data = "single.pdf"
        html_single = form.files(readonly=True)
        assert "single.pdf" in html_single

        # Empty formdata
        form.files.process_formdata([])
        assert form.files.data == []

        # Process data branches
        form.files.process_data(None)
        assert form.files.data == []
        form.files.process_data(["doc.pdf"])
        assert form.files.data == ["doc.pdf"]
        form.files.process_data(("doc2.pdf",))
        assert form.files.data == ["doc2.pdf"]
        form.files.process_data("doc3.pdf")
        assert form.files.data == ["doc3.pdf"]

        # Direct wrap with wrapper_id and oob
        wrapped = wrap_multi_file(
            feretui,
            frequest.session,
            form.files,
            wrapper_id="multi-wrap",
            oob=True,
        )
        assert 'id="multi-wrap"' in wrapped

    def test_image_field(self, feretui, frequest) -> None:
        """Test ImageField rendering with preview and avatar mode."""
        from feretui.form import ImageField, FeretUIForm, wrap_image

        class ProfileForm(FeretUIForm):
            avatar = ImageField("Avatar", is_avatar=True)
            photo = ImageField("Photo", is_avatar=False)

        form = ProfileForm()
        # Empty avatar
        html_avatar_empty = form.avatar()
        assert "feretui-avatar" in html_avatar_empty
        assert "ti-photo" in html_avatar_empty

        # Filled with URL string
        form.photo.data = "/static/uploads/photo.jpg"
        html_photo = form.photo()
        assert "/static/uploads/photo.jpg" in html_photo
        assert "<img" in html_photo
        assert 'src="/static/uploads/photo.jpg"' in html_photo

        # Readonly mode
        html_photo_ro = form.photo(readonly=True)
        assert 'type="file"' not in html_photo_ro
        assert "/static/uploads/photo.jpg" in html_photo_ro

        # Dict with url / filename
        form.photo.data = {"url": "/images/logo.png"}
        html_dict = form.photo()
        assert "/images/logo.png" in html_dict

        # Object with filename
        class ImgObj:
            filename = "/images/portrait.png"

        form.photo.data = ImgObj()
        html_obj = form.photo()
        assert "/images/portrait.png" in html_obj

        # Direct wrap with wrapper_id and oob
        wrapped = wrap_image(
            feretui,
            frequest.session,
            form.photo,
            wrapper_id="photo-wrap",
            oob=True,
        )
        assert 'id="photo-wrap"' in wrapped
        assert 'hx-swap-oob="true"' in wrapped

    def test_monetary_field(self, feretui, frequest) -> None:
        """Test MonetaryField rendering and formatting."""
        from decimal import Decimal
        from feretui.form import MonetaryField, FeretUIForm, wrap_monetary

        class PricingForm(FeretUIForm):
            price_eur = MonetaryField("Price EUR", currency="€", currency_position="after")
            price_usd = MonetaryField("Price USD", currency="$", currency_position="before")

        form = PricingForm()
        # Empty
        html_eur = form.price_eur()
        assert "feretui-monetary" in html_eur
        assert "€" in html_eur

        # EUR with float value
        form.price_eur.data = 1250.5
        html_eur_filled = form.price_eur()
        assert "feretui-monetary" in html_eur_filled

        # EUR readonly
        html_eur_ro = form.price_eur(readonly=True)
        assert "1250.50 €" in html_eur_ro

        # USD before position filled and readonly
        form.price_usd.data = Decimal("99.99")
        html_usd = form.price_usd()
        assert "$" in html_usd
        html_usd_ro = form.price_usd(readonly=True)
        assert "$ 99.99" in html_usd_ro

        # Invalid float fallback
        form.price_eur.data = "invalid-amount"
        assert form.price_eur._value() == "invalid-amount"
        html_inv_ro = form.price_eur(readonly=True)
        assert "invalid-amount" in html_inv_ro

        # raw_data and None data coverage
        form.price_eur.raw_data = ["42.50"]
        assert form.price_eur._value() == "42.50"
        form.price_eur.raw_data = None
        form.price_eur.data = None
        assert form.price_eur._value() == ""

        # Direct wrap with wrapper_id and oob
        wrapped = wrap_monetary(
            feretui,
            frequest.session,
            form.price_eur,
            wrapper_id="eur-wrap",
            oob=True,
        )
        assert 'id="eur-wrap"' in wrapped

    def test_tags_field(self, feretui, frequest) -> None:
        """Test TagsField parsing and rendering."""
        from feretui.form import TagsField, FeretUIForm, wrap_tags

        class ArticleForm(FeretUIForm):
            tags = TagsField("Tags", separator=",")

        form = ArticleForm()
        assert form.tags.data == []

        # Process data from list
        form.tags.process_data(["tech", "python", "ai"])
        assert form.tags.data == ["tech", "python", "ai"]
        html_rendered = form.tags()
        assert "feretui-tag" in html_rendered
        assert "tech" in html_rendered
        assert "python" in html_rendered
        assert "ai" in html_rendered

        # Readonly mode
        html_ro = form.tags(readonly=True)
        assert 'name="tags"' not in html_ro
        assert "tech" in html_ro

        # Process data from comma string
        form.tags.process_data("web, cloud, devops")
        assert form.tags.data == ["web", "cloud", "devops"]

        # Process data from None or non-iterable
        form.tags.process_data(None)
        assert form.tags.data == []
        form.tags.process_data(12345)
        assert form.tags.data == []

        # Process formdata from string
        form.tags.process_formdata(["finance, legal, erp"])
        assert form.tags.data == ["finance", "legal", "erp"]

        # Process formdata from list
        form.tags.process_formdata([["lead", "urgent"]])
        assert form.tags.data == ["lead", "urgent"]

        # Process formdata from non-string/list
        form.tags.process_formdata([123])
        assert form.tags.data == []

        # Process formdata from empty
        form.tags.process_formdata([])
        assert form.tags.data == []

        # Direct wrap with wrapper_id and oob
        wrapped = wrap_tags(
            feretui,
            frequest.session,
            form.tags,
            wrapper_id="tags-wrap",
            oob=True,
        )
        assert 'id="tags-wrap"' in wrapped

    def test_wysiwyg_field(self, feretui, frequest) -> None:
        """Test WYSIWYGField, RichTextField, and HtmlField rendering."""
        from feretui.form import (
            HtmlField,
            RichTextField,
            WYSIWYGField,
            FeretUIForm,
            wrap_wysiwyg,
        )

        assert RichTextField is WYSIWYGField
        assert HtmlField is WYSIWYGField

        class ArticleForm(FeretUIForm):
            content = WYSIWYGField(
                "Article Content",
                min_height="350px",
                placeholder="Type your story here...",
            )
            notes = RichTextField("Internal Notes")

        form = ArticleForm()
        form.content.data = "<p>Hello <strong>World</strong>!</p>"

        # Edit mode rendering
        html_rendered = form.content()
        assert "feretui-wysiwyg-container" in html_rendered
        assert "feretui-wysiwyg-toolbar" in html_rendered
        assert 'data-command="bold"' in html_rendered
        assert 'data-command="italic"' in html_rendered
        assert 'data-command="createLink"' in html_rendered
        assert 'data-placeholder="Type your story here..."' in html_rendered
        assert "min-height: 350px;" in html_rendered
        assert "Hello <strong>World</strong>!" in html_rendered
        assert 'class="feretui-wysiwyg-textarea"' in html_rendered
        assert "<textarea" in html_rendered
        assert 'name="content"' in html_rendered
        assert 'id="content"' in html_rendered

        # Readonly mode rendering
        html_ro = form.content(readonly=True)
        assert "feretui-wysiwyg-preview" in html_ro
        assert "Hello <strong>World</strong>!" in html_ro
        assert "feretui-wysiwyg-toolbar" not in html_ro
        assert "feretui-wysiwyg-textarea" not in html_ro

        # Empty / None data rendering
        form.content.data = None
        html_empty = form.content()
        assert "feretui-wysiwyg-container" in html_empty

        # Errors rendering
        form.content.errors = ["Content is required"]
        html_err = form.content()
        assert "Content is required" in html_err

        # Direct wrap_wysiwyg with wrapper_id, oob, nolabel
        wrapped = wrap_wysiwyg(
            feretui,
            frequest.session,
            form.content,
            wrapper_id="content-wrap",
            oob=True,
            nolabel=True,
        )
        assert 'id="content-wrap"' in wrapped
        assert 'hx-swap-oob="true"' in wrapped
        assert "<label" not in wrapped




