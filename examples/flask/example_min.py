import logging
import urllib
from contextlib import contextmanager
from wsgiref.simple_server import make_server

from flask import Flask, abort, make_response, request, send_file
from multidict import MultiDict

from feretui import (
    AsideHeaderMenu,
    AsideMenu,
    FeretUI,
    Request,
    Session,
    ToolBarButtonMenu,
    ToolBarDropDownMenu,
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
myferet.load_internal_catalog('fr')
Session.SignUpForm.lang.kwargs['choices'].append(('fr', 'Français'))


class MySession(Session):

    def __init__(self, **options) -> None:
        options.setdefault('theme', 'minty')
        options.setdefault('lang', 'fr')
        super().__init__(**options)


myferet.register_auth_menus([
    ToolBarButtonMenu(
        'Sign Up',
        page='signup',
        css_class="is-info",
        visible_callback=menu_for_unauthenticated_user,
    ),
    ToolBarButtonMenu(
        'Log In',
        page='login',
        visible_callback=menu_for_unauthenticated_user,
    ),
])


# /?page=hello
@myferet.register_page(
    templates=['''
    <template id="hello">
      <div class="container">
        <div class="content">
          <h1>Hello my feret</h1>
          <p>Welcome</p>
        </div>
      </div>
    </template>
    '''],
)
def hello(feretui, session, option):
    return feretui.render_template(session, 'hello')


# /?page=foo
myferet.register_static_page(
    'foo',
    '''
    <div class="container">
      <div class="content">
        Bar
      </div>
    </div>
    ''',
)
myferet.register_aside_menus('aside1', [
    AsideHeaderMenu('My aside menu', children=[
        AsideMenu('Hello', page='hello', description="Hello"),
        AsideMenu('Foo', page='foo', icon="fa-solid fa-ghost"),
    ]),
])
myferet.register_toolbar_left_menus([
    ToolBarDropDownMenu(
        'My left menu',
        children=[
            ToolBarMenu(
                'Hello', page="aside-menu", aside="aside1", aside_page='hello',
                description="Go to the hello page",
            ),
            ToolBarMenu(
                'Foo', page="aside-menu", aside="aside1", aside_page='foo',
                icon="fa-solid fa-ghost",
            ),
        ],
    ),
])

# -- app --


@app.route('/')
def index():
    with feretui_session(MySession) as session:
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

    with feretui_session(MySession) as session:
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
