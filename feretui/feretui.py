from collections.abc import Callable
from logging import getLogger
from os.path import dirname, join

from jinja2 import Environment, PackageLoader, select_autoescape

from feretui.actions import (
    action_goto_page,
    action_login_password,
    action_login_signup,
    action_logout,
    action_render_page,
    action_resource_router,
)
from feretui.exceptions import UnexistingAction, UnexistingResource
from feretui.helper import authenticated_or_404
from feretui.menu import menu_login
from feretui.pages import (
    page_404,
    page_forbidden,
    page_homepage,
    page_login,
    page_resource,
    page_signup,
)
from feretui.request import Request
from feretui.resource import Resource
from feretui.response import Response
from feretui.session import Session
from feretui.template import Template
from feretui.translate import (
    TranslatedResource,
    TranslatedTemplate,
    Translation,
)

logger = getLogger(__name__)


def feretui_session_theme(feret: "FeretUI", session: Session) -> str:
    if session.theme:
        return session.theme

    return feret.get_callback('feretui_default_theme')()


class FeretUI:

    translated_messages = []

    def __init__(self):
        self.env = Environment(
            loader=PackageLoader("feretui"),
            autoescape=select_autoescape()
        )

        # List the template to use to generate the UI
        feretui_path = dirname(__file__)
        self.template = Template()

        self.load_feretui_templates(
            join(feretui_path, 'templates', 'feret.tmpl')
        )

        self.statics = {
            'bulma.css': join(
                feretui_path, 'static', 'bulma', 'css', 'bulma.min.css'),
            'htmx.js': join(feretui_path, 'static', 'htmx.1.9.9.min.js'),
            'hyperscript.js': join(
                feretui_path, 'static', 'hyperscript.0.9.12.js'),
            'json-enc.js': join(feretui_path, 'static', 'json-enc.js'),
            'logo.png': join(feretui_path, 'static', 'logo.png'),
        }
        self.statics.update({  # themes https://jenil.github.io/bulmaswatch/
            f'{theme}.css': join(
                feretui_path, 'static', 'themes', f'{theme}.min.css'
            )
            for theme in (
                'cerulean', 'cyborg', 'default', 'journal', 'lumen', 'materia',
                'nuclear', 'sandstone', 'slate', 'spacelab', 'united', 'cosmo',
                'darkly', 'flatly', 'litera', 'lux', 'minty', 'pulse',
                'simplex', 'solar', 'superhero', 'yeti',
            )
        })
        self.css_import = [
            '/feretui/static/bulma.css',
        ]
        self.js_import = [
            '/feretui/static/htmx.js',
            '/feretui/static/hyperscript.js',
            '/feretui/static/json-enc.js',
        ]
        self.callbacks = {
            # feretui_default_theme () => theme
            'feretui_default_theme': lambda: 'default',
            # feretui_session_theme (feretui, session) => theme
            'feretui_session_theme': feretui_session_theme,
            # feretui_navbar_header_left/right (session) =>
            #    [{code:, label:,} or {url:, label:,}]
            'feretui_navbar_header_left': lambda session: [],
            'feretui_navbar_header_right': lambda session: [],
            # feretui_navbar_authentications () =>
            #    [{code:, label:, class:}]
            'feretui_navbar_authentications': lambda: [menu_login],
            # feretui_default_authentication () => code
            'feretui_default_authentication': lambda: menu_login['code'],
            # feretui_langs () => [{code:, label:,}]
            'feretui_langs': lambda: [{'code': 'en', 'label': 'English'}],
        }

        self.pages = {
            '404': page_404,
            'forbidden': page_forbidden,
            'homepage': page_homepage,
            'login': page_login,
            'signup': page_signup,
            'resource': page_resource,
        }

        self.actions = {
            'goto': action_goto_page,
            'render': action_render_page,
            'login_password': action_login_password,
            'login_signup': action_login_signup,
            'logout': action_logout,
            'resource': action_resource_router,
        }

        self.resources = {}

    def load_feretui_templates(
        self,
        template_path: str,
        addons: str = 'feretui'
    ) -> None:
        tt = TranslatedTemplate(template_path, addons=addons)
        Translation.add_translated_template(tt)
        with open(template_path, 'r') as fp:
            self.template.load_file(fp)

    def get_static_file_path(self, filename: str) -> str:
        return self.statics.get(filename)

    def render(self, request: Request) -> str:
        template = self.env.get_template('feret_base.html')
        return template.render(
            feret=self,
            session=request.session,
            querystring=request.raw_querystring,
        )

    # --- callback for internal used ---
    def register_callback(
        self,
        func: Callable[..., ...]
    ) -> Callable[..., ...]:
        if func.__name__ in self.callbacks:
            logger.info(f'Overload callback {func.__name__}')

        self.callbacks[func.__name__] = func
        return func

    def get_callback(self, name: str) -> Callable[..., ...]:
        return self.callbacks[name]

    # --- page to display ---
    def load_page_template(
        self,
        session: Session,
        template_page_id: str,
        **kwargs
    ) -> str:
        template = self.env.from_string(
            self.template.get_template(
                template_page_id,
                lang=session.lang,
            )
        )
        return template.render(feret=self, session=session, **kwargs)

    def register_page(
        self,
        func: Callable[["FeretUI", Session, dict], str],
    ) -> Callable[["FeretUI", Session, dict], str]:
        if func.__name__ in self.pages:
            logger.info(f'Overload page {func.__name__}')

        if func.__doc__:
            doc = func.__doc__.strip()
            if doc.startswith('<template'):
                self.template.load_template_from_str(doc)

        self.pages[func.__name__] = func
        return func

    def get_page(self, pagename: str) -> Callable[..., ...]:
        if pagename not in self.pages:
            return self.get_page('404')

        return self.pages[pagename]

    # --- action to execute ---
    def register_action(
        self,
        func: Callable[["FeretUI", Request], Response]
    ) -> Callable[["FeretUI", Request], Response]:
        if func.__name__ in self.actions:
            logger.info(f'Overload action {func.__name__}')

        self.actions[func.__name__] = func
        return func

    def get_action(self, actionname: str) -> Callable[..., ...]:
        if actionname not in self.actions:
            raise UnexistingAction(actionname)

        return self.actions[actionname]

    def do_action(
        self,
        request: Request,
        action: str
    ) -> Response:
        Translation.set_lang(request.session.lang)
        cmd = action.split('-')
        meth = self.get_action(cmd[0])
        return meth(self, request, *cmd[1:])

    # --- resource to display ---
    def register_resource(
        self, code: str,
        label: str,
        menus: list[dict] = None,
        security: Callable = authenticated_or_404,
        addons: str = None,
    ) -> Callable[[Resource], Resource]:
        def wrapper_cls(cls: Resource) -> Resource:
            if code in self.resources:
                logger.info(f'Overload resource {code}[{label}]')

            self.resources[code] = cls
            cls._code = code
            cls._label = label
            cls._menus = menus
            cls._security = security
            cls.register_sub_entries()
            tr = TranslatedResource(cls, addons)
            Translation.add_translated_resource(tr)
            return cls

        return wrapper_cls

    def get_resource(self, resourcecode: str) -> Resource:
        if resourcecode not in self.resources:
            raise UnexistingResource(resourcecode)

        return self.resources[resourcecode]

    # --- translation ---
    def export_catalog(self, output_path: str, addons: str = None):
        Translation.export_catalog(output_path, addons=addons)

    def load_catalog(self, catalog_path: str, lang: str):
        Translation.load_catalog(catalog_path, lang)
