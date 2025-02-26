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

from collections.abc import Callable, Iterable
from importlib.metadata import entry_points
from logging import getLogger
from pathlib import Path

from jac import CompressorExtension
from jinja2 import Environment, PackageLoader, select_autoescape
from markupsafe import Markup

from feretui.actions import goto, login_password, login_signup, logout, resource
from feretui.context import set_context
from feretui.exceptions import (
    MenuError,
    UnexistingActionError,
    UnexistingResourceError,
)
from feretui.form import FeretUIForm
from feretui.helper import menu_for_unauthenticated_user
from feretui.menus import (
    AsideMenu,
    ChildrenMenu,
    SitemapMenu,
    ToolBarButtonMenu,
    ToolBarButtonsMenu,
    ToolBarDividerMenu,
    ToolBarMenu,
)
from feretui.pages import (
    aside_menu,
    homepage,
    login,
    page_404,
    page_forbidden,
    resource_page,
    signup,
    sitemap,
    static_page,
)
from feretui.request import Request
from feretui.resources.resource import Resource
from feretui.response import Response
from feretui.session import Session
from feretui.template import Template
from feretui.translation import (
    TranslatedFileTemplate,
    TranslatedForm,
    TranslatedMenu,
    TranslatedResource,
    TranslatedStringTemplate,
    Translation,
)

logger = getLogger(__name__)


def import_feretui_addons(feretui: "FeretUI") -> None:
    """Import the main static used by FeretUI client.

    * javascript:
        * Htmx_
        * `hyperscript <https://hyperscript.org/docs/>`_

    * css:
        * `bulma <https://bulma.io/>`_
        * `bulma-tooltip <https://bulma-tooltip.netlify.app/get-started/>`_
        * `bulma-print <ihttps://github.com/suterma/bulma-print>`_

    * font
        * `Fontawesome <https://fontawesome.com/>`_

    * image:
        * FeretUI logo.

    * `themes <https://jenil.github.io/bulmaswatch/>`_

    :param feretui: Instance of the client.
    :type feretui: :class:`.FeretUI`
    """
    feretui_path = Path(__file__).parent

    # ---- JS ----
    feretui.register_js(
        "htmx.js",
        Path(feretui_path, "static", "htmx.1.9.10.js"),
    )
    feretui.register_js(
        "hyperscript.js",
        Path(feretui_path, "static", "hyperscript.0.9.12.js"),
    )

    # ---- CSS ----
    feretui.register_css(
        "bulma.css",
        Path(feretui_path, "static", "bulma.0.9.4.css"),
    )
    feretui.register_css(
        "bulma-tooltip.css",
        Path(feretui_path, "static", "bulma-tooltip.1.2.0.min.css"),
    )
    feretui.register_css(
        "fontawesome/css/all.css",
        Path(
            feretui_path,
            "static",
            "fontawesome-free-6.5.1-web",
            "css",
            "all.min.css",
        ),
        compress=False,
    )
    feretui.register_css(
        "bulma-print.css",
        Path(feretui_path, "static", "bulma-print.1.0.1.css"),
    )

    # ---- Font ----
    for font in (
        "fa-brands-400.ttf",
        "fa-brands-400.woff2",
        "fa-regular-400.ttf",
        "fa-regular-400.woff2",
        "fa-solid-900.ttf",
        "fa-solid-900.woff2",
        "fa-v4compatibility.ttf",
        "fa-v4compatibility.woff2",
    ):
        feretui.register_font(
            f"fontawesome/webfonts/{font}",
            Path(
                feretui_path,
                "static",
                "fontawesome-free-6.5.1-web",
                "webfonts",
                font,
            ),
        )

    # ---- Images ----
    feretui.register_image(
        "logo.png",
        Path(feretui_path, "static", "logo.png"),
    )

    # ---- Themes ----
    for theme in (
        "cerulean",
        "cyborg",
        "default",
        "journal",
        "lumen",
        "materia",
        "nuclear",
        "sandstone",
        "slate",
        "spacelab",
        "united",
        "cosmo",
        "darkly",
        "flatly",
        "litera",
        "lux",
        "minty",
        "pulse",
        "simplex",
        "solar",
        "superhero",
        "yeti",
    ):
        feretui.register_theme(
            theme,
            Path(
                feretui_path,
                "static",
                "themes",
                f"{theme}.min.css",
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
    * pages[dict[str, Callable]] : List of the pages
    * menus[dict[str, :class:`feretui.menus.ToolBarMenu`]] : the key are left
      or right the value are instances of the menu.
    * asides[dict[str, :class:`feretui.menus.AsideMenu`]] : The key is the
      code for the aside-menu page, the values are the instance of the menu.
    * resources[dict[str, :class:`feretui.resource.Resource]] : The key
      is the code of the resource and value the class.

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

    * Page : Declare page called to render inside html body main
        * :meth:`.FeretUI.register_page`
        * :meth:`.FeretUI.register_static_page`
        * :meth:`.FeretUI.get_page`

    * Menu : Declare the menus registered in the feretui instance
        * :meth:`.FeretUI.register_toolbar_left_menus`
        * :meth:`.FeretUI.register_toolbar_right_menus`
        * :meth:`.FeretUI.register_aside_menus`
        * :meth:`.FeretUI.register_user_menus`
        * :meth:`.FeretUI.register_auth_menus`

    * Form : Declare the WTForm class in the feretui instance, need for the
      translation
        * :meth:`.FeretUI.register_form`

    * Resource: Declare the resource to CRUD
        * :meth:`.FeretUI.register_resource`
        * :meth:`.FeretUI.get_resource`


    * Translations : Import and export the catalog
        * :meth:`.FeretUI.export_catalog`
        * :meth:`.FeretUI.load_catalog`

    """

    CSS_IMPORT: dict[str, str] = {}
    JS_IMPORT: dict[str, str] = {}
    IMAGES: dict[str, str] = {}

    def __init__(
        self: "FeretUI",
        base_url: str = "/feretui",
        title: str = "FeretUI",
    ) -> "FeretUI":
        """FeretUI class.

        :param base_url: The prefix of the url for all internal api
        :type base_url: str
        :param title: [FeretUI] The title in the html head
        :type base_url: str
        """
        self.base_url: str = base_url
        self.title: str = title

        # Translation for this instance
        self.translation = Translation(self)

        self.jinja_env = Environment(
            loader=PackageLoader("feretui"),
            autoescape=select_autoescape(),
            extensions=[CompressorExtension],
        )

        def compressor_source_dirs(path: str) -> str:
            """Return the filepath."""
            return self.statics.get(path, path)

        self.jinja_env.compressor_source_dirs = compressor_source_dirs
        self.jinja_env.compressor_output_dir = f"static/dist/{ base_url }"
        self.jinja_env.compressor_static_prefix = f"{ base_url }/static"

        # List the template to use to generate the UI
        feretui_path = Path(__file__).parent
        self.template = Template(self.translation)
        self.register_template_file(
            Path(feretui_path, "templates", "feretui.tmpl"),
            addons="feretui",
        )
        self.register_template_file(
            Path(feretui_path, "templates", "pages.tmpl"),
            addons="feretui",
        )
        self.register_template_file(
            Path(feretui_path, "templates", "menus.tmpl"),
            addons="feretui",
        )
        self.register_template_file(
            Path(feretui_path, "templates", "form.tmpl"),
            addons="feretui",
        )
        self.register_template_file(
            Path(feretui_path, "resources", "templates", "resource.tmpl"),
            addons="feretui",
        )
        self.register_template_file(
            Path(feretui_path, "resources", "templates", "action.tmpl"),
            addons="feretui",
        )
        self.register_template_file(
            Path(feretui_path, "resources", "templates", "common.tmpl"),
            addons="feretui",
        )

        # Static behaviours
        self.statics: dict[str, str] = {}
        self.css_import: list[str] = []
        self.js_import: list[str] = []
        self.images: dict[str, str] = {}
        self.themes: dict[str, str] = {}
        self.fonts: dict[str, str] = {}

        # Menus
        self.menus: dict[str, list[ToolBarMenu]] = {
            "left": [],
            "right": [],
            "user": [],
        }
        self.asides: dict[str, list[AsideMenu]] = {}
        self.auth: dict = {
            "menus": None,
            "addons": None,
        }
        self.register_auth_menus(
            [
                ToolBarButtonMenu(
                    "Log In",
                    page="login",
                    visible_callback=menu_for_unauthenticated_user,
                ),
            ],
        )

        # Actions
        self.actions: dict[str, Callable[[FeretUI, Request], Response]] = {}
        self.register_action(goto)
        self.register_action(login_password)
        self.register_action(login_signup)
        self.register_action(logout)
        self.register_action(resource)

        # Pages
        self.pages: dict[
            str,
            Callable[[FeretUI, Session, dict], Response],
        ] = {}
        self.register_page(name="404")(page_404)
        self.register_page(name="forbidden")(page_forbidden)
        self.register_page()(homepage)
        self.register_page()(sitemap)
        self.register_page("aside-menu")(aside_menu)
        self.register_page()(login)
        self.register_page()(signup)
        self.register_page(name="resource")(resource_page)

        self.register_addons_from_entrypoint()

        # Resources
        self.resources: dict[str, Resource] = {}

    def register_addons_from_entrypoint(self: "FeretUI") -> None:
        """Get the static from the entrypoints.

        The declaration of the entryt point is done in the *pyproject.toml*
        of your project

        ::

            [project.entry-points."feretui.addons"]
            feretui = "feretui.feretui:import_feretui_addons"

        Here the method call is :func:`.import_feretui_addons`.
        """
        for i in entry_points(group="feretui.addons"):
            logger.debug("Load the static from entrypoint: %s", i.name)
            i.load()(self)

    def render(self: "FeretUI", request: Request) -> Response:
        """Return the render of the main page.

        :param request: The feretui request
        :type request: :class: `feretui.request.Request`
        :return: Return the html page athrough a feretui Response
        :rtype: :class: `feretui.response.Response`
        """
        # First put the instance of feretui and the request in
        # the local thread to keep the information
        with set_context(self, request):
            page = request.query.get("page", ["homepage"])[0]
            template = self.render_template(
                request.session,
                "feretui-client",
                page=Markup(
                    self.get_page(page)(
                        self,
                        request.session,
                        request.query,
                    ),
                ),
            )
            # lxml remove the tags html, head and body. So in template
            # they are named feretui-html, feretui-head, feretui-body
            template = template.replace("feretui-html", "html")
            template = template.replace("feretui-head", "head")
            template = template.replace("feretui-body", "body")
            return Response(f"<!DOCTYPE html5>\n{template}")

    # ---------- statics  ----------
    def register_js(self: "FeretUI", name: str, filepath: str) -> None:
        """Register a javascript file to import in the client.

        :param name: name of the file see in the html url
        :type name: str
        :param filepath: Path in server file system
        :type filepath: str
        """
        if name in self.statics:
            logger.warning("The js script %s is overwriting", name)
        else:
            logger.debug("Add the js script %s", name)
            self.js_import.append(name)

        self.statics[name] = filepath

    def register_css(
        self: "FeretUI",
        name: str,
        filepath: str,
        compress: bool = True,
    ) -> None:
        """Register a stylesheet file to import in the client.

        :param name: name of the file see in the html url
        :type name: str
        :param filepath: Path in server file system
        :type filepath: str
        :param compress: if True compress the csv
        :type compress: bool
        """
        if name in self.statics:
            logger.warning("The stylesheet %s is overwriting", name)
        else:
            url = f"{self.base_url}/static/{name}"
            logger.debug("Add the stylesheet %s", url)
            if compress:
                self.css_import.append((compress, name))
            else:
                self.css_import.append((compress, url))

        self.statics[name] = filepath

    def register_image(self: "FeretUI", name: str, filepath: str) -> None:
        """Register an image file to use it in the client.

        :param name: name of the image see in the html url
        :type name: str
        :param filepath: Path in server file system
        :type filepath: str
        """
        if name in self.statics:
            logger.warning("The image %s is overwriting", name)
        else:
            url = f"{self.base_url}/static/{name}"
            logger.debug("Add the image %s", url)
            self.images[name] = url

        self.statics[name] = filepath

    def register_theme(self: "FeretUI", name: str, filepath: str) -> None:
        """Register a theme file to use it in the client.

        :param name: name of the theme see in the html url
        :type name: str
        :param filepath: Path in server file system
        :type filepath: str
        """
        if name in self.statics:
            logger.warning("The theme %s is overwriting", name)
        else:
            logger.debug("Add the available theme %s", name)
            self.themes[name] = name

        self.statics[name] = filepath

    def register_font(self: "FeretUI", name: str, filepath: str) -> None:
        """Register a theme file to use it in the client.

        :param name: name of the font see in the html url
        :type name: str
        :param filepath: Path in server file system
        :type filepath: str
        """
        if name in self.statics:
            logger.warning("The font %s is overwriting", name)
        else:
            url = f"{self.base_url}/static/{name}"
            logger.debug("Add the available font %s", url)
            self.fonts[name] = url

        self.statics[name] = filepath

    def get_theme_url(self: "FeretUI", session: Session) -> str:
        """Return the theme url in function of the session.

        :param feretui: The instance of the client
        :type feretui: :class:`.FeretUI`
        :param session: The session of the user.
        :type session: :class:`feretui.session.Session`
        :return: the url to import stylesheep
        :rtype: str
        """
        return self.themes.get(session.theme, self.themes["default"])

    def get_image_url(self: "FeretUI", name: str) -> str:
        """Get the url for a picture.

        :param name: The name of the picture
        :type name: str
        :return: The url to get it
        :rtype: str
        """
        return self.images[name]

    def get_static_file_path(self: "FeretUI", filename: str) -> str:
        """Get the path in the filesystem for static file name.

        :param name: The name of the static
        :type name: str
        :return: The filesystem path
        :rtype: str
        """
        path = Path(f"./static/dist/{self.base_url}/{filename}")
        if path.exists():
            return path  # pragma: no cover

        return self.statics.get(filename)

    # ---------- Templating  ----------
    def register_template_file(
        self: "FeretUI",
        template_path: str,
        addons: str = None,
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
        with Path(template_path).open() as fp:
            self.template.load_file(fp)

    def register_template_from_str(
        self: "FeretUI",
        template: str,
        addons: str = None,
    ) -> None:
        """Import a template string in FeretUI.

        The template string is imported in :class:`feretui.template.Template`,
        and it is declared in the :class:`feretui.translation.Translation`.

        It is possible to load more than one template string.

        ::

            myferet.register_template_from_str('''
                <template id="my-template">
                    ...
                </template>
            ''')

        :param template: The template to import the instance
                         of FeretUI
        :type template: str
        :param addons: The addons where the message come from
        :type addons: str
        """
        tt = TranslatedStringTemplate(template, addons=addons)
        self.translation.add_translated_template(tt)
        self.template.load_template_from_str(template)

    def render_template(
        self: "FeretUI",
        session: Session,
        template_id: str,
        **kwargs,  # noqa: ANN003
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
        self: "FeretUI",
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
            logger.info("Overload action %r", function.__name__)

        self.actions[function.__name__] = function
        return function

    def execute_action(
        self: "FeretUI",
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
            raise UnexistingActionError(action_name)

        # First put the instance of feretui, the request and
        # the lang in the local thread to keep the information
        with set_context(self, request):
            function = self.actions[action_name]
            return function(self, request)

    # ---------- Page  ----------
    def register_page(
        self: "FeretUI",
        name: str = None,
        templates: Iterable[str] = None,
        forms: Iterable[FeretUIForm] = None,
        addons: str = None,
    ) -> Callable:
        """Register a page.

        This is a decorator to register a page.

        A page is a function :

        * Params

          * FeretUI
          * Session
          * dict

        * return the strof the html page

        ::

            @myferet.register_page()
            def my_page(feretui, session, options):
                return ...

        By default the name is the name of the decorated callable.
        but this nae can be overritting

        ::

            @myferet.register_page(name='my_page')
            def _my_page(feretui, session, options):
                return ...

        If need, the templates can be passed in the decorator and
        are added in the templates librairy

        ::

            @myferet.register_page(template=[
                '''
                    <template id="...">
                        ...
                    </template>
                '''
            ])
            def my_page(feretui, session, options):
                return ...

        You can register a WTForm

        ::

            class MyForm(FeretUIForm):
                ...

            @myferet.register_page(forms=[MyForm])
            def my_page(feretui, session, options):
                return ...


        :param name: The name of the pages stored in FeretUI.pages
        :type name: str
        :param templates: The str of the template to load
        :type templates: list[str]
        :param forms: The WTForm to register at the same time
        :type form: list[:class:`feretui.form.FeretUIForm`]
        :param addons: The addons where the message come from
        :type addons: str
        :return: Return a decorator
        :rtype: Callable
        """
        if isinstance(templates, Iterable):
            for template in templates:
                self.register_template_from_str(template, addons=addons)

        if isinstance(forms, Iterable):
            register = self.register_form(addons=addons)
            for form in forms:
                register(form)

        default_name = name

        def register_page_callback(
            func: Callable[["FeretUI", Session, dict], str],
        ) -> Callable[["FeretUI", Session, dict], str]:
            name = default_name if default_name else func.__name__

            if name in self.pages:
                logger.info("Overload page %r", name)

            self.pages[name] = func
            return func

        return register_page_callback

    def register_static_page(
        self: "FeretUI",
        name: str,
        template: str,
        templates: Iterable[str] = None,
        addons: str = None,
    ) -> None:
        """Register a page.

        This method register the page template and the callable to serve it
        without additionnal callable.

        ::

            myferet.register_static_page('my-page', '<div>My Page</div>')


        If need, the templates can be passed in the decorator and
        are added in the templates librairy

        ::

            myferet.register_static_page(
                'my-page',
                '<div>My Page</div>',
                template=[
                    '''
                        <template id="...">
                            ...
                        </template>
                    '''
                ]
            )

        :param name: The name of the pages stored in FeretUI.pages
        :type name: str
        :param templates: The str of the additionnal templates to load
        :type templates: Iterable[str]
        :param addons: The addons where the message come from
        :type addons: str
        """
        if templates is None:
            templates = []
        if not isinstance(templates, list) and isinstance(templates, Iterable):
            templates = list(templates)

        templates.append(f'<template id="{name}">{template}</template>')
        self.register_page(
            name=name,
            templates=templates,
            addons=addons,
        )(
            static_page(name),
        )

    def get_page(
        self: "FeretUI",
        pagename: str,
    ) -> Callable[["FeretUI", Session, dict], str]:
        """Return the page callable.

        ::

            myferet.get_page('my-page')

        :param pagename: The name of the page
        :type pagename: str
        :return: the callable
        :rtype: Callable[
            [:class:`.FeretUI`, :class:`feretui.session.Session`, dict],
            str]
        """
        if pagename not in self.pages:
            return self.get_page("404")

        return self.pages[pagename]

    # ---------- Menus ----------
    def _register_toolbar_menus(
        self: "FeretUI",
        position: str,
        menus: list[ToolBarMenu],
        addons: str = None,
    ) -> None:
        def add_translation(menu: ToolBarMenu) -> None:
            self.translation.add_translated_menu(
                TranslatedMenu(menu, addons=addons),
            )
            if isinstance(menu, ChildrenMenu):
                for submenu in menu.children:
                    if not isinstance(submenu, ToolBarDividerMenu):
                        add_translation(submenu)

        for menu in menus:
            if not isinstance(menu, ToolBarMenu | ToolBarButtonsMenu):
                raise MenuError(f"{menu} is not a toolbar menu")

            if isinstance(menu, ToolBarDividerMenu):
                raise MenuError(f"You can't register {menu}")

            add_translation(menu)
            self.menus[position].append(menu)

    def register_toolbar_left_menus(
        self: "FeretUI",
        menus: list[ToolBarMenu],
        addons: str = None,
    ) -> None:
        """Register a menu in the left part of the toolbar.

        ::

            myferet.register_toolbar_left_menus([
                ToolBarMenu(...),
            ])

        :param menus: The menus to register
        :type menus: list[:class:`feretui.menus.ToolBarMenu`]
        :param addons: The addons where the message come from
        :type addons: str
        :exception: :class:`feretui.exceptions.MenuError`
        """
        self._register_toolbar_menus("left", menus, addons=addons)

    def register_toolbar_right_menus(
        self: "FeretUI",
        menus: list[ToolBarMenu],
        addons: str = None,
    ) -> None:
        """Register a menu in the right part of the toolbar.

        ::

            myferet.register_toolbar_right_menus([
                ToolBarMenu(...),
            ])

        :param menus: The menus to register
        :type menus: list[:class:`feretui.menus.ToolBarMenu`]
        :param addons: The addons where the message come from
        :type addons: str
        :exception: :class:`feretui.exceptions.MenuError`
        """
        self._register_toolbar_menus("right", menus, addons=addons)

    def register_aside_menus(
        self: "FeretUI",
        code: str,
        menus: list[AsideMenu],
        addons: str = None,
    ) -> None:
        """Register a menu in an aside page.

        ::

            myferet.register_aside_menus(
                'my-aside', [
                    AsideMenu(...),
                ],
            )

        :param code: The code of the aside
        :type code: str
        :param menus: The menus to register
        :type menus: list[:class:`feretui.menus.AsideMenu`]
        :param addons: The addons where the message come from
        :type addons: str
        :exception: :class:`feretui.exceptions.MenuError`
        """
        asides = self.asides.setdefault(code, [])

        def register_menu(menu: AsideMenu) -> None:
            menu.aside = code
            self.translation.add_translated_menu(
                TranslatedMenu(menu, addons=addons),
            )
            if isinstance(menu, ChildrenMenu):
                for submenu in menu.children:
                    if not isinstance(submenu, ToolBarDividerMenu):
                        register_menu(submenu)

        for menu in menus:
            if not isinstance(menu, AsideMenu):
                raise MenuError(f"{menu} is not an aside menu")

            register_menu(menu)
            asides.append(menu)

    def register_auth_menus(
        self: "FeretUI",
        menus: list[ToolBarButtonMenu],
        addons: str = None,
    ) -> None:
        """Register the auth menus.

        ::

            myferet.register_auth_menus([
                ToolBarButtonMenu(...),
            ])

        :param menus: The menus to register
        :type menus: list[:class:`feretui.menus.ToolBarButtonMenu`]
        :param addons: The addons where the message come from
        :type addons: str
        :exception: :class:`feretui.exceptions.MenuError`
        """
        for menu in menus:
            if not isinstance(menu, ToolBarButtonMenu):
                raise MenuError(f"{menu} is not a toolbar button menu")

        self.auth = {
            "menus": ToolBarButtonsMenu(menus),
            "addons": addons,
        }

    def register_user_menus(
        self: "FeretUI",
        menus: list[ToolBarMenu],
        addons: str = None,
    ) -> None:
        """Register a menu in the dropdown in the user menu.

        ::

            myferet.register_user_menus([
                ToolBarMenu(...),
            ])

        :param menus: The menus to register
        :type menus: list[:class:`feretui.menus.ToolBarMenu`]
        :param addons: The addons where the message come from
        :type addons: str
        :exception: :class:`feretui.exceptions.MenuError`
        """
        self._register_toolbar_menus("user", menus, addons=addons)

    def get_aside_menus(self: "FeretUI", code: str) -> list[AsideMenu]:
        """Return the aside menus link with the code.

        :param code: The code of the aside
        :type code: str
        :return: The menus to render
        :rtype: list[:class:`feretui.menus.AsideMenu`
        """
        return self.asides.setdefault(code, [])

    def get_site_map_menus(self: "FeretUI") -> None:
        """Return the sitemap menus.

        :return: The menus to render
        :rtype: :class:`feretui.menus.SitemapMenu`
        """
        return {
            "toolbar": [
                SitemapMenu(self, menu)
                for menu in (
                    self.menus.get("left", []) + self.menus.get("right", [])
                )
            ],
            "auth": [
                SitemapMenu(self, menu) for menu in self.auth["menus"].children
            ],
            "user": [
                SitemapMenu(self, menu) for menu in self.menus.get("user", [])
            ],
        }

    # ---------- Resource  ----------
    def register_resource(
        self: "FeretUI",
        addons: str = None,
    ) -> None:
        """Register and build the resource instance.

        ::

            myferet.register_resource(
                'code of the resource',
                'label',
            )
            class MyResource(Resource):
                pass

        :param addons: The addons where the message come from
        :type addons: str
        """

        def wrap_class(cls: Resource) -> Resource:
            if cls.code in self.resources:
                logger.info("Overload resource %s[%s]", (cls.code, cls.label))

            resource = cls.build()
            self.resources[cls.code] = resource
            tr = TranslatedResource(resource, addons)
            self.translation.add_translated_resource(tr)
            return cls

        return wrap_class

    def get_resource(self: "FeretUI", code: str) -> Resource:
        """Return the resource instance.

        :param code: The code of the instance
        :type code: :class:`feretui.resource.Resource`
        :return: The instance of the resource
        :rtype: :class:`feretui.resource.Resource`
        :exception: :class:`feretui.exceptions.UnexistingResourceError`
        """
        if code not in self.resources:
            raise UnexistingResourceError(code)

        return self.resources[code]

    # ---------- Form  ----------
    def register_form(self: "FeretUI", addons: str = None) -> Callable:
        """Register a WTForm.

        This a decorator.

        ::

            @myferet.register_form()
            class MyForm(FeretUIForm):
                foo = StringField()


        :param addons: The addons where the message come from
        :type addons: str
        """

        def _register_form(form: FeretUIForm) -> FeretUIForm:
            self.translation.add_translated_form(
                TranslatedForm(form, addons=addons),
            )
            return form

        return _register_form

    # ---------- Translation ----------
    def export_catalog(
        self: "FeretUI",
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
        if self.auth["menus"]:
            for menu in self.auth["menus"].children or []:
                self.translation.add_translated_menu(
                    TranslatedMenu(menu, addons=self.auth["addons"]),
                )
        self.translation.export_catalog(output_path, version, addons=addons)

    def load_catalog(self: "FeretUI", catalog_path: str, lang: str) -> None:
        """Load a specific catalog for a language.

        ::
            FeretUI.load_catalog('feretui/locale/fr.po', 'fr')

        :param catalog_path: Path of the catalog
        :type catalog_path: str
        :param lang: Language code
        :type lang: str
        """
        self.translation.load_catalog(catalog_path, lang)

    def load_internal_catalog(self: "FeretUI", lang: str) -> None:
        """Load a specific catalog for a language defined by feretui.

        ::
            FeretUI.load_internal_catalog('fr')

        :param lang: Language code
        :type lang: str
        """
        catalog_path = Path(__file__).parent / "locale" / f"{lang}.po"
        self.load_catalog(catalog_path, lang)
