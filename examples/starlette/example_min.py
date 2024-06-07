import logging
from contextlib import contextmanager

from starlette.applications import Starlette
from starlette.responses import HTMLResponse, FileResponse, Response
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

from multidict import MultiDict
import uvicorn

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


async def index(request):
    with feretui_session(request, MySession) as session:
        frequest = Request(
            method=Request.GET,
            querystring=request.scope['query_string'].decode('utf-8'),
            headers=request.headers,
            session=session,
        )
        res = myferet.render(frequest)
        return HTMLResponse(res.body, headers=res.headers)


async def feretui_static_file(request):
    filepath = myferet.get_static_file_path(request.path_params['filepath'])
    if filepath:
        return FileResponse(filepath)

    return Response('', status_code=404)


async def get_params(request):
    res = {}
    res.update({
        key: request.query_params.getlist(key)
        for key in request.query_params.keys()
        if request.query_params.get(key)
    })

    form = await request.form()
    res.update({
        key: form.getlist(key)
        for key in form.keys()
        if form.get(key)
    })

    return res


async def call_action(request):
    with feretui_session(request, MySession) as session:
        form = await request.form()
        frequest = Request(
            method=getattr(Request, request.method),
            querystring=request.scope['query_string'].decode('utf-8'),
            form=MultiDict(form),
            params=await get_params(request),
            headers=request.headers,
            session=session,
        )
        res = myferet.execute_action(frequest, request.path_params['action'])
        return HTMLResponse(res.body, headers=res.headers)


def startup():
    print('Ready to go')


if __name__ == "__main__":
    app = Starlette(
        debug=True,
        routes=[
            Route('/', index),
            Route('/feretui/static/{filepath:path}', feretui_static_file),
            Route(
                '/feretui/action/{action:str}',
                call_action,
                methods=['GET', 'POST']),
        ],
        middleware=[
            Middleware(SessionMiddleware, secret_key="secret"),
        ],
        on_startup=[startup],
    )
    uvicorn.run(app, port=8080, log_level="info")
