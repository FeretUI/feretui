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
templates. The javascrip library Htmx_ to improve the
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

    myferet.register_template_file('my/template.tmpl')


render the template ::

    template_str = myferet.render_template(
        session, 'my-template', tags=['foo', 'bar'])


If the template need a static file (js, css, image), it is possible to add this
static in existing client

::

    myferet.register_js('my-lib.js', 'path in the filesystem')
    myferet.register_css('my-lib.css', 'path in the filesystem')
    myferet.register_image('my-picture.png', 'path in the filesystem')


.. note::

    Python os lib give helper to find the path where the module is installed.

.. note::

    An existing entrypoint is called at during the initialisation of the
    instance. In this entrypoint you may declare any static you need
    :meth:`feretui.feretui.FeretUI.register_addons_from_entrypoint`.

FeretUI include theme mecanism base on
`Bulma watch <https://jenil.github.io/bulmaswatch/>`_. It is easier to add your
new theme file with :meth:`feretui.feretui.FeretUI.register_theme`.

::

    myferet.register_theme('my-theme', 'path in the filesystem')


FeretUI add Action mechanism. The actions are callbacks and take as arguments
the request and the argument of the action.

* :class:`feretui.FeretUI.register_action`: Decorator to register the callback
  as an action.
* :class:`feretui.FeretUI.execute_action`: Method to execute an action.

FeretUI allow to add page mecanisme. The page are function and take as
arguments the session and the querystring or the body.

* :class:`feretui.FeretUI.register_page`: Decorator to register the page
* :class:`feretui.FeretUI.register_static_page`: Declare a static page
* :class:`feretui.FeretUI.get_page`: Method to return the page function.

::

    @myferet.register_page(
        name='my-page',
        template='''
            <template id="my-page">
                <div>My page</div>
            </template>
        '''
    )
    def my_page(feretui, session, option):
        return feretui.render_template(session, 'my-page')


In the case of the fully static page.

::

    myferet.register_static_page(
        'my-static-page',
        '''
            <div>...</div>
        '''
    )

or

::

    from feretui.pages import static_page

    myferet.register_page(name='my-page')(static_page('my-page-id))


To display the page a menu mecanism exist to call the render method of the
page.

::

    myferet.register_toolbar_right_menus([
        ToolBarMenu(
            'My static page',
            page='my-static-page',
            description="Go to my static page"
        ),
    ])

They are two main type of menu:

* Toolbar: Renderer in the toolbar

  * :class:`feretui.menus.ToolBarMenu`: Simple menu
  * :class:`feretui.menus.ToolBarDropDownMenu`: Dropdown menu
  * :class:`feretui.menus.ToolBarDividerMenu`: Séparator in dropdown menu
  * :class:`feretui.menus.ToolBarUrlMenu`: Link to another url.
  * :class:`feretui.menus.ToolBarButtonMenu`: Simple button menu
  * :class:`feretui.menus.ToolBarButtonsMenu`: Define a group of buttons
  * :class:`feretui.menus.ToolBarButtonUrlMenu`: Link to another url. in a
    button

* Aside: rendere in the aside-menu page

  * :class:`feretui.menus.AsideMenu`: Simple menu
  * :class:`feretui.menus.AsideHeaderMenu`: Display a title and take sub menu.
  * :class:`feretui.menus.AsideUrlMenu`: Link to another url.

The helpers to register or get them are:

* :meth:`feretui.feretui.FeretUI.register_toolbar_left_menus`.
* :meth:`feretui.feretui.FeretUI.register_toolbar_right_menus`.
* :meth:`feretui.feretui.FeretUI.register_aside_menus`.
* :meth:`feretui.feretui.FeretUI.get_aside_menus`.


The client FeretUI add WTForm mecanism. The goal is to display easily
formulaire in the pages and validate the entry in the actions.

To link the form with the translation and the bulma renderer you must inherit
:class:`feretui.form.FeretUIForm`.

If you need to register a password you must use the validator
:class:`feretui.form.Password`

The resource is a set of page and form to represent a data and tools
to manipulate this data.

* :class:`feretui.resources.resource.Resource`
* :class:`feretui.resources.list.LResource`
* :class:`feretui.resources.create.CResource`
* :class:`feretui.resources.list.RResource`
* :class:`feretui.resources.update.UResource`
* :class:`feretui.resources.delete.DResource`
* :class:`feretui.resources.list.LCRUDResource`


The client FeretUI add translation mechanism. This mecanism can be declared
with addon's name attribute. This attribute is used to extract the translation
of FeretUI or an additionnal project. The translated object are:

* :class:`feretui.translation.TranslatedFileTemplate`
* :class:`feretui.translation.TranslatedForm`
* :class:`feretui.translation.TranslatedMenu`
* :class:`feretui.translation.TranslatedStringTemplate`
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
        response = myferet.execute_action(frequest, 'action-arg1-arg2')
        return response.body

.. _Markup: https://markupsafe.palletsprojects.com/en/2.1.x/escaping/
.. _HtmlElement: https://lxml.de/api/lxml.html.HtmlElement-class.html
.. _PoFile: https://polib.readthedocs.io/en/latest/api.html#polib.POFile
.. _WTForms: https://wtforms.readthedocs.io/en/3.1.x/
.. _Form: https://wtforms.readthedocs.io/en/3.1.x/forms/#wtforms.form.Form
.. _Field: https://wtforms.readthedocs.io/en/3.1.x/fields/#the-field-base-class
.. _Htmx: https://htmx.org
.. _MultiDict: https://pypi.org/project/multidict/
"""
from feretui.feretui import FeretUI  # noqa : F401
from feretui.form import FeretUIForm, Password  # noqa : F401
from feretui.helper import (  # noqa : F401
    action_validator,
    action_for_authenticated_user,
    action_for_unauthenticated_user,
    menu_for_authenticated_user,
    menu_for_unauthenticated_user,
    page_for_authenticated_user_or_goto,
    page_for_unauthenticated_user_or_goto,
)
from feretui.menus import (  # noqa : F401
    ToolBarButtonMenu,
    ToolBarButtonsMenu,
    ToolBarButtonUrlMenu,
    ToolBarMenu,
    ToolBarDropDownMenu,
    ToolBarDividerMenu,
    ToolBarUrlMenu,
    AsideMenu,
    AsideHeaderMenu,
    AsideUrlMenu,
)
from feretui.request import Request  # noqa : F401
from feretui.resources import (  # noqa: F401
    Action,
    Actionset,
    LResource,
    CResource,
    DResource,
    GotoViewAction,
    LCRUDResource,
    Resource,
    RResource,
    SelectedRowsAction,
    UResource,
)
from feretui.response import Response  # noqa : F401
from feretui.session import Session  # noqa : F401
