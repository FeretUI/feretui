import logging
import urllib
from contextlib import contextmanager
from wsgiref.simple_server import make_server

from flask import Flask, abort, make_response, request, send_file
from multidict import MultiDict
from wtforms import fields
from wtforms_components import ColorField

from feretui import (
    action_validator,
    action_for_unauthenticated_user,
    FeretUI,
    FeretUIForm,
    Request,
    Response,
    Session,
    ToolBarMenu,
    menu_for_unauthenticated_user,
)

logging.basicConfig(level=logging.DEBUG)

# -- for flask --

app = Flask(__name__)
app.secret_key = b'secret'


@contextmanager
def feretui_session(cls):
    from flask import session
    fsession = None
    try:
        fsession = cls(**session)
        yield fsession
    finally:
        if fsession:
            session.update(fsession.to_dict())


def response(fresponse):
    resp = make_response(fresponse.body)
    resp.headers.update(fresponse.headers)
    return resp

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


@app.route('/')
def index():
    with feretui_session(Session) as session:
        frequest = Request(
            method=Request.GET,
            querystring=request.query_string.decode('utf-8'),
            headers=dict(request.headers),
            session=session,
        )
        return response(myferet.render(frequest))


@app.route('/feretui/static/<path:filepath>')
def feretui_static_file(filepath):
    filepath = myferet.get_static_file_path(filepath)
    if filepath:
        return send_file(filepath.resolve())

    abort(404)
    return None


@app.route('/feretui/action/<action>', methods=['DELETE', 'GET', 'POST'])
def call_action(action):
    params = {}
    if request.method in ['DELETE', 'POST']:
        params = {
            x: request.form.getlist(x)
            for x in request.form
        }
        params.update(urllib.parse.parse_qs(
            request.query_string.decode('utf-8'),
        ))

    with feretui_session(Session) as session:
        frequest = Request(
            method=getattr(Request, request.method),
            querystring=request.query_string.decode('utf-8'),
            form=MultiDict(request.form),
            params=params,
            headers=dict(request.headers),
            session=session,
        )
        return response(myferet.execute_action(frequest, action))


if __name__ == "__main__":
    with make_server('', 8080, app) as httpd:
        logging.info("Serving on port 8080...")
        httpd.serve_forever()
