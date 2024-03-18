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
from wtforms import BooleanField, RadioField, StringField, SelectField
from wtforms.validators import InputRequired, Length, ValidationError

import feretui
from feretui.feretui import FeretUI
from feretui.form import FeretUIForm, Password, get_field_translations, no_wrap
from feretui.request import Request
from feretui.session import Session
from feretui.thread import local


class TestForm:

    def test_form(self) -> None:
        myferet = FeretUI()
        local.feretui = myferet
        session = Session()
        request = Request(session=session)
        local.request = request
        local.lang = 'en'

        class MyForm(FeretUIForm):
            name = StringField()

        myform = MyForm(MultiDict(name='test'))
        assert myform.validate() is True

    def test_form_render_field(self) -> None:
        myferet = FeretUI()
        local.feretui = myferet
        session = Session()
        request = Request(session=session)
        local.request = request
        local.lang = 'en'

        class MyForm(FeretUIForm):
            name = StringField()

        myform = MyForm()
        assert myform.name() == (
            '<div class="field">\n'
            ' <label class="label" for="name">\n'
            '  Name\n'
            '      \n'
            '  <span>\n'
            '   \n'
            '  </span>\n'
            ' </label>\n'
            ' <div class="control">\n'
            '  <input class="input " id="name" name="name" type="text" '
            'value="">\n'
            ' </div>\n'
            ' <div>\n'
            '  \n'
            ' </div>\n'
            '</div>'
        )

    def test_form_render_field_translation(self) -> None:
        myferet = FeretUI()
        local.feretui = myferet
        session = Session()
        request = Request(session=session)
        local.request = request
        local.lang = 'fr'

        class MyForm(FeretUIForm):
            name = StringField()

        myferet.translation.translations[(
            'fr',
            f'form:{MyForm.__module__}:{MyForm.__name__}:field:name:label',
            'Name',
        )] = 'Nom'
        myform = MyForm()
        assert myform.name() == (
            '<div class="field">\n'
            ' <label class="label" for="name">\n'
            '  Nom\n'
            '      \n'
            '  <span>\n'
            '   \n'
            '  </span>\n'
            ' </label>\n'
            ' <div class="control">\n'
            '  <input class="input " id="name" name="name" type="text" '
            'value="">\n'
            ' </div>\n'
            ' <div>\n'
            '  \n'
            ' </div>\n'
            '</div>'
        )

    def test_form_render_field_render_kw(self) -> None:
        myferet = FeretUI()
        local.feretui = myferet
        session = Session()
        request = Request(session=session)
        local.request = request
        local.lang = 'en'

        class MyForm(FeretUIForm):
            name = StringField(render_kw={'foo': 'bar'})

        myform = MyForm()
        assert myform.name() == (
            '<div class="field">\n'
            ' <label class="label" for="name">\n'
            '  Name\n'
            '      \n'
            '  <span>\n'
            '   \n'
            '  </span>\n'
            ' </label>\n'
            ' <div class="control">\n'
            '  <input class="input " foo="bar" id="name" name="name" '
            'type="text" value="">\n'
            ' </div>\n'
            ' <div>\n'
            '  \n'
            ' </div>\n'
            '</div>'
        )

    def test_form_render_field_with_errors(self) -> None:
        myferet = FeretUI()
        local.feretui = myferet
        session = Session()
        request = Request(session=session)
        local.request = request
        local.lang = 'en'

        class MyForm(FeretUIForm):
            name = StringField(validators=[InputRequired()])

        myform = MyForm()
        myform.validate()
        assert myform.name() == (
            '<div class="field">\n'
            ' <label class="label" for="name">\n'
            '  Name\n'
            '      \n'
            '  <span>\n'
            '   \n'
            '  </span>\n'
            ' </label>\n'
            ' <div class="control">\n'
            '  <input class="input is-danger " id="name" name="name" required '
            'type="text" value="">\n'
            ' </div>\n'
            ' <div>\n'
            '  \n'
            '  <p class="help is-danger">\n'
            '   This field is required.\n'
            '  </p>\n'
            '  \n'
            ' </div>\n'
            '</div>'
        )

    def test_form_render_field_required(self) -> None:
        myferet = FeretUI()
        local.feretui = myferet
        session = Session()
        request = Request(session=session)
        local.request = request
        local.lang = 'en'

        class MyForm(FeretUIForm):
            name = StringField(validators=[InputRequired()])

        myform = MyForm(MultiDict(name='test'))
        myform.validate()
        assert myform.name() == (
            '<div class="field">\n'
            ' <label class="label" for="name">\n'
            '  Name\n'
            '      \n'
            '  <span class="content is-small">\n'
            '   (\n'
            '   <span class="has-text-link">\n'
            '    required\n'
            '   </span>\n'
            '   )\n'
            '  </span>\n'
            '  \n'
            '  <span>\n'
            '   \n'
            '  </span>\n'
            ' </label>\n'
            ' <div class="control">\n'
            '  <input class="input is-link " id="name" name="name" required '
            'type="text" value="test">\n'
            ' </div>\n'
            ' <div>\n'
            '  \n'
            ' </div>\n'
            '</div>'
        )

    def test_form_render_field_password(self) -> None:
        myferet = FeretUI()

        path = Path(feretui.__file__).parent
        path = path / 'locale' / 'fr.po'
        myferet.load_catalog(path, 'fr')

        local.feretui = myferet
        session = Session()
        request = Request(session=session)
        local.request = request
        local.lang = 'fr'

        class MyForm(FeretUIForm):
            password = StringField(validators=[Password()])

        myform = MyForm()
        myform.validate()
        assert myform.password() == (
            '<div class="field">\n'
            ' <label class="label" for="password">\n'
            '  Password\n'
            '      \n'
            '  <span>\n'
            '   \n'
            '  </span>\n'
            ' </label>\n'
            ' <div class="control">\n'
            '  <input class="input is-danger " id="password" name="password" '
            'type="text" value="">\n'
            ' </div>\n'
            ' <div>\n'
            '  \n'
            '  <p class="help is-danger">\n'
            '   Le mot de passe doit contenir plus de 12 caractères, avec des '
            'minuscules, avec des majuscules, avec des lettres, avec des '
            'chiffres, avec des caractères spéciaux, sans espaces.\n'
            '  </p>\n'
            '  \n'
            ' </div>\n'
            '</div>'
        )

    def test_form_render_field_length_1(self) -> None:
        myferet = FeretUI()
        local.feretui = myferet
        session = Session()
        request = Request(session=session)
        local.request = request
        local.lang = 'en'

        class MyForm(FeretUIForm):
            name = StringField(validators=[Length(max=1)])

        myform = MyForm(MultiDict(name='test'))
        myform.validate()
        assert myform.name() == (
            '<div class="field">\n'
            ' <label class="label" for="name">\n'
            '  Name\n'
            '      \n'
            '  <span>\n'
            '   \n'
            '  </span>\n'
            ' </label>\n'
            ' <div class="control">\n'
            '  <input class="input is-danger " id="name" maxlength="1" '
            'name="name" type="text" value="test">\n'
            ' </div>\n'
            ' <div>\n'
            '  \n'
            '  <p class="help is-danger">\n'
            '   Field cannot be longer than 1 character.\n'
            '  </p>\n'
            '  \n'
            ' </div>\n'
            '</div>'
        )

    def test_form_render_field_length_2(self) -> None:
        myferet = FeretUI()
        local.feretui = myferet
        session = Session()
        request = Request(session=session)
        local.request = request
        local.lang = 'en'

        class MyForm(FeretUIForm):
            name = StringField(validators=[Length(max=0)])

        myform = MyForm(MultiDict(name='test'))
        myform.validate()
        assert myform.name() == (
            '<div class="field">\n'
            ' <label class="label" for="name">\n'
            '  Name\n'
            '      \n'
            '  <span>\n'
            '   \n'
            '  </span>\n'
            ' </label>\n'
            ' <div class="control">\n'
            '  <input class="input is-danger " id="name" maxlength="0" '
            'name="name" type="text" value="test">\n'
            ' </div>\n'
            ' <div>\n'
            '  \n'
            '  <p class="help is-danger">\n'
            '   Field cannot be longer than 0 characters.\n'
            '  </p>\n'
            '  \n'
            ' </div>\n'
            '</div>'
        )

    def test_form_render_bool(self) -> None:
        myferet = FeretUI()
        local.feretui = myferet
        session = Session()
        request = Request(session=session)
        local.request = request
        local.lang = 'en'

        class MyForm(FeretUIForm):
            test = BooleanField()

        myform = MyForm()
        assert myform.test() == (
            '<div class="field">\n'
            ' <label class="checkbox" for="test">\n'
            '  <input id="test" name="test" type="checkbox" value="y">\n'
            '        Test\n'
            '  <span>\n'
            '   \n'
            '  </span>\n'
            ' </label>\n'
            ' <div>\n'
            '  \n'
            ' </div>\n'
            '</div>'
        )

    def test_form_render_bool_description(self) -> None:
        myferet = FeretUI()
        local.feretui = myferet
        session = Session()
        request = Request(session=session)
        local.request = request
        local.lang = 'en'

        class MyForm(FeretUIForm):
            test = BooleanField(description="Test")

        myform = MyForm()
        assert myform.test() == (
            '<div class="field">\n'
            ' <label class="checkbox" for="test">\n'
            '  <input id="test" name="test" type="checkbox" value="y">\n'
            '        Test\n'
            '  <span>\n'
            '   \n'
            '   <span class="ml-0 icon has-tooltip-bottom has-tooltip-arrow" '
            'data-tooltip="Test">\n'
            '    <i class="fa-solid fa-circle-info is-small">\n'
            '    </i>\n'
            '   </span>\n'
            '   \n'
            '  </span>\n'
            ' </label>\n'
            ' <div>\n'
            '  \n'
            ' </div>\n'
            '</div>'
        )

    def test_form_render_radio(self) -> None:
        myferet = FeretUI()
        local.feretui = myferet
        session = Session()
        request = Request(session=session)
        local.request = request
        local.lang = 'en'

        class MyForm(FeretUIForm):
            test = RadioField(choices=[('foo', 'Foo'), ('bar', 'Bar')])

        myform = MyForm()
        assert myform.test() == (
            '<div class="field">\n'
            ' <label class="label" for="test">\n'
            '  Test\n'
            '      \n'
            '  <span>\n'
            '   \n'
            '  </span>\n'
            ' </label>\n'
            ' <div class="control">\n'
            '  <ul>\n'
            '   \n'
            '   <li>\n'
            '    <label class="radio" for="test">\n'
            '     <input id="test-0" name="test" type="radio" value="foo">\n'
            '                <label class="radio" for="test-0">Foo</label>\n'
            '                \n'
            '     <span>\n'
            '      \n'
            '     </span>\n'
            '    </label>\n'
            '   </li>\n'
            '   \n'
            '   <li>\n'
            '    <label class="radio" for="test">\n'
            '     <input id="test-1" name="test" type="radio" value="bar">\n'
            '                <label class="radio" for="test-1">Bar</label>\n'
            '                \n'
            '     <span>\n'
            '      \n'
            '     </span>\n'
            '    </label>\n'
            '   </li>\n'
            '   \n'
            '  </ul>\n'
            ' </div>\n'
            ' <div>\n'
            '  \n'
            ' </div>\n'
            '</div>'
        )

    def test_form_render_radio_required(self) -> None:
        myferet = FeretUI()
        local.feretui = myferet
        session = Session()
        request = Request(session=session)
        local.request = request
        local.lang = 'en'

        class MyForm(FeretUIForm):
            test = RadioField(
                choices=[('foo', 'Foo'), ('bar', 'Bar')],
                validators=[InputRequired()])

        myform = MyForm()
        assert myform.test() == (
            '<div class="field">\n'
            ' <label class="label" for="test">\n'
            '  Test\n'
            '      \n'
            '  <span class="content is-small">\n'
            '   (\n'
            '   <span class="has-text-link">\n'
            '    required\n'
            '   </span>\n'
            '   )\n'
            '  </span>\n'
            '  \n'
            '  <span>\n'
            '   \n'
            '  </span>\n'
            ' </label>\n'
            ' <div class="control">\n'
            '  <ul>\n'
            '   \n'
            '   <li>\n'
            '    <label class="radio" for="test">\n'
            '     <input id="test-0" name="test" required type="radio" '
            'value="foo">\n'
            '                <label class="radio" for="test-0">Foo</label>\n'
            '                \n'
            '     <span>\n'
            '      \n'
            '     </span>\n'
            '    </label>\n'
            '   </li>\n'
            '   \n'
            '   <li>\n'
            '    <label class="radio" for="test">\n'
            '     <input id="test-1" name="test" required type="radio" '
            'value="bar">\n'
            '                <label class="radio" for="test-1">Bar</label>\n'
            '                \n'
            '     <span>\n'
            '      \n'
            '     </span>\n'
            '    </label>\n'
            '   </li>\n'
            '   \n'
            '  </ul>\n'
            ' </div>\n'
            ' <div>\n'
            '  \n'
            ' </div>\n'
            '</div>'
        )

    def test_form_render_radio_description(self) -> None:
        myferet = FeretUI()
        local.feretui = myferet
        session = Session()
        request = Request(session=session)
        local.request = request
        local.lang = 'en'

        class MyForm(FeretUIForm):
            test = RadioField(
                choices=[('foo', 'Foo'), ('bar', 'Bar')], description="Test")

        myform = MyForm()
        assert myform.test() == (
            '<div class="field">\n'
            ' <label class="label" for="test">\n'
            '  Test\n'
            '      \n'
            '  <span>\n'
            '   \n'
            '   <span class="ml-0 icon has-tooltip-bottom has-tooltip-arrow" '
            'data-tooltip="Test">\n'
            '    <i class="fa-solid fa-circle-info is-small">\n'
            '    </i>\n'
            '   </span>\n'
            '   \n'
            '  </span>\n'
            ' </label>\n'
            ' <div class="control">\n'
            '  <ul>\n'
            '   \n'
            '   <li>\n'
            '    <label class="radio" for="test">\n'
            '     <input id="test-0" name="test" type="radio" value="foo">\n'
            '                <label class="radio" for="test-0">Foo</label>\n'
            '                \n'
            '     <span>\n'
            '      \n'
            '     </span>\n'
            '    </label>\n'
            '   </li>\n'
            '   \n'
            '   <li>\n'
            '    <label class="radio" for="test">\n'
            '     <input id="test-1" name="test" type="radio" value="bar">\n'
            '                <label class="radio" for="test-1">Bar</label>\n'
            '                \n'
            '     <span>\n'
            '      \n'
            '     </span>\n'
            '    </label>\n'
            '   </li>\n'
            '   \n'
            '  </ul>\n'
            ' </div>\n'
            ' <div>\n'
            '  \n'
            ' </div>\n'
            '</div>'
        )

    def test_form_render_radio_honrizontal(self) -> None:
        myferet = FeretUI()
        local.feretui = myferet
        session = Session()
        request = Request(session=session)
        local.request = request
        local.lang = 'en'

        class MyForm(FeretUIForm):
            test = RadioField(
                choices=[('foo', 'Foo'), ('bar', 'Bar')],
                render_kw=dict(vertical=False),
            )

        myform = MyForm()
        assert myform.test() == (
            '<div class="field">\n'
            ' <label class="label" for="test">\n'
            '  Test\n'
            '      \n'
            '  <span>\n'
            '   \n'
            '  </span>\n'
            ' </label>\n'
            ' <div class="control">\n'
            '  \n'
            '  <label class="radio" for="test">\n'
            '   <input id="test-0" name="test" type="radio" value="foo">\n'
            '            <label class="radio" for="test-0">Foo</label>\n'
            '            \n'
            '   <span>\n'
            '    \n'
            '   </span>\n'
            '  </label>\n'
            '  \n'
            '  <label class="radio" for="test">\n'
            '   <input id="test-1" name="test" type="radio" value="bar">\n'
            '            <label class="radio" for="test-1">Bar</label>\n'
            '            \n'
            '   <span>\n'
            '    \n'
            '   </span>\n'
            '  </label>\n'
            '  \n'
            ' </div>\n'
            ' <div>\n'
            '  \n'
            ' </div>\n'
            '</div>'
        )

    def test_no_wrap(self) -> None:
        myferet = FeretUI()
        local.feretui = myferet
        session = Session()
        request = Request(session=session)
        local.request = request
        local.lang = 'en'

        class MyForm(FeretUIForm):
            test = StringField()

        form = MyForm()
        assert no_wrap(form.test) == (
            '<input id="test" name="test" type="text" value="">'
        )

    def test_add_translation(self) -> None:
        FeretUIForm.register_translation('One test')

    def test_password_validator(self) -> None:
        validator = Password()

        class MyForm(FeretUIForm):
            password = StringField()

        myform = MyForm(MultiDict(password='test'))
        with pytest.raises(ValidationError):
            validator(myform, myform.password)

    def test_password_validator_2(self) -> None:
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
            (':field:foo:label', 'Foo'), (':field:foo:description', 'Bar')
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
