import logging
from contextlib import contextmanager
from os import path

from bottle import abort, app, request, response, route, run, static_file
from BottleSessions import BottleSessions
from multidict import MultiDict
from wtforms import fields
from wtforms_components import ColorField

from feretui import (
    FeretUI,
    FeretUIForm,
    Request,
    Response,
    Session,
    ToolBarMenu,
    action_for_unauthenticated_user,
    action_validator,
    menu_for_unauthenticated_user,
)

logging.basicConfig(level=logging.DEBUG)

# -- for bottle --


@contextmanager
def feretui_session(cls):
    session = None
    try:
        session = cls(**request.session)
        yield session
    finally:
        if session:
            request.session.update(session.to_dict())


def add_response_headers(headers) -> None:
    for k, v in headers.items():
        response.set_header(k, v)

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
        return Response('', headers=headers)

    return Response(my_form_page(feretui, request.session, {'form': form}))


myferet.register_toolbar_left_menus([
    ToolBarMenu(
        'My form',
        page='my_form',
        visible_callback=menu_for_unauthenticated_user,
    ),
])

# -- app --


@route('/')
def index():
    with feretui_session(Session) as session:
        frequest = Request(
            method=Request.GET,
            querystring=request.query_string,
            headers=dict(request.headers),
            session=session,
        )
        res = myferet.render(frequest)
        add_response_headers(res.headers)
        return res.body


@route('/feretui/static/<filepath:path>')
def feretui_static_file(filepath):
    filepath = myferet.get_static_file_path(filepath)
    if filepath:
        root, name = path.split(filepath)
        return static_file(name, root)

    abort(404)
    return None


@route('/feretui/action/<action>', method=['GET', 'POST'])
def call_action(action):
    with feretui_session(Session) as session:
        frequest = Request(
            method=getattr(Request, request.method),
            querystring=request.query_string,
            form=MultiDict(request.forms),
            params=MultiDict(request.params),
            headers=dict(request.headers),
            session=session,
        )
        res = myferet.execute_action(frequest, action)
        add_response_headers(res.headers)
        return res.body


if __name__ == "__main__":
    app = app()
    cache_config = {
        'cache_type': 'FileSystem',
        'cache_dir': './sess_dir',
        'threshold': 2000,
    }
    BottleSessions(
        app, session_backing=cache_config, session_cookie='appcookie')
    run(host="localhost", port=8080, debug=True, reloader=1)
