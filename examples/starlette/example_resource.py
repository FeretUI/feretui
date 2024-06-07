import logging
from contextlib import contextmanager

from starlette.applications import Starlette
from starlette.responses import HTMLResponse, FileResponse, Response
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

from multidict import MultiDict
import uvicorn
from sqlalchemy import String, create_engine, func, select
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
            with SQLASession(engine) as session:
                return [
                    session.get(User, pk).name
                    for pk in pks
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

    def update(self, forms) -> None:
        with SQLASession(engine) as session:
            for form in forms:
                user = session.get(User, form.pk.data)
                if user:
                    form.populate_obj(user)
                    session.commit()

    def delete(self, pks) -> None:
        with SQLASession(engine) as session:
            for pk in pks:
                session.delete(session.get(User, pk))

            session.commit()


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


if __name__ == "__main__":
    app = Starlette(
        debug=True,
        routes=[
            Route('/', index),
            Route('/feretui/static/{filepath:path}', feretui_static_file),
            Route(
                '/feretui/action/{action:str}',
                call_action,
                methods=['GET', 'POST', "DELETE"]),
        ],
        middleware=[
            Middleware(SessionMiddleware, secret_key="secret"),
        ],
        on_startup=[startup],
    )
    uvicorn.run(app, port=8080, log_level="info")
