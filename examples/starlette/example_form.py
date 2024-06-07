import logging
from contextlib import contextmanager

from starlette.applications import Starlette
from starlette.responses import HTMLResponse, FileResponse, Response
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

from multidict import MultiDict
import uvicorn
from wtforms import fields
from wtforms_components import ColorField

from feretui import (
    FeretUI,
    FeretUIForm,
    Request,
    Response as FResponse,
    Session,
    ToolBarMenu,
    action_for_unauthenticated_user,
    action_validator,
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
        return FResponse('', headers=headers)

    return FResponse(my_form_page(feretui, request.session, {'form': form}))


myferet.register_toolbar_left_menus([
    ToolBarMenu(
        'My form',
        page='my_form',
        visible_callback=menu_for_unauthenticated_user,
    ),
])

# -- app --


async def index(request):
    with feretui_session(request, Session) as session:
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
    with feretui_session(request, Session) as session:
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
