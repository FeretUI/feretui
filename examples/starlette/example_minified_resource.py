import logging
from contextlib import contextmanager

from starlette.applications import Starlette
from starlette.responses import HTMLResponse, FileResponse, Response
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

from multidict import MultiDict
import uvicorn
from sqlalchemy import (
    String, Integer, Text, create_engine, func, select, inspect
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)
from sqlalchemy.orm import (
    Session as SQLASession,
)
from wtforms import PasswordField, RadioField
from wtforms.validators import EqualTo, InputRequired
from wtforms_components import PassiveHiddenField

from feretui import (
    Action,
    Actionset,
    FeretUI,
    GotoViewAction,
    LCRUDResource,
    Password,
    Request,
    Resource,
    SelectedRowsAction,
    Session,
    FeretUIForm,
)
from wtforms_alchemy import model_form_factory

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


class TodoList(Base):
    __tablename__ = "todo_list"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(30), nullable=False)
    comment: Mapped[str] = mapped_column(Text)


engine = create_engine("sqlite:///resource.db")
Base.metadata.create_all(engine)

# SqlA + FeretUI


class FormFromSqla:

    WtFormsCls = FeretUIForm

    def __init__(self, SqlAModel, primary_keys_is_hidden=True):
        self.SqlAModel = SqlAModel
        self.mapper = inspect(SqlAModel)
        self.primary_keys_is_hidden = primary_keys_is_hidden
        self.bases = []
        self.properties = {}

    def _call_bases(self, resourceCls):
        if resourceCls:
            self.bases.append(resourceCls)

        self.bases.append(model_form_factory(FeretUIForm))

    def wtforms_pk_properties(self):
        pks = [x.name for x in self.mapper.primary_key]
        if len(pks) == 1:
            def pk(instance):
                return getattr(instance, pks[0])

            self.properties['pk'] = property(pk)

    def wtforms_hidden_pk_properties(self):
        for pk in self.mapper.primary_key:
            self.properties[pk.name] = PassiveHiddenField()

    def _call_properties(self):
        if not hasattr(self.SqlAModel, 'pk'):
            self.wtforms_pk_properties()
        if self.primary_keys_is_hidden:
            self.wtforms_hidden_pk_properties()

    def __call__(self, formCls=None):
        self._call_bases(formCls)
        self._call_properties()

        Meta = getattr(formCls, 'Meta', None)
        if Meta is None:
            Meta = type('Meta', tuple(), {})

        self.properties['Meta'] = Meta
        setattr(Meta, 'model', self.SqlAModel)
        setattr(Meta, 'include_primary_keys', True)

        return type(
            f'Form{self.SqlAModel.__name__}',
            tuple(self.bases),
            self.properties,
        )


class SqlAResourceBase:

    class MetaViewDelete:

        def get_label_from_pks(self, pks):
            Model = self.resource.Form.Meta.model
            with SQLASession(engine) as session:
                return [
                    getattr(session.get(Model, pk), self.resource.record_label)
                    for pk in pks
                ]

    def create(self, form):
        Model = self.Form.Meta.model
        mapper = inspect(Model)
        pk = [x.name for x in mapper.primary_key][0]
        with SQLASession(engine) as session:
            instance = session.get(Model, form.pk.data)
            if instance:
                raise Exception('Already exist')

            instance = Model()
            form.populate_obj(instance)
            session.add(instance)
            session.commit()

            return getattr(instance, pk)

    def read(self, form_cls, pk):
        Model = self.Form.Meta.model
        with SQLASession(engine) as session:
            instance = session.get(Model, pk)
            if instance:
                return form_cls(MultiDict(instance.__dict__))
            return None

    def filtered_reads(self, form_cls, filters, offset, limit):
        forms = []
        total = 0
        Model = self.Form.Meta.model
        with SQLASession(engine) as session:
            stmt = select(Model).where()
            for key, values in filters:
                if len(values) == 1:
                    stmt = stmt.filter(
                        getattr(Model, key).ilike(f'%{values[0]}%'),
                    )
                elif len(values) > 1:
                    stmt = stmt.filter(getattr(Model, key).in_(values))

            stmt_count = select(func.count()).select_from(
                stmt.subquery())
            total = session.execute(stmt_count).scalars().first()

            stmt = stmt.offset(offset).limit(limit)
            for entry in session.scalars(stmt):
                forms.append(form_cls(MultiDict(entry.__dict__)))

        return {
            'total': total,
            'forms': forms,
        }

    def update(self, forms) -> None:
        Model = self.Form.Meta.model
        with SQLASession(engine) as session:
            for form in forms:
                instance = session.get(Model, form.pk.data)
                if instance:
                    form.populate_obj(instance)
                    session.commit()

    def delete(self, pks) -> None:
        Model = self.Form.Meta.model
        with SQLASession(engine) as session:
            for pk in pks:
                session.delete(session.get(Model, pk))

            session.commit()


class From_SqlA_Form:

    SqlAResourceBase = SqlAResourceBase

    def __init__(self, SqlAForm, record_label='pk'):
        self.SqlAForm = SqlAForm
        self.record_label = record_label

    def __call__(self, resourceCls):
        bases = [x for x in resourceCls.__mro__]
        bases.insert(1, self.SqlAResourceBase)
        # put hidden on pk
        return type(
            resourceCls.__name__,
            tuple(bases),
            {
                'Form': self.SqlAForm,
                'record_label': self.record_label,
            },
        )


menus = []


def register_in_menu(resourceCls):
    menus.append(resourceCls)
    return resourceCls


def allResourceMenus(isaside=None):
    res = []
    for menu in menus:
        res.append(menu.menu)

    return res


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


@FormFromSqla(User)
class WtFormUser:
    lang = RadioField(
        label='Language',
        choices=[('en', 'English'), ('fr', 'Français')],
        validators=[InputRequired()],
    )
    theme = RadioField(
        choices=[
            ('journal', 'Journal'),
            ('minthy', 'Minthy'),
            ('darkly', 'Darkly'),
        ],
    )


@register_in_menu
@myferet.register_resource()
@From_SqlA_Form(WtFormUser, record_label="name")
class RUser(LCRUDResource, Resource):
    code = 'c1'
    label = 'user'

    class MetaViewList:

        class Form:
            lang = None

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

    def print_1(self, *a, **kw) -> None:
        print(1, a, kw)

    def print_10(self, *a, **kw) -> None:
        print(10, a, kw)


@register_in_menu
@myferet.register_resource()
@From_SqlA_Form(FormFromSqla(TodoList)(), record_label="title")
class ruser(LCRUDResource, Resource):
    code = 'c2'
    label = 'Todo'


myferet.register_toolbar_left_menus(allResourceMenus())


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
