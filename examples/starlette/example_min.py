import logging
from contextlib import asynccontextmanager, contextmanager

import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

from feretui import (
    AsideHeaderMenu,
    AsideMenu,
    FeretUI,
    Session,
    ToolBarButtonMenu,
    ToolBarDropDownMenu,
    ToolBarMenu,
    menu_for_unauthenticated_user,
)

logging.basicConfig(level=logging.DEBUG)

# -- for starlette --


@contextmanager
def feretui_session(request, cls):
    session = None
    try:
        session = cls(**request.session)
        yield session
    finally:
        if session:
            request.session.update(session.to_dict())

# -- for feretui --


myferet = FeretUI()
myferet.load_internal_catalog('fr')
Session.SignUpForm.lang.kwargs['choices'].append(('fr', 'Français'))


class MySession(Session):

    def __init__(self, **options) -> None:
        options.setdefault('theme', 'default')
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
        AsideMenu('Foo', page='foo', icon="ti ti-ghost"),
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
                icon="ti ti-ghost",
            ),
        ],
    ),
])

# -- app --

from feretui.ext.starlette import get_routes_for_feretui_client


def startup():
    print('Ready to go')


@asynccontextmanager
async def lifespan(app):
    startup()
    yield


routes = get_routes_for_feretui_client(myferet, session_cls=MySession)

app = Starlette(
    debug=True,
    routes=routes,
    middleware=[
        Middleware(SessionMiddleware, secret_key="secret"),
    ],
    lifespan=lifespan,
)


if __name__ == "__main__":
    uvicorn.run(app, port=8080, log_level="info")
