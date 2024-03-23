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
* widget wrapper for renderer it with bulma class, with label in a
  **field div**.

  * :func:`.wrap_input`
  * :func:`.wrap_bool`
  * :func:`.wrap_radio`
  * :func:`.no_wrap`

The wrappers, excepted :func:`._no wrap`, added behaviours in kwargs of
the **__call__** method of the field:

* readonly : Put the field in a readonly mode
* no-label : Donc display the label but keep the bulma class in th
  **field div**
* data-readonly : with no label and readonly. The main diference is fot
  the wrapper :func:`.wrap_radio`, because only the label of the selected
  radio is displayed

Added the also the validators

* :class:`.Password`
"""
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from markupsafe import Markup
from password_validator import PasswordValidator
from polib import POFile
from wtforms.fields import BooleanField, Field, RadioField, SelectFieldBase
from wtforms.fields.core import UnboundField
from wtforms.form import Form
from wtforms.validators import InputRequired, ValidationError
from wtforms.widgets.core import clean_key
from wtforms_components import read_only

from feretui.thread import local

if TYPE_CHECKING:

    from feretui.translation import Translation


def wrap_input(field: Field, **kwargs: dict) -> Markup:
    """Render input field.

    :param field: The field to validate
    :type field: Field_
    :return: The renderer of the widget as html.
    :rtype: Markup_
    """
    if kwargs.pop('data-readonly', False) is True:
        kwargs['nolabel'] = True
        kwargs['readonly'] = True

    myferet = local.feretui
    session = local.request.session

    input_class = ["input"]
    required = False
    readonly = False

    if kwargs.get('readonly', False):
        input_class.append('is-static')
        read_only(field)
        readonly = True

    else:
        if field.errors:
            input_class.append("is-danger")

        for validator in field.validators:
            if isinstance(validator, InputRequired):
                if (not field.errors):
                    input_class.append("is-link")

                required = True

    c = kwargs.pop('class', '') or kwargs.pop('class_', '')
    kwargs['class'] = '{} {}'.format(' '.join(input_class), c)

    return Markup(myferet.render_template(
        session,
        "feretui-input-field",
        label=None if kwargs.pop('nolabel', False) else field.label,
        widget=field.widget(field, **kwargs),
        required=required,
        readonly=readonly,
        tooltip=field.description,
        errors=field.errors,
    ))


def wrap_bool(field: "Field", **kwargs: dict) -> Markup:
    """Render boolean field.

    :param field: The field to validate
    :type field: Field_
    :return: The renderer of the widget as html.
    :rtype: Markup_
    """
    readonly = False
    if kwargs.pop('data-readonly', False) is True:
        kwargs['nolabel'] = True
        kwargs['readonly'] = True

    myferet = local.feretui
    session = local.request.session

    if kwargs.pop('readonly', False):
        read_only(field)
        readonly = True

    return Markup(myferet.render_template(
        session,
        "feretui-bool-field",
        label=None if kwargs.pop('nolabel', False) else field.label,
        widget=field.widget(field, **kwargs),
        readonly=readonly,
        tooltip=field.description,
        errors=field.errors,
    ))


def wrap_radio(
    field: "Field",
    **kwargs: dict,  # noqa: ARG001
) -> Markup:
    """Render radio field.

    :param field: The field to validate
    :type field: Field_
    :return: The renderer of the widget as html.
    :rtype: Markup_
    """
    myferet = local.feretui
    session = local.request.session
    vertical = kwargs.pop('vertical', True)
    if vertical:
        template_id = "feretui-radio-field-vertical"
    else:
        template_id = "feretui-radio-field-horizontal"

    if kwargs.pop('data-readonly', False) is True:
        for choice in field.choices:
            if choice[0] == field.data:
                return Markup(f'<span>{choice[1]}</span>')

        return Markup('<span></span>')

    required = False
    readonly = False
    for validator in field.validators:
        if isinstance(validator, InputRequired):
            required = True

    if kwargs.get('readonly'):
        read_only(field)
        kwargs['disabled'] = True
        readonly = True

    return Markup(myferet.render_template(
        session,
        template_id,
        label=None if kwargs.pop('nolabel', False) else field.label,
        field=field,
        required=required,
        readonly=readonly,
        options=kwargs,
        tooltip=field.description,
        errors=field.errors,
    ))


def no_wrap(field: "Field", **kwargs: dict) -> Markup:
    """Render the field widget.

    :param field: The field to validate
    :type field: Field_
    :return: The renderer of the widget as html.
    :rtype: Markup_
    """
    return field.widget(field, **kwargs)


def gettext(
    form: Form,
    string: str,
    context_suffix: str = '',
) -> str:
    """Translate the string."""
    translation = local.feretui.translation
    lang = local.lang
    for form_cls in form.__mro__:
        if hasattr(form_cls, 'get_context'):
            context = form_cls.get_context() + context_suffix
            res = translation.get(
                lang,
                context,
                string,
                message_as_default=False,
            )
            if res is not None:
                return res

    return string


def get_field_translations(
    form_cls: Form,
    unbound_field: UnboundField,
    options: dict,
    callback: Callable,
) -> tuple[tuple, dict]:
    """Find the attribute to translate and apply the callback."""
    context_suffix = f":field:{options['name']}:"

    args = list(unbound_field.args)
    kwargs = unbound_field.kwargs.copy()

    if args:
        label = args.pop(0)
    elif unbound_field.kwargs.get('label'):
        label = unbound_field.kwargs.pop('label')
    else:
        label = options['name'].replace('_', ' ').title()

    kwargs['label'] = callback(form_cls, label, context_suffix + 'label')

    if kwargs.get('description'):
        kwargs['description'] = callback(
            form_cls,
            kwargs.get('description', ''),
            context_suffix + 'description',
        )

    if 'choices' in kwargs:
        choices = kwargs.pop('choices')
        if callable(choices):
            choices = choices()

        if isinstance(choices, dict):
            choices = choices.items()

        new_choices = []
        for choice in choices:
            choice = list(choice)
            new_choices.append(choice)

            choice[1] = callback(
                form_cls,
                choice[1],
                context_suffix + f'choice:{choice[0]}:label',
            )
            if len(choice) == 3 and choice[2].get('description'):
                choice[2]['description'] = callback(
                    form_cls,
                    choice[2]['description'],
                    context_suffix + f'choice:{choice[0]}:description',
                )

        kwargs['choices'] = new_choices

    return args, kwargs


class FormTranslations:
    """Class who did the link between Form and FeretUI translations."""

    def __init__(self: "FormTranslations", form: "FeretUIForm") -> None:
        """FormTranslations class."""
        self.form = form

    def gettext(self: "FormTranslations", string: str) -> str:
        """Return the translation."""
        return gettext(self.form.__class__, string)

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
        SelectFieldBase._Option: no_wrap,
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

    @classmethod
    def export_catalog(
        cls: "FeretUIForm",
        translation: "Translation",
        po: POFile,
    ) -> None:
        """Export the Form translation in the catalog.

        :param translation: The translation instance to add also inside it.
        :type translation: :class:`.Translation`
        :param po: The catalog instance
        :type po: PoFile_
        """

        def callback(form_cls: Form, string: str, context_suffix: str) -> str:
            context = form_cls.get_context() + context_suffix
            po.append(translation.define(context, string))
            return string

        for attr in dir(cls):
            field_cls = getattr(cls, attr)
            if not isinstance(field_cls, UnboundField):
                continue

            get_field_translations(cls, field_cls, {'name': attr}, callback)

    class Meta:
        """Meta class.

        Added
        * Translation
        * Bulma render
        """

        def bind_field(
            self: Any,
            form: Form,
            unbound_field: UnboundField,
            options: dict,
        ) -> Field:
            """Bind the field to the form.

            Added translation for the field
            """
            args, kwargs = get_field_translations(
                form.__class__,
                unbound_field,
                options,
                gettext,
            )
            return UnboundField(
                unbound_field.field_class, *args, **kwargs,
            ).bind(form=form, **options)

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
        form: Form,  # noqa: ARG002, U100
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
