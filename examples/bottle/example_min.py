import logging
from os import path

from bottle import response, app, debug, request, route, run, static_file
from BottleSessions import BottleSessions

from feretui import (
    AsideHeaderMenu,
    AsideMenu,
    FeretUI,
    Request,
    Session,
    ToolBarButtonMenu,
    ToolBarDropDownMenu,
    ToolBarMenu,
)
from contextlib import contextmanager

logging.basicConfig(level=logging.DEBUG)


class Session(Session):

    def __init__(self) -> None:
        super().__init__()
        self.theme = "minty"
        self.lang = 'fr'


@contextmanager
def feretui_session(cls):
    session = cls()
    try:
        session.__dict__.update(request.session)
        yield session
    finally:
        request.session.update(session.__dict__)


myferet = FeretUI()
myferet.load_internal_catalog('fr')


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
        AsideMenu('Hello', page='hello', tooltip="Hello"),
        AsideMenu('Foo', page='foo', icon="fa-solid fa-ghost"),
    ]),
])
myferet.register_toolbar_left_menus([
    ToolBarDropDownMenu('My left menu', children=[
        ToolBarMenu(
            'Hello', page="aside-menu", aside="aside1", aside_page='hello',
            tooltip="Go to the hello page",
        ),
        ToolBarMenu(
            'Foo', page="aside-menu", aside="aside1", aside_page='foo',
            icon="fa-solid fa-ghost",
        ),
    ]),
])


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
        for k, v in res.headers.items():
            response.set_header(k, v)

        return res.body


@route('/feretui/static/<filepath:path>')
def feretui_static_file(filepath):
    filepath = myferet.get_static_file_path(filepath)
    if filepath:
        root, name = path.split(filepath)
        return static_file(name, root)

    return None


@route('/feretui/action/<action>', method=['GET'])
def get_action(action):
    with feretui_session(Session) as session:
        frequest = Request(
            method=Request.GET,
            querystring=request.query_string,
            headers=dict(request.headers),
            session=session,
        )
        res = myferet.execute_action(frequest, action)
        for k, v in res.headers.items():
            response.set_header(k, v)

        return res.body


@route('/feretui/action/<action>', method=['POST'])
def post_action(action):
    with feretui_session(Session) as session:
        frequest = Request(
            method=Request.POST,
            body=request.body.read(),
            headers=dict(request.headers),
            session=session,
        )
        res = myferet.execute_action(frequest, action)
        for k, v in res.headers.items():
            response.set_header(k, v)

        return res.body


if __name__ == "__main__":
    app = app()
    cache_config = {
        'cache_type': 'FileSystem',
        'cache_dir': './sess_dir',
        'threshold': 2000,
    }
    btl = BottleSessions(
        app, session_backing=cache_config, session_cookie='appcookie')
    debug(True)
    run(host="localhost", port=8080)
