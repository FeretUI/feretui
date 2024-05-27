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

Default view
~~~~~~~~~~~~

Forms
~~~~~

Actions
~~~~~~~

Existing views
~~~~~~~~~~~~~~

* :class:`feretui.resources.list.LResource`
* :class:`feretui.resources.create.CResource`
* :class:`feretui.resources.read.RResource`
* :class:`feretui.resources.update.UResource`
* :class:`feretui.resources.delete.DResource`
* :class:`feretui.resources.LCRUDResource`

Create your own view
~~~~~~~~~~~~~~~~~~~~

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

~~~~~~~~~~~
Translation
~~~~~~~~~~~

The decorateur register the forms and the templates in
the client feretui. So no action is needed to translate
the resource other that the standard translation of the project.

~~~~~~~~
Examples
~~~~~~~~

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
