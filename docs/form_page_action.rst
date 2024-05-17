.. This file is a part of the FeretUI project
..
..    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

Page and action
---------------

~~~~
Page
~~~~

The page is a function who return html on a string

::

    @myferet.register_page()
    def my_page(feretui, session, options):
        return "<div>My HTML.</div>"


* feretui is the instance of the client
* session is the feretui session
* options is the querystring, because the page is only rendering in the GET call.

To display the page, rendere the feretui client with page attribute un the query string

::

    http /?page=mypage

Javascript / CSS / picture
~~~~~~~~~~~~~~~~~~~~~~~~~~

By defaut some lib are loaded and executed in the main page:

* `_Htmx <https://htmx.org>`_
* `hyperscript <https://hyperscript.org/docs/>`_
* `bulma <https://bulma.io/>`_
* `bulma-tooltip <https://bulma-tooltip.netlify.app/get-started/>`_
* `bulma-print <ihttps://github.com/suterma/bulma-print>`_
* `Fontawesome <https://fontawesome.com/>`_
* `themes <https://jenil.github.io/bulmaswatch/>`_

If you need some additionnal javascript, css or picture use the methods:

* :meth:`.FeretUI.register_js`
* :meth:`.FeretUI.register_css`
* :meth:`.FeretUI.register_font`
* :meth:`.FeretUI.register_image`
* :meth:`.FeretUI.register_theme`


.. note::

    All the statics must be on the host.


Templating
~~~~~~~~~~

The template are writing in file(s) and register with :meth:`feretui.feretui.FeretUI.register_template_file`.

my/template/file::

    <templates>
      <template id="my-page">
        <div>My HTML.</div>
      </template>
    </templates>

In the project::

    myferet.register_template_file('my/template/file')

Update the page to renderer the template::

    @myferet.register_page()
    def my_page(feretui, session, options):
        return feretui.render_template(session, 'my-page')


FeretUI use a templating compilation based on `Jinja2 <https://jinja.palletsprojects.com/en/2.10.x/>`_.

my/template/file::

    <templates>
      <template id="my-page">
        <div>Hello {{ name }}</div>
      </template>
    </templates>

Update the page to renderer the template::

    @myferet.register_page()
    def my_page(feretui, session, options):
        return feretui.render_template(
            session, 
            'my-page',
            name=options.get('name', 'My feret'),
        )

.. warning::

    All the behaviours of jinja are available. The only limit is
    the if instruction can not be inside a node attribute.

The templating of FeretUI allow to update, include of copy an existing template.
This behaviour is used to add modularity in the project.

::

    <templates>
      <template extend="my-page">
        <xpath expression="//div" action="insertInside">
          <include template="template id" />
        </xpath>
      </template>
    </templates>


.. warning::

    You can not use extend if the id does not exist
    and you can not use the id twice


::

    To copy an existing template and modify the new template you
    need to filled **extend** (existing id) and **id** (new id)
    attributes.


The existing xpath action are:

* insertInside
* insertBefore
* insertAfter
* replace
* remove
* attributes

Static page
~~~~~~~~~~~

If you need to write a litle and 

~~~~~~
Action
~~~~~~
