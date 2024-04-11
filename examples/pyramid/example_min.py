import logging
from contextlib import contextmanager
from wsgiref.simple_server import make_server

from multidict import MultiDict
from pyramid.config import Configurator
from pyramid.httpexceptions import exception_response
from pyramid.response import FileResponse, Response
from pyramid.view import view_config
from pyramid_beaker import session_factory_from_settings

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


@view_config(route_name='feretui', request_method='GET')
def feretui(request):
    with feretui_session(MySession, request.session) as session:
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
    with feretui_session(MySession, request.session) as session:
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
