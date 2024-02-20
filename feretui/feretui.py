# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Module feretui.feretui.

A FeretUI instance represent one client. Each instance is a specific clent.
Each client are isolated.

::

    from feretui import FeretUI, Session, Request

    myferet = FeretUI()
    session = Session()
    request = Request(session=session)

    response = myferet.render(request)

The static files, themes and templates can be added:

* directly in the client with :meth:`.FeretUI.register_js`,
  :meth:`.FeretUI.register_css`,
  :meth:`.FeretUI.register_font`,
  :meth:`.FeretUI.register_image`,
  :meth:`.FeretUI.register_theme` and
  :meth:`.FeretUI.register_template_file`
* with the entry point.

  The declaration of the entryt point is done in the *pyproject.toml*
  of your project

  ::

      [project.entry-points."feretui.addons"]
      feretui = "feretui.feretui:import_feretui_addons"

  the method call is :func:`.import_feretui_addons`.
"""
from collections.abc import Callable
from importlib.metadata import entry_points
from logging import getLogger
from os.path import dirname, join

from jinja2 import Environment, PackageLoader, select_autoescape

from feretui.actions import goto, render
from feretui.exceptions import UnexistingAction
from feretui.pages import homepage, page_404, page_forbidden
from feretui.request import Request
from feretui.response import Response
from feretui.session import Session
from feretui.template import Template
from feretui.thread import local
from feretui.translation import (
    TranslatedFileTemplate,
    TranslatedPageTemplate,
    Translation,
)

logger = getLogger(__name__)


def import_feretui_addons(feretui: "FeretUI") -> None:
    """Import the main static used by FeretUI client.

    * templates:
        * feretui.tmpl

    * javascript:
        * `htmx <https://htmx.org/>`_
        * `hyperscript <https://hyperscript.org/docs/>`_
        * `json-enc <https://htmx.org/extensions/json-enc/>`_

    * css:
        * `bulma <https://bulma.io/>`_

    * font
        * `Fontawesome <https://fontawesome.com/>`_

    * image:
        * FeretUI logo.

    * `themes <https://jenil.github.io/bulmaswatch/>`_

    :param feretui: Instance of the client.
    :type feretui: :class:`.FeretUI`
    """
    feretui_path = dirname(__file__)

    # ---- JS ----
    feretui.register_js(
        'htmx.js',
        join(feretui_path, 'static', 'htmx.1.9.10.js'),
    )
    feretui.register_js(
        'hyperscript.js',
        join(feretui_path, 'static', 'hyperscript.0.9.12.js'),
    )
    feretui.register_js(
        'json-enc.js',
        join(feretui_path, 'static', 'json-enc.js'),
    )

    # ---- CSS ----
    feretui.register_css(
        'bulma.css',
        join(feretui_path, 'static', 'bulma.0.9.4.css'),
    )
    feretui.register_css(
        'fontawesome/css/all.css',
        join(
            feretui_path,
            'static',
            'fontawesome-free-6.5.1-web',
            'css',
            'all.min.css',
        ),
    )

    # ---- Font ----
    for font in (
        'fa-brands-400.ttf', 'fa-brands-400.woff2', 'fa-regular-400.ttf',
        'fa-regular-400.woff2', 'fa-solid-900.ttf', 'fa-solid-900.woff2',
        'fa-v4compatibility.ttf', 'fa-v4compatibility.woff2',
    ):
        feretui.register_font(
            f'fontawesome/webfonts/{font}',
            join(
                feretui_path,
                'static',
                'fontawesome-free-6.5.1-web',
                'webfonts',
                font,
            ),
        )

    # ---- Images ----
    feretui.register_image(
        'logo.png',
        join(feretui_path, 'static', 'logo.png'),
    )

    # ---- Themes ----
    for theme in (
        'cerulean', 'cyborg', 'default', 'journal', 'lumen', 'materia',
        'nuclear', 'sandstone', 'slate', 'spacelab', 'united', 'cosmo',
        'darkly', 'flatly', 'litera', 'lux', 'minty', 'pulse',
        'simplex', 'solar', 'superhero', 'yeti',
    ):
        feretui.register_theme(
            theme,
            join(
                feretui_path, 'static', 'themes', f'{theme}.min.css',
            ),
        )


class FeretUI:
    """Feretui class.

    Attributes
    ----------
    * base_url[str] : The url for this client
    * title[str] : The title of the html head
    * jinja_env[Environment] : The environnement of jinja
    * template[:class: `feretui.template.Template`]: Templates load
    * statics[dict[str, str]]: The static filepath on server stored by name
    * css_import[list[str]] : List of the urls of the css to load
    * js_import[list[str]] : List of the urls of the script javascript to load
    * images[dict[str, str]] : List of the image and their url
    * themes[dict[str, str]] : List of the theme and their url
    * fonts[dict[str, str]] : List of the font and their url
    * actions[dict[str, Callable]] : List of the action callables

    The instance provide methodes to use

    * Templating : Import and get the template, need for display the client.
        * :meth:`.FeretUI.register_template_file`
        * :meth:`.FeretUI.render_template`

    * Static files : Declare static file to import in the client.
        * :meth:`.FeretUI.register_js`
        * :meth:`.FeretUI.register_css`
        * :meth:`.FeretUI.register_font`
        * :meth:`.FeretUI.register_image`
        * :meth:`.FeretUI.register_theme`

    * Action : Declare action called by the web server api.
        * :meth:`.FeretUI.register_action`
        * :meth:`.FeretUI.execute_action`

    * Translations : Import and export the catalog
        * :meth:`.FeretUI.export_catalog`
        * :meth:`.FeretUI.load_catalog`

    """

    CSS_IMPORT: dict[str, str] = {}
    JS_IMPORT: dict[str, str] = {}
    IMAGES: dict[str, str] = {}

    def __init__(self, base_url: str = "/feretui", title: str = "FeretUI"):
        """FeretUI class.

        :param base_url: The prefix of the url for all internal api
        :type base_url: str
        :param title: [FeretUI] The title in the html head
        :type base_url: str
        """
        self.base_url: str = base_url
        self.title: str = title

        # Translation for this instance
        self.translation = Translation()

        self.jinja_env = Environment(
            loader=PackageLoader("feretui"),
            autoescape=select_autoescape(),
        )

        # List the template to use to generate the UI
        feretui_path = dirname(__file__)
        self.template = Template(self.translation)
        self.register_template_file(
            join(feretui_path, 'templates', 'feretui.tmpl'),
        )
        self.register_template_file(
            join(feretui_path, 'templates', 'pages.tmpl'),
        )

        # Static behaviours
        self.statics: dict[str, str] = {}
        self.css_import: list[str] = []
        self.js_import: list[str] = []
        self.images: dict[str, str] = {}
        self.themes: dict[str, str] = {}
        self.fonts: dict[str, str] = {}

        # Actions
        self.actions: dict[str, Callable[["FeretUI", Request], Response]] = {}
        self.register_action(render)
        self.register_action(goto)

        # Pages
        self.pages: dict[str, Callable[
            ["FeretUI", Session, dict], Response],
        ] = {
            '404': page_404,  # because a function can not be called 404
        }
        self.register_page()(page_forbidden)
        self.register_page()(homepage)

        self.register_addons_from_entrypoint()

    def register_addons_from_entrypoint(self) -> None:
        """Get the static from the entrypoints.

        The declaration of the entryt point is done in the *pyproject.toml*
        of your project

        ::

            [project.entry-points."feretui.addons"]
            feretui = "feretui.feretui:import_feretui_addons"

        Here the method call is :func:`.import_feretui_addons`.
        """
        for i in entry_points(group='feretui.addons'):
            logger.debug("Load the static from entrypoint: %s", i.name)
            i.load()(self)

    def render(self, request: Request) -> Response:
        """Return the render of the main page.

        :param request: The feretui request
        :type request: :class: `feretui.request.Request`
        :return: Return the html page athrough a feretui Response
        :rtype: :class: `feretui.response.Response`
        """
        # First put the instance of feretui and the request in
        # the local thread to keep the information
        local.feretui = self
        local.request = request

        template = self.render_template(
            request.session,
            'feretui-client',
            querystring=request.raw_querystring,
        )
        # lxml remove the tags html, head and body. So in template
        # they are named feretui-html, feretui-head, feretui-body
        template = template.replace('feretui-html', 'html')
        template = template.replace('feretui-head', 'head')
        template = template.replace('feretui-body', 'body')
        return Response(f'<!DOCTYPE html5>\n{template}')

    # ---------- statics  ----------
    def register_js(self, name: str, filepath: str) -> None:
        """Register a javascript file to import in the client.

        :param name: name of the file see in the html url
        :type name: str
        :param filepath: Path in server file system
        :type filepath: str
        """
        if name in self.statics:
            logger.warning('The js script %s is overwriting', name)
        else:
            url = f"{self.base_url}/static/{name}"
            logger.debug('Add the js script %s', url)
            self.js_import.append(url)

        self.statics[name] = filepath

    def register_css(self, name: str, filepath: str) -> None:
        """Register a stylesheet file to import in the client.

        :param name: name of the file see in the html url
        :type name: str
        :param filepath: Path in server file system
        :type filepath: str
        """
        if name in self.statics:
            logger.warning('The stylesheet %s is overwriting', name)
        else:
            url = f"{self.base_url}/static/{name}"
            logger.debug('Add the stylesheet %s', url)
            self.css_import.append(url)

        self.statics[name] = filepath

    def register_image(self, name: str, filepath: str) -> None:
        """Register an image file to use it in the client.

        :param name: name of the image see in the html url
        :type name: str
        :param filepath: Path in server file system
        :type filepath: str
        """
        if name in self.statics:
            logger.warning('The image %s is overwriting', name)
        else:
            url = f"{self.base_url}/static/{name}"
            logger.debug('Add the image %s', url)
            self.images[name] = url

        self.statics[name] = filepath

    def register_theme(self, name: str, filepath: str) -> None:
        """Register a theme file to use it in the client.

        :param name: name of the theme see in the html url
        :type name: str
        :param filepath: Path in server file system
        :type filepath: str
        """
        if name in self.statics:
            logger.warning('The theme %s is overwriting', name)
        else:
            url = f"{self.base_url}/static/{name}"
            logger.debug('Add the available theme %s', url)
            self.themes[name] = url

        self.statics[name] = filepath

    def register_font(self, name: str, filepath: str) -> None:
        """Register a theme file to use it in the client.

        :param name: name of the font see in the html url
        :type name: str
        :param filepath: Path in server file system
        :type filepath: str
        """
        if name in self.statics:
            logger.warning('The font %s is overwriting', name)
        else:
            url = f"{self.base_url}/static/{name}"
            logger.debug('Add the available font %s', url)
            self.fonts[name] = url

        self.statics[name] = filepath

    def get_theme_url(self, session: Session) -> str:
        """Return the theme url in function of the session.

        :param feretui: The instance of the client
        :type feretui: :class:`.FeretUI`
        :param session: The session of the user.
        :type session: :class:`feretui.session.Session`
        :return: the url to import stylesheep
        :rtype: str
        """
        return self.themes.get(session.theme, self.themes['default'])

    def get_image_url(self, name: str) -> str:
        """Get the url for a picture.

        :param name: The name of the picture
        :type name: str
        :return: The url to get it
        :rtype: str
        """
        return self.images[name]

    def get_static_file_path(self, filename: str) -> str:
        """Get the path in the filesystem for static file name.

        :param name: The name of the static
        :type name: str
        :return: The filesystem path
        :rtype: str
        """
        return self.statics.get(filename)

    # ---------- Templating  ----------
    def register_template_file(
        self,
        template_path: str,
        addons: str = 'feretui',
    ) -> None:
        """Import a template file in FeretUI.

        The template file is imported in :class:`feretui.template.Template`,
        and it is declared in the :class:`feretui.translation.Translation`.

        It is possible to load more than one template file.

        ::

            myferet.register_template_file('path/of/template.tmpl')

        :param template_path: The template file path to import the instance
                              of FeretUI
        :type template_path: str
        :param addons: The addons where the message come from
        :type addons: str
        """
        tt = TranslatedFileTemplate(template_path, addons=addons)
        self.translation.add_translated_template(tt)
        with open(template_path) as fp:
            self.template.load_file(fp)

    def render_template(
        self,
        session: Session,
        template_id: str,
        **kwargs,
    ) -> str:
        """Get a compiled template.

        The compiled template from :class:`feretui.template.Template`,
        This template is translated in function of the lang attribute
        of the session. All the named arguments is used by jinja librairy
        to improve the render.

        ::

            myferet.render_template(session, 'my-template')

        The jinja render is done after the compilation of the template.
        Because the template is stored in function of the declared templates
        and the language. The jinja depend of the execution in function
        of the parameter and can be saved but recomputed at each call.

        :param session: The user feretui's session
        :type session: :class:`feretui.session.Session`
        :param template_id: The identify of the template
        :type template_id: str
        :return: The compiled templated through
                 :class:`feretui.template.Template` and jinja
        :rtype: str
        """
        template = self.jinja_env.from_string(
            self.template.get_template(
                template_id,
                lang=session.lang,
            ),
        )
        return template.render(feretui=self, session=session, **kwargs)

    # ---------- Action  ----------
    def register_action(
        self,
        function: Callable[["FeretUI", Request], Response],
    ) -> Callable[["FeretUI", Request], Response]:
        """Register an action.

        It is a Decorator to register an action need by the
        client or the final project.

        The action is a callable with two params:

        * feretui [:class:`.FeretUI`] : The client instance.
        * request [:class:`feretui.request.Request`] : The request

        ::

            @myferet.register_action
            def my_action(feretui, request):
                return Response(...)

        :param function: The action callable to store
        :type function: Callable[[:class:`.FeretUI`,
                        :class:`feretui.request.Request`],
                        :class:`feretui.response.Response`]
        :return: The stored action callable
        :rtype: Callable[[:class:`.FeretUI`,
                :class:`feretui.request.Request`],
                :class:`feretui.response.Response`]
        """
        if function.__name__ in self.actions:
            logger.info(f'Overload action {function.__name__}')

        self.actions[function.__name__] = function
        return function

    def execute_action(
        self,
        request: Request,
        action_name: str,
    ) -> Response:
        """Execute a stored action.

        Get and execute the action stored in the client. The
        parameters need for the good working of the action
        must be passed by the body or the querystring from the
        request.

        ::

            request = Request(...)
            myferet.execute_action(request, 'my_action')

        :param request: The feretui request from api.
        :type request: :class:`feretui.request.Request`
        :param action_name: The name of the action
        :type action_name: str
        :return: The result of the action
        :rtype: :class:`feretui.response.Response`
        """
        if action_name not in self.actions:
            raise UnexistingAction(action_name)

        # First put the instance of feretui, the request and
        # the lang in the local thread to keep the information
        local.feretui = self
        local.request = request
        local.lang = request.session.lang

        function = self.actions[action_name]
        return function(self, request)

    # ---------- Page  ----------
    def register_page(self, name=None, template=None, addons='feretui'):
        if template:
            tt = TranslatedPageTemplate(template, addons=addons)
            self.translation.add_translated_template(tt)
            self.template.load_template_from_str(template)

        default_name = name

        def register_page_callback(
            func: Callable[["FeretUI", Session, dict], str],
        ) -> Callable[["FeretUI", Session, dict], str]:
            name = default_name if default_name else func.__name__

            if name in self.pages:
                logger.info(f'Overload page {func.name}')

            self.pages[name] = func
            return func

        return register_page_callback

    def get_page(self, pagename: str) -> Callable[..., ...]:
        if pagename not in self.pages:
            return self.get_page('404')

        return self.pages[pagename]

    # ---------- Translation ----------
    def export_catalog(
        self,
        output_path: str,
        version: str,
        addons: str = None,
    ) -> None:
        """Export the catalog at the POT format.

        ::

            FeretUI.export_catalog(
                'feretui/locale/feretui.pot', addons='feretui')

        :param output_path: The path where write the catalog
        :type output_path: str
        :param version: The version of the catalog
        :type version: str
        :param addons: The addons where the message come from
        :type addons: str
        """
        self.translation.export_catalog(output_path, version, addons=addons)

    def load_catalog(self, catalog_path: str, lang: str) -> None:
        """Load a specific catalog for a language.

        ::
            FeretUI.load_catalog('feretui/locale/fr.po', 'fr')

        :param catalog_path: Path of the catalog
        :type catalog_path: str
        :param lang: Language code
        :type lang: str
        """
        self.translation.load_catalog(catalog_path, lang)
