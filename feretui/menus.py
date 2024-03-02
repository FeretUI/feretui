# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from feretui.exceptions import MenuError
from feretui.thread import local


class Menu:
    template_id = None

    def __init__(self, label, icon=None, tooltip=None, **querystring):
        if not querystring:
            raise MenuError(f'{self.__class__.__name__} must have querystring')

        for value in querystring.values():
            if not isinstance(value, str):
                raise MenuError('The querystring entries must be string')

        self.label = label
        self.icon = icon
        self.tooltip = tooltip
        self.querystring = querystring
        self.context = 'menu:'

    def __str__(self):
        return f'<{self.__class__.__name__} {self.context}>'

    def is_visible(self, session):
        return True

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

    def get_url(self, feretui, querystring):
        return local.request.get_url_from_dict(
            base_url=f'{ feretui.base_url }/action/goto',
            querystring=querystring,
        )

    def render(self, feretui, session):
        return feretui.render_template(
            session,
            self.template_id,
            label=self.get_label(feretui),
            tooltip=self.get_tooltip(feretui),
            icon=self.icon,
            url=self.get_url(feretui, self.querystring),
        )


class ChildrenMenu:

    def __init__(self, children):
        if not children:
            raise MenuError(f'{self.__class__.__name__} must have children')

        self.children = children

    def render(self, feretui, session):
        return feretui.render_template(
            session,
            self.template_id,
            label=self.get_label(feretui),
            tooltip=self.get_tooltip(feretui),
            icon=self.icon,
            children=self.children,
        )


class UrlMenu:

    def get_url(self, feretui, querystring):
        return querystring['url']


class ToolBarMenu(Menu):
    template_id = 'toolbar-menu'

    def __init__(self, label, tooltip=None, **querystring):
        super().__init__(label, tooltip=tooltip, **querystring)
        self.context = 'menu:toolbar:' + ':'.join(
            f'{key}:{value}'
            for key, value in self.querystring.items()
        )


class ToolBarDropDownMenu(ChildrenMenu, ToolBarMenu):
    template_id = 'toolbar-dropdown-menu'

    def __init__(self, label, children=None, **querystring):
        ToolBarMenu.__init__(self, label, type='dropdown', **querystring)
        ChildrenMenu.__init__(self, children)
        for child in children:
            if isinstance(child, ToolBarDropDownMenu):
                raise MenuError('ToolBarDropDownMenu menu can not be cascaded')


class ToolBarDividerMenu(ToolBarMenu):

    def __init__(self):
        self.context = ''
        pass

    def render(self, feretui, session):
        return feretui.render_template(session, 'toolbar-divider-menu')


class ToolBarUrlMenu(UrlMenu, ToolBarMenu):
    template_id = 'toolbar-url-menu'

    def __init__(self, label, url, **kw):
        super().__init__(label, url=url, **kw)


class AsideMenu(Menu):
    template_id = 'aside-menu'

    def __init__(self, label, tooltip=None, **querystring):
        super().__init__(label, tooltip=tooltip, **querystring)
        self.context = 'menu:aside:' + ':'.join(
            f'{key}:{value}'
            for key, value in self.querystring.items()
        )
        self.aside = ''

    def get_url(self, feretui, querystring):
        querystring = querystring.copy()
        querystring['in-aside'] = [self.aside]
        return super().get_url(feretui, querystring)


class AsideHeaderMenu(ChildrenMenu, AsideMenu):
    template_id = 'aside-header-menu'

    def __init__(self, label, children=None, **querystring):
        AsideMenu.__init__(self, label, type='header', **querystring)
        ChildrenMenu.__init__(self, children)


class AsideUrlMenu(UrlMenu, AsideMenu):
    template_id = 'aside-url-menu'

    def __init__(self, label, url, **kw):
        super().__init__(label, url=url, **kw)
