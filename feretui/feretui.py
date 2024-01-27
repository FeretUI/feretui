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

The static files can be added:

* directly in the client with :meth:`.FeretUI.register_js_static`,
  :meth:`.FeretUI.register_css_static` and
  :meth:`.FeretUI.register_image_static`
* with the entry point.

  The declaration of the entryt point is done in the *pyproject.toml*
  of your project

  ::

      [project.entry-points."feretui.static"]
      feretui = "feretui.feretui:import_feretui_statics"

  the method call is :func:`.import_feretui_statics`.
"""
from logging import getLogger
from os.path import dirname, join

from jinja2 import Environment, PackageLoader, select_autoescape
from pkg_resources import iter_entry_points

from feretui.request import Request
from feretui.response import Response
from feretui.session import Session
from feretui.template import Template
from feretui.translation import (
    TranslatedTemplate,
    Translation,
)

logger = getLogger(__name__)


def import_feretui_statics(feretui: "FeretUI") -> None:
    """Import the main static used by FeretUI client.

    * javascript:

        * `htmx <https://htmx.org/>`_
        * `hyperscript <https://hyperscript.org/docs/>`_
        * `json-enc <https://htmx.org/extensions/json-enc/>`_

    * css:

        * `bulma <https://bulma.io/>`_

    * image:

        * FeretUI logo.


    :param feretui: Instance of the client.
    :type fereui: :class:`.FeretUI`
    """
    feretui_path = dirname(__file__)
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
    feretui.register_css_static(
        'bulma.css',
        join(feretui_path, 'static', 'bulma.0.9.4.css')
    )
    feretui.register_image_static(
        'logo.png',
        join(feretui_path, 'static', 'logo.png')
    )


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

        * :meth:`.FeretUI.import_templates_file`
        * :meth:`.FeretUI.render_template`

    * static files : Declare static file to import in the client.

        * :meth:`.FeretUI.register_js_static`
        * :meth:`.FeretUI.register_css_static`
        * :meth:`.FeretUI.register_image_static`

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

        self.jinja_env = Environment(
            loader=PackageLoader("feretui"),
            autoescape=select_autoescape()
        )

        # List the template to use to generate the UI
        feretui_path = dirname(__file__)
        self.template = Template()

        self.import_templates_file(
            join(feretui_path, 'templates', 'feretui.tmpl')
        )

        # Static behaviours
        self.statics: dict[str, str] = {}
        self.css_import: list[str] = []
        self.js_import: list[str] = []
        self.images: dict[str, str] = {}
        self.statics_from_entrypoint()

    def render(self, request: Request) -> Response:
        """Return the render of the main page.

        :param request: The feretui request
        :type request: :class: `feretui.request.Request`
        :return: Return the html page athrough a feretui Response
        :rtype: :class: `feretui.response.Response`
        """
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
    def statics_from_entrypoint(self) -> None:
        """Get the static from the entrypoints.

        The declaration of the entryt point is done in the *pyproject.toml*
        of your project

        ::

            [project.entry-points."feretui.static"]
            feretui = "feretui.feretui:import_feretui_statics"

        Here the method call is :func:`.import_feretui_statics`.
        """
        for i in iter_entry_points('feretui.static'):
            logger.debug("Load the static from entrypoint: %s", i.name)
            i.load()(self)

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
    def import_templates_file(
        self,
        template_path: str,
        addons: str = 'feretui'
    ) -> None:
        """Import a template file in FeretUI.

        The template file is imported in :class:`feretui.template.Template`,
        and it is declared in the :class:`feretui.translation.Translation`.

        It is possible to load more than one template file.

        ::

            myferet.import_templates_file('path/of/template.tmpl')

        :param template_path: The template file path to import the instance
                              of FeretUI
        :type template_path: str
        :param addons: The addons where the message come from
        :type addons: str
        """
        tt = TranslatedTemplate(template_path, addons=addons)
        Translation.add_translated_template(tt)
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
    @classmethod
    def export_catalog(
        cls,
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
        Translation.export_catalog(output_path, version, addons=addons)

    @classmethod
    def load_catalog(cls, catalog_path: str, lang: str) -> None:
        """Load a specific catalog for a language.

        ::
            FeretUI.load_catalog('feretui/locale/fr.po', 'fr')

        :param catalog_path: Path of the catalog
        :type catalog_path: str
        :param lang: Language code
        :type lang: str
        """
        Translation.load_catalog(catalog_path, lang)
