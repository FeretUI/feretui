import urllib
from typing import TYPE_CHECKING, Callable

import polib
from pydantic import ValidationError

from feretui.exceptions import ResourceError
from feretui.fields import Field
from feretui.request import Request
from feretui.response import Response
from feretui.schema import format_errors
from feretui.session import Session
from feretui.translate import Translation
from feretui.views import (
    Actionset,
    EditView,
    FormView,
    ListView,
    NewView,
    View,
)

if TYPE_CHECKING:
    from feretui.feretui import FeretUI


class Resource:
    _code: str = None  # filled by the decorator
    _label: str = None  # filled by the decorator
    _menus: list[dict] = []  # filled by the decorator
    _security: Callable = []  # filled by the decorator
    _fields: list[Field] = []

    _list_view: ListView = ListView()
    _new_view: NewView = NewView()
    _form_view: FormView = FormView()
    _edit_view: EditView = EditView()

    default_view: str = 'list'

    on_list_create_button_redirect_to: str = 'new'
    on_list_do_click_on_row_redirect_to: str = 'form'

    on_new_after_create_redirect_to: str = 'form'

    on_form_create_button_redirect_to: str = 'new'
    on_form_edit_button_redirect_to: str = 'edit'
    on_form_has_delete_button: bool = True
    on_form_return_button_redirect_to: str = 'list'

    on_edit_after_update_redirect_to: str = 'form'
    on_edit_cancel_button_redirect_to: str = 'form'

    def __init__(self, id: str = None):
        self.id = id

    def __str__(self):
        return f'<{self._code} id={self.id}>'

    @classmethod
    def get_view_url_from_options(cls, options: dict) -> str:
        viewcode = options.get('view')
        if viewcode is None:
            options['view'] = cls.default_view

        querystring = urllib.parse.urlencode(options, doseq=True)
        return f'/feretui/action/resource-render?{querystring}'

    @classmethod
    def get_label(cls):
        lang = Translation.local.lang
        return Translation.get(
            lang, f'resouce:{cls._code}:label', cls._label
        )

    @classmethod
    def get_navbar_menu(cls):
        return {
            'code': f'resource?resource={cls._code}',
            'label': cls.get_label(),
        }

    @classmethod
    def render_menus(cls):
        return cls._menus

    @classmethod
    def get_actions(cls, feret: "FeretUI", session: Session, options: dict):
        attr = f"_{options.get('view', ['list'])[0]}_view"
        view = getattr(cls, attr)
        if hasattr(view, 'get_actions'):
            return view.get_actions(feret, session, cls)

        return []

    @classmethod
    def register_sub_entries(cls):
        fields = []
        for attr_name, attr in cls.__dict__.items():
            if isinstance(attr, Field):
                attr.name = attr_name
                attr.register_sub_entries(cls)
                fields.append(attr)
            elif isinstance(attr, View):
                attr.register_sub_entries(cls)

        cls._fields = fields

    @classmethod
    def export_catalog(cls, po: polib.POEntry):
        po.append(Translation.define(
            f'resource:{cls._code}:label',
            cls._label,
        ))
        # fields
        for field in cls.get_all_fields():
            field.export_catalog(po)

        # views
        if cls._list_view:
            cls._list_view.export_catalog(po)

        if cls._new_view:
            cls._new_view.export_catalog(po)

        if cls._form_view:
            cls._form_view.export_catalog(po)

        if cls._edit_view:
            cls._edit_view.export_catalog(po)

    @classmethod
    def get_all_fields(cls):
        return cls._fields

    @classmethod
    def _router_render(cls, feret: "FeretUI", request: Request) -> Response:
        viewcode = request.query['view'][0]
        view = getattr(cls, f"_{viewcode}_view")
        return Response(
            view.render(feret, request.session, request.query, cls)
        )

    @classmethod
    def _router_action(cls, feret: "FeretUI", request: Request) -> Response:
        query = request.get_query_string_from_current_url()
        viewcode = query['view'][0]
        code = request.query['code'][0]
        view = getattr(cls, f"_{viewcode}_view")
        resource = cls()
        ids = query.get('id')
        if ids:
            resource = cls(ids[0])

        for actionset in view.actions:
            for action in actionset.actions:
                if action.code == code:
                    res = getattr(resource, action.method)(feret, request)
                    if res:
                        if not isinstance(res, Response):
                            res = Response(str(res))
                    else:
                        res = Response('')

                    return res

        return Response('')

    @classmethod
    def _router_row_action(
        cls,
        feret: "FeretUI",
        request: Request
    ) -> Response:
        query = request.get_query_string_from_current_url()
        viewcode = query['view'][0]
        code = request.query['code'][0]
        view = getattr(cls, f"_{viewcode}_view")
        ids = request.query.get('id')
        resource = cls(ids[0])

        for field in view.fields:
            if not isinstance(field, Actionset):
                continue
            for action in field.actions:
                if action.code == code:
                    res = getattr(resource, action.method)(feret, request)
                    if res:
                        if not isinstance(res, Response):
                            res = Response(str(res))
                    else:
                        res = Response('')

                    return res

        return Response('')

    @classmethod
    def _router_pagination(
        cls,
        feret: "FeretUI",
        request: Request
    ) -> Response:
        newqs = request.get_query_string_from_current_url().copy()
        newqs.update(request.query)
        viewcode = newqs['view'][0]
        view = getattr(cls, f"_{viewcode}_view")
        return Response(
            view.render(feret, request.session, newqs, cls),
            headers={
                'HX-Push-Url': request.get_url_from_dict(newqs),
            }
        )

    @classmethod
    def _router_filter(
        cls,
        feret: "FeretUI",
        request: Request
    ) -> Response:
        newqs = request.get_query_string_from_current_url().copy()
        viewcode = newqs['view'][0]
        view = getattr(cls, f"_{viewcode}_view")
        mode = request.query.get('mode', ['add'])[0]
        field_name = (
            f"filter-{request.query['name'][0]}-{request.query['operator'][0]}"
        )
        newqs['offset'] = ['0']
        filters = newqs.setdefault(field_name, [])
        filters_ = filters.pop().split(',') if filters else []
        value = request.query['value'][0]
        if mode == 'add':
            if value not in filters_:
                filters_.append(value)
        else:
            filters_ = [x for x in filters_ if x != value]
            if not filters_:
                newqs.pop(field_name)

        filters.append(','.join(filters_))
        return Response(
            view.render(feret, request.session, newqs, cls),
            headers={
                'HX-Push-Url': request.get_url_from_dict(newqs),
            }
        )

    @classmethod
    def _router_create(
        cls,
        feret: "FeretUI",
        request: Request
    ) -> Response:
        try:
            Schema = cls._new_view.get_pydantic_schema(feret, request, cls)
            id = cls().create(**dict(Schema(**request.body)))
            query = request.get_query_string_from_current_url()
            query['view'] = [cls.on_new_after_create_redirect_to]
            query['id'] = id
            return Response(
                '',
                headers={
                    'HX-Redirect': request.get_url_from_dict(query)
                }
            )
        except ValidationError as e:
            return Response(
                feret.load_page_template(
                    request.session,
                    'feretui-page-pydantic-failed',
                    errors=format_errors(e.errors()),
                )
            )
        except Exception:
            return Response(
                feret.load_page_template(
                    request.session,
                    'feretui-page-error-500'
                )
            )

    @classmethod
    def _router_update(
        cls,
        feret: "FeretUI",
        request: Request
    ) -> Response:
        try:
            Schema = cls._edit_view.get_pydantic_schema(feret, request, cls)
            ids = request.query['id']
            cls(ids[0]).update(**dict(Schema(**request.body)))
            query = request.get_query_string_from_current_url()
            query['view'] = [cls.on_edit_after_update_redirect_to]
            return Response(
                '',
                headers={
                    'HX-Redirect': request.get_url_from_dict(query),
                }
            )
        except ValidationError as e:
            return Response(
                feret.load_page_template(
                    request.session,
                    'feretui-page-pydantic-failed',
                    errors=format_errors(e.errors()),
                )
            )
        except Exception:
            return Response(
                feret.load_page_template(
                    request.session,
                    'feretui-page-error-500'
                )
            )

    @classmethod
    def _router_delete(
        cls,
        feret: "FeretUI",
        request: Request
    ) -> Response:
        cls(request.query['id'][0]).delete()
        return Response(
            '',
            headers={
                'HX-Redirect': request.get_url_from_dict({
                    'page': ['resource'],
                    'resource': [cls._code],
                    'view': ['list'],
                }),
            }
        )

    def create(self, **kwargs):
        raise ResourceError('Must be overwriting')

    @classmethod
    def filtered_reads(
        cls,
        filters: list[tuple[str, str, str]],
        fields: str,
        offset: int,
        limit: int,
    ):
        raise ResourceError('Must be overwriting')

    def read(
        self,
        fields: str,
    ):
        raise ResourceError('Must be overwriting')

    def update(self, **kwargs):
        raise ResourceError('Must be overwriting')

    def delete(self):
        raise ResourceError('Must be overwriting')
