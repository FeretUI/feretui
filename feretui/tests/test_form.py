# This file is a part of the FeretUI project
#
#    Copyright (C) 2023-2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest
from multidict import MultiDict
from wtforms import BooleanField, StringField
from wtforms.validators import InputRequired, Length, ValidationError

from feretui.feretui import FeretUI
from feretui.form import FeretUIForm, Password
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
        assert myform.name() == ''

    def test_form_render_field_translation(self) -> None:
        myferet = FeretUI()
        local.feretui = myferet
        session = Session()
        request = Request(session=session)
        local.request = request
        local.lang = 'fr'

        class MyForm(FeretUIForm):
            name = StringField()

        myferet.translation.translations[
            ('fr', f'form:{MyForm.__module__}:{MyForm.__name__}', 'Name')
        ] = 'Nom'
        myform = MyForm()
        assert myform.name() == ''

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
        assert myform.name() == ''

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
        assert myform.name() == ''

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
        assert myform.name() == ''

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
        assert myform.name() == ''

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
        assert myform.name() == ''

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
        assert myform.test() == ''

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
            has_digits=False,
            has_symbols=False,
            has_spaces=True,
        )

        class MyForm(FeretUIForm):
            password = StringField()

        myform = MyForm(MultiDict(password='test'))
        with pytest.raises(ValidationError):
            validator(myform, myform.password)
