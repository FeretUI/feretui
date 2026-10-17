import operator
from functools import reduce

from django.db.models import Q
from multidict import MultiDict
from wtforms import PasswordField, RadioField, SelectField, StringField
from wtforms.validators import EqualTo, InputRequired

from feretui import (
    Action,
    Actionset,
    AsideHeaderMenu,
    AsideMenu,
    FeretUI,
    GotoViewAction,
    LCRUDResource,
    Password,
    Resource,
    SelectedRowsAction,
    Session,
    ToolBarDropDownMenu,
    ToolBarMenu,
    menu_for_authenticated_user,
)
from feretui.context import cvar_request
from feretui.resources.update import DefaultViewUpdate

from .models import User

myferet = FeretUI()
myferet.load_internal_catalog('fr')
theme_choices = [(k, k.capitalize()) for k in myferet.themes.keys()]


class MySession(Session):
    def __init__(self, user_id=None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.user_id = user_id
        if self.user_id:
            user = User.objects.filter(login=self.user_id).first()
            if user and user.theme:
                self.theme = user.theme
            if user and user.lang:
                self.lang = user.lang

    def login(self, form) -> bool:
        user = User.objects.filter(
            login=form.login.data,
            password=form.password.data,
        )
        if user.exists():
            user = user.first()
            self.user = user.name or user.login
            self.user_id = user.login
            self.lang = user.lang or 'en'
            self.theme = user.theme or 'default'
            return True

        raise Exception('Login or password invalid')


@myferet.register_resource()
class RUser(LCRUDResource, Resource):
    code = 'c1'
    label = 'User'

    class Form:
        login = StringField(validators=[InputRequired()])
        name = StringField()
        lang = RadioField(
            label='Language',
            choices=[('en', 'English'), ('fr', 'Français')],
            validators=[InputRequired()],
            render_kw={"vertical": False},
        )
        theme = SelectField(
            label='Theme',
            choices=theme_choices,
        )

        @property
        def pk(self):
            return self.login

    class MetaViewList:

        class Form:
            theme = SelectField(
                choices=theme_choices,
            )
            lang = None
            # print_1 = PostButtonField()

        class Filter:
            lang = SelectField(choices=[('en', 'English'), ('fr', 'Français')])

        actions = [
            Actionset('Print', [
                Action('Print 1', 'print_1'),
                SelectedRowsAction('Print 10', 'print_10'),
            ]),
        ]

    class MetaViewCreate:

        class Form:
            password = PasswordField(validators=[Password()])
            password_confirm = PasswordField(
                validators=[InputRequired(), EqualTo('password')],
            )

    class MetaViewRead:

        class Form:
            theme = SelectField(
                choices=theme_choices,
            )
            lang = SelectField(choices=[('en', 'English'), ('fr', 'Français')])

        actions = [
            Actionset('Print', [
                GotoViewAction('Update password', 'update_password'),
                Action('Print 1', 'print_1'),
                Action('Print 10', 'print_10'),
            ]),
        ]

    class MetaViewUpdatePassword(DefaultViewUpdate):
        code = 'update_password'
        after_update_redirect_to = 'read'
        cancel_button_redirect_to = 'read'

        header_template = """
        <h1>Update the password for {{ form.pk.data }}</h1>
        """

        body_template = """
          <div class="container mb-4">
            {% if error %}
            <div class="notification is-danger">
              {{ error }}
            </div>
            {% endif %}
            {{ form.password }}
            {{ form.password_confirm }}
          </div>
        """

        class Form:
            name = None
            lang = None
            theme = None
            password = PasswordField(validators=[Password()])
            password_confirm = PasswordField(
                validators=[InputRequired(), EqualTo('password')],
            )

    class MetaViewDelete:

        def get_label_from_pks(self, pks):
            return [
                user.name
                for user in User.objects.filter(login__in=pks).all()
            ]

    def print_1(self, *a, **kw) -> None:
        print(1, a, kw)

    def print_10(self, *a, **kw) -> None:
        print(10, a, kw)

    def create(self, form):
        user = User.objects.filter(login=form.login.data)
        if not user.exists():
            raise Exception('User already exist')

        user = User()
        form.populate_obj(user)
        user.save()

        return user.login

    def read(self, form_cls, pk):
        user = User.objects.filter(login=pk)
        if user.exists():
            return form_cls(MultiDict(user.first().__dict__))

        return None

    def filtered_reads(self, form_cls, filters, offset, limit):
        forms = []
        total = 0
        users = User.objects.filter()
        for key, values in filters:
            users = users.filter(
                reduce(
                    operator.or_,
                    (Q(**{f'{key}__contains': x}) for x in values),
                ),
            )

        total = users.count()
        for user in users[offset:offset + limit]:
            forms.append(form_cls(MultiDict(user.__dict__)))

        return {
            'total': total,
            'forms': forms,
        }

    def update(self, forms) -> None:
        for form in forms:
            user = User.objects.get(login=form.pk.data)
            if user:
                form.populate_obj(user)
                user.save()
                try:
                    req = cvar_request.get()
                    if req and getattr(req, "session", None):
                        if req.session.user_id == user.login and user.theme:
                            req.session.theme = user.theme
                except LookupError:
                    pass

    def delete(self, pks) -> None:
        User.objects.get(login__in=pks).delete()


myferet.register_aside_menus('aside1', [
    AsideHeaderMenu('My aside menu', children=[
        AsideMenu('Home page', page='homepage', icon="ti ti-ghost"),
        AsideMenu('User', page='resource', resource='c1'),
    ]),
])
myferet.register_toolbar_left_menus([
    RUser.menu,
    ToolBarDropDownMenu(
        'My left menu',
        visible_callback=menu_for_authenticated_user,
        children=[
            ToolBarMenu(
                'Other Menu',
                page="aside-menu",
                aside="aside1",
                aside_page='resource',
                resource='c1',
            ),
        ],
    ),
])
