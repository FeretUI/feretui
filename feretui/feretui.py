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

"""
from os.path import dirname, join

from jinja2 import Environment, PackageLoader, select_autoescape

from feretui.request import Request
from feretui.response import Response
from feretui.session import Session
from feretui.template import Template
from feretui.translation import (
    TranslatedTemplate,
    Translation,
)


class FeretUI:
    """Feretui class.

    Attributes
    ----------
    * jinja_env[Environment] : The environnement of jinja
    * template[:class: `feretui.template.Template`]: Templates load

    The instance provide methodes to use

    * Templating : Import and get the template, need for display the client.

        * :meth:`.Feretui.import_templates_file`
        * :meth:`.Feretui.render_template`

    * Translations : Import and export the catalog

        * :meth:`.Feretui.export_catalog`
        * :meth:`.Feretui.load_catalog`

    """

    def __init__(self):
        """FeretUI class."""
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
        return template.render(feret=self, session=session, **kwargs)

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
