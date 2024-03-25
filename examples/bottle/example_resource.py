import logging
from contextlib import contextmanager
from os import path

from bottle import abort, app, debug, request, response, route, run, static_file
from BottleSessions import BottleSessions
from multidict import MultiDict

from feretui import (
    FeretUI,
    Request,
    Session,
    Resource,
    Password,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    Session as SQLASession,
)
from sqlalchemy import create_engine, String, select, func
from wtforms import StringField, RadioField, PasswordField
from wtforms.validators import InputRequired

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
    def __init__(self, user_id=None, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id

    def login(self, form):
        with SQLASession(engine) as session:
            stmt = select(User).where(
                User.login == form.login.data,
                User.password == form.password.data
            )
            user = session.scalars(stmt).one_or_none()
            if user:
                self.user = user.name or user.login
                self.user_id = user.login
                self.lang = user.lang or 'en'
                self.theme = user.theme or 'journal'
                return True

            raise Exception('Login or password invalid')


@myferet.register_resource(
    'c1',
    'User',
    # access rules
)
class RUser(Resource):

    class Form:
        login = StringField(validators=[InputRequired()])
        name = StringField()
        lang = RadioField(
            label='Language',
            choices=[('en', 'English'), ('fr', 'Français')],
            validators=[InputRequired()],
            render_kw=dict(vertical=False),
        )
        password = PasswordField(validators=[Password()])
        theme = RadioField(
            choices=[
                ('journal', 'Journal'),
                ('minthy', 'Minthy'),
                ('darkly', 'Darkly'),
            ],
            render_kw=dict(vertical=False),
        )

        @property
        def pk(self):
            return self.login

    @classmethod
    def create(self, form):
        with SQLASession(engine) as session:
            user = User()
            form.populate_obj(user)
            session.add(user)
            session.commit()

        return user.login

    def read(self, form_cls):
        with SQLASession(engine) as session:
            user = session.get(User, self.pk)
            if user:
                return form_cls(MultiDict(user.__dict__))

    @classmethod
    def filtered_reads(self, form_cls, filters, offset, limit):
        forms = []
        total = 0
        with SQLASession(engine) as session:
            stmt = select(User).where()
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

    def update(self, form):
        with SQLASession(engine) as session:
            user = session.get(User, self.pk)
            if user:
                form.populate_obj(user)
                session.commit()
                return user.login

    def delete(self):
        with SQLASession(engine) as session:
            session.delete(session.get(User, self.pk))
            session.commit()


myferet.register_toolbar_left_menus([
    RUser.menu()
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


@route('/feretui/action/<action>', method=['GET', 'DELETE'])
def get_action(action):
    with feretui_session(MySession) as session:
        frequest = Request(
            method=Request.GET,
            querystring=request.query_string,
            headers=dict(request.headers),
            session=session,
        )
        res = myferet.execute_action(frequest, action)
        add_response_headers(res.headers)
        return res.body


@route('/feretui/action/<action>', method=['POST', 'PUT', 'PATCH'])
def post_action(action):
    with feretui_session(MySession) as session:
        frequest = Request(
            method=Request.POST,
            form=MultiDict(request.forms),
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
    debug(True)
    run(host="localhost", port=8080)
