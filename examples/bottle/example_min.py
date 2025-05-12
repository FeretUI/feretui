import logging
from bottle import app, run
from BottleSessions import BottleSessions

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

from feretui.ext.bottle import declare_routes_for_feretui_client

logging.basicConfig(level=logging.DEBUG)


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


declare_routes_for_feretui_client(myferet, session_cls=MySession)


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
