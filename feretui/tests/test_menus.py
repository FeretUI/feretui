# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest
from feretui.exceptions import MenuError
from feretui.feretui import FeretUI
from feretui.menus import (
    AsideHeaderMenu,
    AsideMenu,
    AsideUrlMenu,
    ToolBarDividerMenu,
    ToolBarDropDownMenu,
    ToolBarMenu,
    ToolBarUrlMenu,
)
from feretui.session import Session
from feretui.request import Request
from feretui.thread import local


class TestMenu:

    def test_ToolBarDividerMenu(self):
        myferet = FeretUI()
        session = Session()
        assert ToolBarDividerMenu().render(
            myferet, session) == '<hr class="navbar-divider">'

    def test_ToolBarDropDownMenu_without_children(self):
        with pytest.raises(MenuError):
            ToolBarDropDownMenu('Test')

    def test_ToolBarDropDownMenu(self):
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)
        local.request = request
        assert ToolBarDropDownMenu(
            'Test',
            children=[ToolBarMenu('Test', page='test')]
        ).render(myferet, session) == (
            '<div class="navbar-item has-dropdown is-hoverable">\n'
            ' <a class="navbar-link">\n'
            '  <span>\n'
            '   \n'
            '  </span>\n'
            '  <strong>\n'
            '   Test\n'
            '  </strong>\n'
            '  <span>\n'
            '   \n'
            '  </span>\n'
            ' </a>\n'
            ' <div class="navbar-dropdown">\n'
            '  \n'
            '          \n'
            '            <a class="navbar-item" hx-get="/feretui/action/goto?page=test" hx-swap="innerHTML" hx-target="#feretui-body">\n'
            ' <span>\n'
            '  \n'
            ' </span>\n'
            ' <strong>\n'
            '  Test\n'
            ' </strong>\n'
            ' <span>\n'
            '  \n'
            ' </span>\n'
            '</a>\n'
            '          \n'
            '        \n'
            ' </div>\n'
            '</div>'
        )

    def test_ToolBarDropDownMenu_tooltip(self):
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)
        local.request = request
        assert ToolBarDropDownMenu(
            'Test',
            tooltip='Test',
            children=[ToolBarMenu('Test', page='test')]
        ).render(myferet, session) == (
            '<div class="navbar-item has-dropdown is-hoverable">\n'
            ' <a class="navbar-link">\n'
            '  <span>\n'
            '   \n'
            '  </span>\n'
            '  <strong>\n'
            '   Test\n'
            '  </strong>\n'
            '  <span>\n'
            '   \n'
            '   <span class="ml-0 icon has-tooltip-bottom has-tooltip-arrow" data-tooltip="Test">\n'
            '    <i class="fa-solid fa-circle-info is-small">\n'
            '    </i>\n'
            '   </span>\n'
            '   \n'
            '  </span>\n'
            ' </a>\n'
            ' <div class="navbar-dropdown">\n'
            '  \n'
            '          \n'
            '            <a class="navbar-item" hx-get="/feretui/action/goto?page=test" hx-swap="innerHTML" hx-target="#feretui-body">\n'
            ' <span>\n'
            '  \n'
            ' </span>\n'
            ' <strong>\n'
            '  Test\n'
            ' </strong>\n'
            ' <span>\n'
            '  \n'
            ' </span>\n'
            '</a>\n'
            '          \n'
            '        \n'
            ' </div>\n'
            '</div>'
        )

    def test_ToolBarDropDownMenu_cascad(self):
        with pytest.raises(MenuError):
            ToolBarDropDownMenu(
                'Test',
                children=[
                    ToolBarDropDownMenu(
                        'Test',
                        children=[
                            ToolBarMenu('Test', page='test')
                        ]
                    )
                ]
            )

    def test_ToolBarMenu_without_qs(self):
        with pytest.raises(MenuError):
            ToolBarMenu('Test')

    def test_ToolBarMenu(self):
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)
        local.request = request
        assert ToolBarMenu('Test', page='test').render(myferet, session) == (
            '<a class="navbar-item" hx-get="/feretui/action/goto?page=test" hx-swap="innerHTML" hx-target="#feretui-body">\n'
            ' <span>\n'
            '  \n'
            ' </span>\n'
            ' <strong>\n'
            '  Test\n'
            ' </strong>\n'
            ' <span>\n'
            '  \n'
            ' </span>\n'
            '</a>'
        )

    def test_ToolBarMenu_tooltip(self):
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)
        local.request = request
        assert ToolBarMenu(
            'Test', page='test', tooltip="Test").render(myferet, session) == (
                '<a class="navbar-item" hx-get="/feretui/action/goto?page=test" hx-swap="innerHTML" hx-target="#feretui-body">\n'
                ' <span>\n'
                '  \n'
                ' </span>\n'
                ' <strong>\n'
                '  Test\n'
                ' </strong>\n'
                ' <span>\n'
                '  \n'
                '  <span class="ml-0 icon has-tooltip-bottom has-tooltip-arrow" data-tooltip="Test">\n'
                '   <i class="fa-solid fa-circle-info is-small">\n'
                '   </i>\n'
                '  </span>\n'
                '  \n'
                ' </span>\n'
                '</a>'
            )

    def test_ToolBarMenu_with_children_kwargs(self):
        with pytest.raises(MenuError):
            ToolBarMenu('Test', page='test', children=[])

    def test_ToolBarUrlMenu(self):
        myferet = FeretUI()
        session = Session()
        assert ToolBarUrlMenu(
            'Test',
            'https://feretui.readthedocs.io/en/latest/',
        ).render(myferet, session) == (
            '<a class="navbar-item" href="https://feretui.readthedocs.io/en/latest/">\n'
            ' <span>\n'
            '  \n'
            ' </span>\n'
            ' <strong>\n'
            '  Test\n'
            ' </strong>\n'
            ' <span>\n'
            '  \n'
            ' </span>\n'
            '</a>'
        )

    def test_ToolBarUrlMenu_tooltip(self):
        myferet = FeretUI()
        session = Session()
        assert ToolBarUrlMenu(
            'Test',
            'https://feretui.readthedocs.io/en/latest/',
            tooltip='Test',
        ).render(myferet, session) == (
            '<a class="navbar-item" href="https://feretui.readthedocs.io/en/latest/">\n'
            ' <span>\n'
            '  \n'
            ' </span>\n'
            ' <strong>\n'
            '  Test\n'
            ' </strong>\n'
            ' <span>\n'
            '  \n'
            '  <span class="ml-0 icon has-tooltip-bottom has-tooltip-arrow" data-tooltip="Test">\n'
            '   <i class="fa-solid fa-circle-info is-small">\n'
            '   </i>\n'
            '  </span>\n'
            '  \n'
            ' </span>\n'
            '</a>'
        )

    def test_AsideHeaderMenu_without_children(self):
        with pytest.raises(MenuError):
            AsideHeaderMenu('Test')

    def test_AsideHeaderMenu(self):
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)
        local.request = request
        assert AsideHeaderMenu(
            'Test',
            children=[AsideMenu('Test', page='test')]
        ).render(myferet, session) == (
            '<div>\n'
            ' <p class="menu-label">\n'
            '  <span>\n'
            '   \n'
            '  </span>\n'
            '  <span>\n'
            '   <strong>\n'
            '    Test\n'
            '   </strong>\n'
            '  </span>\n'
            '  <span>\n'
            '   \n'
            '  </span>\n'
            ' </p>\n'
            ' <ul>\n'
            '  \n'
            '          \n'
            '  <li>\n'
            '   <a class="menu-label" hx-get="/feretui/action/goto?page=test&amp;in-aside=" hx-swap="innerHTML" hx-target="#feretui-aside-body">\n'
            ' <span>\n'
            '  \n'
            ' </span>\n'
            ' <span>\n'
            '  Test\n'
            ' </span>\n'
            ' <span>\n'
            '  \n'
            ' </span>\n'
            '</a>\n'
            '  </li>\n'
            '  \n'
            '        \n'
            ' </ul>\n'
            '</div>'
        )

    def test_AsideHeaderMenu_tooltip(self):
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)
        local.request = request
        assert AsideHeaderMenu(
            'Test',
            tooltip='Test',
            children=[AsideMenu('Test', page='test')]
        ).render(myferet, session) == (
            '<div>\n'
            ' <p class="menu-label">\n'
            '  <span>\n'
            '   \n'
            '  </span>\n'
            '  <span>\n'
            '   <strong>\n'
            '    Test\n'
            '   </strong>\n'
            '  </span>\n'
            '  <span>\n'
            '   \n'
            '   <span class="ml-0 icon has-tooltip-bottom has-tooltip-arrow" data-tooltip="Test">\n'
            '    <i class="fa-solid fa-circle-info is-small">\n'
            '    </i>\n'
            '   </span>\n'
            '   \n'
            '  </span>\n'
            ' </p>\n'
            ' <ul>\n'
            '  \n'
            '          \n'
            '  <li>\n'
            '   <a class="menu-label" hx-get="/feretui/action/goto?page=test&amp;in-aside=" hx-swap="innerHTML" hx-target="#feretui-aside-body">\n'
            ' <span>\n'
            '  \n'
            ' </span>\n'
            ' <span>\n'
            '  Test\n'
            ' </span>\n'
            ' <span>\n'
            '  \n'
            ' </span>\n'
            '</a>\n'
            '  </li>\n'
            '  \n'
            '        \n'
            ' </ul>\n'
            '</div>'
        )

    def test_AsideHeaderMenu_cascade(self):
        myferet = FeretUI()
        session = Session()
        assert AsideHeaderMenu(
            'Test',
            children=[
                AsideHeaderMenu(
                    'Test',
                    children=[AsideMenu('Test', page='test')]
                )
            ]
        ).render(myferet, session) == (
            '<div>\n'
            ' <p class="menu-label">\n'
            '  <span>\n'
            '   \n'
            '  </span>\n'
            '  <span>\n'
            '   <strong>\n'
            '    Test\n'
            '   </strong>\n'
            '  </span>\n'
            '  <span>\n'
            '   \n'
            '  </span>\n'
            ' </p>\n'
            ' <ul>\n'
            '  \n'
            '          \n'
            '  <li>\n'
            '   <div>\n'
            ' <p class="menu-label">\n'
            '  <span>\n'
            '   \n'
            '  </span>\n'
            '  <span>\n'
            '   <strong>\n'
            '    Test\n'
            '   </strong>\n'
            '  </span>\n'
            '  <span>\n'
            '   \n'
            '  </span>\n'
            ' </p>\n'
            ' <ul>\n'
            '  \n'
            '          \n'
            '  <li>\n'
            '   <a class="menu-label" hx-get="/feretui/action/goto?page=test&amp;in-aside=" hx-swap="innerHTML" hx-target="#feretui-aside-body">\n'
            ' <span>\n'
            '  \n'
            ' </span>\n'
            ' <span>\n'
            '  Test\n'
            ' </span>\n'
            ' <span>\n'
            '  \n'
            ' </span>\n'
            '</a>\n'
            '  </li>\n'
            '  \n'
            '        \n'
            ' </ul>\n'
            '</div>\n'
            '  </li>\n'
            '  \n'
            '        \n'
            ' </ul>\n'
            '</div>'
        )

    def test_AsideMenu_without_qs(self):
        with pytest.raises(MenuError):
            AsideMenu('Test')

    def test_AsideMenu(self):
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)
        local.request = request
        assert AsideMenu('Test', page='test').render(myferet, session) == (
            '<a class="menu-label" hx-get="/feretui/action/goto?page=test&amp;in-aside=" hx-swap="innerHTML" hx-target="#feretui-aside-body">\n'
            ' <span>\n'
            '  \n'
            ' </span>\n'
            ' <span>\n'
            '  Test\n'
            ' </span>\n'
            ' <span>\n'
            '  \n'
            ' </span>\n'
            '</a>'
        )

    def test_AsideMenu_tooltip(self):
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)
        local.request = request
        assert AsideMenu(
            'Test', page='test', tooltip="Test"
        ).render(myferet, session) == (
            '<a class="menu-label" hx-get="/feretui/action/goto?page=test&amp;in-aside=" hx-swap="innerHTML" hx-target="#feretui-aside-body">\n'
            ' <span>\n'
            '  \n'
            ' </span>\n'
            ' <span>\n'
            '  Test\n'
            ' </span>\n'
            ' <span>\n'
            '  \n'
            '  <span class="ml-0 icon has-tooltip-bottom has-tooltip-arrow" data-tooltip="Test">\n'
            '   <i class="fa-solid fa-circle-info is-small">\n'
            '   </i>\n'
            '  </span>\n'
            '  \n'
            ' </span>\n'
            '</a>'
        )

    def test_AsideMenu_with_children_kwargs(self):
        with pytest.raises(MenuError):
            AsideMenu('Test', page='test', children=[])

    def test_AsideUrlMenu(self):
        myferet = FeretUI()
        session = Session()
        assert AsideUrlMenu(
            'Test',
            'https://feretui.readthedocs.io/en/latest/',
        ).render(myferet, session) == (
            '<a class="menu-label" href="https://feretui.readthedocs.io/en/latest/">\n'
            ' <span>\n'
            '  \n'
            ' </span>\n'
            ' <span>\n'
            '  Test\n'
            ' </span>\n'
            ' <span>\n'
            '  \n'
            ' </span>\n'
            '</a>'
        )

    def test_AsideUrlMenu_tooltip(self):
        myferet = FeretUI()
        session = Session()
        assert AsideUrlMenu(
            'Test',
            'https://feretui.readthedocs.io/en/latest/',
            tooltip='Test',
        ).render(myferet, session) == (
            '<a class="menu-label" href="https://feretui.readthedocs.io/en/latest/">\n'
            ' <span>\n'
            '  \n'
            ' </span>\n'
            ' <span>\n'
            '  Test\n'
            ' </span>\n'
            ' <span>\n'
            '  \n'
            '  <span class="ml-0 icon has-tooltip-bottom has-tooltip-arrow" data-tooltip="Test">\n'
            '   <i class="fa-solid fa-circle-info is-small">\n'
            '   </i>\n'
            '  </span>\n'
            '  \n'
            ' </span>\n'
            '</a>'
        )
