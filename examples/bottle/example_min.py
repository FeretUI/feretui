import logging
from contextlib import contextmanager
from os import path

from bottle import abort, app, request, response, route, run, static_file
from BottleSessions import BottleSessions
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
    menu_for_authenticated_user,
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
myferet.load_internal_catalog('fr')
Session.SignUpForm.lang.kwargs['choices'].append(('fr', 'Français'))


class MySession(Session):

    def __init__(self, **options) -> None:
        options.setdefault('theme', 'minty')
        options.setdefault('lang', 'fr')
        super().__init__(**options)


myferet.register_auth_menus([
    ToolBarButtonMenu('Sign Up', page='signup', css_class="is-info"),
    ToolBarButtonMenu('Log In', page='login'),
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
        visible_callback=menu_for_authenticated_user,
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


@route('/')
def index():
    with feretui_session(MySession) as session:
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
    with feretui_session(MySession) as session:
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
