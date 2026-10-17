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
from feretui.form import FeretUIForm, Password, get_field_translations, no_wrap, onchange


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
        assert 'hx-post="/feretui/action/resource?action=onchange&field=price"' in price_html
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


