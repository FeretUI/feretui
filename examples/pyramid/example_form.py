import logging
from contextlib import contextmanager
from wsgiref.simple_server import make_server

from multidict import MultiDict
from pyramid.config import Configurator
from pyramid.httpexceptions import exception_response
from pyramid.response import FileResponse, Response
from pyramid.view import view_config
from pyramid_beaker import session_factory_from_settings
from wtforms import fields
from wtforms_components import ColorField

from feretui import (
    action_validator,
    action_for_unauthenticated_user,
    FeretUI,
    FeretUIForm,
    Request,
    Response as FResponse,
    Session,
    ToolBarMenu,
    menu_for_unauthenticated_user,
)

logging.basicConfig(level=logging.DEBUG)

# -- for Pyramid --


@contextmanager
def feretui_session(feretui_session_cls, pyramid_session):
    fsession = None
    try:
        fsession = feretui_session_cls(**pyramid_session)
        yield fsession
    finally:
        if fsession:
            pyramid_session.update(fsession.to_dict())
            pyramid_session.save()

# -- for feretui --


myferet = FeretUI()


class MyForm(FeretUIForm):
    bool_field = fields.BooleanField()
    date_field = fields.DateField()
    datetime_field = fields.DateTimeLocalField()
    decimal_field = fields.DecimalField()
    decimal_range_field = fields.DecimalRangeField()
    email_field = fields.EmailField()
    float_field = fields.FloatField()
    integer_field = fields.IntegerField()
    integer_range_field = fields.IntegerRangeField()
    month_field = fields.MonthField()
    string_field = fields.StringField()
    tel_field = fields.TelField()
    time_field = fields.TimeField()
    color_field = ColorField()


@myferet.register_page(
    name='my_form',
    templates=['''
      <template id="my-form">
        <form
          hx-post="{{ feretui.base_url }}/action/my_form"
          hx-swap="outerHTML"
          hx-trigger="submit"
        >
          <div class="container content">
            <h1>My form</h1>
            {% for field in form %}
            {{ field }}
            {% endfor %}
            <div class="buttons">
              <button
                class="button is-primary is-fullwidth"
                type="submit"
              >
                Submit
              </button>
            </div>
          </div>
        </form>
      </template>
    '''],
    forms=[MyForm],
)
def my_form_page(feretui, session, option):
    form = option.get('form', MyForm())
    return feretui.render_template(session, 'my-form', form=form)


@myferet.register_action
@action_validator(methods=[Request.POST])
@action_for_unauthenticated_user
def my_form(feretui, request):
    form = MyForm(request.form)
    if form.validate():
        print(form.data)
        base_url = request.get_base_url_from_current_url()
        headers = {
            'HX-Redirect': f'{base_url}?page=homepage',
        }
        return FResponse('', headers=headers)

    return FResponse(my_form_page(feretui, request.session, {'form': form}))


myferet.register_toolbar_left_menus([
    ToolBarMenu(
        'My form',
        page='my_form',
        visible_callback=menu_for_unauthenticated_user,
    ),
])

# -- app --


@view_config(route_name='feretui', request_method='GET')
def feretui(request):
    with feretui_session(Session, request.session) as session:
        frequest = Request(
            method=Request.GET,
            querystring=request.query_string,
            headers=dict(request.headers),
            session=session,
        )
        response = myferet.render(frequest)
        return Response(
            response.body,
            headers=response.headers,
        )


@view_config(route_name='feretui_static_file', request_method='GET')
def feretui_static_file(request):
    filepath = myferet.get_static_file_path(
        '/'.join(request.matchdict['filepath']),
    )
    if filepath:
        return FileResponse(filepath)

    raise exception_response(404)


@view_config(
    route_name='call_action',
    request_method=('DELETE', 'GET', 'POST'),
)
def call_action(request):
    action = request.matchdict['action']
    with feretui_session(Session, request.session) as session:
        frequest = Request(
            method=getattr(Request, request.method),
            querystring=request.query_string,
            form=MultiDict(request.POST),
            params=request.params.dict_of_lists(),
            headers=dict(request.headers),
            session=session,
        )
        response = myferet.execute_action(frequest, action)
        return Response(
            response.body,
            headers=response.headers,
        )


if __name__ == "__main__":
    session_factory = session_factory_from_settings({})
    with Configurator() as config:
        config.include('pyramid_beaker')
        config.set_session_factory(session_factory)
        config.add_route('feretui', '/')
        config.add_route('feretui_static_file', '/feretui/static/*filepath')
        config.add_route('call_action', '/feretui/action/{action}')
        config.scan()
        app = config.make_wsgi_app()

    with make_server('', 8080, app) as httpd:
        logging.info("Serving on port 8080...")
        httpd.serve_forever()
