import urllib
from typing import TYPE_CHECKING, Callable

import polib
from lxml import html
from lxml.etree import Element
from pydantic import BaseModel, create_model

from feretui.exceptions import DatasetError, ResourceFilterError, ViewError
from feretui.fields import Field
from feretui.request import Request
from feretui.session import Session
from feretui.translate import Translation

if TYPE_CHECKING:
    from feretui.feretui import FeretUI
    from feretui.resource import Resource


class Data(dict):
    pass


class Dataset:
    def __init__(self, data: list[tuple[str, Data]], total: int):
        self.data = data
        self.total = total


class Filter:

    def __init__(self, field: Field, code: str = None):
        self.field = field
        self.code = code
        self.Resource: "Resource" = None  # filled by resource

    def render(
        self,
        feretui: "FeretUI",
        session: Session,
    ):
        if not self.field.name:
            if not self.code:
                raise ResourceFilterError('No code defined')

            self.field.name = self.code

        return self.field.get_render_filter(feretui, session, self.Resource)

    def register_sub_entries(self, Resource: "Resource"):
        self.Resource = Resource
        self.field.register_sub_entries(Resource)


class Action:

    def __init__(
        self,
        label: str,
        method: str,
        code: str = None,
        invisible: bool | Callable[Session, bool] = False,
    ):
        self.actionset: "Actionset" = None  # filled by resource
        self.label = label
        self.method = method
        self.code = code or method
        self.url = f'/feretui/action/resource-action?code={self.code}'
        self.invisible = invisible

    def register_sub_entries(self, actionset: "Actionset"):
        self.actionset = actionset

    def export_catalog(self, po: polib.POEntry):
        po.append(Translation.define(
            (
                f'resource:{self.actionset.view.Resource._code}:'
                f'view:{self.actionset.view.__class__.__name__}:'
                f'actionset:action:{self.code}:label'
            ),
            self.label,
        ))

    def get_label(self):
        lang = Translation.local.lang
        return Translation.get(
            lang,
            (
                f'resource:{self.actionset.view.Resource._code}:'
                f'view:{self.actionset.view.__class__.__name__}:'
                f'actionset:action:{self.code}:label'
            ),
            self.label,
        )

    def render(
        self,
        feret: "FeretUI",
        session: Session,
        Resource: "Resource",
        row_number: str,
    ):
        url = f'/feretui/action/resource-row_action?code={self.code}'
        return feret.load_page_template(
            session,
            'feretui-field-action',
            url=url,
            Resource=Resource,
            id=row_number,
            label=self.get_label(),
        )

    def is_invisible(
        self,
        session: Session,
    ) -> bool:
        if callable(self.invisible):
            return self.invisible(session)

        return self.invisible


class Actionset:

    def __init__(self, label: str, actions: list[Action]):
        self.view: "View" = None  # filled by resource
        self.label = label
        self.actions = actions

    def get_label(self):
        lang = Translation.local.lang
        return Translation.get(
            lang,
            (
                f'resource:{self.view.Resource._code}:'
                f'view:{self.view.__class__.__name__}:'
                'actionset:label'
            ),
            self.label,
        )

    def register_sub_entries(self, view: "View"):
        self.view = view
        for action in self.actions:
            action.register_sub_entries(self)

    def export_catalog(self, po: polib.POEntry):
        po.append(Translation.define(
            (
                f'resource:{self.view.Resource._code}:'
                f'view:{self.view.__class__.__name__}:'
                'actionset:label'
            ),
            self.label,
        ))
        for action in self.actions:
            action.export_catalog(po)

    def get_render_buttons(
        self,
        feret: "FeretUI",
        session: Session,
        Resource: "Resource",
        row_number: str,
    ):
        return feret.load_page_template(
            session,
            'feretui-field-action-set',
            Resource=Resource,
            id=row_number,
            label=self.get_label(),
            actions=self.actions,
        )

    def is_invisible(
        self,
        session: Session,
        el: Element = None,
        view_type: str = None
    ) -> bool:
        return all([
            action.is_invisible(session)
            for action in self.actions
        ])


class View:

    def __init__(
        self,
        label: str = None,
    ):
        self.Resource: "Resource" = None  # filled by resource
        self.label = label

    def register_sub_entries(self, Resource: "Resource"):
        self.Resource = Resource

    def export_catalog(self, po: polib.POEntry):
        po.append(Translation.define(
            (
                f'resource:{self.Resource._code}:'
                f'view:{self.__class__.__name__}:label'
            ),
            self.label,
        ))

    def get_label(self, resource_label: str):
        lang = Translation.local.lang
        return Translation.get(
            lang,
            (
                f'resource:{self.Resource._code}:'
                f'view:{self.__class__.__name__}:label'
            ),
            self.label,
        )

    def get_actions(
        self,
        feret: "FeretUI",
        session: Session,
        ResourceCls: "Resource",
    ):
        return []

    def render(
        self,
        feret: "FeretUI",
        session: Session,
        options: dict[str, list[str]],
        ResourceCls: "Resource",
    ) -> str:
        raise ViewError('render must be overwriting')

    def get_transition_querystring(
        self,
        options: dict,
        **kwargs: dict[str, str],
    ):
        options = options.copy()
        for key, value in kwargs.items():
            if value is None:
                options.pop(key, None)
            elif isinstance(value, list):
                options[key] = value
            else:
                options[key] = [value]

        return urllib.parse.urlencode(options, doseq=True)


class ActionsMixinForView:

    def __init__(
        self,
        actions: list[Actionset] = None,
    ):
        self.actions = actions

    def get_actions(
        self,
        feret: "FeretUI",
        session: Session,
        ResourceCls: "Resource",
    ):
        res = super().get_actions(feret, session, ResourceCls)
        res.extend([
            feret.load_page_template(
                session,
                'feretui-page-resource-action-set',
                actionset=actionset,
                Resource=ResourceCls,
            )
            for actionset in self.actions
            if not actionset.is_invisible(session, None, self.template_type)
        ])
        return res

    def register_sub_entries(self, Resource: "Resource"):
        super().register_sub_entries(Resource)
        for actionset in self.actions:
            actionset.register_sub_entries(self)

    def export_catalog(self, po: polib.POEntry):
        super().export_catalog(po)
        for actionset in self.actions:
            actionset.export_catalog(po)


class ListView(ActionsMixinForView, View):
    template_type: str = 'list'

    def __init__(
        self,
        fields: list[Field] = None,
        filters: list[Filter] = None,
        limit: int = 15,
        label: str = None,
        actions: list[Actionset] = None,
    ):
        View.__init__(self, label=label)
        ActionsMixinForView.__init__(self, actions=actions)
        self.fields = fields
        self.filters = filters
        self.limit = limit

    def register_sub_entries(self, Resource: "Resource"):
        super().register_sub_entries(Resource=Resource)
        for field in self.fields:
            if isinstance(field, Actionset):
                field.register_sub_entries(self)

        for filter_ in self.filters:
            filter_.register_sub_entries(Resource)

    def export_catalog(self, po: polib.POEntry):
        super().export_catalog(po)
        if self.fields:
            for field in self.fields:
                if isinstance(field, Actionset):
                    field.export_catalog(po)

    def get_actions(
        self,
        feret: "FeretUI",
        session: Session,
        ResourceCls: "Resource",
    ):
        res = super().get_actions(feret, session, ResourceCls)
        if self.filters:
            res.insert(
                0,
                feret.load_page_template(
                    session,
                    'feretui-page-resource-filter',
                    filters=self.filters,
                )
            )

        return res

    def render(
        self,
        feret: "FeretUI",
        session: Session,
        options: dict,
        ResourceCls: "Resource",
    ) -> str:
        fields = self.fields
        if fields is None:
            fields = ResourceCls.get_all_fields()

        fields = [
            field
            for field in fields
            if not field.is_invisible(session, None, self.template_type)
        ]

        fields_str = [f.name for f in fields if isinstance(f, Field)]
        filters = [
            tuple(k.split('-')[1:] + [v[0].split(',')])
            for k, v in options.items()
            if k.startswith('filter-')
        ]
        offset = options.get('offset', 0)
        if isinstance(offset, list):
            offset = offset[0]

        offset = int(offset)
        dataset = ResourceCls.filtered_reads(
            filters,
            fields_str,
            offset,
            self.limit,
        )
        if not isinstance(dataset, Dataset):
            raise DatasetError(f'{dataset} is not a Dataset')

        paginations = range(0, dataset.total, self.limit)

        create_view_qs = self.get_transition_querystring(
            options,
            view=ResourceCls.on_list_create_button_redirect_to,
        )

        open_view_qs = self.get_transition_querystring(
            options,
            id=None,
            view=ResourceCls.on_list_do_click_on_row_redirect_to,
        )

        return feret.load_page_template(
            session,
            'feretui-page-resource-list',
            label=self.get_label(ResourceCls.get_label()),
            Resource=ResourceCls,
            fields=fields,
            filters=filters,
            offset=offset,
            limit=self.limit,
            paginations=paginations,
            dataset=dataset,
            create_view_qs=create_view_qs,
            open_view_qs=open_view_qs,
        )


class TemplateMixinForView:

    def __init__(
        self,
        template_id: str = None,
        template_src: str = None,
    ):
        self.template_id = template_id
        self.template_src = template_src
        self._fields: list[Field] = None
        self._pydantic_model: dict[str, BaseModel] = {}
        self._pydantic_use_default: bool = True

    def _get_template(
        self,
        feret: "FeretUI",
        session: Session,
        ResourceCls: "Resource",
    ) -> str:
        if self.template_src:
            pass
        elif self.template_id:
            self.template_src = feret.load_page_template(
                session,
                self.template_id
            )
        else:
            fields = ResourceCls.get_all_fields()
            self.template_src = feret.load_page_template(
                session,
                'feretui-view-autogenerated-template',
                fields=fields,
            )

        return html.fromstring(self.template_src)

    def get_field_names_from_template(
        self,
        feret: "FeretUI",
        session: Session,
        ResourceCls: "Resource",
    ) -> list[str]:
        if not self._fields:
            element = self._get_template(feret, session, ResourceCls)
            self._fields = [
                getattr(ResourceCls, el.attrib['name'])
                for el in element.findall('.//field')
            ]

        return self._fields

    def get_template(
        self,
        feret: "FeretUI",
        session: Session,
        options: dict,
        ResourceCls: "Resource",
        data: Data,
        render_field_method: str = 'get_render_rw_with_label',
    ) -> str:
        element = self._get_template(feret, session, ResourceCls)
        for el in element.findall('.//field'):
            el.tag = 'div'
            field = getattr(ResourceCls, el.attrib['name'])
            if field.is_invisible(session, el, self.template_type):
                continue

            field_tmpl = getattr(field, render_field_method)(
                feret, session, self, el, data)
            if isinstance(field_tmpl, str):
                field_tmpl = html.fromstring(field_tmpl)

            el.append(field_tmpl)

        return html.tostring(element, encoding='unicode')

    def get_pydantic_schema(
        self,
        feret: "FeretUI",
        request: Request,
        ResourceCls: "Resource",
    ) -> BaseModel:
        session = request.session
        fields = self.get_field_names_from_template(
            feret, request.session, ResourceCls)
        if not self._pydantic_model.get(session.user):
            pydantic_fields = {}
            pydantic_validators = {}
            for field in fields:
                field.get_pydantic_field(
                    request.session,
                    self,
                    pydantic_fields,
                    use_default=self._pydantic_use_default,
                )
                field.get_pydantic_validators(
                    request.session, self, pydantic_validators
                )

            self._pydantic_model[session.user] = create_model(
                self.Resource._code,
                **pydantic_fields,
                __validators__=pydantic_validators,
            )

        return self._pydantic_model[session.user]


class NewView(TemplateMixinForView, View):
    template_type = 'new'

    def __init__(
        self,
        template_id: str = None,
        template_src: str = None,
        label: str = None,
    ):
        View.__init__(self, label=label)
        TemplateMixinForView.__init__(
            self,
            template_id=template_id,
            template_src=template_src,
        )

    def render(
        self,
        feret: "FeretUI",
        session: Session,
        options: dict,
        ResourceCls: "Resource",
    ) -> str:
        fields = ResourceCls.get_all_fields()
        data = Data({
            field.name: field.get_default()
            for field in fields
        })

        template = self.get_template(
            feret,
            session,
            options,
            ResourceCls,
            data,
        )

        return feret.load_page_template(
            session,
            'feretui-page-resource-new',
            label=self.get_label(f'New {ResourceCls.get_label()}'),
            template=template,
            Resource=ResourceCls,
        )


class FormView(TemplateMixinForView, ActionsMixinForView, View):
    template_type = 'form'

    def __init__(
        self,
        template_id: str = None,
        template_src: str = None,
        actions: list[Actionset] = None,
        label: str = None,
    ):
        View.__init__(self, label=label)
        TemplateMixinForView.__init__(
            self,
            template_id=template_id,
            template_src=template_src,
        )
        ActionsMixinForView.__init__(self, actions)
        self.actions = actions

    def render(
        self,
        feret: "FeretUI",
        session: Session,
        options: dict,
        ResourceCls: "Resource",
    ) -> str:
        fields = ResourceCls.get_all_fields()
        ids = options.get('id')
        data = ResourceCls(id=ids[0]).read([field.name for field in fields])
        template = self.get_template(
            feret,
            session,
            options,
            ResourceCls,
            render_field_method='get_render_ro_with_label',
            data=data,
        )

        create_view_qs = self.get_transition_querystring(
            options,
            view=ResourceCls.on_form_create_button_redirect_to,
        )
        edit_view_qs = self.get_transition_querystring(
            options,
            view=ResourceCls.on_form_edit_button_redirect_to,
        )
        return_view_qs = self.get_transition_querystring(
            options,
            view=ResourceCls.on_form_return_button_redirect_to,
        )

        return feret.load_page_template(
            session,
            'feretui-page-resource-form',
            label=self.get_label(ResourceCls.get_label()),
            template=template,
            Resource=ResourceCls,
            create_view_qs=create_view_qs,
            has_delete_button=ResourceCls.on_form_has_delete_button,
            edit_view_qs=edit_view_qs,
            return_view_qs=return_view_qs,
            id=ids[0],
        )


class EditView(TemplateMixinForView, View):
    template_type = 'edit'

    def __init__(
        self,
        template_id: str = None,
        template_src: str = None,
        label: str = None,
    ):
        View.__init__(self, label=label)
        TemplateMixinForView.__init__(
            self,
            template_id=template_id,
            template_src=template_src,
        )
        self._pydantic_use_default = False

    def render(
        self,
        feret: "FeretUI",
        session: Session,
        options: dict,
        ResourceCls: "Resource",
    ) -> str:
        fields = ResourceCls.get_all_fields()
        ids = options.get('id')
        data = ResourceCls(id=ids[0]).read([field.name for field in fields])
        template = self.get_template(
            feret,
            session,
            options,
            ResourceCls,
            data=data,
        )

        cancel_view_qs = self.get_transition_querystring(
            options,
            view=ResourceCls.on_edit_cancel_button_redirect_to,
        )
        return feret.load_page_template(
            session,
            'feretui-page-resource-edit',
            label=self.get_label(ResourceCls.get_label()),
            template=template,
            Resource=ResourceCls,
            cancel_view_qs=cancel_view_qs,
            id=ids[0],
        )
