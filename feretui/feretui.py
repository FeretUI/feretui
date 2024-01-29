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

* directly in the client with :meth:`.FeretUI.register_js_static`,
  :meth:`.FeretUI.register_css_static`,
  :meth:`.FeretUI.register_image_static`,
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
from importlib.metadata import entry_points
from logging import getLogger
from os.path import dirname, join

from jinja2 import Environment, PackageLoader, select_autoescape

from feretui.request import Request
from feretui.response import Response
from feretui.session import Session
from feretui.template import Template
from feretui.thread import local
from feretui.translation import (
    TranslatedTemplate,
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

    * image:
        * FeretUI logo.

    * `themes <https://jenil.github.io/bulmaswatch/>`_

    :param feretui: Instance of the client.
    :type feretui: :class:`.FeretUI`
    """
    feretui_path = dirname(__file__)

    # ---- Templates ----
    feretui.register_template_file(
        join(feretui_path, 'templates', 'feretui.tmpl')
    )

    # ---- JS ----
    feretui.register_js_static(
        'htmx.js',
        join(feretui_path, 'static', 'htmx.1.9.10.js')
    )
    feretui.register_js_static(
        'hyperscript.js',
        join(feretui_path, 'static', 'hyperscript.0.9.12.js')
    )
    feretui.register_js_static(
        'json-enc.js',
        join(feretui_path, 'static', 'json-enc.js')
    )

    # ---- CSS ----
    feretui.register_css_static(
        'bulma.css',
        join(feretui_path, 'static', 'bulma.0.9.4.css')
    )

    # ---- Images ----
    feretui.register_image_static(
        'logo.png',
        join(feretui_path, 'static', 'logo.png')
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
                feretui_path, 'static', 'themes', f'{theme}.min.css'
            ),
        )


def callback_get_theme_url(feretui: "FeretUI", session: Session) -> str:
    """Return the theme url in function of the session.

    :param feretui: The instance of the client
    :type feretui: :class:`.FeretUI`
    :param session: The session of the user.
    :type session: :class:`feretui.session.Session`
    :return: the url to import stylesheep
    :rtype: str
    """
    return feretui.themes.get(session.theme, feretui.themes['default'])


class FeretUI:
    """Feretui class.

    Attributes
    ----------
    * base_url[str] : The url for this client
    * jinja_env[Environment] : The environnement of jinja
    * template[:class: `feretui.template.Template`]: Templates load
    * statics[dict[str, str]]: The static filepath on server stored by name
    * css_import[list[str]] : List of the urls of the css to load
    * js_import[list[str]] : List of the urls of the script javascript to load
    * images[dict[str, str]] : List of the image and their url

    The instance provide methodes to use

    * Templating : Import and get the template, need for display the client.

        * :meth:`.FeretUI.register_template_file`
        * :meth:`.FeretUI.render_template`

    * static files : Declare static file to import in the client.

        * :meth:`.FeretUI.register_js_static`
        * :meth:`.FeretUI.register_css_static`
        * :meth:`.FeretUI.register_image_static`
        * :meth:`.FeretUI.register_theme`

    * Translations : Import and export the catalog

        * :meth:`.FeretUI.export_catalog`
        * :meth:`.FeretUI.load_catalog`

    """

    CSS_IMPORT: dict[str, str] = {}
    JS_IMPORT: dict[str, str] = {}
    IMAGES: dict[str, str] = {}

    def __init__(self, base_url: str = "/feretui"):
        """FeretUI class.

        :param base_url: The prefix of the url for all internal api
        :type base_url: str
        """
        self.base_url: str = base_url

        # Translation for this instance
        self.translation = Translation()

        self.jinja_env = Environment(
            loader=PackageLoader("feretui"),
            autoescape=select_autoescape()
        )

        # List the template to use to generate the UI
        self.template = Template(self.translation)

        # Static behaviours
        self.statics: dict[str, str] = {}
        self.css_import: list[str] = []
        self.js_import: list[str] = []
        self.images: dict[str, str] = {}
        self.themes: dict[str, str] = {}

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
        return Response(template)

    # ---------- statics  ----------
    def register_js_static(self, name: str, filepath: str) -> None:
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

    def register_css_static(self, name: str, filepath: str) -> None:
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

    def register_image_static(self, name: str, filepath: str) -> None:
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

    def get_theme_url(self, session: Session) -> str:
        """Return the theme url in function of the session.

        :param feretui: The instance of the client
        :type feretui: :class:`.FeretUI`
        :param session: The session of the user.
        :type session: :class:`feretui.session.Session`
        :return: the url to import stylesheep
        :rtype: str
        """
        return callback_get_theme_url(self, session)

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
        addons: str = 'feretui'
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
        tt = TranslatedTemplate(template_path, addons=addons)
        self.translation.add_translated_template(tt)
        with open(template_path) as fp:
            self.template.load_file(fp)

    def render_template(
        self,
        session: Session,
        template_id: str,
        **kwargs
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
            )
        )
        return template.render(feretui=self, session=session, **kwargs)

    # ---------- Translation ----------
    def export_catalog(
        self,
        output_path: str,
        version: str,
        addons: str = None
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
