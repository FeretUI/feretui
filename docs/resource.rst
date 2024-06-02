.. This file is a part of the FeretUI project
..
..    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

Resource
--------

The resource is a set of views to represente and manipulate the data to display and to
modify.

::

    from feretui import Resource

    @myferet.register_resource()
    class MyResource(Resource):
        code: str = 'my-resource'
        label: str = 'My resource'

        ...

.. warning::

    The decorator not only register the resource in the feretui client. It also build the views
    in the resource.


~~~~~
Menus
~~~~~

To define a menu you could:

Method 1::

    MyResource.menu

Method 2::

    ToolBarMenu(
        MyResource.label,
        page="resource",
        resource=MyResource.code
        visible_callback=menu_for_authenticated_user,
    )

The two methods give the same result.

~~~~~
Views
~~~~~

The views are the renders used by your application.

Existing views
~~~~~~~~~~~~~~

* List : :class:`feretui.resources.list.LResource`
* Create / New : :class:`feretui.resources.create.CResource`
* Read : :class:`feretui.resources.read.RResource`
* Update / Edit : :class:`feretui.resources.update.UResource`
* Delete / Remove : :class:`feretui.resources.delete.DResource`
* List + Create + Read + Update + Delete : :class:`feretui.resources.LCRUDResource`

You can update the configuration of the view in your
resource::

    from feretui import Resource, LResource

    @myferet.register_resource()
    class MyResource(LResource, Resource):
        code: str = 'my-resource'
        label: str = 'My resource'

        class MetaViewList:
            limit: int = 5  # display only 5 lines in the pagination.

Forms
~~~~~

The Forms are the base of the representation of the all views.

The declaration of the View is done in the :

* Recource class
* MetaView class

::

    class MyResource(LResource, Resource):

        class Form:
            code = StringField()

        class MetaViewList:

            class Form:
                label = StringField()

The **Form** class is a mixin not the final the Form.
The MetaView's Form's class inherit also the Resource Form class.

In the previous example the Resource, the build form have got two fields:

* code
* label

The mecanism is not use full if you are only one MetaView's type.

The build of the resource class :

* transform the MetaView's Form's class as a Form
* Add FeretUIForm in the inheritance
* Declare in the FeretUI instance

Actions
~~~~~~~

Some views can declare actions:

* List : :class:`feretui.resources.list.LResource`
* Read : :class:`feretui.resources.read.RResource`

The actions is declared in the MetaView's class

    class MyResource(RResource, Resource):

        class MetaViewRead:

            actions = [
                Actionset('Title of the set of actions', [
                    GotoViewAction('Title of the action', 'my_resource_method'),
                ]),
            ]

        def my_resource_method(self, feretui, request, **kwargs):
            ...


The method called is defined on the resource the same method can be called by any view
that declare the action set.

The action's type are:

* :class:`feretui.resources.actions.Action` : call the method
* :class:`feretui.resources.actions.GotoViewAction` : call the goto main action to change page
* :class:`feretui.resources.actions.SelectedRowsAction` : call the method only if a row is selected. 
  This action can be called only on a MetaView List type

~~~~~~~~~~~~~~~~~~~~~~~
Visibility and security
~~~~~~~~~~~~~~~~~~~~~~~

The resource take the visibility and the autorisation mecanism
of the main object.

Menus
~~~~~

::

    from feretui import Resource, menu_for_authenticated_user

    @myferet.register_resource()
    class MyResource(Resource):
        code: str = 'my-resource'
        label: str = 'My resource'
        menu_visibility: Callable = staticmethod(menu_for_authenticated_user)

you also create your own method inside ::

    from feretui import Resource

    @myferet.register_resource()
    class MyResource(Resource):
        code: str = 'my-resource'
        label: str = 'My resource'

        @staticmethod
        def menu_visibility(session: Session) -> bool:
            return True  # always displayed

.. warning::

    You can use classmethod or static method, but not
    a method, because the menu is down with the class and
    not the instance.

Pages
~~~~~

::

    from feretui import Resource, page_for_authenticated_user_or_goto, login

    @myferet.register_resource()
    class MyResource(Resource):
        code: str = 'my-resource'
        label: str = 'My resource'

        page_visibility: Callable = staticmethod(
            page_for_authenticated_user_or_goto(login))

Actions
~~~~~~~

::

    from feretui import Resource, action_for_authenticated_user

    @myferet.register_resource()
    class MyResource(Resource):
        code: str = 'my-resource'
        label: str = 'My resource'

        action_security: Callable = staticmethod(action_for_authenticated_user)

~~~~~~~~~~~~~~~~~~~~~~~~~~~
Create your own view's type
~~~~~~~~~~~~~~~~~~~~~~~~~~~

To create a new view you need to create:

* default class attribute defined in a class, this document the possibility
  of the configuration of your view.

  Example for the list view::
  
      class DefaultViewList:
          """Default value for the view list."""
  
          label: str = None
          limit: int = 20
          create_button_redirect_to: str = None
          delete_button_redirect_to: str = None
          do_click_on_entry_redirect_to: str = None

* The class View, define the render and the actions
  Example for the list view::

      class ListView(MultiView, LabelMixinForView, View):
          """List view."""
          code: str = 'list'
      
          def render(
              self: "ListView",
              feretui: "FeretUI",
              session: Session,
              options: dict,
          ) -> str:
              """Render the view.
      
              :param feretui: The feretui client
              :type feretui: :class:`feretui.feretui.FeretUI`
              :param session: The Session
              :type session: :class:`feretui.session.Session`
              :param options: The options come from the body or the query string
              :type options: dict
              :return: The html page in
              :rtype: str.
              """

* Th mixin class to build the view in the resource.
  Example for the list view::

      class LResource:
          """LResource class."""
      
          default_view: str = 'list'
      
          MetaViewList = DefaultViewList
      
          def build_view(
              self: "LResource",
              view_cls_name: str,
          ) -> Resource:
              """Return the view instance in fonction of the MetaView attributes.
      
              :param view_cls_name: name of the meta attribute
              :type view_cls_name: str
              :return: An instance of the view
              :rtype: :class:`feretui.resources.view.View`
              """
              if view_cls_name.startswith('MetaViewList'):
                  meta_view_cls = self.get_meta_view_class(view_cls_name)
                  meta_view_cls.append(ListView)
                  view_cls = type(
                      'ListView',
                      tuple(meta_view_cls),
                      {},
                  )
                  if not self.default_view:
                      self.default_view = view_cls.code
      
                  return view_cls(self)
      
              return super().build_view(view_cls_name)


The name of the **MetaView** should be **MetaView`code`**.

~~~~~~~~~~~
Translation
~~~~~~~~~~~

The decorateur register the forms and the templates in
the client feretui. So no action is needed to translate
the resource other that the standard translation of the project.

~~~~~~~~
Examples
~~~~~~~~

Example 2
~~~~~~~~~

This is an example with SQLAlchemy to manage the printer in the application.


DB model::

    class Printer(Base):
        __tablename__ = "device_printer"

        pk: Mapped[int] = mapped_column(Integer, primary_key=True)
        url: Mapped[str] = mapped_column(String(30), nullable=False)
        label: Mapped[str] = mapped_column(String(20), nullable=False)

Resource::

    from wtforms_components import read_only


    @myferet.register_resource()
    class RPrinter(LCRUDResource, Resource):
        code = 'c2'
        label = 'Printers'

        class Form:
            pk = IntegerField()
            url = URLField(validators=[InputRequired()])
            label = StringField(validators=[InputRequired()])

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                read_only(self.pk)

        def create(self, form):
            with SQLASession(engine) as session:
                printer = session.get(Printer, form.pk.data)
                if printer:
                    raise Exception('printer already exist')

                printer = Printer()
                form.populate_obj(printer)
                session.add(printer)
                session.commit()

                return printer.pk

        def read(self, form_cls, pk):
            with SQLASession(engine) as session:
                printer = session.get(Printer, pk)
                if user:
                    return form_cls(MultiDict(printer.__dict__))
                return None

        def filtered_reads(self, form_cls, filters, offset, limit):
            forms = []
            total = 0
            with SQLASession(engine) as session:
                stmt = select(Printer).where()
                stmt_count = select(func.count()).select_from(
                    stmt.subquery())
                total = session.execute(stmt_count).scalars().first()

                stmt = stmt.offset(offset).limit(limit)
                for printer in session.scalars(stmt):
                    forms.append(form_cls(MultiDict(printer.__dict__)))

            return {
                'total': total,
                'forms': forms,
            }

        def update(self, forms) -> None:
            with SQLASession(engine) as session:
                for form in forms:
                    printer = session.get(Printer, form.pk.data)
                    if printer:
                        form.populate_obj(printer)
                        session.commit()

        def delete(self, pks) -> None:
            with SQLASession(engine) as session:
                for pk in pks:
                    session.delete(session.get(Printer, pk))

                session.commit()


Example 2
~~~~~~~~~

This is an example with SQLAlchemy to manage the user in the application.


DB model::

    class User(Base):
        __tablename__ = "user_account"

        login: Mapped[str] = mapped_column(
            String(30), primary_key=True, nullable=False)
        password: Mapped[str] = mapped_column(String(30), nullable=False)
        name: Mapped[str] = mapped_column(String(20))
        lang: Mapped[str] = mapped_column(String(2), default="fr")
        theme: Mapped[str] = mapped_column(String(10), default="minthy")

Resource::

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

            class Filter:
                lang = SelectField(choices=[('en', 'English'), ('fr', 'Français')])

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
