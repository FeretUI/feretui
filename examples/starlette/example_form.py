import logging
from contextlib import asynccontextmanager, contextmanager

import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from wtforms import fields
from wtforms_components import ColorField

from feretui import (
    FeretUI,
    FeretUIForm,
    Request,
    Session,
    ToolBarMenu,
    action_for_unauthenticated_user,
    action_validator,
    menu_for_unauthenticated_user,
)
from feretui import (
    Response as FResponse,
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

from feretui.ext.starlette import get_routes_for_feretui_client


def startup():
    print('Ready to go')


@asynccontextmanager
async def lifespan(app):
    startup()
    yield


routes = get_routes_for_feretui_client(myferet, session_cls=Session)

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
