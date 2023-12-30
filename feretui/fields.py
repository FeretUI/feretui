from typing import TYPE_CHECKING, Any, Callable, Optional

import polib
from lxml import html
from lxml.etree import Element, SubElement
from pydantic import Field as PField
from pydantic import field_validator

from feretui.exceptions import FieldError
from feretui.schema import required_validator
from feretui.session import Session
from feretui.translate import Translation

if TYPE_CHECKING:
    from feretui.feretui import FeretUI
    from feretui.resource import Data, Resource
    from feretui.view import View


class Field:
    _pydantic_type = Any
    ro_without_label_template_name: str = 'feretui-field-ro'
    ro_with_label_template_name: str = None
    filter_template_name: str = None

    def __init__(
        self,
        label: str = None,
        required: bool | list[str] | Callable[Session, bool] = False,
        readonly: bool | list[str] | Callable[Session, bool] = False,
        invisible: bool | list[str] | Callable[Session, bool] = False,
        default: Any = None,
    ):
        self.name: str = None  # filled by resource
        self.Resource: "Resource" = None  # filled by resource
        self.label = label
        self.required = required
        self.readonly = readonly
        self.invisible = invisible
        self.default = default

    def register_sub_entries(self, Resource: "Resource"):
        self.Resource = Resource

    def export_catalog(self, po: polib.POEntry):
        if self.label is None:
            self.label = self.name.capitalize()

        po.append(Translation.define(
            f'resource:{self.Resource._code}:field:{self.name}:label',
            self.label,
        ))

    def get_label(self, el: Element = None) -> str:
        if el and el.attrib.get('label'):
            return el.attrib['label']

        if self.label is None:
            self.label = self.name.capitalize()

        lang = Translation.local.lang
        return Translation.get(
            lang,
            f'resource:{self.Resource._code}:field:{self.name}:label',
            self.label,
        )
        return self.label

    def is_(
        self,
        attr: str,
        session: Session,
        el: Element = None,
        view_type: str = None
    ) -> bool:
        if el and el.attrib.get(attr) == attr:
            return True

        entry = getattr(self, attr)
        if isinstance(entry, list):
            return view_type in entry

        if callable(entry):
            return entry(session)

        return entry

    def is_required(
        self,
        session: Session,
        el: Element = None,
        view_type: str = None
    ):
        return self.is_('required', session, el=el, view_type=view_type)

    def is_readonly(
        self,
        session: Session,
        el: Element = None,
        view_type: str = None,
    ):
        return self.is_('readonly', session, el=el, view_type=view_type)

    def is_invisible(
        self,
        session: Session,
        el: Element = None,
        view_type: str = None,
    ):
        return self.is_('invisible', session, el=el, view_type=view_type)

    def get_default(self):
        if not self.default:
            return ''

        if callable(self.default):
            return self.default()

        return self.default

    def get_pydantic_field(
        self,
        session: Session,
        view: "View",
        pydantic_fields: dict,
        use_default: bool = True
    ) -> None:
        if (
            self.is_readonly(session, None, view.template_type)
            or self.is_invisible(session, None, view.template_type)
        ):
            return

        pydantic_type = self._pydantic_type
        field_kwargs = {}
        if self.is_required(session, None, view) is False:
            pydantic_type = Optional[pydantic_type]

        if use_default and self.default is not None:
            if callable(self.default):
                field_kwargs['default_factory'] = self.default
            else:
                field_kwargs['default'] = self.default

        pydantic_fields[self.name] = (
            pydantic_type,
            PField(**field_kwargs),
        )

    def get_pydantic_validators(
        self,
        session: Session,
        view: "View",
        pydantic_validators: dict,
    ):
        if (
            self.is_readonly(session, None, view.template_type)
            or self.is_invisible(session, None, view.template_type)
        ):
            return

        if self.is_required(session, None, view):
            pydantic_validators.update({
                f'field_{self.name}_required': field_validator(
                    self.name)(required_validator)
            })

    def get_render_ro_without_label(
        self,
        feretui: "FeretUI",
        session: Session,
        value: Any
    ):
        if not self.ro_without_label_template_name:
            raise FieldError('ro_without_label_template_name is empty')

        return feretui.load_page_template(
            session,
            self.ro_without_label_template_name,
            label=False,
            value=value,
        )

    def get_render_filter(
        self,
        feretui: "FeretUI",
        session: Session,
        Resource: "Resource",
    ):
        if not self.filter_template_name:
            raise FieldError('filter_template_name is empty')

        return feretui.load_page_template(
            session,
            self.filter_template_name,
            Resource=Resource,
            name=self.name,
            label=self.get_label(),
        )

    def get_render_rw_with_label(
        self,
        feretui: "FeretUI",
        session: Session,
        view: "View",
        el: Element,
        data: "Data",
    ):
        field = Element('div')
        field.set('class', 'field')

        label = SubElement(field, 'label')
        label.set('class', 'label')
        label.text = self.get_label(el)

        control = SubElement(field, 'div')
        control.set('class', 'control')
        self.get_render_rw_with_label_input(
            feretui, session, view, control, el, data)

        return html.tostring(field, encoding='unicode')

    def get_render_ro_with_label(
        self,
        feretui: "FeretUI",
        session: Session,
        view: "View",
        el: Element,
        data: "Data",
    ):
        if not self.ro_with_label_template_name:
            raise FieldError('ro_with_label_template_name is empty')

        return feretui.load_page_template(
            session,
            self.ro_with_label_template_name,
            name=self.name,
            label=self.get_label(el),
            value=data.get(self.name) or '',
        )


class InputTypeMixin:

    def format_input_value(self, value):
        return value

    def get_render_rw_with_label_input(
        self,
        feretui: "FeretUI",
        session: Session,
        view: "View",
        control: Element,
        el: Element,
        data: "Data",
    ):
        input_class = ['input']
        _input = SubElement(control, 'input')
        _input.set('name', self.name)

        value = self.format_input_value(data.get(self.name))
        if value is not None:
            _input.set('value', value)

        if self.is_readonly(session, el, view.template_type):
            input_class.append('is-static')
            _input.set('readonly', 'readonly')
        elif self.is_required(session, el, view.template_type):
            input_class.append('is-link')
            _input.set('required', 'required')

        _input.set('class', ' '.join(input_class))

        return _input


class String(InputTypeMixin, Field):
    _pydantic_type = str
    ro_with_label_template_name: str = 'feretui-field-string-ro'
    filter_template_name: str = 'feretui-field-string-filter'

    def get_render_rw_with_label_input(
        self,
        feretui: "FeretUI",
        session: Session,
        view: "View",
        control: Element,
        el: Element,
        data: "Data",
    ):
        _input = super().get_render_rw_with_label_input(
            feretui, session, view, control, el, data)
        _input.set('type', 'text')
        return _input


class Integer(InputTypeMixin, Field):
    _pydantic_type = int
    ro_with_label_template_name: str = 'feretui-field-integer-ro'
    filter_template_name: str = 'feretui-field-integer-filter'

    def format_input_value(self, value):
        return str(value)

    def get_render_rw_with_label_input(
        self,
        feretui: "FeretUI",
        session: Session,
        view: "View",
        control: Element,
        el: Element,
        data: "Data",
    ):
        _input = super().get_render_rw_with_label_input(
            feretui, session, view, control, el, data)
        _input.set('type', 'number')
        _input.set('step', "1")
        return _input
