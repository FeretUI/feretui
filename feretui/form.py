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
            if hasattr(form_cls, 'get_context'):
                res = translation.get(
                    lang,
                    form_cls.get_context(),
                    string,
                    message_as_default=False,
                )
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
    TRANSLATED_MESSAGES = [
        # From WTForms
        "Not a valid integer value.",
        "Not a valid decimal value.",
        "Not a valid float value.",
        "Not a valid datetime value.",
        "Not a valid date value.",
        "Not a valid time value.",
        "Not a valid week value.",
        "Invalid Choice: could not coerce.",
        "Choices cannot be None.",
        "Not a valid choice.",
        "Invalid choice(s): one or more data inputs could not be coerced.",
        "Choices cannot be None.",
        "'%(value)s' is not a valid choice for this field.",
        "'%(value)s' are not valid choices for this field.",
        "Invalid CSRF Token.",
        "CSRF token missing.",
        "CSRF failed.",
        "CSRF token expired.",
        "Invalid field name '%s'.",
        "Field must be equal to %(other_name)s.",
        "Field must be at least %(min)d character long.",
        "Field must be at least %(min)d characters long.",
        "Field cannot be longer than %(max)d character.",
        "Field cannot be longer than %(max)d characters.",
        "Field must be exactly %(max)d character long.",
        "Field must be exactly %(max)d characters long.",
        "Field must be between %(min)d and %(max)d characters long.",
        "Number must be at least %(min)s.",
        "Number must be at most %(max)s.",
        "Number must be between %(min)s and %(max)s.",
        "This field is required.",
        "This field is required.",
        "Invalid input.",
        "Invalid email address.",
        "Invalid IP address.",
        "Invalid Mac address.",
        "Invalid URL.",
        "Invalid UUID.",
        "Invalid value, must be one of: %(values)s.",
        "Invalid value, can't be any of: %(values)s.",
        "This field cannot be edited",
        "This field is disabled and cannot have a value",
        # From WTForms Components
        'Not a valid time.',
        'Not a valid decimal range value',
        'Not a valid float range value',
        'Not a valid int range value',
        'Not a valid date range value',
        'Not a valid datetime range value',
        'Not a valid choice',
        'Not a valid color.',
        'Invalid choice(s): one or more data inputs could not be coerced',
        "'%(value)s' is not a valid choice for this field",
        'Date must be greater than %(min)s.',
        'Date must be less than %(max)s.',
        'Date must be between %(min)s and %(max)s.',
        'Time must be greater than %(min)s.',
        'Time must be less than %(max)s.',
        'Time must be between %(min)s and %(max)s.',
        'Invalid email address.',
        'This field contains invalid JSON',
    ]

    @classmethod
    def register_translation(cls, message) -> None:
        if message not in FeretUIForm.TRANSLATED_MESSAGES:
            FeretUIForm.TRANSLATED_MESSAGES.append(message)

        return message

    @classmethod
    def get_context(cls) -> str:
        return f'form:{cls.__module__}:{cls.__name__}'

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


PasswordInvalid = FeretUIForm.register_translation(
    'The password should have {msg}.')
PasswordMinSize = FeretUIForm.register_translation(
    'more than {min_size} caractere')
PasswordMaxSize = FeretUIForm.register_translation(
    'less than {max_size} caractere')
PasswordWithLowerCase = FeretUIForm.register_translation('with lowercase')
PasswordWithoutLowerCase = FeretUIForm.register_translation(
    'without lowercase')
PasswordWithUpperCase = FeretUIForm.register_translation('with uppercase')
PasswordWithoutUpperCase = FeretUIForm.register_translation(
    'without uppercase')
PasswordWithDigits = FeretUIForm.register_translation('with digits')
PasswordWithoutDigits = FeretUIForm.register_translation('without digits')
PasswordWithSymbols = FeretUIForm.register_translation('with symbols')
PasswordWithoutSymbols = FeretUIForm.register_translation('without symbols')
PasswordWithSpaces = FeretUIForm.register_translation('with spaces')
PasswordWithoutSpaces = FeretUIForm.register_translation('without spaces')


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
