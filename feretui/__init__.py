# This file is a part of the FeretUI project
#
#    Copyright (C) 2023-2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Feretui.

Small web client to build an admin user interface without any link with a
framework.

This project is not a nodejs project. The client is generated with static
templates. The javascrip library `htmx <https://htmx.org>`_ to improve the
capability to manipulate the DOM and to add HTTP verb (DELETE, PUT, PATCH).

The client is not a Framework, and don't use any web-server, orm, connector
Frameworks. The goal is to separate the concept between both.

In a classical project the database, the ORM model's and the user interface
is declared on the same place. They are both the same configuration. But It is
a mistake, because that limit the possibility and force to have only entry
point by the user interface. The rules as *required*, *readonly*, ... should
be depending only on the user-interface. It is possible to define an interface
based on more than one Model, or with another constraints.

To isolate it about the web-server projects, This project add objects to do
absctract with web server:

* :class:`feretui.request.Request` : It is the class object used by FeretUI
  to represent web-server request.
* :class:`feretui.response.Response` : It is the class object used by FeretUI
  to respond at the client query.
* :class:`feretui.session.Session` : It is the class object used by FeretUI
  to define to represent an user session, it is not the Session of the
  web-server.

FeretUI include to mecanism of templating:

* :class:`feretui.template.Template` : Import template by addons, the template
  can be modified by another template file. They are compiled by id and
  language. The compiled template are stored.
* `jinja <https://jinja.palletsprojects.com/en/3.1.x/>`_.

The both are used in the same time, the internal allow the modularity, and
jinja allow the loop and setter the variable inside the template

[my/template.tmpl] ::

    <template id="my-template">
      <ul>
        {% for tag in tags %}
        <li>{{ tag }}</li>
        {% endfor %}
      </ul>
    </template>

import of the template file ::

    myferet.import_templates_file('my/template.tmpl')


render the template ::

    template_str = myferet.render_template(
        session, 'my-template', tags=['foo', 'bar'])


If the template need a static file (js, css, image), it is possible to add this
static in existing client

::

    myferet.register_js_static('my-lib.js', 'path in the filesystem')
    myferet.register_css_static('my-lib.css', 'path in the filesystem')
    myferet.register_image_static('my-picture.png', 'path in the filesystem')


.. note::

    Python os lib give helper to find the path where the module is installed.

.. note::

    An existing entrypoint is called at during the initialisation of the
    instance. In this entrypoint you may declare any static you need
    :meth:`feretui.feretui.FeretUI.statics_from_entrypoint`.


The client FeretUI add translation mechanism. This mecanism can be declared
with addon's name attribute. This attribute is used to extract the translation
of FeretUI or an additionnal project. The translated object are:

* :class:`feretui.translation.TranslatedMessage`
* :class:`feretui.translation.TranslatedTemplate`

To export the translation, the console script *export-feretui-catalog* extract
all the translation messages in pot file.

::

    from feretui import FeretUI, Session


    myferet = FeretUI()
    session = Session()

    @route('an/url')
    def do_something(request):
        frequest = Request(
            session=session,
            method=Request.POST,
            body=request.body.read(),
            headers=dict(request.headers),
        )
        ...

"""
from feretui.feretui import FeretUI  # noqa : F401
from feretui.request import Request  # noqa : F401
from feretui.response import Response  # noqa : F401
from feretui.session import Session  # noqa : F401
