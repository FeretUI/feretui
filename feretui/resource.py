from wtforms import IntegerField
from wtforms.validators import InputRequired
from feretui.menus import ToolBarMenu
from feretui.session import Session
from feretui.request import Request
from feretui.response import Response
from feretui.view import ListView
from typing import TYPE_CHECKING, Callable
from markupsafe import Markup

if TYPE_CHECKING:
    from feretui.feretui import FeretUI


class Resource:
    _code: str = None  # filled by the decorator
    _label: str = None  # filled by the decorator

    class Form:
        pk = IntegerField(validators=[InputRequired()])

    list_view: ListView = ListView()
    # new_view: NewView = NewView()
    # form_view: FormView = FormView()
    # edit_view: EditView = EditView()

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

    @classmethod
    def menu(cls, menu_cls=ToolBarMenu, label=None, **kwargs):
        kwargs = kwargs.copy()
        if 'aside' in kwargs:
            kwargs['aside_page'] = "resource"
        else:
            kwargs['page'] = "resource"

        return menu_cls(
            label or cls._label,
            resource=cls._code,
            **kwargs
        )

    @classmethod
    def render(cls, feretui, session, options):
        viewcode = options.setdefault('view', [cls.default_view])[0]
        view = getattr(cls, f"{viewcode}_view")
        # TODO security
        return feretui.render_template(
            session,
            'feretui-page-resource',
            view=Markup(view.render(cls, feretui, session, options)),
        )

    @classmethod
    def router_call(cls, feret, request) -> Response:
        # TODO validate is POST
        # TODO is declaredin the view
        # TODO is visible
        func = getattr(cls, request.params['method'])
        res = func(feret, request)
        if res:
            if not isinstance(res, Response):
                res = Response(str(res))
        else:
            res = Response('')

        return res

    # @classmethod
    # def _router_row_action(
    #     cls,
    #     feret: "FeretUI",
    #     request: Request
    # ) -> Response:
    #     query = request.get_query_string_from_current_url()
    #     viewcode = query['view'][0]
    #     code = request.query['code'][0]
    #     view = getattr(cls, f"{viewcode}_view")
    #     ids = request.query.get('id')
    #     resource = cls(ids[0])

    #     for field in view.fields:
    #         if not isinstance(field, Actionset):
    #             continue
    #         for action in field.actions:
    #             if action.code == code:
    #                 res = getattr(resource, action.method)(feret, request)
    #                 if res:
    #                     if not isinstance(res, Response):
    #                         res = Response(str(res))
    #                 else:
    #                     res = Response('')

    #                 return res

    #     return Response('')

    @classmethod
    def router_pagination(
        cls,
        feret: "FeretUI",
        request: Request
    ) -> Response:
        newqs = request.get_query_string_from_current_url().copy()
        base_url = request.get_base_url_from_current_url()
        newqs['offset'] = request.query['offset']
        return Response(
            cls.render(feret, request.session, newqs),
            headers={
                'HX-Push-Url': request.get_url_from_dict(base_url, newqs),
            }
        )

    # @classmethod
    # def _router_filter(
    #     cls,
    #     feret: "FeretUI",
    #     request: Request
    # ) -> Response:
    #     newqs = request.get_query_string_from_current_url().copy()
    #     viewcode = newqs['view'][0]
    #     view = getattr(cls, f"{viewcode}_view")
    #     mode = request.query.get('mode', ['add'])[0]
    #     field_name = (
    #         f"filter-{request.query['name'][0]}-{request.query['operator'][0]}"
    #     )
    #     newqs['offset'] = ['0']
    #     filters = newqs.setdefault(field_name, [])
    #     filters_ = filters.pop().split(',') if filters else []
    #     value = request.query['value'][0]
    #     if mode == 'add':
    #         if value not in filters_:
    #             filters_.append(value)
    #     else:
    #         filters_ = [x for x in filters_ if x != value]
    #         if not filters_:
    #             newqs.pop(field_name)

    #     filters.append(','.join(filters_))
    #     return Response(
    #         view.render(feret, request.session, newqs, cls),
    #         headers={
    #             'HX-Push-Url': request.get_url_from_dict(newqs),
    #         }
    #     )

    # @classmethod
    # def _router_create(
    #     cls,
    #     feret: "FeretUI",
    #     request: Request
    # ) -> Response:
    #     try:
    #         Schema = cls._new_view.get_pydantic_schema(feret, request, cls)
    #         id = cls().create(**dict(Schema(**request.body)))
    #         query = request.get_query_string_from_current_url()
    #         query['view'] = [cls.on_new_after_create_redirect_to]
    #         query['id'] = id
    #         return Response(
    #             '',
    #             headers={
    #                 'HX-Redirect': request.get_url_from_dict(query)
    #             }
    #         )
    #     except ValidationError as e:
    #         return Response(
    #             feret.load_page_template(
    #                 request.session,
    #                 'feretui-page-pydantic-failed',
    #                 errors=format_errors(e.errors()),
    #             )
    #         )
    #     except Exception:
    #         return Response(
    #             feret.load_page_template(
    #                 request.session,
    #                 'feretui-page-error-500'
    #             )
    #         )

    # @classmethod
    # def _router_update(
    #     cls,
    #     feret: "FeretUI",
    #     request: Request
    # ) -> Response:
    #     try:
    #         Schema = cls._edit_view.get_pydantic_schema(feret, request, cls)
    #         ids = request.query['id']
    #         cls(ids[0]).update(**dict(Schema(**request.body)))
    #         query = request.get_query_string_from_current_url()
    #         query['view'] = [cls.on_edit_after_update_redirect_to]
    #         return Response(
    #             '',
    #             headers={
    #                 'HX-Redirect': request.get_url_from_dict(query),
    #             }
    #         )
    #     except ValidationError as e:
    #         return Response(
    #             feret.load_page_template(
    #                 request.session,
    #                 'feretui-page-pydantic-failed',
    #                 errors=format_errors(e.errors()),
    #             )
    #         )
    #     except Exception:
    #         return Response(
    #             feret.load_page_template(
    #                 request.session,
    #                 'feretui-page-error-500'
    #             )
    #         )

    # @classmethod
    # def _router_delete(
    #     cls,
    #     feret: "FeretUI",
    #     request: Request
    # ) -> Response:
    #     cls(request.query['id'][0]).delete()
    #     return Response(
    #         '',
    #         headers={
    #             'HX-Redirect': request.get_url_from_dict({
    #                 'page': ['resource'],
    #                 'resource': [cls._code],
    #                 'view': ['list'],
    #             }),
    #         }
    #     )

    def __init__(self, pk):
        self.pk = pk

    @classmethod
    def create(cls, form):
        raise ResourceError('Must be overwriting')

    @classmethod
    def filtered_reads(
        cls,
        form_cls,
        filters: list[tuple[str, str, str]],
        offset: int,
        limit: int,
    ):
        raise ResourceError('Must be overwriting')

    def read(
        self,
        form_cls,
    ):
        raise ResourceError('Must be overwriting')

    def update(self, form):
        raise ResourceError('Must be overwriting')

    def delete(self):
        raise ResourceError('Must be overwriting')
