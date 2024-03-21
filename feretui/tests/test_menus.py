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
from feretui.helper import (
    menu_for_authenticated_user,
    menu_for_unauthenticated_user,
)
from feretui.menus import (
    AsideHeaderMenu,
    AsideMenu,
    AsideUrlMenu,
    ToolBarButtonMenu,
    ToolBarButtonsMenu,
    ToolBarButtonUrlMenu,
    ToolBarDividerMenu,
    ToolBarDropDownMenu,
    ToolBarMenu,
    ToolBarUrlMenu,
)
from feretui.request import Request
from feretui.session import Session
from feretui.thread import local


class TestMenu:

    def test_ToolBarDividerMenu(self) -> None:
        myferet = FeretUI()
        session = Session()
        assert ToolBarDividerMenu().render(
            myferet, session) == '<hr class="navbar-divider">'

    def test_ToolBarDividerMenu_is_visible_1(self) -> None:
        session = Session()
        assert ToolBarDividerMenu(
            visible_callback=menu_for_authenticated_user,
        ).is_visible(session) is False

    def test_ToolBarDividerMenu_is_visible_2(self) -> None:
        session = Session(user="Test")
        assert ToolBarDividerMenu(
            visible_callback=menu_for_authenticated_user,
        ).is_visible(session) is True

    def test_ToolBarDividerMenu_is_visible_3(self) -> None:
        session = Session()
        assert ToolBarDividerMenu(
            visible_callback=menu_for_unauthenticated_user,
        ).is_visible(session) is True

    def test_ToolBarDividerMenu_is_visible_4(self) -> None:
        session = Session(user="Test")
        assert ToolBarDividerMenu(
            visible_callback=menu_for_unauthenticated_user,
        ).is_visible(session) is False

    def test_ToolBarDropDownMenu_without_children(self) -> None:
        with pytest.raises(MenuError):
            ToolBarDropDownMenu('Test')

    def test_ToolBarDropDownMenu(self, snapshot) -> None:
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)
        local.request = request
        snapshot.assert_match(
            ToolBarDropDownMenu(
                'Test',
                children=[ToolBarMenu('Test', page='test')],
            ).render(myferet, session),
            'snapshot.html',
        )

    def test_ToolBarDropDownMenu_tooltip(self, snapshot) -> None:
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)
        local.request = request
        snapshot.assert_match(
            ToolBarDropDownMenu(
                'Test',
                tooltip='Test',
                children=[ToolBarMenu('Test', page='test')],
            ).render(myferet, session),
            'snapshot.html',
        )

    def test_ToolBarDropDownMenu_cascad(self) -> None:
        with pytest.raises(MenuError):
            ToolBarDropDownMenu(
                'Test',
                children=[
                    ToolBarDropDownMenu(
                        'Test',
                        children=[
                            ToolBarMenu('Test', page='test'),
                        ],
                    ),
                ],
            )

    def test_ToolBarDropDownMenu_is_visible_1(self) -> None:
        session = Session()
        assert ToolBarDropDownMenu(
            'Test',
            children=[
                ToolBarMenu('Test', page='test'),
            ],
            visible_callback=menu_for_authenticated_user,
        ).is_visible(session) is False

    def test_ToolBarDropDownMenu_is_visible_2(self) -> None:
        session = Session(user="Test")
        assert ToolBarDropDownMenu(
            'Test',
            children=[
                ToolBarMenu('Test', page='test'),
            ],
            visible_callback=menu_for_authenticated_user,
        ).is_visible(session) is True

    def test_ToolBarDropDownMenu_is_visible_3(self) -> None:
        session = Session(user="Test")
        assert ToolBarDropDownMenu(
            'Test',
            children=[
                ToolBarMenu(
                    'Test',
                    page='test',
                    visible_callback=menu_for_authenticated_user,
                ),
            ],
        ).is_visible(session) is True

    def test_ToolBarDropDownMenu_is_visible_4(self) -> None:
        session = Session()
        assert ToolBarDropDownMenu(
            'Test',
            children=[
                ToolBarMenu('Test', page='test'),
            ],
            visible_callback=menu_for_unauthenticated_user,
        ).is_visible(session) is True

    def test_ToolBarDropDownMenu_is_visible_5(self) -> None:
        session = Session(user="Test")
        assert ToolBarDropDownMenu(
            'Test',
            children=[
                ToolBarMenu('Test', page='test'),
            ],
            visible_callback=menu_for_unauthenticated_user,
        ).is_visible(session) is False

    def test_ToolBarDropDownMenu_is_visible_6(self) -> None:
        session = Session(user="Test")
        assert ToolBarDropDownMenu(
            'Test',
            children=[
                ToolBarMenu(
                    'Test',
                    page='test',
                    visible_callback=menu_for_unauthenticated_user,
                ),
            ],
        ).is_visible(session) is False

    def test_ToolBarMenu_without_qs(self) -> None:
        with pytest.raises(MenuError):
            ToolBarMenu('Test')

    def test_ToolBarMenu(self, snapshot) -> None:
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)
        local.request = request
        snapshot.assert_match(
            ToolBarMenu('Test', page='test').render(myferet, session),
            'snapshot.html',
        )

    def test_ToolBarMenu_tooltip(self, snapshot) -> None:
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)
        local.request = request
        snapshot.assert_match(
            ToolBarMenu(
                'Test', page='test', tooltip="Test",
            ).render(myferet, session),
            'snapshot.html',
        )

    def test_ToolBarMenu_with_children_kwargs(self) -> None:
        with pytest.raises(MenuError):
            ToolBarMenu('Test', page='test', children=[])

    def test_ToolBarMenu_is_visible_1(self) -> None:
        session = Session()
        assert ToolBarMenu(
            'Test', page='test',
            visible_callback=menu_for_authenticated_user,
        ).is_visible(session) is False

    def test_ToolBarMenu_is_visible_2(self) -> None:
        session = Session(user="Test")
        assert ToolBarMenu(
            'Test', page='test',
            visible_callback=menu_for_authenticated_user,
        ).is_visible(session) is True

    def test_ToolBarMenu_is_visible_3(self) -> None:
        session = Session()
        assert ToolBarMenu(
            'Test', page='test',
            visible_callback=menu_for_unauthenticated_user,
        ).is_visible(session) is True

    def test_ToolBarMenu_is_visible_4(self) -> None:
        session = Session(user="Test")
        assert ToolBarMenu(
            'Test', page='test',
            visible_callback=menu_for_unauthenticated_user,
        ).is_visible(session) is False

    def test_ToolBarUrlMenu(self, snapshot) -> None:
        myferet = FeretUI()
        session = Session()
        snapshot.assert_match(
            ToolBarUrlMenu(
                'Test',
                'https://feretui.readthedocs.io/en/latest/',
            ).render(myferet, session),
            'snapshot.html',
        )

    def test_ToolBarUrlMenu_tooltip(self, snapshot) -> None:
        myferet = FeretUI()
        session = Session()
        snapshot.assert_match(
            ToolBarUrlMenu(
                'Test',
                'https://feretui.readthedocs.io/en/latest/',
                tooltip='Test',
            ).render(myferet, session),
            'snapshot.html',
        )

    def test_ToolBarUrlMenu_is_visible_1(self) -> None:
        session = Session()
        assert ToolBarUrlMenu(
            'Test',
            'https://feretui.readthedocs.io/en/latest/',
            visible_callback=menu_for_authenticated_user,
        ).is_visible(session) is False

    def test_ToolBarUrlMenu_is_visible_2(self) -> None:
        session = Session(user="Test")
        assert ToolBarUrlMenu(
            'Test',
            'https://feretui.readthedocs.io/en/latest/',
            visible_callback=menu_for_authenticated_user,
        ).is_visible(session) is True

    def test_ToolBarUrlMenu_is_visible_3(self) -> None:
        session = Session()
        assert ToolBarUrlMenu(
            'Test',
            'https://feretui.readthedocs.io/en/latest/',
            visible_callback=menu_for_unauthenticated_user,
        ).is_visible(session) is True

    def test_ToolBarUrlMenu_is_visible_4(self) -> None:
        session = Session(user="Test")
        assert ToolBarUrlMenu(
            'Test',
            'https://feretui.readthedocs.io/en/latest/',
            visible_callback=menu_for_unauthenticated_user,
        ).is_visible(session) is False

    def test_ToolBarButtonsMenu(self, snapshot) -> None:
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)
        local.request = request
        snapshot.assert_match(
            ToolBarButtonsMenu(
                [ToolBarButtonMenu('Test', page='test')],
            ).render(myferet, session),
            'snapshot.html',
        )

    def test_ToolBarButtonsMenu_cascad(self) -> None:
        with pytest.raises(MenuError):
            ToolBarButtonsMenu([
                ToolBarButtonsMenu([
                    ToolBarButtonMenu('Test', page='test'),
                ]),
            ])

    def test_ToolBarButtonsMenu_is_visible_1(self) -> None:
        session = Session()
        assert ToolBarButtonsMenu(
            [
                ToolBarButtonMenu('Test', page='test'),
            ],
            visible_callback=menu_for_authenticated_user,
        ).is_visible(session) is False

    def test_ToolBarButtonsMenu_is_visible_2(self) -> None:
        session = Session(user="Test")
        assert ToolBarButtonsMenu(
            [
                ToolBarButtonMenu('Test', page='test'),
            ],
            visible_callback=menu_for_authenticated_user,
        ).is_visible(session) is True

    def test_ToolBarButtonsMenu_is_visible_3(self) -> None:
        session = Session(user="Test")
        assert ToolBarButtonsMenu(
            [
                ToolBarButtonMenu(
                    'Test',
                    page='test',
                    visible_callback=menu_for_authenticated_user,
                ),
            ],
        ).is_visible(session) is True

    def test_ToolBarButtonsMenu_is_visible_4(self) -> None:
        session = Session()
        assert ToolBarButtonsMenu(
            [
                ToolBarButtonMenu('Test', page='test'),
            ],
            visible_callback=menu_for_unauthenticated_user,
        ).is_visible(session) is True

    def test_ToolBarButtonsMenu_is_visible_5(self) -> None:
        session = Session(user="Test")
        assert ToolBarButtonsMenu(
            [
                ToolBarButtonMenu('Test', page='test'),
            ],
            visible_callback=menu_for_unauthenticated_user,
        ).is_visible(session) is False

    def test_ToolBarButtonsMenu_is_visible_6(self) -> None:
        session = Session(user="Test")
        assert ToolBarButtonsMenu(
            [
                ToolBarButtonMenu(
                    'Test',
                    page='test',
                    visible_callback=menu_for_unauthenticated_user,
                ),
            ],
        ).is_visible(session) is False

    def test_ToolBarButtonMenu(self, snapshot) -> None:
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)
        local.request = request
        snapshot.assert_match(
            ToolBarButtonMenu('Test', page='test').render(myferet, session),
            'snapshot.html',
        )

    def test_ToolBarButtonMenu_tooltip(self, snapshot) -> None:
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)
        local.request = request
        snapshot.assert_match(
            ToolBarButtonMenu(
                'Test', page='test', tooltip="Test",
            ).render(myferet, session),
            'snapshot.html',
        )

    def test_ToolBarButtonMenu_is_visible(self) -> None:
        session = Session()
        assert ToolBarButtonMenu(
            'Test', page='test',
            visible_callback=menu_for_authenticated_user,
        ).is_visible(session) is False

    def test_ToolBarButtonMenu_with_children_kwargs(self) -> None:
        with pytest.raises(MenuError):
            ToolBarButtonMenu('Test', page='test', children=[])

    def test_ToolBarButtonUrlMenu(self, snapshot) -> None:
        myferet = FeretUI()
        session = Session()
        snapshot.assert_match(
            ToolBarButtonUrlMenu(
                'Test',
                'https://feretui.readthedocs.io/en/latest/',
            ).render(myferet, session),
            'snapshot.html',
        )

    def test_ToolBarButtonUrlMenu_tooltip(self, snapshot) -> None:
        myferet = FeretUI()
        session = Session()
        snapshot.assert_match(
            ToolBarButtonUrlMenu(
                'Test',
                'https://feretui.readthedocs.io/en/latest/',
                tooltip='Test',
            ).render(myferet, session),
            'snapshot.html',
        )

    def test_ToolBarButtonUrlMenu_is_visible(self) -> None:
        session = Session()
        assert ToolBarButtonUrlMenu(
            'Test',
            'https://feretui.readthedocs.io/en/latest/',
            visible_callback=menu_for_authenticated_user,
        ).is_visible(session) is False

    def test_AsideHeaderMenu_without_children(self) -> None:
        with pytest.raises(MenuError):
            AsideHeaderMenu('Test')

    def test_AsideHeaderMenu(self, snapshot) -> None:
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)
        local.request = request
        snapshot.assert_match(
            AsideHeaderMenu(
                'Test',
                children=[AsideMenu('Test', page='test')],
            ).render(myferet, session),
            'snapshot.html',
        )

    def test_AsideHeaderMenu_tooltip(self, snapshot) -> None:
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)
        local.request = request
        snapshot.assert_match(
            AsideHeaderMenu(
                'Test',
                tooltip='Test',
                children=[AsideMenu('Test', page='test')],
            ).render(myferet, session),
            'snapshot.html',
        )

    def test_AsideHeaderMenu_cascade(self, snapshot) -> None:
        myferet = FeretUI()
        session = Session()
        snapshot.assert_match(
            AsideHeaderMenu(
                'Test',
                children=[
                    AsideHeaderMenu(
                        'Test',
                        children=[AsideMenu('Test', page='test')],
                    ),
                ],
            ).render(myferet, session),
            'snapshot.html',
        )

    def test_AsideHeaderMenu_is_visible_1(self) -> None:
        session = Session()
        assert AsideHeaderMenu(
            'Test',
            children=[AsideMenu('Test', page='test')],
            visible_callback=menu_for_authenticated_user,
        ).is_visible(session) is False

    def test_AsideHeaderMenu_is_visible_2(self) -> None:
        session = Session()
        assert AsideHeaderMenu(
            'Test',
            children=[AsideMenu(
                'Test',
                page='test',
                visible_callback=menu_for_authenticated_user,
            )],
        ).is_visible(session) is False

    def test_AsideMenu_without_qs(self) -> None:
        with pytest.raises(MenuError):
            AsideMenu('Test')

    def test_AsideMenu(self, snapshot) -> None:
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)
        local.request = request
        snapshot.assert_match(
            AsideMenu('Test', page='test').render(myferet, session),
            'snapshot.html',
        )

    def test_AsideMenu_tooltip(self, snapshot) -> None:
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)
        local.request = request
        snapshot.assert_match(
            AsideMenu(
                'Test', page='test', tooltip="Test",
            ).render(myferet, session),
            'snapshot.html',
        )

    def test_AsideMenu_with_children_kwargs(self) -> None:
        with pytest.raises(MenuError):
            AsideMenu('Test', page='test', children=[])

    def test_AsideMenu_is_visible(self) -> None:
        session = Session()
        assert AsideMenu(
            'Test',
            page='test',
            visible_callback=menu_for_authenticated_user,
        ).is_visible(session) is False

    def test_AsideUrlMenu(self, snapshot) -> None:
        myferet = FeretUI()
        session = Session()
        snapshot.assert_match(
            AsideUrlMenu(
                'Test',
                'https://feretui.readthedocs.io/en/latest/',
            ).render(myferet, session),
            'snapshot.html',
        )

    def test_AsideUrlMenu_tooltip(self, snapshot) -> None:
        myferet = FeretUI()
        session = Session()
        snapshot.assert_match(
            AsideUrlMenu(
                'Test',
                'https://feretui.readthedocs.io/en/latest/',
                tooltip='Test',
            ).render(myferet, session),
            'snapshot.html',
        )

    def test_AsideUrlMenu_is_visible(self) -> None:
        session = Session()
        assert AsideUrlMenu(
            'test',
            'https://feretui.readthedocs.io/en/latest/',
            visible_callback=menu_for_authenticated_user,
        ).is_visible(session) is False
