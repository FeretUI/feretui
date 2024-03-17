import inspect
import logging
from os import path

import redis
from bottle import HTTPResponse, app, debug, request, route, run, static_file
from bottle_session import Session as BottleSession
from bottle_session import SessionPlugin

from feretui import (
    AsideHeaderMenu,
    AsideMenu,
    FeretUI,
    FeretUIForm,
    Request,
    Session,
    ToolBarButtonMenu,
    ToolBarDropDownMenu,
    ToolBarMenu,
)
from wtforms import StringField, BooleanField
from wtforms.validators import InputRequired

logging.basicConfig(level=logging.DEBUG)


class MySessionPlugin(SessionPlugin):

    def apply(self, callback, context):
        context.config.get('session')
        try:
            args = inspect.signature(context.callback).parameters
        except AttributeError:
            args = inspect.getargspec(context.callback)[0]

        if self.keyword not in args:
            return callback

        def wrapper(*args, **kwargs):
            r = redis.Redis(connection_pool=self.connection_pool)
            kwargs[self.keyword] = MySession(
                r,
                self.cookie_name,
                self.cookie_lifetime,
                self.cookie_secure,
                self.cookie_httponly,
            )
            rv = callback(*args, **kwargs)
            return rv

        return wrapper


class MySession(Session, BottleSession):

    def __init__(
        self,
        rdb,
        cookie_name='bottle.session',
        cookie_lifetime=None,
        cookie_secure=False,
        cookie_httponly=False,
    ):
        Session.__init__(self)
        BottleSession.__init__(
            self,
            rdb,
            cookie_name,
            cookie_lifetime,
            cookie_secure,
            cookie_httponly,
        )
        self.theme = "minty"
        self.lang = 'fr'


myferet = FeretUI()
myferet.load_internal_catalog('fr')


@myferet.register_form()
class HelloForm(FeretUIForm):
    name = StringField(
        validators=[InputRequired()],
        description="PLop"
    )
    mybool = BooleanField(description='titi')


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
          <form>
            <div class="container">
              {{ form.name }}
              {{ form.mybool }}
            </div>
          </form>
        </div>
      </div>
    </template>
    ''']
)
def hello(feretui, session, option):
    form = HelloForm()
    return feretui.render_template(session, 'hello', form=form)


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
def index(session):
    frequest = Request(
        method=Request.GET,
        querystring=request.query_string,
        headers=dict(request.headers),
        session=session,
    )
    response = myferet.render(frequest)
    return HTTPResponse(
        body=response.body,
        status=response.status_code,
        headers=response.headers,
    )


@route('/feretui/static/<filepath:path>')
def feretui_static_file(session, filepath):
    filepath = myferet.get_static_file_path(filepath)
    if filepath:
        root, name = path.split(filepath)
        return static_file(name, root)

    return None


@route('/feretui/action/<action>', method=['GET'])
def get_action(session, action):
    frequest = Request(
        method=Request.GET,
        querystring=request.query_string,
        headers=dict(request.headers),
        session=session,
    )
    response = myferet.execute_action(frequest, action)
    return HTTPResponse(
        body=response.body,
        status=response.status_code,
        headers=response.headers,
    )


@route('/feretui/action/<action>', method=['POST'])
def post_action(session, action):
    frequest = Request(
        method=Request.POST,
        body=request.body.read(),
        headers=dict(request.headers),
        session=session,
    )
    response = myferet.execute_action(frequest, action)
    return HTTPResponse(
        body=response.body,
        status=response.status_code,
        headers=response.headers,
    )


if __name__ == "__main__":
    app = app()
    plugin = MySessionPlugin(cookie_lifetime=600)
    app.install(plugin)
    debug(True)
    run(host="localhost", port=8080)
