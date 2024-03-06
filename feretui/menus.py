# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Menu mecanism.

Define the menu class to display its and define the actions call when the
menus are clicked.

The menus are splited in two groups.

* Toolbar menu

  * :class:`.ToolBarMenu`
  * :class:`.ToolBarDropDownMenu`
  * :class:`.ToolBarUrlMenu`
  * :class:`.ToolBarDividerMenu`

* Aside: The menu is display in the aside-menu page

  * :class:`.AsideMenu`
  * :class:`.AsideHeaderMenu`
  * :class:`.AsideUrlMenu`


::

    myferet.register_aside_menus('aside1', [
        AsideHeaderMenu('Menu A1', children=[
            AsideMenu('Sub Menu A11', page='submenu11'),
            AsideMenu('Sub Menu A12', page='submenu12'),
        ]),
    ])
    myferet.register_aside_menus('aside2', [
        AsideHeaderMenu('Menu A2', children=[
            AsideMenu('Sub Menu A21', page='submenu21'),
            AsideMenu('Sub Menu A22', page='submenu22'),
        ]),
    ])
    myferet.register_toolbar_left_menus([
        ToolBarDropDownMenu('Menu Tb1', children=[
            ToolBarMenu(
                'Menu Tb11', page="aside-menu", aside="aside1",
                aside_page='submenu11',
            ),
            ToolBarDividerMenu(),
            ToolBarMenu(
                'Menu Tb12', page="aside-menu", aside="aside2",
                aside_page='submenu22',
            ),
        ]),
        ToolBarMenu('Menu Tb2', page="my-page"),
    ])

"""
from typing import TYPE_CHECKING

from feretui.exceptions import MenuError
from feretui.session import Session
from feretui.thread import local

if TYPE_CHECKING:
    from feretui.feretui import FeretUI


class Menu:
    """Mixin class Menu.

    All the menu inherit this class. It is added behaviours:

    * Translated label
    * Translated tooltip
    * icon
    * querystring
    * render

    ::

        menu = Menu('My label')
        if menu.is_visible(session):
            menu.render(myferet, session)

    """

    template_id: str = None
    """The template id to display in the :meth:`.Menu.render`"""

    def __init__(
        self: "Menu",
        label: str,
        icon: str = None,
        tooltip: str = None,
        **querystring: dict[str, str],
    ) -> None:
        """Menu constructor.

        :param label: The label of the menu
        :type label: str
        :param icon: The icon html class used in the render
        :type icon: str
        :param tooltip: The tooltip, it is a helper to understand the role
                        of the menu
        :type tooltip: str
        :param querystring: The querystring of the api called
        :type querystring: str
        :exception: :class:`feretui.exceptions.MenuError`
        """
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

    def __str__(self: "Menu") -> str:
        """Return the instance as a string."""
        return f'<{self.__class__.__name__} {self.context}>'

    def is_visible(self: "Menu", session: Session) -> bool:  # noqa: ARG002
        """Return True if the menu can be rendering.

        :param session: The session of the user
        :type session: :class:`feretui.session.Session`
        :return: True
        :rtype: bool
        """
        return True

    def get_label(self: "Menu", feretui: "FeretUI") -> str:
        """Return the translated label.

        :param feretui: The feretui client instance.
        :type feretui: :class:`feretui.feretui.FeretUI`
        :return: The label translated in the user lang
        :rtype: str
        """
        lang = local.lang
        return feretui.translation.get(
            lang,
            f'{self.context}:label',
            self.label,
        )

    def get_tooltip(self: "Menu", feretui: "FeretUI") -> str:
        """Return the translated tooltip.

        :param feretui: The feretui client instance.
        :type feretui: :class:`feretui.feretui.FeretUI`
        :return: The tooltip translated in the user lang
        :rtype: str
        """
        if not self.tooltip:
            return ''

        lang = local.lang
        return feretui.translation.get(
            lang,
            f'{self.context}:tooltip',
            self.tooltip,
        )

    def get_url(
        self: "Menu",
        feretui: "FeretUI",
        querystring: dict[str, str],
    ) -> str:
        """Return the url to put in hx-get attribute of the a tag.

        :param feretui: The feretui client instance.
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param querystring: The querysting to pass at the api
        :type querysting: dict[str, str]
        :return: The url
        :rtype: str
        """
        return local.request.get_url_from_dict(
            base_url=f'{ feretui.base_url }/action/goto',
            querystring=querystring,
        )

    def render(self: "Menu", feretui: "FeretUI", session: Session) -> str:
        """Return the html of the menu.

        :param feretui: The feretui client instance.
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The session of the user
        :type session: :class:`feretui.session.Session`
        :return: The html
        :rtype: str
        """
        return feretui.render_template(
            session,
            self.template_id,
            label=self.get_label(feretui),
            tooltip=self.get_tooltip(feretui),
            icon=self.icon,
            url=self.get_url(feretui, self.querystring),
        )


class ChildrenMenu:
    """Mixin children class.

    This mixin add children behaviour for:

    * :class:`.ToolBarDropDownMenu`
    * :class:`.AsideHeaderMenu`
    """

    def __init__(self: "ChildrenMenu", children: list[Menu]) -> None:
        """Initialize the children.

        :param children: The list of the children
        :type children: list[:class:`.Menu`
        """
        if not children:
            raise MenuError(f'{self.__class__.__name__} must have children')

        self.children = children

    def render(self: "Menu", feretui: "FeretUI", session: Session) -> str:
        """Return the html of the menu.

        :param feretui: The feretui client instance.
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The session of the user
        :type session: :class:`feretui.session.Session`
        :return: The html
        :rtype: str
        """
        return feretui.render_template(
            session,
            self.template_id,
            label=self.get_label(feretui),
            tooltip=self.get_tooltip(feretui),
            icon=self.icon,
            children=self.children,
        )


class UrlMenu:
    """Mixin class for give an external url."""

    def get_url(
        self: "Menu",
        feretui: "FeretUI",  # noqa: ARG002
        querystring: dict[str, str],
    ) -> str:
        """Return the external url from the querystring.

        :param feretui: The feretui client instance.
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param querystring: The querysting to pass at the api
        :type querysting: dict[str, str]
        :return: The url
        :rtype: str
        """
        return querystring['url']


class ToolBarMenu(Menu):
    """Menu class for the toolbar.

    ::

        menu = ToolBarMenu('My label')
        if menu.is_visible(session):
            menu.render(myferet, session)

    """

    template_id = 'toolbar-menu'

    def __init__(
        self: "ToolBarMenu",
        label: str,
        **kwargs: dict[str, str],
    ) -> None:
        """Call the Menu constructor and update the context.

        see :class:`.Menu`
        """
        super().__init__(label, **kwargs)
        self.context = 'menu:toolbar:' + ':'.join(
            f'{key}:{value}'
            for key, value in self.querystring.items()
        )


class ToolBarDropDownMenu(ChildrenMenu, ToolBarMenu):
    """DropDown for toolbar.

    ::

        menu = ToolBarDropDownMenu(
            'Label',
            children=[ToolBarMenu('My label')])
        if menu.is_visible(session):
            menu.render(myferet, session)

    """

    template_id = 'toolbar-dropdown-menu'

    def __init__(
        self: "ToolBarDropDownMenu",
        label: str,
        children: list[ToolBarMenu] = None,
        **kwargs: dict[str, str],
    ) -> None:
        """Construct the dropdown menu.

        Inherits of ToolbarMenu and ChildrenMenu
        """
        ToolBarMenu.__init__(self, label, type='dropdown', **kwargs)
        ChildrenMenu.__init__(self, children)
        for child in children:
            if isinstance(child, ToolBarDropDownMenu):
                raise MenuError('ToolBarDropDownMenu menu can not be cascaded')


class ToolBarDividerMenu(ToolBarMenu):
    """Simple Divider."""

    template_id: str = 'toolbar-divider-menu'

    def __init__(self: "ToolBarDividerMenu") -> None:
        """Separate two menu in DropDown menu."""
        self.context = ''
        pass

    def render(
        self: "ToolBarDividerMenu",
        feretui: "FeretUI",
        session: Session,
    ) -> str:
        """Return the html of the menu.

        :param feretui: The feretui client instance.
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The session of the user
        :type session: :class:`feretui.session.Session`
        :return: The html
        :rtype: str
        """
        return feretui.render_template(session, self.template_id)


class ToolBarUrlMenu(UrlMenu, ToolBarMenu):
    """Menu class to add a link to another web api.

    ::

        menu = ToolBarUrlMenu('My label', url="https://bulma.io")
        if menu.is_visible(session):
            menu.render(myferet, session)
    """

    template_id = 'toolbar-url-menu'

    def __init__(
        self: "ToolBarUrlMenu",
        label: str,
        url: str,
        **kw: dict[str, str],
    ) -> None:
        """Call the menu constructor and update the context.

        see :class:`.menu`

        :param label: the label of the menu
        :type label: str
        :param url: the http url
        :type url: str
        :param icon: the icon html class used in the render
        :type icon: str
        :param tooltip: the tooltip, it is a helper to understand the role
                        of the menu
        :type tooltip: str
        """
        super().__init__(label, url=url, **kw)


class ToolBarButtonMenu(Menu):
    template_id = 'toolbar-button-menu'

    def __init__(
        self: "ToolBarMenu",
        label: str,
        css_class: str = None,
        **kwargs: dict[str, str],
    ) -> None:
        super().__init__(label, **kwargs)
        self.css_class = css_class
        self.context = 'menu:toolbar:button:' + ':'.join(
            f'{key}:{value}'
            for key, value in self.querystring.items()
        )

    def render(self: "Menu", feretui: "FeretUI", session: Session) -> str:
        """Return the html of the menu.

        :param feretui: The feretui client instance.
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The session of the user
        :type session: :class:`feretui.session.Session`
        :return: The html
        :rtype: str
        """
        return feretui.render_template(
            session,
            self.template_id,
            label=self.get_label(feretui),
            tooltip=self.get_tooltip(feretui),
            icon=self.icon,
            url=self.get_url(feretui, self.querystring),
            css_class=self.css_class,
        )


class ToolBarButtonsMenu(ChildrenMenu, ToolBarButtonMenu):
    template_id = 'toolbar-buttons-menu'

    def __init__(
        self: "ToolBarDropDownMenu",
        children: ToolBarMenu,
    ) -> None:
        """Construct the dropdown menu.

        Inherits of ToolbarMenu and ChildrenMenu
        """
        ToolBarButtonMenu.__init__(self, None, type='buttons')
        ChildrenMenu.__init__(self, children)
        for child in children:
            if isinstance(child, ChildrenMenu):
                raise MenuError('ToolBarButtonsMenu menu can not be cascaded')


class ToolBarButtonUrlMenu(ToolBarButtonMenu, ToolBarUrlMenu):
    template_id = 'toolbar-button-url-menu'


class AsideMenu(Menu):
    """Menu class for the aside menu page.

    ::

        menu = AsideMenu('My label')
        if menu.is_visible(session):
            menu.render(myferet, session)

    """

    template_id = 'aside-menu'

    def __init__(
        self: "AsideMenu",
        label: str,
        **kwargs: dict[str, str],
    ) -> None:
        """Call the Menu constructor and update the context.

        see :class:`.Menu`
        """
        super().__init__(label, **kwargs)
        self.context = 'menu:aside:' + ':'.join(
            f'{key}:{value}'
            for key, value in self.querystring.items()
        )
        self.aside = ''

    def get_url(
        self: "AsideMenu",
        feretui: "FeretUI",
        querystring: dict[str, str],
    ) -> str:
        """Return the url to put in hx-get attribute of the a tag.

        :param feretui: The feretui client instance.
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param querystring: The querysting to pass at the api
        :type querysting: dict[str, str]
        :return: The url
        :rtype: str
        """
        querystring = querystring.copy()
        querystring['in-aside'] = [self.aside]
        return super().get_url(feretui, querystring)


class AsideHeaderMenu(ChildrenMenu, AsideMenu):
    """Hieracal menu for aside.

    ::

        menu = AsideHeaderMenu(
            'Label',
            children=[AsideMenu('My label')])
        if menu.is_visible(session):
            menu.render(myferet, session)

    """

    template_id = 'aside-header-menu'

    def __init__(
        self: "AsideHeaderMenu",
        label: str,
        children: list[ToolBarMenu] = None,
        **kwargs: dict[str, str],
    ) -> None:
        """Construct the dropdown menu.

        Inherits of ToolbarMenu and ChildrenMenu
        """
        AsideMenu.__init__(self, label, type='header', **kwargs)
        ChildrenMenu.__init__(self, children)


class AsideUrlMenu(UrlMenu, AsideMenu):
    """Menu class to add a link to another web api.

    ::

        menu = ToolBarUrlMenu('My label', url="https://bulma.io")
        if menu.is_visible(session):
            menu.render(myferet, session)
    """

    template_id = 'aside-url-menu'

    def __init__(
        self: "AsideUrlMenu",
        label: str,
        url: str,
        **kw: dict[str, str],
    ) -> None:
        """Call the menu constructor and update the context.

        see :class:`.menu`

        :param label: the label of the menu
        :type label: str
        :param url: the http url
        :type url: str
        :param icon: the icon html class used in the render
        :type icon: str
        :param tooltip: the tooltip, it is a helper to understand the role
                        of the menu
        :type tooltip: str
        """
        super().__init__(label, url=url, **kw)
