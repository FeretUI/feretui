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

If you need to write a litle template without any form or control some helper can help you

Method 1::

    from feretui.pages import static_page

    myferet.register_page(name='my_page')(static_page('my-page'))

Method 2::

    myferet.register_static_page(
        'my_page',
        '''
        <div>My HTML.</div>
        ''',
    )


.. warning::

    The second method register the template in the template instance
    of feretui instance.

    If the template id already exists then an error is raised. In this
    cas the method can not be overwritten.


Template directly in the register_page
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The goal is to defined the page with the template in the same location
in the project.

::

    @myferet.register_page(
        templates=['''
          <template id="my-page">
            <div>My HTML.</div>
          </template>
        '''],
    )
    def my_page(feretui, session, options):
        return feretui.render_template(session, 'my-page')

.. warning::

    The second method register the template in the template instance
    of feretui instance.

    If the template id already exists then an error is raised. In this
    cas the method can not be overwritten.

Added form on your page
~~~~~~~~~~~~~~~~~~~~~~~

FeretUI implement a base class for `wtforms <https://wtforms.readthedocs.io/en/3.1.x/>`_.

::

    from feretui import FeretUIForm

    class MyForm(FeretUIForm):
        ...


The base class:

* overwrite gettext and ngettext for the translation
* overwrite the render of the field to add bulma class on the input

You use it directly in the page or the action.

::

    @myferet.register_page(
        templates=['''
          <template id="my-page">
            <form
              hx-post="{{ feretui.base_url }}/action/my_form"
              hx-swap="outerHTML"
              hx-trigger="submit"
            >
              <div class="container content">
                <h1>My form</h1>
                {% for field in form %}
                {{ field }}
                {% endfor %}
                <div class="buttons">
                  <button
                    class="button is-primary is-fullwidth"
                    type="submit"
                  >
                    Submit
                  </button>
                </div>
              </div>
            </form>
          </template>
        '''],
    )
    def my_page(feretui, session, options):
        form = option.get('form', MyForm())
        return feretui.render_template(session, 'my-page', form=form)

You need to register the Form to export the translation.

Method 1::

    @myferet.register_form()
    class MyForm(FeretUIForm):
        ...


Method 2::

    @myferet.register_page(
        templates=['''
          <template id="my-page">
            <form
              hx-post="{{ feretui.base_url }}/action/my_form"
              hx-swap="outerHTML"
              hx-trigger="submit"
            >
              <div class="container content">
                <h1>My form</h1>
                {% for field in form %}
                {{ field }}
                {% endfor %}
                <div class="buttons">
                  <button
                    class="button is-primary is-fullwidth"
                    type="submit"
                  >
                    Submit
                  </button>
                </div>
              </div>
            </form>
          </template>
        '''],
        forms=[MyForm],
    )
    def my_page(feretui, session, options):
        form = option.get('form', MyForm())
        return feretui.render_template(session, 'my-page', form=form)


Visibility
~~~~~~~~~~

Each page can be visible in function rules. If the
condition of the visibility is not validate the a redirect 
to another page is done.

Some rules already exists:

* :class:`feretui.helper.page_for_authenticated_user_or_goto`
* :class:`feretui.helper.page_for_unauthenticated_user_or_goto`

By default they are no rule on the page, anybody can see them

::

    from feretui import page_for_authenticated_user_or_goto, page_404

    @myferet.register_page()
    @page_for_authenticated_user_or_goto(page_404)
    def my_page(feretui, session, options):
        return feretui.render_template(session, 'my-page')


All the page can be choosen by the redirection, by default feretui give:

* :func:`feretui.pages.page_404`
* :func:`feretui.pages.page_forbidden`
* :func:`feretui.pages.homepage`
* :func:`feretui.pages.login`
* :func:`feretui.pages.signup`

.. note::

    The template of these pages can be overwritten. You also create and use
    your own page.

To create your own function to redirect::

    def page_for_ ... _or_goto(
        fallback_page: str | Callable,
    ) -> Callable:
        def wrap_func(func: Callable) -> Callable:

            @wraps(func)
            def wrap_call(
                feretui: "FeretUI",
                session: Session,
                options: dict,
            ) -> str:
                if some_check_with_sesion(session):
                    return func(feretui, session, options)

                page = fallback_page
                if isinstance(fallback_page, str):
                    page = feretui.get_page(fallback_page)

                return page(feretui, session, options)

            return wrap_call

        return wrap_func


The session can be overloaded and passed during the creation of the 
request. By default only the **user** attribute exist on the session.

Translation
~~~~~~~~~~~

The templates are always translated, No action is needed to translate them
other that the standard translation of the project.

~~~~~~
Action
~~~~~~

An action is function call by the api at the url **/{{ myferet.base_url }}/actions/{{ name of the action }}**

::

    from feretui import Response

    @myferet.register_action
    def my_action(feretui, request):
        return Response(...)


.. warning::

    The action have to return a response instance, need by the web server.


Validate the methods and the response.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default the actions can be called by any http method. To filter and validate the return 
you must used the :func:`feretui.helper.action_validator`.

::

    from feretui import action_validator, Response, RequestMethod

    @myferet.register_action
    @action_validator(methods=[RequestMethod.POST])
    def my_action(feretui, request):
        return Response(...)

Used form with your action
~~~~~~~~~~~~~~~~~~~~~~~~~~

FeretUI implement a base class for `wtforms <https://wtforms.readthedocs.io/en/3.1.x/>`_.

::

    from feretui import FeretUIForm

    class MyForm(FeretUIForm):
        ...


The base class:

* overwrite gettext and ngettext for the translation
* overwrite the render of the field to add bulma class on the input

You use it directly in the page or the action.

::

    from feretui import action_validator, Response, RequestMethod

    @myferet.register_action
    @action_validator(methods=[RequestMethod.POST])
    def my_action(feretui, request):
        form = MyForm(request.form)
        if form.validate():
            ...
            return Response(...)

        return Response(my_page(feretui, request.session, {'form': form}))


Security
~~~~~~~~

To protect the action and indicate if the action is callable you should
use the decorator:

* :class:`feretui.helper.action_for_authenticated_user`
* :class:`feretui.helper.action_for_unauthenticated_user`

By default they are no rule on the action, anybody can call them

::

    from feretui import action_validator, Response, RequestMethod, action_for_authenticated_user

    @myferet.register_action
    @action_validator(methods=[RequestMethod.POST])
    @action_for_authenticated_user
    def my_action(feretui, request):
        return Response(...)


To create your own function to protect you action::

    class MyActionException(ActionError):
        pass


    def action_for_...(func: Callable) -> Callable:
        @wraps(func)
        def wrapper_call(
            feret: "FeretUI",
            request: Response,
        ) -> Response:
            if something_with_session(request.session):
                raise MyActionException(...)

            return func(feret, request)

        return wrapper_call
