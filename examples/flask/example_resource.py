import logging
import urllib
from contextlib import contextmanager
from wsgiref.simple_server import make_server

from flask import Flask, abort, make_response, request, send_file
from flask_sqlalchemy import SQLAlchemy
from multidict import MultiDict
from sqlalchemy import String, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)
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
    Request,
    Resource,
    SelectedRowsAction,
    Session,
    ToolBarDropDownMenu,
    ToolBarMenu,
    menu_for_authenticated_user,
)
from feretui.resources.update import DefaultViewUpdate

logging.basicConfig(level=logging.DEBUG)

# -- for flask + SQLAlchemy --


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.secret_key = b'secret'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///resource.db"
db.init_app(app)


@contextmanager
def feretui_session(cls):
    from flask import session
    fsession = None
    try:
        fsession = cls(**session)
        yield fsession
    finally:
        if fsession:
            session.update(fsession.to_dict())


def response(fresponse):
    resp = make_response(fresponse.body)
    resp.headers.update(fresponse.headers)
    return resp


# -- SQLA --


class User(db.Model):
    __tablename__ = "user_account"

    login: Mapped[str] = mapped_column(
        String(30), primary_key=True, nullable=False)
    password: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(20))
    lang: Mapped[str] = mapped_column(String(2), default="fr")
    theme: Mapped[str] = mapped_column(String(10), default="minthy")


with app.app_context():
    db.create_all()
    stmt = db.select(User).where(User.login == 'admin')
    user = db.session.scalars(stmt).one_or_none()
    if not user:
        db.session.add(User(
            login='admin',
            password='admin',
            name='Administrator',
        ))
        db.session.add_all([
            User(login=f'foo{x}', password=f'bar{x}', name='Foo')
            for x in range(100)
        ])
        db.session.commit()

# -- for feretui --


myferet = FeretUI()
myferet.load_internal_catalog('fr')


class MySession(Session):
    def __init__(self, user_id=None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.user_id = user_id

    def login(self, form) -> bool:
        stmt = db.select(User).where(
            User.login == form.login.data,
            User.password == form.password.data,
        )
        user = db.session.execute(stmt).scalars().one_or_none()
        if user:
            self.user = user.name or user.login
            self.user_id = user.login
            self.lang = user.lang or 'en'
            self.theme = user.theme or 'journal'
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
            return [
                db.session.get(User, pk).name
                for pk in pks
            ]

    def print_1(self, *a, **kw) -> None:
        print(1, a, kw)

    def print_10(self, *a, **kw) -> None:
        print(10, a, kw)

    def create(self, form):
        user = db.get(User, form.login.data)
        if user:
            raise Exception('User already exist')

        user = User()
        form.populate_obj(user)
        db.session.add(user)
        db.session.commit()

        return user.login

    def read(self, form_cls, pk):
        user = db.get(User, pk)
        if user:
            return form_cls(MultiDict(user.__dict__))
        return None

    def filtered_reads(self, form_cls, filters, offset, limit):
        forms = []
        total = 0
        stmt = db.select(User).where()
        for key, values in filters:
            if len(values) == 1:
                stmt = stmt.filter(
                    getattr(User, key).ilike(f'%{values[0]}%'),
                )
            elif len(values) > 1:
                stmt = stmt.filter(getattr(User, key).in_(values))

        stmt_count = db.select(func.count()).select_from(
            stmt.subquery())
        total = db.session.execute(stmt_count).scalars().first()

        stmt = stmt.offset(offset).limit(limit)
        for user in db.session.scalars(stmt):
            forms.append(form_cls(MultiDict(user.__dict__)))

        return {
            'total': total,
            'forms': forms,
        }

    def update(self, forms) -> None:
        for form in forms:
            user = db.session.get(User, form.pk.data)
            if user:
                form.populate_obj(user)

        db.session.commit()

    def delete(self, pks) -> None:
        for pk in pks:
            db.session.delete(db.session.get(User, pk))

        db.session.commit()


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

# -- app --


@app.route('/')
def index():
    with feretui_session(MySession) as session:
        frequest = Request(
            method=Request.GET,
            querystring=request.query_string.decode('utf-8'),
            headers=dict(request.headers),
            session=session,
        )
        return response(myferet.render(frequest))


@app.route('/feretui/static/<path:filepath>')
def feretui_static_file(filepath):
    filepath = myferet.get_static_file_path(filepath)
    if filepath:
        return send_file(filepath.resolve())

    abort(404)
    return None


@app.route('/feretui/action/<action>', methods=['DELETE', 'GET', 'POST'])
def call_action(action):
    params = {}
    if request.method in ['DELETE', 'POST']:
        params = {
            x: request.form.getlist(x)
            for x in request.form
        }
        params.update(urllib.parse.parse_qs(
            request.query_string.decode('utf-8'),
        ))

    with feretui_session(MySession) as session:
        frequest = Request(
            method=getattr(Request, request.method),
            querystring=request.query_string.decode('utf-8'),
            form=MultiDict(request.form),
            params=params,
            headers=dict(request.headers),
            session=session,
        )
        return response(myferet.execute_action(frequest, action))


if __name__ == "__main__":

    with make_server('', 8080, app) as httpd:
        logging.info("Serving on port 8080...")
        httpd.serve_forever()
