# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Module feretui.form.

Addons for WTForms_. The form is usefull to create a formular in a page.

The class :class:`.FeretUIForm` are behaviour like:

* the link with the feretui translation.
* widget wrapper for renderer it with bulma class.

  * :func:`.wrap_input`
  * :func:`.wrap_bool`

Added the also the validators

* :class:`.Password`
"""
from typing import Any

from markupsafe import Markup
from password_validator import PasswordValidator
from wtforms.fields import BooleanField, Field, RadioField, SelectFieldBase
from wtforms.form import Form
from wtforms.validators import InputRequired, ValidationError
from wtforms.widgets.core import RadioInput, clean_key

from feretui.thread import local


def wrap_input(field: Field, **kwargs: dict) -> Markup:
    """Render input field.

    :param field: The field to validate
    :type field: Field_
    :return: The renderer of the widget as html.
    :rtype: Markup_
    """
    feretui = local.feretui
    session = local.request.session

    input_class = ["input"]
    required = False
    if field.errors:
        input_class.append("is-danger")
    else:
        for validator in field.validators:
            if isinstance(validator, InputRequired):
                input_class.append("is-link")
                required = True

    c = kwargs.pop('class', '') or kwargs.pop('class_', '')
    kwargs['class'] = '{} {}'.format(' '.join(input_class), c)
    return Markup(feretui.render_template(
        session,
        "feretui-input-field",
        label=field.label,
        widget=field.widget(field, **kwargs),
        required=required,
        tooltip=field.gettext(field.description),
        errors=field.errors,
    ))


def wrap_bool(field: "Field", **kwargs: dict) -> Markup:
    """Render boolean field.

    :param field: The field to validate
    :type field: Field_
    :return: The renderer of the widget as html.
    :rtype: Markup_
    """
    feretui = local.feretui
    session = local.request.session

    return Markup(feretui.render_template(
        session,
        "feretui-bool-field",
        label=field.label,
        widget=field.widget(field, **kwargs),
        tooltip=field.gettext(field.description),
        errors=field.errors,
    ))


def wrap_radio(field: "Field", **kwargs: dict) -> Markup:
    """Render radio field.

    :param field: The field to validate
    :type field: Field_
    :return: The renderer of the widget as html.
    :rtype: Markup_
    """
    feretui = local.feretui
    session = local.request.session

    required = False
    for validator in field.validators:
        if isinstance(validator, InputRequired):
            required = True

    return Markup(feretui.render_template(
        session,
        "feretui-radio-field",
        label=field.label,
        widget=field.widget(field, **kwargs),
        required=required,
        tooltip=field.gettext(field.description),
        errors=field.errors,
    ))


def wrap_option(field: "Field", **kwargs: dict) -> Markup:
    """Render option from select/radio field.

    :param field: The field to validate
    :type field: Field_
    :return: The renderer of the widget as html.
    :rtype: Markup_
    """
    if not isinstance(field.widget, RadioInput):
        return field.widget(field, **kwargs)

    feretui = local.feretui
    session = local.request.session

    return Markup(feretui.render_template(
        session,
        "feretui-radio-option",
        widget=field.widget(field, class_="radio", **kwargs),
    ))


class FormTranslations:
    """Class who did the link between Form and FeretUI translations."""

    def __init__(self: "FormTranslations", form: "FeretUIForm") -> None:
        """FormTranslations class."""
        self.form = form

    def gettext(self: "FormTranslations", string: str) -> str:
        """Return the translation."""
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

    def ngettext(
        self: "FormTranslations",
        singular: str,
        plural: str,
        n: int,
    ) -> str:
        """Return the translation."""
        if n == 1:
            return self.gettext(singular)

        return self.gettext(plural)


class FeretUIForm(Form):
    """Form base class.

    The goal is to give at the Form used by FeretUI the behaviour like:

    * translation
    * bulma renderer

    It is not required to used it. If the translation or the renderer is not
    automaticly done by FeretUI.

    ::

        class MyForm(FeretUIForm):
            name = StringField()

    """

    WRAPPERS = {
        BooleanField: wrap_bool,
        RadioField: wrap_radio,
        SelectFieldBase._Option: wrap_option,
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
        'This field contains invalid JSON',
    ]

    @classmethod
    def register_translation(cls: "FeretUIForm", message: str) -> str:
        """Register a translation come from validator.

        Some text is defined in the validator or WTForms_ addons. They
        can not be export easily. This register give the possibility for
        the devloper to define their.
        """
        if message not in FeretUIForm.TRANSLATED_MESSAGES:
            FeretUIForm.TRANSLATED_MESSAGES.append(message)

        return message

    @classmethod
    def get_context(cls: "FeretUIForm") -> str:
        """Return the context for the translation."""
        return f'form:{cls.__module__}:{cls.__name__}'

    class Meta:
        """Meta class.

        Added
        * Translation
        * Bulma render
        """

        def render_field(self: Any, field: Field, render_kw: dict) -> Markup:
            """Render the field.

            :param field: The field to render
            :type field: Field_
            :return: The renderer of the widget as html.
            :rtype: Markup_
            """
            render_kw = {clean_key(k): v for k, v in render_kw.items()}

            other_kw = getattr(field, "render_kw", None)
            if other_kw is not None:
                other_kw = {clean_key(k): v for k, v in other_kw.items()}
                render_kw = dict(other_kw, **render_kw)

            wrapper = FeretUIForm.WRAPPERS.get(
                field.__class__, FeretUIForm.DEFAULT_WRAPPER)
            return wrapper(field, **render_kw)

        def get_translations(
            self: Any,
            form: "FeretUIForm",
        ) -> FormTranslations:
            """Return Translation class.

            :param form: The form instance
            :type form: :class:`.FeretUIForm`
            :return: The translation class to link feretui translation.
            :rtype: :class:`.FormTranslations`
            """
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
PasswordWithLetters = FeretUIForm.register_translation('with letters')
PasswordWithoutLetters = FeretUIForm.register_translation('without letters')
PasswordWithDigits = FeretUIForm.register_translation('with digits')
PasswordWithoutDigits = FeretUIForm.register_translation('without digits')
PasswordWithSymbols = FeretUIForm.register_translation('with symbols')
PasswordWithoutSymbols = FeretUIForm.register_translation('without symbols')
PasswordWithSpaces = FeretUIForm.register_translation('with spaces')
PasswordWithoutSpaces = FeretUIForm.register_translation('without spaces')


class Password(InputRequired):
    """Password validator.

    It is a generic validator for WTForms_. It is based on the library
    `password-validator
    <https://github.com/tarunbatra/password-validator-python>`_.

    ::

        class MyForm(Form):
            password = PasswordField(validators=[Password()])

    :param min_size: The minimal size of the password. If None then
                     no minimal size.
    :type min_size: int
    :param max_size: The maximal size. If None then no maximal size.
    :type max_size: int
    :param has_lowercase: If True the password must have one or more
                          lowercase.
                          If False the password must not have any
                          lowercase
                          If None no rule on the lowercase
    :type has_lowercase: bool
    :param has_uppercase: If True the password must have one or more
                          uppercase.
                          If False the password must not have any
                          uppercase
                          If None no rule on the uppercase
    :type has_uppercase: bool
    :param has_letters: If True the password must have one or more
                        letters.
                        If False the password must not have any
                        letters
                        If None no rule on the letters
    :type has_letters: bool
    :param has_digits: If True the password must have one or more
                       digits.
                       If False the password must not have any
                       digits
                       If None no rule on the digits
    :type has_digits: bool
    :param has_symbols: If True the password must have one or more
                        symbols.
                        If False the password must not have any
                        symbols
                        If None no rule on the symbols
    :type has_symbols: bool
    :param has_spaces: If True the password must have one or more
                       spaces.
                       If False the password must not have any
                       spaces
                       If None no rule on the spaces
    :type has_spaces: bool
    """

    def __init__(
        self: "Password",
        min_size: int = 12,
        max_size: int = None,
        has_lowercase: bool = True,
        has_uppercase: bool = True,
        has_letters: bool = True,
        has_digits: bool = True,
        has_symbols: bool = True,
        has_spaces: bool = False,
    ) -> None:
        """Password class."""
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

        for has, attr, true_msg, false_msg in (
            (has_lowercase, 'lowercase', PasswordWithLowerCase,
             PasswordWithoutLowerCase),
            (has_uppercase, 'uppercase', PasswordWithUpperCase,
             PasswordWithoutUpperCase),
            (has_letters, 'letters', PasswordWithLetters,
             PasswordWithoutLetters),
            (has_digits, 'digits', PasswordWithDigits,
             PasswordWithoutDigits),
            (has_symbols, 'symbols', PasswordWithSymbols,
             PasswordWithoutSymbols),
            (has_spaces, 'spaces', PasswordWithSpaces,
             PasswordWithoutSpaces),
        ):
            if has is True:
                getattr(self.schema.has(), attr)()
                self.waiting.append((true_msg, {}))
            elif has is False:
                getattr(self.schema.has().no(), attr)()
                self.waiting.append((false_msg, {}))

    def __call__(
        self: "PasswordWithoutSpaces",
        form: Form,  # noqa: ARG002
        field: Field,
    ) -> None:
        """Validate if the field is a valid password.

        :param form: A Form
        :type form: Form_
        :param field: The field to validate
        :type field: Field_
        :exception': ValidationError_
        """
        if not self.schema.validate(field.data):
            msg = field.gettext(PasswordInvalid).format(
                msg=', '.join(
                    field.gettext(x[0]).format(**x[1])
                    for x in self.waiting
                ),
            )
            raise ValidationError(msg)
