.. This file is a part of the FeretUI project
..
..    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

SQLAlchemy
----------

This parts does not explain how to create and use a SQLAlchemy project, only 
how to link SQLalchemy with FeretUI.

To help you with SQLAlchemy see the `documentation <https://www.sqlalchemy.org/>`_.

~~~~~~~~~~~
Simple case
~~~~~~~~~~~

The contextmanager **sqlalchemy.Session** create a session with the database.
No need more to link them.

::

    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session as SQLASession

    engine = create_engine('sqlite:///mydb.db')
    myferet = FeretUI()

    @myferet.register_action
    @action_validator(methods=[Request.Post])
    def my_action(feretui, request):
        with SQLASession(engine) as session:
            DO stuff with the session


~~~~~~~~~~~
With a Form
~~~~~~~~~~~

WTForms add helper to work with SQLAlchemy `see <https://wtforms.readthedocs.io/en/3.1.x/crash_course/#getting-started>`_.

::

    from ..mymodels import MyModel
    from ..myforms import MyForm

    @myferet.register_action
    @action_validator(methods=[Request.Post])
    def create_or_update(feretui, request):
        with SQLASession(engine) as session:
            mymodel = session.get(MyModel, request.form.pk)
            if mymodel:
                form = MyForm(request.form, mymodel)
            else:
                mymodel = MyForm()
                session.add(mymodel)
                form = MyForm(request.form)

            if form.validate():
                form.populate_obj(mymodel)
            else:
                raise Exception()

.. note::

    They are not difference between action and resource.

~~~~~~~~~~~~~~~
Case with flask
~~~~~~~~~~~~~~~

In the Flask world, the `flask_sqlalchemy <form.populate_obj(user)>`_'s project add
helper to link perfectly Flask and Sqlalchemy, but the previous explanation
works too.

If you want to do a project with any web server, use the previous explanation but
if you use only flask so use the flask_sqlalchemy's project.

::

    from flask_sqlalchemy import SQLAlchemy
    from .mymodels import MyModel

    db = SQLAlchemy(...)

    myferet = FeretUI()

    @myferet.register_action
    @action_validator(methods=[Request.Post])
    def my_action(feretui, request):
        mymodel = MyModel()
        db.session.add(mymodel)
        db.session.commit()

~~~~~~~~~~~~~~~~~
Case with Pyramid
~~~~~~~~~~~~~~~~~

In the Pyramid world, the `zope.sqlalchemy <https://github.com/zopefoundation/zope.sqlalchemy/tree/master/src/zope/sqlalchemy>`_'s project add
helper to link perfectly the transaction between pyramid and Sqlalchemy, but the previous explanation
works too.

If you want to do a project with any web server, use the previous explanation but
if you use only pyramid so use the zope.sqlalchemy's project.

::

    from zope.sqlalchemy import register
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, scoped_session
    from .mymodels import MyModel

    engine = create_engine('sqlite:///mydb.db')

    DBSession = scoped_session(sessionmaker(bind=engine))
    mysession = DBSession()
    register(DBSession)

    myferet = FeretUI()

    @myferet.register_action
    @action_validator(methods=[Request.Post])
    def my_action(feretui, request):
        mymodel = MyModel()
        mysession.add(mymodel)
