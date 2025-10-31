from multidict import MultiDict
from anyblok_feretui.bloks.feretui.myferet import myferet, MySession
from wtforms import PasswordField, RadioField, SelectField, StringField
from wtforms.validators import EqualTo, InputRequired

from feretui import (
    Action,
    Actionset,
    AsideHeaderMenu,
    AsideMenu,
    GotoViewAction,
    LCRUDResource,
    Password,
    Resource,
    SelectedRowsAction,
    ToolBarDropDownMenu,
    ToolBarMenu,
    menu_for_authenticated_user,
)
from feretui.resources.update import DefaultViewUpdate
from feretui.context import ContextProperties


class MySession(MySession):
    def __init__(self, user_id=None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.user_id = user_id

    def login(self, form) -> bool:
        User = self.anyblok.Pyramid.User
        CredentialStore = self.anyblok.Pyramid.CredentialStore
        user = User.query().filter(User.login == form.login.data,).one_or_none()
        credential = CredentialStore.query().filter(
            CredentialStore.login == form.login.data,
        ).one_or_none()
        if user and credential and credential.password == form.password.data:
            self.user = user.name
            self.user_id = user.login
            self.lang = str(user.lang) if user.lang else 'en'
            self.theme = str(user.theme) if user.theme else 'journal'
            return True

        raise Exception('Login or password invalid')


@myferet.register_resource()
class RUser(LCRUDResource, Resource, ContextProperties):
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
        theme = RadioField(
            choices=[
                ('journal', 'Journal'),
                ('minthy', 'Minthy'),
                ('darkly', 'Darkly'),
            ],
            render_kw={"vertical": False},
        )

        @property
        def pk(self):
            return self.login

    class MetaViewList:

        class Form:
            theme = SelectField(
                choices=[
                    ('journal', 'Journal'),
                    ('minthy', 'Minthy'),
                    ('darkly', 'Darkly'),
                ],
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
                choices=[
                    ('journal', 'Journal'),
                    ('minthy', 'Minthy'),
                    ('darkly', 'Darkly'),
                ],
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
            User = self.resource.anyblok.Pyramid.User
            return User.query().filter(User.login.in_(pks)).all().name

    @property
    def anyblok (self):
        return self.request.session.anyblok

    def print_1(self, *a, **kw) -> None:
        print(1, a, kw)

    def print_10(self, *a, **kw) -> None:
        print(10, a, kw)

    def create(self, form):
        user = self.anyblok.Pyramid.User.query().get(form.login.data)
        if user:
            raise Exception('User already exist')

        User = self.anyblok.Pyramid.User
        Credential = self.anyblok.Pyramid.CredentialStore
        user = User.insert(
            login=form.login.data,
            name=form.name.data,
            lang=form.lang.data,
            theme=form.theme.data)
        Credential.insert(login=form.login.data, password=form.password.data)
        return user.login

    def read(self, form_cls, pk):
        user = self.anyblok.Pyramid.User.query().get(pk)
        if user:
            return form_cls(MultiDict(user.to_dict()))
        return None

    def filtered_reads(self, form_cls, filters, offset, limit):
        forms = []
        total = 0
        User = self.anyblok.Pyramid.User
        query = User.query()
        for key, values in filters:
            if len(values) == 1:
                query = query.filter(
                    getattr(User, key).ilike(f'%{values[0]}%'),
                )
            elif len(values) > 1:
                query = query.filter(getattr(User, key).in_(values))

        total = query.count()

        query = query.offset(offset).limit(limit)
        for user in query:
            forms.append(form_cls(MultiDict(user.to_dict())))

        return {
            'total': total,
            'forms': forms,
        }

    def update(self, forms) -> None:
        for form in forms:
            user = self.anyblok.Pyramid.User.query().get(form.pk.data)
            if user:
                form.populate_obj(user)

    def delete(self, pks) -> None:
        for pk in pks:
            self.anyblok.Pyramid.User.query().get(pk).delete()


myferet.register_aside_menus('aside1', [
    AsideHeaderMenu('My aside menu', children=[
        AsideMenu('Home page', page='homepage', icon="fa-solid fa-ghost"),
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
