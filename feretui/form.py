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
  * :func:`.wrap_fieldset`
  * :func:`.wrap_select_multiple`
  * :func:`.no_wrap`

The wrappers, excepted :func:`._no wrap`, added behaviours in kwargs of
the **__call__** method of the field:

* readonly : Put the field in a readonly mode
* no-label : Donc display the label but keep the bulma class in th
  **field div**

Added the also the validators

* :class:`.Password`
"""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from markupsafe import Markup, escape
from password_validator import PasswordValidator
from polib import POFile
from wtforms.fields import (
    BooleanField,
    DecimalField,
    Field,
    FormField,
    HiddenField,
    RadioField,
    SelectField,
    SelectFieldBase,
    SelectMultipleField,
)
from wtforms.fields.core import UnboundField
from wtforms.form import Form
from wtforms.validators import InputRequired, ValidationError
from wtforms.widgets import FileInput, ListWidget, TextArea, TextInput
from wtforms.widgets.core import clean_key
from wtforms_components import read_only

from feretui.context import ContextProperties, cvar_feretui, cvar_request

if TYPE_CHECKING:
    from feretui.feretui import FeretUI
    from feretui.session import Session
    from feretui.translation import Translation


def wrap_input(
    feretui: "FeretUI",
    session: "Session",
    field: Field,
    **kwargs: dict,
) -> Markup:
    """Render input field.

    :param feretui: The feretui client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param session: The Session
    :type session: :class:`feretui.session.Session`
    :param field: The field to validate
    :type field: Field_
    :return: The renderer of the widget as html.
    :rtype: Markup_
    """
    input_class = ["input"]
    required = False
    readonly = False

    if kwargs.get("readonly", False):
        input_class.append("is-static")
        read_only(field)
        readonly = True

    else:
        if field.errors:
            input_class.append("is-danger")

        for validator in field.validators:
            if isinstance(validator, InputRequired):
                if not field.errors:
                    input_class.append("is-link")

                required = True

    c = kwargs.pop("class", "") or kwargs.pop("class_", "")
    kwargs["class"] = "{} {}".format(" ".join(input_class), c)
    wrapper_id = kwargs.pop("wrapper_id", None)
    oob = kwargs.pop("oob", False)

    html = Markup(
        feretui.render_template(
            session,
            "feretui-input-field",
            label=None if kwargs.pop("nolabel", False) else field.label,
            widget=field.widget(field, **kwargs),
            required=required,
            readonly=readonly,
            description=field.description,
            errors=field.errors,
        ),
    )
    if wrapper_id:
        oob_attr = ' hx-swap-oob="true"' if oob else ""
        return Markup(f'<div id="{wrapper_id}"{oob_attr}>{html}</div>')  # noqa: S704

    return html


def wrap_bool(
    feretui: "FeretUI",
    session: "Session",
    field: Field,
    **kwargs: dict,
) -> Markup:
    """Render boolean field.

    :param feretui: The feretui client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param session: The Session
    :type session: :class:`feretui.session.Session`
    :param field: The field to validate
    :type field: Field_
    :return: The renderer of the widget as html.
    :rtype: Markup_
    """
    readonly = False

    if kwargs.pop("readonly", False):
        read_only(field)
        readonly = True

    wrapper_id = kwargs.pop("wrapper_id", None)
    oob = kwargs.pop("oob", False)

    html = Markup(
        feretui.render_template(
            session,
            "feretui-bool-field",
            label=None if kwargs.pop("nolabel", False) else field.label,
            widget=field.widget(field, **kwargs),
            readonly=readonly,
            description=field.description,
            errors=field.errors,
        ),
    )
    if wrapper_id:
        oob_attr = ' hx-swap-oob="true"' if oob else ""
        return Markup(f'<div id="{wrapper_id}"{oob_attr}>{html}</div>')  # noqa: S704

    return html


def wrap_radio(
    feretui: "FeretUI",
    session: "Session",
    field: "Field",
    **kwargs: dict,  # noqa: ARG001
) -> Markup:
    """Render radio field.

    :param feretui: The feretui client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param session: The Session
    :type session: :class:`feretui.session.Session`
    :param field: The field to validate
    :type field: Field_
    :return: The renderer of the widget as html.
    :rtype: Markup_
    """
    vertical = kwargs.pop("vertical", True)
    if vertical:
        template_id = "feretui-radio-field-vertical"
    else:
        template_id = "feretui-radio-field-horizontal"

    required = False
    readonly = False
    for validator in field.validators:
        if isinstance(validator, InputRequired):
            required = True

    if kwargs.get("readonly"):
        read_only(field)
        kwargs["disabled"] = True
        readonly = True

    wrapper_id = kwargs.pop("wrapper_id", None)
    oob = kwargs.pop("oob", False)

    html = Markup(
        feretui.render_template(
            session,
            template_id,
            label=None if kwargs.pop("nolabel", False) else field.label,
            field=field,
            required=required,
            readonly=readonly,
            options=kwargs,
            description=field.description,
            errors=field.errors,
        ),
    )
    if wrapper_id:
        oob_attr = ' hx-swap-oob="true"' if oob else ""
        return Markup(f'<div id="{wrapper_id}"{oob_attr}>{html}</div>')  # noqa: S704

    return html


def wrap_fieldset(
    feretui: "FeretUI",
    session: "Session",
    field: "Field",
    **kwargs: dict,
) -> Markup:
    """Render fieldset.

    It is used to group fields with a `fieldset` tag. It is required for
    accessibility (RGAA 11.5).

    :param feretui: The feretui client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param session: The Session
    :type session: :class:`feretui.session.Session`
    :param field: The field to validate
    :type field: Field_
    :return: The renderer of the widget as html.
    :rtype: Markup_
    """
    required = False
    readonly = False
    for validator in field.validators:
        if isinstance(validator, InputRequired):
            required = True

    if kwargs.get("readonly"):
        read_only(field)
        kwargs["disabled"] = True
        readonly = True

    wrapper_id = kwargs.pop("wrapper_id", None)
    oob = kwargs.pop("oob", False)

    html = Markup(
        feretui.render_template(
            session,
            "feretui-fieldset",
            label=None if kwargs.pop("nolabel", False) else field.label,
            widget=field.widget(field, **kwargs),
            required=required,
            readonly=readonly,
            description=field.description,
            errors=field.errors,
        ),
    )
    if wrapper_id:
        oob_attr = ' hx-swap-oob="true"' if oob else ""
        return Markup(f'<div id="{wrapper_id}"{oob_attr}>{html}</div>')  # noqa: S704

    return html


def wrap_select_multiple(
    feretui: "FeretUI",
    session: "Session",
    field: "Field",
    **kwargs: dict,
) -> Markup:
    """Render select multiple field.

    If the select multiple field uses a `ListWidget`, it is rendered as a
    fieldset (RGAA 11.5). Otherwise, it is rendered as a standard input.

    :param feretui: The feretui client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param session: The Session
    :type session: :class:`feretui.session.Session`
    :param field: The field to validate
    :type field: Field_
    :return: The renderer of the widget as html.
    :rtype: Markup_
    """
    if isinstance(field.widget, ListWidget):
        return wrap_fieldset(feretui, session, field, **kwargs)

    return wrap_input(feretui, session, field, **kwargs)


def no_wrap(
    feretui: "FeretUI",  # noqa: ARG001
    session: "Session",  # noqa: ARG001
    field: "Field",
    **kwargs: dict,
) -> Markup:
    """Render the field widget.

    :param feretui: The feretui client
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param session: The Session
    :type session: :class:`feretui.session.Session`
    :param field: The field to validate
    :type field: Field_
    :return: The renderer of the widget as html.
    :rtype: Markup_
    """
    return field.widget(field, **kwargs)


class StatusBarWidget:
    """Widget for rendering a pipeline/workflow status bar."""

    def __init__(self: "StatusBarWidget", clickable: bool = True) -> None:
        """Initialize StatusBarWidget.

        :param clickable: Whether stage buttons can be clicked to update state.
        :type clickable: bool
        """
        self.clickable = clickable

    def __call__(
        self: "StatusBarWidget",
        field: SelectField,
        **kwargs: dict,
    ) -> Markup:
        """Render the status bar for a WTForms field.

        :param field: The WTForms field.
        :type field: :class:`wtforms.fields.SelectField`
        :return: HTML markup.
        :rtype: :class:`markupsafe.Markup`
        """
        choices = getattr(field, "choices", [])
        current_value = str(field.data) if field.data is not None else ""
        readonly = kwargs.get("readonly", False) or not self.clickable
        field_id = kwargs.get("id", field.id)
        field_name = kwargs.get("name", field.name)

        return self.render(
            stages=choices,
            current=current_value,
            readonly=readonly,
            field_id=field_id,
            field_name=field_name,
        )

    def render(
        self: "StatusBarWidget",
        stages: list[tuple[str, str]],
        current: str | None = None,
        readonly: bool = False,
        field_id: str = "status-bar",
        field_name: str = "status",
    ) -> Markup:
        """Render stages into an HTML status bar.

        :param stages: List of (key, label) tuples.
        :type stages: list[tuple[str, str]]
        :param current: Active stage key.
        :type current: str | None
        :param readonly: Whether clicking is disabled.
        :type readonly: bool
        :param field_id: HTML id attribute for hidden input.
        :type field_id: str
        :param field_name: HTML name attribute for hidden input.
        :type field_name: str
        :return: HTML markup.
        :rtype: :class:`markupsafe.Markup`
        """
        keys = [str(k) for k, _ in stages]
        current_str = str(current) if current is not None else ""
        current_idx = keys.index(current_str) if current_str in keys else -1

        items = []
        for idx, (val, label) in enumerate(stages):
            val_str = str(val)
            if idx == current_idx:
                state_cls = "is-current current"
                aria = ' aria-current="step"'
            elif current_idx != -1 and idx < current_idx:
                state_cls = "is-passed passed"
                aria = ""
            else:
                state_cls = "is-future future"
                aria = ""

            if readonly or val_str == current_str:
                btn = (
                    f'<button type="button" class="status-step {state_cls}"'
                    f" disabled{aria}>{escape(label)}</button>"
                )
            else:
                onclick = (
                    f"var el=document.getElementById('{escape(field_id)}');"
                    f"if(el){{el.value='{escape(val_str)}';"
                    "el.dispatchEvent(new Event('change',{bubbles:true}));}"
                )
                btn = (
                    f'<button type="button" class="status-step {state_cls}"'
                    f' onclick="{onclick}"{aria}>{escape(label)}</button>'
                )

            items.append(f'<li class="{state_cls}">{btn}</li>')

        hidden_input = (
            f'<input type="hidden" name="{escape(field_name)}"'
            f' id="{escape(field_id)}" value="{escape(current_str)}">'
        )
        steps_html = "".join(items)
        html = (
            '<nav class="feretui-status-bar" aria-label="Workflow Status">'
            f"{hidden_input}"
            f'<ul class="status-bar-steps">{steps_html}</ul>'
            "</nav>"
        )
        return Markup(html)  # noqa: S704


class StatusBarField(SelectField):
    """Field for workflow status bar pipeline."""

    widget = StatusBarWidget()

    def __init__(
        self: "StatusBarField",
        label: str | None = None,
        validators: list | None = None,
        choices: list[tuple[str, str]] | None = None,
        clickable: bool = True,
        **kwargs: dict,
    ) -> None:
        """Initialize StatusBarField.

        :param label: Field label.
        :type label: str | None
        :param validators: Field validators.
        :type validators: list | None
        :param choices: Stage choices (key, label).
        :type choices: list[tuple[str, str]] | None
        :param clickable: Whether user can click to change stages.
        :type clickable: bool
        """
        super().__init__(
            label=label,
            validators=validators,
            choices=choices or [],
            **kwargs,
        )
        self.widget = StatusBarWidget(clickable=clickable)


def wrap_status_bar(
    feretui: "FeretUI",
    session: "Session",
    field: StatusBarField,
    **kwargs: dict,
) -> Markup:
    """Render status bar field with optional wrapper and OOB support.

    :param feretui: The feretui client.
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param session: The Session.
    :type session: :class:`feretui.session.Session`
    :param field: The status bar field.
    :type field: :class:`StatusBarField`
    :return: HTML markup.
    :rtype: :class:`markupsafe.Markup`
    """
    wrapper_id = kwargs.pop("wrapper_id", None)
    oob = kwargs.pop("oob", False)
    widget_html = field.widget(field, **kwargs)
    html = Markup(
        feretui.render_template(
            session,
            "feretui-status-bar-field",
            label=None if kwargs.pop("nolabel", False) else field.label,
            widget=widget_html,
            description=field.description,
            errors=field.errors,
        ),
    )
    if wrapper_id:
        oob_attr = ' hx-swap-oob="true"' if oob else ""
        return Markup(f'<div id="{wrapper_id}"{oob_attr}>{html}</div>')  # noqa: S704

    return html


def wrap_hidden(
    feretui: "FeretUI",  # noqa: ARG001
    session: "Session",  # noqa: ARG001
    field: Field,
    **kwargs: dict,
) -> Markup:
    """Render hidden field without label or surrounding markup."""
    return Markup(field.widget(field, **kwargs))


class Many2OneField(SelectField):
    """Field representing a Many-to-One relationship to another Resource."""

    def __init__(
        self: "Many2OneField",
        label: str | None = None,
        validators: list | None = None,
        resource: str | None = None,
        choices: object | None = None,
        **kwargs: dict,
    ) -> None:
        """Initialize Many2OneField."""
        super().__init__(label, validators, choices=choices or [], **kwargs)
        self.target_resource = resource


def wrap_many2one(
    feretui: "FeretUI",
    session: "Session",
    field: Many2OneField,
    **kwargs: dict,
) -> Markup:
    """Render many2one field as link or select with navigation button."""
    readonly = kwargs.pop("readonly", False)
    target_resource = getattr(field, "target_resource", None)
    val = str(field.data) if field.data is not None else ""

    display_text = val
    if hasattr(field, "choices") and field.choices:
        for c_val, c_label in field.choices:
            if str(c_val) == val:
                display_text = str(c_label)
                break

    link_url = ""
    goto_url = ""
    if target_resource and val:
        link_url = (
            f"/?page=resource&resource={target_resource}&view=read&pk={val}"
        )
        base_url = getattr(feretui, "base_url", "/feretui")
        goto_url = (
            f"{base_url}/action/goto?page=resource&"
            f"resource={target_resource}&view=read&pk={val}"
        )

    wrapper_id = kwargs.pop("wrapper_id", None)
    oob = kwargs.pop("oob", False)
    widget_html = field.widget(field, **kwargs) if not readonly else ""

    html = Markup(
        feretui.render_template(
            session,
            "feretui-many2one-field",
            label=None if kwargs.pop("nolabel", False) else field.label,
            widget=widget_html,
            readonly=readonly,
            display_text=display_text,
            link_url=link_url,
            goto_url=goto_url,
            target_resource=target_resource,
            description=field.description,
            errors=field.errors,
        ),
    )
    if wrapper_id:
        oob_attr = ' hx-swap-oob="true"' if oob else ""
        return Markup(f'<div id="{wrapper_id}"{oob_attr}>{html}</div>')  # noqa: S704

    return html


class One2ManyField(Field):
    """Field representing a One-to-Many / Many-to-Many sub-table in a Form."""

    def __init__(
        self: "One2ManyField",
        label: str | None = None,
        validators: list | None = None,
        columns: list[tuple[str, str]] | None = None,
        target_resource: str | None = None,
        can_create: bool = True,
        can_edit: bool = True,
        can_delete: bool = True,
        can_view: bool = True,
        add_label: str | None = None,
        **kwargs: dict,
    ) -> None:
        """Initialize One2ManyField."""
        super().__init__(label, validators, **kwargs)
        self.columns = columns or []
        self.target_resource = target_resource
        self.can_create = can_create
        self.can_edit = can_edit
        self.can_delete = can_delete
        self.can_view = can_view
        self.add_label = add_label
        self.data: list = []

    def process_data(self: "One2ManyField", value: object) -> None:
        """Process data for One2ManyField."""
        if value is None:
            self.data = []
        elif isinstance(value, list):
            self.data = value
        elif hasattr(value, "__iter__"):
            self.data = list(value)
        else:
            self.data = []


def wrap_one2many(
    feretui: "FeretUI",
    session: "Session",
    field: One2ManyField,
    **kwargs: dict,
) -> Markup:
    """Render one2many field as an embedded sub-table."""
    readonly = kwargs.pop("readonly", False)
    target_resource = getattr(field, "target_resource", None)
    can_create = getattr(field, "can_create", True)
    can_edit = getattr(field, "can_edit", True)
    can_delete = getattr(field, "can_delete", True)
    can_view = getattr(field, "can_view", True)
    add_label = getattr(field, "add_label", None) or "Add a line"
    columns = getattr(field, "columns", [])
    first_col = columns[0][0] if columns else ""

    base_url = getattr(feretui, "base_url", "/feretui")
    create_href = (
        f"/?page=resource&resource={target_resource}&view=create"
        if target_resource
        else ""
    )
    create_goto = (
        f"{base_url}/action/goto?page=resource&resource={target_resource}&view=create"
        if target_resource
        else ""
    )

    rows: list[dict[str, object]] = []
    raw_data = getattr(field, "data", []) or []
    for item in raw_data:
        row_dict: dict[str, object] = {}
        pk_val = (
            getattr(item, "id", getattr(item, "pk", ""))
            if not isinstance(item, dict)
            else item.get("id", item.get("pk", ""))
        )
        pk_str = str(pk_val) if pk_val else ""
        row_dict["pk"] = pk_str

        row_dict["read_href"] = (
            f"/?page=resource&resource={target_resource}&view=read&pk={pk_str}"
            if target_resource and pk_str
            else ""
        )
        row_dict["read_goto"] = (
            f"{base_url}/action/goto?page=resource&"
            f"resource={target_resource}&view=read&pk={pk_str}"
            if target_resource and pk_str
            else ""
        )
        row_dict["edit_href"] = (
            f"/?page=resource&resource={target_resource}&"
            f"view=update&pk={pk_str}"
            if target_resource and pk_str
            else ""
        )
        row_dict["edit_goto"] = (
            f"{base_url}/action/goto?page=resource&"
            f"resource={target_resource}&view=update&pk={pk_str}"
            if target_resource and pk_str
            else ""
        )
        row_dict["delete_href"] = (
            f"/?page=resource&resource={target_resource}&"
            f"view=delete&pk={pk_str}"
            if target_resource and pk_str
            else ""
        )
        row_dict["delete_goto"] = (
            f"{base_url}/action/goto?page=resource&"
            f"resource={target_resource}&view=delete&pk={pk_str}"
            if target_resource and pk_str
            else ""
        )

        for col_name, _ in columns:
            if isinstance(item, dict):
                row_dict[col_name] = str(item.get(col_name, ""))
            else:
                row_dict[col_name] = str(getattr(item, col_name, ""))
        rows.append(row_dict)

    wrapper_id = kwargs.pop("wrapper_id", None)
    oob = kwargs.pop("oob", False)

    html = Markup(
        feretui.render_template(
            session,
            "feretui-one2many-field",
            label=None if kwargs.pop("nolabel", False) else field.label,
            columns=columns,
            first_column=first_col,
            rows=rows,
            target_resource=target_resource,
            create_href=create_href,
            create_goto=create_goto,
            can_create=can_create,
            can_edit=can_edit,
            can_delete=can_delete,
            can_view=can_view,
            add_label=add_label,
            readonly=readonly,
            description=field.description,
            errors=field.errors,
        ),
    )
    if wrapper_id:
        oob_attr = ' hx-swap-oob="true"' if oob else ""
        return Markup(f'<div id="{wrapper_id}"{oob_attr}>{html}</div>')  # noqa: S704

    return html


class Many2ManyField(One2ManyField):
    """Field representing a Many-to-Many relationship in a Form."""


def wrap_many2many(
    feretui: "FeretUI",
    session: "Session",
    field: Many2ManyField,
    **kwargs: dict,
) -> Markup:
    """Render many2many field as an embedded sub-table.

    :param feretui: The feretui client.
    :type feretui: :class:`feretui.feretui.FeretUI`
    :param session: The user session.
    :type session: :class:`feretui.session.Session`
    :param field: The many2many field to render.
    :type field: :class:`feretui.form.Many2ManyField`
    :return: Rendered HTML Markup.
    """
    return wrap_one2many(feretui, session, field, **kwargs)


class FileField(Field):
    """Field representing a file upload."""

    widget = FileInput()

    def __init__(
        self: "FileField",
        label: str | None = None,
        validators: list | None = None,
        allowed_extensions: list[str] | set[str] | None = None,
        max_size: int | None = None,
        **kwargs: dict,
    ) -> None:
        """Initialize FileField."""
        super().__init__(label, validators, **kwargs)
        self.allowed_extensions = (
            set(allowed_extensions) if allowed_extensions else None
        )
        self.max_size = max_size

    def process_formdata(self: "FileField", valuelist: list) -> None:
        """Process submitted form data for file."""
        if valuelist:
            self.data = valuelist[0]
        else:
            self.data = None


def wrap_file(
    feretui: "FeretUI",
    session: "Session",
    field: FileField,
    **kwargs: dict,
) -> Markup:
    """Render file upload field."""
    readonly = kwargs.pop("readonly", False)
    filename = ""
    if field.data:
        if isinstance(field.data, str):
            filename = field.data
        elif hasattr(field.data, "filename"):
            filename = str(getattr(field.data, "filename", ""))
        elif isinstance(field.data, dict):
            filename = str(field.data.get("filename", ""))

    wrapper_id = kwargs.pop("wrapper_id", None)
    oob = kwargs.pop("oob", False)
    widget_html = field.widget(field, **kwargs) if not readonly else ""

    html = Markup(
        feretui.render_template(
            session,
            "feretui-file-field",
            label=None if kwargs.pop("nolabel", False) else field.label,
            widget=widget_html,
            readonly=readonly,
            filename=filename,
            description=field.description,
            errors=field.errors,
        ),
    )
    if wrapper_id:
        oob_attr = ' hx-swap-oob="true"' if oob else ""
        return Markup(f'<div id="{wrapper_id}"{oob_attr}>{html}</div>')  # noqa: S704

    return html


class MultiFileField(Field):
    """Field representing multiple file uploads."""

    widget = FileInput(multiple=True)

    def __init__(
        self: "MultiFileField",
        label: str | None = None,
        validators: list | None = None,
        allowed_extensions: list[str] | set[str] | None = None,
        max_size: int | None = None,
        **kwargs: dict,
    ) -> None:
        """Initialize MultiFileField."""
        super().__init__(label, validators, **kwargs)
        self.allowed_extensions = (
            set(allowed_extensions) if allowed_extensions else None
        )
        self.max_size = max_size

    def process_formdata(self: "MultiFileField", valuelist: list) -> None:
        """Process submitted form data for multiple files."""
        self.data = list(valuelist) if valuelist else []

    def process_data(self: "MultiFileField", value: object) -> None:
        """Process initial data loaded into field."""
        if value is None:
            self.data = []
        elif isinstance(value, list):
            self.data = value
        elif hasattr(value, "__iter__") and not isinstance(value, str):
            self.data = list(value)
        else:
            self.data = [value]


def wrap_multi_file(
    feretui: "FeretUI",
    session: "Session",
    field: MultiFileField,
    **kwargs: dict,
) -> Markup:
    """Render multiple files upload field."""
    readonly = kwargs.pop("readonly", False)
    filenames: list[str] = []
    if field.data:
        items = field.data if isinstance(field.data, list) else [field.data]
        for it in items:
            if isinstance(it, str):
                filenames.append(it)
            elif hasattr(it, "filename"):
                filenames.append(str(getattr(it, "filename", "")))
            elif isinstance(it, dict):
                filenames.append(str(it.get("filename", "")))

    filename_str = ", ".join(filenames)
    wrapper_id = kwargs.pop("wrapper_id", None)
    oob = kwargs.pop("oob", False)
    widget_html = field.widget(field, **kwargs) if not readonly else ""

    html = Markup(
        feretui.render_template(
            session,
            "feretui-file-field",
            label=None if kwargs.pop("nolabel", False) else field.label,
            widget=widget_html,
            readonly=readonly,
            filename=filename_str,
            description=field.description,
            errors=field.errors,
        ),
    )
    if wrapper_id:
        oob_attr = ' hx-swap-oob="true"' if oob else ""
        return Markup(f'<div id="{wrapper_id}"{oob_attr}>{html}</div>')  # noqa: S704

    return html


class ImageField(FileField):
    """Field representing an image upload with preview."""

    def __init__(
        self: "ImageField",
        label: str | None = None,
        validators: list | None = None,
        is_avatar: bool = False,
        **kwargs: dict,
    ) -> None:
        """Initialize ImageField."""
        super().__init__(label, validators, **kwargs)
        self.is_avatar = is_avatar


def wrap_image(
    feretui: "FeretUI",
    session: "Session",
    field: ImageField,
    **kwargs: dict,
) -> Markup:
    """Render image upload field with preview."""
    readonly = kwargs.pop("readonly", False)
    image_url = ""
    if field.data:
        if isinstance(field.data, str):
            image_url = field.data
        elif hasattr(field.data, "filename"):
            image_url = str(getattr(field.data, "filename", ""))
        elif isinstance(field.data, dict):
            image_url = str(
                field.data.get("url", field.data.get("filename", "")),
            )

    wrapper_id = kwargs.pop("wrapper_id", None)
    oob = kwargs.pop("oob", False)
    is_avatar = getattr(field, "is_avatar", False)
    widget_html = field.widget(field, **kwargs) if not readonly else ""

    html = Markup(
        feretui.render_template(
            session,
            "feretui-image-field",
            label=None if kwargs.pop("nolabel", False) else field.label,
            widget=widget_html,
            readonly=readonly,
            image_url=image_url,
            is_avatar=is_avatar,
            description=field.description,
            errors=field.errors,
        ),
    )
    if wrapper_id:
        oob_attr = ' hx-swap-oob="true"' if oob else ""
        return Markup(f'<div id="{wrapper_id}"{oob_attr}>{html}</div>')  # noqa: S704

    return html


class MonetaryField(DecimalField):
    """Field representing a monetary / currency amount."""

    def __init__(
        self: "MonetaryField",
        label: str | None = None,
        validators: list | None = None,
        places: int = 2,
        currency: str = "€",
        currency_position: str = "after",
        **kwargs: dict,
    ) -> None:
        """Initialize MonetaryField."""
        super().__init__(label, validators, places=places, **kwargs)
        self.currency = currency
        self.currency_position = currency_position

    def _value(self: "MonetaryField") -> str:
        """Format the decimal value safely."""
        if self.raw_data:
            return self.raw_data[0]
        if self.data is None:
            return ""
        try:
            return f"{float(self.data):.{self.places}f}"
        except (ValueError, TypeError):
            return str(self.data)


def wrap_monetary(
    feretui: "FeretUI",
    session: "Session",
    field: MonetaryField,
    **kwargs: dict,
) -> Markup:
    """Render monetary field with currency symbol."""
    readonly = kwargs.pop("readonly", False)
    currency = getattr(field, "currency", "€")
    currency_pos = getattr(field, "currency_position", "after")
    val_str = ""
    if field.data is not None:
        try:
            val_str = f"{float(field.data):.2f}"
        except (ValueError, TypeError):
            val_str = str(field.data)

    wrapper_id = kwargs.pop("wrapper_id", None)
    oob = kwargs.pop("oob", False)
    render_kw = kwargs.setdefault("render_kw", {})
    existing_class = render_kw.get("class", "")
    render_kw["class"] = f"{existing_class} feretui-monetary".strip()
    widget_html = field.widget(field, **kwargs) if not readonly else ""

    html = Markup(
        feretui.render_template(
            session,
            "feretui-monetary-field",
            label=None if kwargs.pop("nolabel", False) else field.label,
            widget=widget_html,
            readonly=readonly,
            value=val_str,
            currency=currency,
            currency_position=currency_pos,
            description=field.description,
            errors=field.errors,
        ),
    )
    if wrapper_id:
        oob_attr = ' hx-swap-oob="true"' if oob else ""
        return Markup(f'<div id="{wrapper_id}"{oob_attr}>{html}</div>')  # noqa: S704

    return html


class TagsField(Field):
    """Field representing tags or badges."""

    widget = TextInput()

    def __init__(
        self: "TagsField",
        label: str | None = None,
        validators: list | None = None,
        separator: str = ",",
        **kwargs: dict,
    ) -> None:
        """Initialize TagsField."""
        super().__init__(label, validators, **kwargs)
        self.separator = separator
        self.data: list[str] = []

    def _value(self: "TagsField") -> str:
        """Return the string representation for the widget."""
        return self.separator.join(self.data) if self.data else ""

    def process_formdata(self: "TagsField", valuelist: list) -> None:
        """Process form data from user input."""
        if valuelist:
            raw = valuelist[0]
            if isinstance(raw, str):
                self.data = [
                    t.strip() for t in raw.split(self.separator) if t.strip()
                ]
            elif isinstance(raw, list):
                self.data = [str(t).strip() for t in raw if str(t).strip()]
            else:
                self.data = []
        else:
            self.data = []

    def process_data(self: "TagsField", value: object) -> None:
        """Process initial data loaded into field."""
        if value is None:
            self.data = []
        elif isinstance(value, str):
            self.data = [
                t.strip() for t in value.split(self.separator) if t.strip()
            ]
        elif isinstance(value, list | tuple | set):
            self.data = [str(t).strip() for t in value if str(t).strip()]
        else:
            self.data = []


def wrap_tags(
    feretui: "FeretUI",
    session: "Session",
    field: TagsField,
    **kwargs: dict,
) -> Markup:
    """Render tags field as badges and input."""
    readonly = kwargs.pop("readonly", False)
    tags = getattr(field, "data", []) or []

    wrapper_id = kwargs.pop("wrapper_id", None)
    oob = kwargs.pop("oob", False)
    widget_html = field.widget(field, **kwargs) if not readonly else ""

    html = Markup(
        feretui.render_template(
            session,
            "feretui-tags-field",
            label=None if kwargs.pop("nolabel", False) else field.label,
            widget=widget_html,
            readonly=readonly,
            tags=tags,
            description=field.description,
            errors=field.errors,
        ),
    )
    if wrapper_id:
        oob_attr = ' hx-swap-oob="true"' if oob else ""
        return Markup(f'<div id="{wrapper_id}"{oob_attr}>{html}</div>')  # noqa: S704

    return html


class WYSIWYGField(Field):
    """Field representing a rich-text / WYSIWYG editor."""

    widget = TextArea()

    def __init__(
        self: "WYSIWYGField",
        label: str | None = None,
        validators: list | None = None,
        min_height: str = "200px",
        placeholder: str | None = None,
        **kwargs: dict,
    ) -> None:
        """Initialize WYSIWYGField."""
        super().__init__(label, validators, **kwargs)
        self.min_height = min_height
        self.placeholder = placeholder or ""


RichTextField = WYSIWYGField
HtmlField = WYSIWYGField


def wrap_wysiwyg(
    feretui: "FeretUI",
    session: "Session",
    field: WYSIWYGField,
    **kwargs: dict,
) -> Markup:
    """Render WYSIWYG editor field."""
    readonly = kwargs.pop("readonly", False)
    val = str(field.data) if field.data is not None else ""
    min_height = getattr(field, "min_height", "200px")
    placeholder = getattr(field, "placeholder", "")

    wrapper_id = kwargs.pop("wrapper_id", None)
    oob = kwargs.pop("oob", False)

    html = Markup(
        feretui.render_template(
            session,
            "feretui-wysiwyg-field",
            field=field,
            label=None if kwargs.pop("nolabel", False) else field.label,
            readonly=readonly,
            value=val,
            min_height=min_height,
            placeholder=placeholder,
            description=field.description,
            errors=field.errors,
        ),
    )
    if wrapper_id:
        oob_attr = ' hx-swap-oob="true"' if oob else ""
        return Markup(f'<div id="{wrapper_id}"{oob_attr}>{html}</div>')  # noqa: S704

    return html


def gettext(
    form: Form,
    string: str,
    context_suffix: str = "",
) -> str:
    """Translate the string."""
    feret = cvar_feretui.get(None)
    req = cvar_request.get(None)
    if not feret or not req or not hasattr(req, "session"):
        return string

    translation = feret.translation
    lang = req.session.lang
    for form_cls in form.__mro__:
        if hasattr(form_cls, "get_context"):
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
        args = list(args)
        args[0] = callback(form_cls, args[0], context_suffix + "label")
        args = tuple(args)
    elif unbound_field.kwargs.get("label"):
        kwargs["label"] = callback(
            form_cls,
            kwargs["label"],
            context_suffix + "label",
        )
    else:
        label = options["name"].replace("_", " ").title()
        kwargs["label"] = callback(form_cls, label, context_suffix + "label")

    if kwargs.get("description"):
        kwargs["description"] = callback(
            form_cls,
            kwargs.get("description", ""),
            context_suffix + "description",
        )

    if "choices" in kwargs:
        choices = kwargs.pop("choices")
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
                context_suffix + f"choice:{choice[0]}:label",
            )
            if len(choice) == 3 and choice[2].get("description"):
                choice[2]["description"] = callback(
                    form_cls,
                    choice[2]["description"],
                    context_suffix + f"choice:{choice[0]}:description",
                )

        kwargs["choices"] = new_choices

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


def onchange(*fields: str) -> Callable[[Callable], Callable]:
    """Register a method of FeretUIForm as an onchange handler for fields.

    ::

        class OrderLineForm(FeretUIForm):
            price = DecimalField()
            quantity = IntegerField()
            subtotal = DecimalField()

            @onchange("price", "quantity")
            def _calc_subtotal(self) -> None:
                self.subtotal.data = (
                    (self.price.data or 0) * (self.quantity.data or 0)
                )

    :param fields: The field names that trigger this onchange method
    :type fields: tuple[str, ...]
    :return: Decorator function
    :rtype: Callable
    """

    def decorator(func: Callable) -> Callable:
        func._onchange_fields = list(fields)
        return func

    return decorator


class FeretUIForm(Form):
    """Form base class.

    The goal is to give at the Form used by FeretUI the behaviour like:

    * translation
    * bulma renderer
    * onchange HTMX reactivity

    It is not required to used it. If the translation or the renderer is not
    automaticly done by FeretUI.

    ::

        class MyForm(FeretUIForm):
            name = StringField()

    """

    onchange_warning: str | None = None

    @classmethod
    def get_onchange_handlers(
        cls: type["FeretUIForm"],
    ) -> dict[str, list[Callable]]:
        """Return mapping of triggering field name to list of handler methods.

        :return: Dict mapping field names to list of handler callables
        :rtype: dict[str, list[Callable]]
        """
        handlers: dict[str, list[Callable]] = {}
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name, None)
            if callable(attr) and hasattr(attr, "_onchange_fields"):
                for field_name in attr._onchange_fields:
                    handlers.setdefault(field_name, []).append(attr)
        return handlers

    @classmethod
    def has_onchange(cls: type["FeretUIForm"]) -> bool:
        """Return True if form has any onchange handlers.

        :return: True if form has onchange handlers
        :rtype: bool
        """
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name, None)
            if callable(attr) and hasattr(attr, "_onchange_fields"):
                return True
        return False

    def process_onchange(
        self: "FeretUIForm",
        changed_field: str,
    ) -> list[str]:
        """Execute onchange handlers for `changed_field`.

        :param changed_field: Name of the field that changed
        :type changed_field: str
        :return: List of names of fields that were modified by handlers
        :rtype: list[str]
        """
        handlers = self.get_onchange_handlers().get(changed_field, [])
        initial_values = {
            name: getattr(self, name).data for name in self._fields
        }
        for handler in handlers:
            handler(self)

        return [
            name
            for name, initial_val in initial_values.items()
            if getattr(self, name).data != initial_val
        ]

    WRAPPERS = {
        BooleanField: wrap_bool,
        FormField: wrap_fieldset,
        RadioField: wrap_radio,
        SelectFieldBase._Option: no_wrap,
        SelectMultipleField: wrap_select_multiple,
        StatusBarField: wrap_status_bar,
        Many2OneField: wrap_many2one,
        One2ManyField: wrap_one2many,
        Many2ManyField: wrap_many2many,
        HiddenField: wrap_hidden,
        FileField: wrap_file,
        MultiFileField: wrap_multi_file,
        ImageField: wrap_image,
        MonetaryField: wrap_monetary,
        TagsField: wrap_tags,
        WYSIWYGField: wrap_wysiwyg,
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
        "Not a valid time.",
        "Not a valid decimal range value",
        "Not a valid float range value",
        "Not a valid int range value",
        "Not a valid date range value",
        "Not a valid datetime range value",
        "Not a valid choice",
        "Not a valid color.",
        "Invalid choice(s): one or more data inputs could not be coerced",
        "'%(value)s' is not a valid choice for this field",
        "Date must be greater than %(min)s.",
        "Date must be less than %(max)s.",
        "Date must be between %(min)s and %(max)s.",
        "Time must be greater than %(min)s.",
        "Time must be less than %(max)s.",
        "Time must be between %(min)s and %(max)s.",
        "This field contains invalid JSON",
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
        return f"form:{cls.__module__}:{cls.__name__}"

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

            get_field_translations(cls, field_cls, {"name": attr}, callback)

    class Meta(ContextProperties):
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

            Added translation for the field and automatic HTMX onchange hook
            """
            args, kwargs = get_field_translations(
                form.__class__,
                unbound_field,
                options,
                gettext,
            )
            field_name = options.get("name")
            if isinstance(form, FeretUIForm) and form.__class__.has_onchange():
                handlers = form.__class__.get_onchange_handlers()
                if field_name in handlers:
                    render_kw = kwargs.setdefault("render_kw", {})
                    if (
                        "hx-post" not in render_kw
                        and "hx_post" not in render_kw
                    ):
                        feret = cvar_feretui.get(None)
                        base_url = feret.base_url if feret else "/feretui"
                        render_kw["hx-post"] = (
                            f"{base_url}/action/resource"
                            f"?action=onchange&field={field_name}"
                        )
                        render_kw["hx-trigger"] = "change"
                        render_kw["hx-swap"] = "none"

            bound_field = UnboundField(
                unbound_field.field_class,
                *args,
                **kwargs,
            ).bind(form=form, **options)
            bound_field._form = form
            return bound_field

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

            form = getattr(field, "_form", None)
            if (
                form is not None
                and hasattr(form.__class__, "has_onchange")
                and form.__class__.has_onchange()
                and "wrapper_id" not in render_kw
            ):
                render_kw["wrapper_id"] = f"field-{field.name}-wrapper"

            wrapper = FeretUIForm.DEFAULT_WRAPPER
            for cls in field.__class__.__mro__:
                if cls in FeretUIForm.WRAPPERS:
                    wrapper = FeretUIForm.WRAPPERS[cls]
                    break
            return wrapper(
                self.feretui,
                self.request.session,
                field,
                **render_kw,
            )

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
    "The password should have {msg}.",
)
PasswordMinSize = FeretUIForm.register_translation(
    "more than {min_size} caractere",
)
PasswordMaxSize = FeretUIForm.register_translation(
    "less than {max_size} caractere",
)
PasswordWithLowerCase = FeretUIForm.register_translation("with lowercase")
PasswordWithoutLowerCase = FeretUIForm.register_translation("without lowercase")
PasswordWithUpperCase = FeretUIForm.register_translation("with uppercase")
PasswordWithoutUpperCase = FeretUIForm.register_translation("without uppercase")
PasswordWithLetters = FeretUIForm.register_translation("with letters")
PasswordWithoutLetters = FeretUIForm.register_translation("without letters")
PasswordWithDigits = FeretUIForm.register_translation("with digits")
PasswordWithoutDigits = FeretUIForm.register_translation("without digits")
PasswordWithSymbols = FeretUIForm.register_translation("with symbols")
PasswordWithoutSymbols = FeretUIForm.register_translation("without symbols")
PasswordWithSpaces = FeretUIForm.register_translation("with spaces")
PasswordWithoutSpaces = FeretUIForm.register_translation("without spaces")


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
            self.waiting.append(
                (
                    PasswordMinSize,
                    {"min_size": min_size},
                ),
            )

        if max_size:
            self.schema.min(max_size)
            self.waiting.append(
                (
                    PasswordMaxSize,
                    {"max_size": max_size},
                ),
            )

        for has, attr, true_msg, false_msg in (
            (
                has_lowercase,
                "lowercase",
                PasswordWithLowerCase,
                PasswordWithoutLowerCase,
            ),
            (
                has_uppercase,
                "uppercase",
                PasswordWithUpperCase,
                PasswordWithoutUpperCase,
            ),
            (
                has_letters,
                "letters",
                PasswordWithLetters,
                PasswordWithoutLetters,
            ),
            (has_digits, "digits", PasswordWithDigits, PasswordWithoutDigits),
            (
                has_symbols,
                "symbols",
                PasswordWithSymbols,
                PasswordWithoutSymbols,
            ),
            (has_spaces, "spaces", PasswordWithSpaces, PasswordWithoutSpaces),
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
                msg=", ".join(
                    field.gettext(x[0]).format(**x[1]) for x in self.waiting
                ),
            )
            raise ValidationError(msg)
