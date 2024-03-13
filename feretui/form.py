# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from markupsafe import Markup
from password_validator import PasswordValidator
from wtforms.fields import BooleanField, RadioField
from wtforms.form import Form
from wtforms.validators import InputRequired, ValidationError
from wtforms.widgets.core import clean_key

from feretui.thread import local


def wrap_input(field, **kwargs):
    myferet = local.feretui
    session = local.request.session

    input_class = ["input"]
    if field.errors:
        input_class.append("is-danger")
    else:
        for validator in field.validators:
            if isinstance(validator, InputRequired):
                input_class.append("is-link")

    c = kwargs.pop('class', '') or kwargs.pop('class_', '')
    kwargs['class'] = '{} {}'.format(' '.join(input_class), c)
    return Markup(myferet.render_template(
        session,
        "feretui-input-field",
        label=field.label,
        widget=field.widget(field, **kwargs),
        errors=field.errors,
    ))


def wrap_bool(field, **kwargs):
    myferet = local.feretui
    session = local.request.session

    return Markup(myferet.render_template(
        session,
        "feretui-bool-field",
        label=field.label,
        widget=field.widget(field, **kwargs),
        errors=field.errors,
    ))


class FormTranslations:

    def __init__(self, form) -> None:
        self.form = form

    def gettext(self, string):
        translation = local.feretui.translation
        lang = local.lang
        for form_cls in self.form.__class__.__mro__:
            context = f'form:{form_cls.__module__}:{form_cls.__name__}'

            res = translation.get(
                lang, context, string, message_as_default=False)

            if res is not None:
                return res

        return string

    def ngettext(self, singular, plural, n):
        if n == 1:
            return self.gettext(singular)

        return self.gettext(plural)


class FeretUIForm(Form):

    WRAPPERS = {
        BooleanField: wrap_bool,
        RadioField: wrap_bool,
    }
    DEFAULT_WRAPPER = wrap_input

    @classmethod
    def register_translation(cls, txt) -> None:
        pass

    class Meta:

        def render_field(self, field, render_kw):
            render_kw = {clean_key(k): v for k, v in render_kw.items()}

            other_kw = getattr(field, "render_kw", None)
            if other_kw is not None:
                other_kw = {clean_key(k): v for k, v in other_kw.items()}
                render_kw = dict(other_kw, **render_kw)

            wrapper = FeretUIForm.WRAPPERS.get(
                field.__class__, FeretUIForm.DEFAULT_WRAPPER)
            return wrapper(field, **render_kw)

        def get_translations(self, form):
            return FormTranslations(form)


PasswordInvalid = 'The password should have {msg}.'
FeretUIForm.register_translation(PasswordInvalid)
PasswordMinSize = 'more than {min_size} caractere'
FeretUIForm.register_translation(PasswordMinSize)
PasswordMaxSize = 'less than {max_size} caractere'
FeretUIForm.register_translation(PasswordMaxSize)
PasswordWithLowerCase = 'with lowercase'
FeretUIForm.register_translation(PasswordWithLowerCase)
PasswordWithoutLowerCase = 'without lowercase'
FeretUIForm.register_translation(PasswordWithoutLowerCase)
PasswordWithUpperCase = 'with uppercase'
FeretUIForm.register_translation(PasswordWithUpperCase)
PasswordWithoutUpperCase = 'without uppercase'
FeretUIForm.register_translation(PasswordWithoutUpperCase)
PasswordWithDigits = 'with digits'
FeretUIForm.register_translation(PasswordWithDigits)
PasswordWithoutDigits = 'without digits'
FeretUIForm.register_translation(PasswordWithoutDigits)
PasswordWithSymbols = 'with symbols'
FeretUIForm.register_translation(PasswordWithSymbols)
PasswordWithoutSymbols = 'without symbols'
FeretUIForm.register_translation(PasswordWithoutSymbols)
PasswordWithSpaces = 'with spaces'
FeretUIForm.register_translation(PasswordWithSpaces)
PasswordWithoutSpaces = 'without spaces'
FeretUIForm.register_translation(PasswordWithoutSpaces)


class Password:
    def __init__(
        self,
        min_size: int = 12,
        max_size: int = None,
        has_lowercase: bool = True,
        has_uppercase: bool = True,
        has_digits: bool = True,
        has_symbols: bool = True,
        has_spaces: bool = False,
    ) -> None:
        self.schema = PasswordValidator()
        self.waiting = []
        if min_size:
            self.schema.min(min_size)
            self.waiting.append((
                PasswordMinSize,
                {"min_size": min_size},
            ))

        if max_size:
            self.schema.min(max_size)
            self.waiting.append((
                PasswordMaxSize,
                {"max_size": max_size},
            ))

        if has_lowercase:
            self.schema.has().lowercase()
            self.waiting.append((
                PasswordWithLowerCase,
                {},
            ))
        else:
            self.schema.has().no().lowercase()
            self.waiting.append((
                PasswordWithoutLowerCase,
                {},
            ))

        if has_uppercase:
            self.schema.has().uppercase()
            self.waiting.append((
                PasswordWithUpperCase,
                {},
            ))
        else:
            self.schema.has().no().uppercase()
            self.waiting.append((
                PasswordWithoutUpperCase,
                {},
            ))

        if has_digits:
            self.schema.has().digits()
            self.waiting.append((
                PasswordWithDigits,
                {},
            ))
        else:
            self.schema.has().no().digits()
            self.waiting.append((
                PasswordWithoutDigits,
                {},
            ))

        if has_symbols:
            self.schema.has().symbols()
            self.waiting.append((
                PasswordWithSymbols,
                {},
            ))
        else:
            self.schema.has().no().symbols()
            self.waiting.append((
                PasswordWithoutSymbols,
                {},
            ))

        if has_spaces:
            self.schema.has().spaces()
            self.waiting.append((
                PasswordWithSpaces,
                {},
            ))
        else:
            self.schema.has().no().spaces()
            self.waiting.append((
                PasswordWithoutSpaces,
                {},
            ))

    def __call__(self, form, field):
        if not self.schema.validate(field.data):
            msg = field.gettext(PasswordInvalid).format(
                msg=', '.join(
                    field.gettext(x[0]).format(**x[1])
                    for x in self.waiting
                ),
            )
            raise ValidationError(msg)
