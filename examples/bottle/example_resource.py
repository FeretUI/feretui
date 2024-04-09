import logging
from contextlib import contextmanager
from os import path

from bottle import abort, app, request, response, route, run, static_file
from BottleSessions import BottleSessions
from multidict import MultiDict
from sqlalchemy import String, create_engine, func, select

# Password,
# PostButtonField,
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)
from sqlalchemy.orm import (
    Session as SQLASession,
)
from wtforms import PasswordField, RadioField, SelectField, StringField
from wtforms.validators import EqualTo, InputRequired

from feretui import (
    Action,
    Actionset,
    FeretUI,
    LCRUDResource,
    Password,
    Request,
    Resource,
    SelectedRowsAction,
    Session,
)

logging.basicConfig(level=logging.DEBUG)

# -- for bottle --


@contextmanager
def feretui_session(cls):
    session = None
    try:
        session = cls(**request.session)
        yield session
    finally:
        if session:
            request.session.update(session.to_dict())


def add_response_headers(headers) -> None:
    for k, v in headers.items():
        response.set_header(k, v)

# -- SQLA --


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user_account"

    login: Mapped[str] = mapped_column(
        String(30), primary_key=True, nullable=False)
    password: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(20))
    lang: Mapped[str] = mapped_column(String(2), default="fr")
    theme: Mapped[str] = mapped_column(String(10), default="minthy")


engine = create_engine("sqlite:///resource.db")
Base.metadata.create_all(engine)
# -- for feretui --


myferet = FeretUI()
myferet.load_internal_catalog('fr')


class MySession(Session):
    def __init__(self, user_id=None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.user_id = user_id

    def login(self, form) -> bool:
        with SQLASession(engine) as session:
            stmt = select(User).where(
                User.login == form.login.data,
                User.password == form.password.data,
            )
            user = session.scalars(stmt).one_or_none()
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

    page_security = None
    action_security = None

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
                Action('Print 1', 'print_1'),
                Action('Print 10', 'print_10'),
            ]),
        ]

    def print_1(self, *a, **kw) -> None:
        print(1, a, kw)

    def print_10(self, *a, **kw) -> None:
        print(10, a, kw)

    def create(self, form):
        with SQLASession(engine) as session:
            user = session.get(User, form.login.data)
            if user:
                raise Exception('User already exist')

            user = User()
            form.populate_obj(user)
            session.add(user)
            session.commit()

            return user.login

    def read(self, form_cls, pk):
        with SQLASession(engine) as session:
            user = session.get(User, pk)
            if user:
                return form_cls(MultiDict(user.__dict__))
            return None

    def filtered_reads(self, form_cls, filters, offset, limit):
        forms = []
        total = 0
        with SQLASession(engine) as session:
            stmt = select(User).where()
            for key, values in filters:
                if len(values) == 1:
                    stmt = stmt.filter(
                        getattr(User, key).ilike(f'%{values[0]}%'),
                    )
                elif len(values) > 1:
                    stmt = stmt.filter(getattr(User, key).in_(values))

            stmt_count = select(func.count()).select_from(
                stmt.subquery())
            total = session.execute(stmt_count).scalars().first()

            stmt = stmt.offset(offset).limit(limit)
            for user in session.scalars(stmt):
                forms.append(form_cls(MultiDict(user.__dict__)))

        return {
            'total': total,
            'forms': forms,
        }

    def update(self, form, pk):
        with SQLASession(engine) as session:
            user = session.get(User, pk)
            if user:
                form.populate_obj(user)
                session.commit()
                return user.login
            return None

    def delete(self, pks) -> None:
        with SQLASession(engine) as session:
            for pk in pks:
                session.delete(session.get(User, pk))

            session.commit()


myferet.register_toolbar_left_menus([
    RUser.menu,
])

# -- app --


@route('/')
def index():
    with feretui_session(MySession) as session:
        frequest = Request(
            method=Request.GET,
            querystring=request.query_string,
            headers=dict(request.headers),
            session=session,
        )
        res = myferet.render(frequest)
        add_response_headers(res.headers)
        return res.body


@route('/feretui/static/<filepath:path>')
def feretui_static_file(filepath):
    filepath = myferet.get_static_file_path(filepath)
    if filepath:
        root, name = path.split(filepath)
        return static_file(name, root)

    abort(404)
    return None


@route('/feretui/action/<action>', method=['DELETE', 'GET', 'POST'])
def call_action(action):
    with feretui_session(MySession) as session:
        frequest = Request(
            method=getattr(Request, request.method),
            querystring=request.query_string,
            form=MultiDict(request.forms),
            params=request.params.dict,
            headers=dict(request.headers),
            session=session,
        )
        res = myferet.execute_action(frequest, action)
        add_response_headers(res.headers)
        return res.body


if __name__ == "__main__":
    with SQLASession(engine) as session:
        stmt = select(User).where(User.login == 'admin')
        user = session.scalars(stmt).one_or_none()
        if not user:
            session.add(User(
                login='admin',
                password='admin',
                name='Administrator',
            ))
            session.add_all([
                User(login=f'foo{x}', password=f'bar{x}', name='Foo')
                for x in range(100)
            ])
            session.commit()

    app = app()
    cache_config = {
        'cache_type': 'FileSystem',
        'cache_dir': './sess_dir',
        'threshold': 2000,
    }
    BottleSessions(
        app, session_backing=cache_config, session_cookie='appcookie')
    run(host="localhost", port=8080, debug=True, reloader=1)
