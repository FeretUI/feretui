from wtforms import fields
from wtforms_components import ColorField

from feretui import (
    FeretUI,
    FeretUIForm,
    Request,
    Response,
    ToolBarMenu,
    action_for_unauthenticated_user,
    action_validator,
    menu_for_unauthenticated_user,
)


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
        return Response('', headers=headers)

    return Response(my_form_page(feretui, request.session, {'form': form}))


myferet.register_toolbar_left_menus([
    ToolBarMenu(
        'My form',
        page='my_form',
        visible_callback=menu_for_unauthenticated_user,
    ),
])
