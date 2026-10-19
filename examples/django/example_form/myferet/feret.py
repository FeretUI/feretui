from wtforms import fields
from wtforms_components import ColorField

from feretui import (
    FeretUI,
    FeretUIForm,
    FileField,
    ImageField,
    Many2ManyField,
    Many2OneField,
    MonetaryField,
    MultiFileField,
    One2ManyField,
    Request,
    Response,
    StatusBarField,
    TagsField,
    ToolBarMenu,
    WYSIWYGField,
    action_for_unauthenticated_user,
    action_validator,
    menu_for_unauthenticated_user,
)

myferet = FeretUI()


class SubForm(FeretUIForm):
    """Sub-form demonstrating nested fieldsets."""

    sub_title = fields.StringField("Sub Title", default="Sample section title")
    sub_description = fields.StringField(
        "Sub Description", default="Sample section description"
    )


class MyForm(FeretUIForm):
    # Boolean & Text fields
    bool_field = fields.BooleanField("Boolean Field", default=True)
    string_field = fields.StringField("String Field", default="Sample text")
    password_field = fields.PasswordField("Password Field", default="secret123")
    textarea_field = fields.TextAreaField(
        "Text Area Field", default="This is a multiline text area."
    )
    email_field = fields.EmailField("Email Field", default="user@example.com")
    tel_field = fields.TelField("Telephone Field", default="+33 1 23 45 67 89")
    url_field = fields.URLField("URL Field", default="https://github.com/anyblok/feretui")
    search_field = fields.SearchField("Search Field", default="Search keywords")
    color_field = ColorField("Color Field", default="#3273dc")

    # Numeric & Monetary fields
    integer_field = fields.IntegerField("Integer Field", default=42)
    integer_range_field = fields.IntegerRangeField("Integer Range Field", default=50)
    float_field = fields.FloatField("Float Field", default=3.14)
    decimal_field = fields.DecimalField("Decimal Field", default=100.50)
    decimal_range_field = fields.DecimalRangeField("Decimal Range Field", default=75.0)
    monetary_field = MonetaryField(
        "Monetary Field", currency="€", currency_position="after", default=1250.00
    )

    # Date & Time fields
    date_field = fields.DateField("Date Field")
    datetime_field = fields.DateTimeLocalField("DateTime Local Field")
    time_field = fields.TimeField("Time Field")
    month_field = fields.MonthField("Month Field")

    # Selection & Radio fields
    select_field = fields.SelectField(
        "Select Field",
        choices=[("opt1", "Option 1"), ("opt2", "Option 2")],
        default="opt1",
    )
    select_multiple_field = fields.SelectMultipleField(
        "Select Multiple Field",
        choices=[("opt1", "Option 1"), ("opt2", "Option 2"), ("opt3", "Option 3")],
        default=["opt1", "opt2"],
    )
    radio_field = fields.RadioField(
        "Radio Field",
        choices=[("choice_a", "Choice A"), ("choice_b", "Choice B")],
        default="choice_a",
    )
    hidden_field = fields.HiddenField("Hidden Field", default="hidden_value")

    # FeretUI ERP fields
    status_field = StatusBarField(
        "Status Bar Field",
        choices=[("draft", "Draft"), ("in_progress", "In Progress"), ("done", "Done")],
        default="in_progress",
    )
    many2one_field = Many2OneField(
        "Many2One Field",
        choices=[("1", "Resource #1"), ("2", "Resource #2")],
        resource="item",
        default="1",
    )
    tags_field = TagsField(
        "Tags Field",
        separator=",",
        default=["erp", "python", "feretui"],
    )
    file_field = FileField("File Field (Document)", allowed_extensions=["pdf", "txt", "png"])
    multi_file_field = MultiFileField("Multi-File Field (Attachments)")
    image_field = ImageField("Image Field (Avatar)", is_avatar=True)
    one2many_field = One2ManyField(
        "One2Many Field",
        columns=[("code", "Code"), ("name", "Name"), ("qty", "Quantity")],
        default=lambda: [
            {"code": "L01", "name": "Item A", "qty": "10"},
            {"code": "L02", "name": "Item B", "qty": "20"},
        ],
    )
    many2many_field = Many2ManyField(
        "Many2Many Field",
        columns=[("name", "Category"), ("desc", "Description")],
        default=lambda: [
            {"name": "Tech", "desc": "Technology category"},
            {"name": "Admin", "desc": "Administration category"},
        ],
    )
    wysiwyg_field = WYSIWYGField(
        "WYSIWYG Field",
        default="<p>Welcome to <strong>FeretUI CMS</strong>! Edit rich text seamlessly.</p>",
    )

    # Sub-form (Fieldset)
    sub_form = fields.FormField(SubForm, label="Fieldset / Sub-Form")


@myferet.register_page(
    name='my_form',
    templates=['''
      <template id="my-form">
        <form
          hx-post="{{ feretui.base_url }}/action/my_form"
          hx-swap="outerHTML"
          hx-trigger="submit"
          hx-encoding="multipart/form-data"
          enctype="multipart/form-data"
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
    forms=[MyForm, SubForm],
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
