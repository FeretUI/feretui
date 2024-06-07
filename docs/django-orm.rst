.. This file is a part of the FeretUI project
..
..    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

Django
------

This parts does not explain how to create and use a django project, only 
how to link django orm with FeretUI.

To help you with SQLAlchemy see the `documentation <https://www.sqlalchemy.org/>`_.

~~~~~~~~~~~
Simple case
~~~~~~~~~~~

See the `ORM's documentation <https://docs.djangoproject.com/en/5.0/#the-model-layer/>`_ to create and use Model.

::

    from .models import MyModel

    @myferet.register_action
    @action_validator(methods=[Request.Post])
    def my_action(feretui, request):
        query = MyModel.objects.all()


~~~~~~~~~~~
With a Form
~~~~~~~~~~~

WTForms add helper to work with django `see <https://wtforms.readthedocs.io/en/3.1.x/crash_course/#getting-started>`_.

::

    from ..models import MyModel
    from ..myforms import MyForm

    @myferet.register_action
    @action_validator(methods=[Request.Post])
    def create_or_update(feretui, request):
        mymodel = MyModel.objects.get(pk=request.form.pk)
        if mymodel:
            form = MyForm(request.form, mymodel)
        else:
            mymodel = MyForm()
            form = MyForm(request.form)

        if form.validate():
            form.populate_obj(mymodel)
            mymodel.save()
        else:
            raise Exception()

.. note::

    They are not difference between action and resource.

.. warning::

    An issue exist to activate CSRF, for the moment you should stop to use the middleware
