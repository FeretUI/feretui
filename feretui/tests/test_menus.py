# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest

from feretui.exceptions import MenuError
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


class TestMenu:

    def test_ToolBarDividerMenu(self, feretui, session) -> None:
        assert ToolBarDividerMenu().render(
            feretui, session) == '<hr class="navbar-divider">'

    def test_ToolBarDividerMenu_is_visible_1(self, session) -> None:
        assert ToolBarDividerMenu(
            visible_callback=menu_for_authenticated_user,
        ).is_visible(session) is False

    def test_ToolBarDividerMenu_is_visible_2(
        self, authenticated_session
    ) -> None:
        assert ToolBarDividerMenu(
            visible_callback=menu_for_authenticated_user,
        ).is_visible(authenticated_session) is True

    def test_ToolBarDividerMenu_is_visible_3(self, session) -> None:
        assert ToolBarDividerMenu(
            visible_callback=menu_for_unauthenticated_user,
        ).is_visible(session) is True

    def test_ToolBarDividerMenu_is_visible_4(
        self, authenticated_session
    ) -> None:
        assert ToolBarDividerMenu(
            visible_callback=menu_for_unauthenticated_user,
        ).is_visible(authenticated_session) is False

    def test_ToolBarDropDownMenu_without_children(self) -> None:
        with pytest.raises(MenuError):
            ToolBarDropDownMenu('Test')

    def test_ToolBarDropDownMenu(
        self, snapshot, feretui, session, frequest
    ) -> None:
        snapshot.assert_match(
            ToolBarDropDownMenu(
                'Test',
                children=[ToolBarMenu('Test', page='test')],
            ).render(feretui, session),
            'snapshot.html',
        )

    def test_ToolBarDropDownMenu_description(
        self, snapshot, feretui, session, frequest,
    ) -> None:
        snapshot.assert_match(
            ToolBarDropDownMenu(
                'Test',
                description='Test',
                children=[ToolBarMenu('Test', page='test')],
            ).render(feretui, session),
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

    def test_ToolBarDropDownMenu_is_visible_1(self, session) -> None:
        assert ToolBarDropDownMenu(
            'Test',
            children=[
                ToolBarMenu('Test', page='test'),
            ],
            visible_callback=menu_for_authenticated_user,
        ).is_visible(session) is False

    def test_ToolBarDropDownMenu_is_visible_2(
        self, authenticated_session,
    ) -> None:
        assert ToolBarDropDownMenu(
            'Test',
            children=[
                ToolBarMenu('Test', page='test'),
            ],
            visible_callback=menu_for_authenticated_user,
        ).is_visible(authenticated_session) is True

    def test_ToolBarDropDownMenu_is_visible_3(
        self, authenticated_session
    ) -> None:
        assert ToolBarDropDownMenu(
            'Test',
            children=[
                ToolBarMenu(
                    'Test',
                    page='test',
                    visible_callback=menu_for_authenticated_user,
                ),
            ],
        ).is_visible(authenticated_session) is True

    def test_ToolBarDropDownMenu_is_visible_4(self, session) -> None:
        assert ToolBarDropDownMenu(
            'Test',
            children=[
                ToolBarMenu('Test', page='test'),
            ],
            visible_callback=menu_for_unauthenticated_user,
        ).is_visible(session) is True

    def test_ToolBarDropDownMenu_is_visible_5(
        self, authenticated_session
    ) -> None:
        assert ToolBarDropDownMenu(
            'Test',
            children=[
                ToolBarMenu('Test', page='test'),
            ],
            visible_callback=menu_for_unauthenticated_user,
        ).is_visible(authenticated_session) is False

    def test_ToolBarDropDownMenu_is_visible_6(
        self, authenticated_session
    ) -> None:
        assert ToolBarDropDownMenu(
            'Test',
            children=[
                ToolBarMenu(
                    'Test',
                    page='test',
                    visible_callback=menu_for_unauthenticated_user,
                ),
            ],
        ).is_visible(authenticated_session) is False

    def test_ToolBarMenu_without_qs(self) -> None:
        with pytest.raises(MenuError):
            ToolBarMenu('Test')

    def test_ToolBarMenu(self, snapshot, feretui, session, frequest) -> None:
        snapshot.assert_match(
            ToolBarMenu('Test', page='test').render(feretui, session),
            'snapshot.html',
        )

    def test_ToolBarMenu_description(
        self, snapshot, feretui, session, frequest
    ) -> None:
        snapshot.assert_match(
            ToolBarMenu(
                'Test', page='test', description="Test",
            ).render(feretui, session),
            'snapshot.html',
        )

    def test_ToolBarMenu_with_children_kwargs(self) -> None:
        with pytest.raises(MenuError):
            ToolBarMenu('Test', page='test', children=[])

    def test_ToolBarMenu_is_visible_1(self, session) -> None:
        assert ToolBarMenu(
            'Test', page='test',
            visible_callback=menu_for_authenticated_user,
        ).is_visible(session) is False

    def test_ToolBarMenu_is_visible_2(self, authenticated_session) -> None:
        assert ToolBarMenu(
            'Test', page='test',
            visible_callback=menu_for_authenticated_user,
        ).is_visible(authenticated_session) is True

    def test_ToolBarMenu_is_visible_3(self, session) -> None:
        assert ToolBarMenu(
            'Test', page='test',
            visible_callback=menu_for_unauthenticated_user,
        ).is_visible(session) is True

    def test_ToolBarMenu_is_visible_4(self, authenticated_session) -> None:
        assert ToolBarMenu(
            'Test', page='test',
            visible_callback=menu_for_unauthenticated_user,
        ).is_visible(authenticated_session) is False

    def test_ToolBarUrlMenu(self, snapshot, feretui, session) -> None:
        snapshot.assert_match(
            ToolBarUrlMenu(
                'Test',
                'https://feretui.readthedocs.io/en/latest/',
            ).render(feretui, session),
            'snapshot.html',
        )

    def test_ToolBarUrlMenu_description(
        self, snapshot, feretui, session
    ) -> None:
        snapshot.assert_match(
            ToolBarUrlMenu(
                'Test',
                'https://feretui.readthedocs.io/en/latest/',
                description='Test',
            ).render(feretui, session),
            'snapshot.html',
        )

    def test_ToolBarUrlMenu_is_visible_1(self, session) -> None:
        assert ToolBarUrlMenu(
            'Test',
            'https://feretui.readthedocs.io/en/latest/',
            visible_callback=menu_for_authenticated_user,
        ).is_visible(session) is False

    def test_ToolBarUrlMenu_is_visible_2(self, authenticated_session) -> None:
        assert ToolBarUrlMenu(
            'Test',
            'https://feretui.readthedocs.io/en/latest/',
            visible_callback=menu_for_authenticated_user,
        ).is_visible(authenticated_session) is True

    def test_ToolBarUrlMenu_is_visible_3(self, session) -> None:
        assert ToolBarUrlMenu(
            'Test',
            'https://feretui.readthedocs.io/en/latest/',
            visible_callback=menu_for_unauthenticated_user,
        ).is_visible(session) is True

    def test_ToolBarUrlMenu_is_visible_4(self, authenticated_session) -> None:
        assert ToolBarUrlMenu(
            'Test',
            'https://feretui.readthedocs.io/en/latest/',
            visible_callback=menu_for_unauthenticated_user,
        ).is_visible(authenticated_session) is False

    def test_ToolBarButtonsMenu(
        self, snapshot, feretui, session, frequest
    ) -> None:
        snapshot.assert_match(
            ToolBarButtonsMenu(
                [ToolBarButtonMenu('Test', page='test')],
            ).render(feretui, session),
            'snapshot.html',
        )

    def test_ToolBarButtonsMenu_cascad(self) -> None:
        with pytest.raises(MenuError):
            ToolBarButtonsMenu([
                ToolBarButtonsMenu([
                    ToolBarButtonMenu('Test', page='test'),
                ]),
            ])

    def test_ToolBarButtonsMenu_is_visible_1(self, session) -> None:
        assert ToolBarButtonsMenu(
            [
                ToolBarButtonMenu('Test', page='test'),
            ],
            visible_callback=menu_for_authenticated_user,
        ).is_visible(session) is False

    def test_ToolBarButtonsMenu_is_visible_2(
        self, authenticated_session
    ) -> None:
        assert ToolBarButtonsMenu(
            [
                ToolBarButtonMenu('Test', page='test'),
            ],
            visible_callback=menu_for_authenticated_user,
        ).is_visible(authenticated_session) is True

    def test_ToolBarButtonsMenu_is_visible_3(
        self, authenticated_session
    ) -> None:
        assert ToolBarButtonsMenu(
            [
                ToolBarButtonMenu(
                    'Test',
                    page='test',
                    visible_callback=menu_for_authenticated_user,
                ),
            ],
        ).is_visible(authenticated_session) is True

    def test_ToolBarButtonsMenu_is_visible_4(self, session) -> None:
        assert ToolBarButtonsMenu(
            [
                ToolBarButtonMenu('Test', page='test'),
            ],
            visible_callback=menu_for_unauthenticated_user,
        ).is_visible(session) is True

    def test_ToolBarButtonsMenu_is_visible_5(
        self, authenticated_session
    ) -> None:
        assert ToolBarButtonsMenu(
            [
                ToolBarButtonMenu('Test', page='test'),
            ],
            visible_callback=menu_for_unauthenticated_user,
        ).is_visible(authenticated_session) is False

    def test_ToolBarButtonsMenu_is_visible_6(
        self, authenticated_session
    ) -> None:
        assert ToolBarButtonsMenu(
            [
                ToolBarButtonMenu(
                    'Test',
                    page='test',
                    visible_callback=menu_for_unauthenticated_user,
                ),
            ],
        ).is_visible(authenticated_session) is False

    def test_ToolBarButtonMenu(
        self, snapshot, feretui, session, frequest
    ) -> None:
        snapshot.assert_match(
            ToolBarButtonMenu('Test', page='test').render(feretui, session),
            'snapshot.html',
        )

    def test_ToolBarButtonMenu_desciption(
        self, snapshot, feretui, session, frequest
    ) -> None:
        snapshot.assert_match(
            ToolBarButtonMenu(
                'Test', page='test', description="Test",
            ).render(feretui, session),
            'snapshot.html',
        )

    def test_ToolBarButtonMenu_is_visible(self, session) -> None:
        assert ToolBarButtonMenu(
            'Test', page='test',
            visible_callback=menu_for_authenticated_user,
        ).is_visible(session) is False

    def test_ToolBarButtonMenu_with_children_kwargs(self) -> None:
        with pytest.raises(MenuError):
            ToolBarButtonMenu('Test', page='test', children=[])

    def test_ToolBarButtonUrlMenu(self, snapshot, feretui, session) -> None:
        snapshot.assert_match(
            ToolBarButtonUrlMenu(
                'Test',
                'https://feretui.readthedocs.io/en/latest/',
            ).render(feretui, session),
            'snapshot.html',
        )

    def test_ToolBarButtonUrlMenu_description(
        self, snapshot, feretui, session
    ) -> None:
        snapshot.assert_match(
            ToolBarButtonUrlMenu(
                'Test',
                'https://feretui.readthedocs.io/en/latest/',
                description='Test',
            ).render(feretui, session),
            'snapshot.html',
        )

    def test_ToolBarButtonUrlMenu_is_visible(self, session) -> None:
        assert ToolBarButtonUrlMenu(
            'Test',
            'https://feretui.readthedocs.io/en/latest/',
            visible_callback=menu_for_authenticated_user,
        ).is_visible(session) is False

    def test_AsideHeaderMenu_without_children(self) -> None:
        with pytest.raises(MenuError):
            AsideHeaderMenu('Test')

    def test_AsideHeaderMenu(
        self, snapshot, feretui, session, frequest
    ) -> None:
        snapshot.assert_match(
            AsideHeaderMenu(
                'Test',
                children=[AsideMenu('Test', page='test')],
            ).render(feretui, session),
            'snapshot.html',
        )

    def test_AsideHeaderMenu_description(
        self, snapshot, feretui, session, frequest
    ) -> None:
        snapshot.assert_match(
            AsideHeaderMenu(
                'Test',
                description='Test',
                children=[AsideMenu('Test', page='test')],
            ).render(feretui, session),
            'snapshot.html',
        )

    def test_AsideHeaderMenu_cascade(
        self, snapshot, feretui, session, frequest
    ) -> None:
        snapshot.assert_match(
            AsideHeaderMenu(
                'Test',
                children=[
                    AsideHeaderMenu(
                        'Test',
                        children=[AsideMenu('Test', page='test')],
                    ),
                ],
            ).render(feretui, session),
            'snapshot.html',
        )

    def test_AsideHeaderMenu_is_visible_1(self, session) -> None:
        assert AsideHeaderMenu(
            'Test',
            children=[AsideMenu('Test', page='test')],
            visible_callback=menu_for_authenticated_user,
        ).is_visible(session) is False

    def test_AsideHeaderMenu_is_visible_2(self, session) -> None:
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

    def test_AsideMenu(self, snapshot, feretui, session, frequest) -> None:
        snapshot.assert_match(
            AsideMenu('Test', page='test').render(feretui, session),
            'snapshot.html',
        )

    def test_AsideMenu_description(
        self, snapshot, feretui, session, frequest
    ) -> None:
        snapshot.assert_match(
            AsideMenu(
                'Test', page='test', description="Test",
            ).render(feretui, session),
            'snapshot.html',
        )

    def test_AsideMenu_with_children_kwargs(self) -> None:
        with pytest.raises(MenuError):
            AsideMenu('Test', page='test', children=[])

    def test_AsideMenu_is_visible(self, session) -> None:
        assert AsideMenu(
            'Test',
            page='test',
            visible_callback=menu_for_authenticated_user,
        ).is_visible(session) is False

    def test_AsideUrlMenu(self, snapshot, feretui, session) -> None:
        snapshot.assert_match(
            AsideUrlMenu(
                'Test',
                'https://feretui.readthedocs.io/en/latest/',
            ).render(feretui, session),
            'snapshot.html',
        )

    def test_AsideUrlMenu_description(
        self, snapshot, feretui, session
    ) -> None:
        snapshot.assert_match(
            AsideUrlMenu(
                'Test',
                'https://feretui.readthedocs.io/en/latest/',
                description='Test',
            ).render(feretui, session),
            'snapshot.html',
        )

    def test_AsideUrlMenu_is_visible(self, session) -> None:
        assert AsideUrlMenu(
            'test',
            'https://feretui.readthedocs.io/en/latest/',
            visible_callback=menu_for_authenticated_user,
        ).is_visible(session) is False
