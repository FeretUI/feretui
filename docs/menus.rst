.. This file is a part of the FeretUI project
..
..    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

Menus
-----

The menus is not create automaticly. It is a part of the user interface.

Four area exists:

* Toolbar (left and/or right) in the header.
* Auth, special part of the Toolbar
* User, special part of the Toolbar when the user is connected.
* Aside, at the left part of the window.

The menu refere a page without hard link. If the page does not exist then the 
page 404 is called.

~~~~~~~~~~~~~~
Toolbar's menu
~~~~~~~~~~~~~~

The existing menu's types are:

* :class:`feretui.menus.ToolBarMenu`
* :class:`feretui.menus.ToolBarDropDownMenu`
* :class:`feretui.menus.ToolBarUrlMenu`
* :class:`feretui.menus.ToolBarDividerMenu`
* :class:`feretui.menus.ToolBarButtonMenu`
* :class:`feretui.menus.ToolBarButtonsMenu`
* :class:`feretui.menus.ToolBarButtonUrlMenu`

To register one or more menu use:

* :meth:`feretui.feretui.FeretUI.register_toolbar_left_menus`.
* :meth:`feretui.feretui.FeretUI.register_toolbar_right_menus`.


::

    myferet.register_toolbar_left_menus([
        ToolBarDropDownMenu('Menu Tb1', children=[
            ToolBarMenu('Menu Tb11', page='submenu11'),
            ToolBarDividerMenu(),
            ToolBarMenu('Menu Tb12', page='submenu12'),
        ]),
        ToolBarMenu('Menu Tb2', page="my-page"),
    ])

~~~~~~~~~~~
Auth's menu
~~~~~~~~~~~

The existing menu's type is: :class:`feretui.menus.ToolBarButtonMenu`

To register one or more menu use: :meth:`feretui.feretui.FeretUI.register_auth_menus`.


::

    myferet.register_auth_menus([
        ToolBarButtonMenu('Sign Up', page='signup', css_class="is-info"),
        ToolBarButtonMenu('Log In', page='login'),
    ])

~~~~~~~~~~~
User's menu
~~~~~~~~~~~

The existing menu's types are:

* :class:`feretui.menus.ToolBarMenu`
* :class:`feretui.menus.ToolBarDropDownMenu`
* :class:`feretui.menus.ToolBarUrlMenu`

To register one or more menu use: :meth:`feretui.feretui.FeretUI.register_user_menus`.

::

    myferet.register_user_menus([
        ToolBarMenu(...),
    ])

~~~~~~~~~~~~~~
Aside's menu
~~~~~~~~~~~~~~

The existing menu's types are:

* :class:`feretui.menus.AsideMenu`
* :class:`feretui.menus.AsideHeaderMenu`
* :class:`feretui.menus.AsideUrlMenu`

To register one or more menu use: :meth:`feretui.feretui.FeretUI.register_aside_menus`.

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

To display the aside's menu it shoul be declared in another menu.

::

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

.. note::

    The page is display in the aside page.

~~~~~~~~~~
Visibility
~~~~~~~~~~

Each menu can be displayed or not in function of visibility rules.

Some rules already exists:

* :class:`feretui.helper.menu_for_authenticated_user`
* :class:`feretui.helper.menu_for_unauthenticated_user` [default]
* :class:`feretui.helper.menu_for_all_users`

::

    myferet.register_toolbar_left_menus([
        ToolBarMenu(
            'My menu', 
            page="my-page",
            visible_callback=menu_for_unauthenticated_user,
        ),
    ])

To create your own function::

    def my_visibilit_callback(session: Session) -> bool:
        if some_check_with_sesion(session):
            return True

        return False

The session can be overloaded and passed during the creation of the 
request. By default only the **user** attribute exist on the session.

~~~~~~~~~~~
Translation
~~~~~~~~~~~

The menus are always translated, No action is needed to translate them
that the standard translation of the project.
