from feretui.exceptions import MenuError
from feretui.thread import local


class Menu:

    def __init__(self, label, tooltip=None, **querystring):
        if not querystring:
            raise MenuError(f'{self.__class__.__name__} must have querystring')

        for value in querystring.values():
            if not isinstance(value, str):
                raise MenuError('The querystring entries must be string')

        self.label = label
        self.tooltip = tooltip
        self.querystring = querystring
        self.context = 'menu:'

    def __str__(self):
        return f'<{self.__class__.__name__} {self.context}>'

    def is_visible(self, session):
        return True

    def get_html_class(self, html_class, position="bottom"):
        if self.tooltip:
            html_class.extend([
                f"has-tooltip-{position}",
                "has-tooltip-arrow",
            ])

        return ' '.join(html_class)

    def get_label(self, feretui) -> str:
        lang = local.lang
        return feretui.translation.get(
            lang,
            f'{self.context}:label',
            self.label,
        )

    def get_tooltip(self, feretui) -> str:
        if not self.tooltip:
            return ''

        lang = local.lang
        return feretui.translation.get(
            lang,
            f'{self.context}:tooltip',
            self.tooltip,
        )


class ChildrenMenu:

    def __init__(self, children):
        self.children = children


class ToolBarMenu(Menu):

    def __init__(self, label, tooltip=None, **querystring):
        super().__init__(label, tooltip=tooltip, **querystring)
        self.context = 'menu:toolbar:' + ':'.join(
            f'{key}:{value}'
            for key, value in self.querystring.items()
        )

    def get_url(self, feretui):
        return local.request.get_url_from_dict(
            base_url=f'{ feretui.base_url }/action/goto',
            querystring=self.querystring,
        )

    def render(self, feretui, session):
        html_class = self.get_html_class(["navbar-item"])
        return feretui.render_template(
            session,
            'toolbar-menu',
            label=self.get_label(feretui),
            html_class=html_class,
            tooltip=self.get_tooltip(feretui),
            url=self.get_url(feretui),
        )


class ToolBarDropDownMenu(ChildrenMenu, ToolBarMenu):

    def __init__(self, label, children=None, **querystring):
        if not children:
            raise MenuError('ToolBarDropDownMenu must have children')

        for child in children:
            if isinstance(child, ToolBarDropDownMenu):
                raise MenuError('ToolBarDropDownMenu menu can not be cascaded')

        ToolBarMenu.__init__(self, label, type='dropdown', **querystring)
        ChildrenMenu.__init__(self, children)

    def render(self, feretui, session):
        html_class = self.get_html_class(
            ["navbar-item", "has-dropdown", "is-hoverable"],
            position="right",
        )
        return feretui.render_template(
            session,
            'toolbar-dropdown-menu',
            label=self.get_label(feretui),
            html_class=html_class,
            tooltip=self.get_tooltip(feretui),
            children=self.children,
        )


class ToolBarDividerMenu(ToolBarMenu):

    def __init__(self):
        self.context = ''
        pass

    def render(self, feretui, session):
        return feretui.render_template(session, 'toolbar-divider-menu')


class ToolBarUrlMenu(ToolBarMenu):

    def __init__(self, label, url, tooltip=None):
        super().__init__(label, url=url, tooltip=tooltip)

    def get_url(self, feretui):
        return self.querystring['url']

    def render(self, feretui, session):
        html_class = self.get_html_class(["navbar-item"])
        return feretui.render_template(
            session,
            'toolbar-url-menu',
            label=self.get_label(feretui),
            html_class=html_class,
            tooltip=self.get_tooltip(feretui),
            url=self.get_url(feretui),
        )
