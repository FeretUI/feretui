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

myferet = FeretUI()
myferet.load_internal_catalog('fr')
Session.SignUpForm.lang.kwargs['choices'].append(('fr', 'Français'))


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
