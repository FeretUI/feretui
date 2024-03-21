# This file is a part of the FeretUI project
#
#    Copyright (C) 2023-2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Unittest.

with pytest.
"""
import pytest  # noqa: F401

from feretui.exceptions import MenuError, UnexistingActionError
from feretui.feretui import FeretUI
from feretui.form import FeretUIForm
from feretui.menus import (
    AsideHeaderMenu,
    AsideMenu,
    Menu,
    ToolBarDividerMenu,
    ToolBarDropDownMenu,
    ToolBarMenu,
    ToolBarButtonMenu,
)
from feretui.pages import homepage, page_404
from feretui.request import Request
from feretui.response import Response
from feretui.session import Session


class TestFeretUI:
    """Test of FeretUI class."""

    def test_render(self, snapshot) -> None:
        """Test the main render without any options."""
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)
        response = myferet.render(request)
        assert isinstance(response, Response)
        snapshot.assert_match(response.body, 'snapshot.html')

    def test_get_static_file_path(self) -> None:
        """Test get_static_file_path."""
        myferet = FeretUI()
        assert (
            myferet.get_static_file_path('bulma.css')
            == myferet.statics['bulma.css']
        )

    def test_register_and_execute_action(self) -> None:
        """Test get_static_file_path."""
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)

        @myferet.register_action
        def my_action(feretui, request):
            return id(feretui)

        assert myferet.execute_action(request, 'my_action') == id(myferet)

    def test_execute_unexisting_action(self) -> None:
        """Test get_static_file_path."""
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)

        with pytest.raises(UnexistingActionError):
            myferet.execute_action(request, 'my_action')

    def test_register_page(self) -> None:
        def page(myferet, mysession) -> None:
            pass

        myferet = FeretUI()

        myferet.register_page()(page)
        assert myferet.pages['page'] is page

    def test_register_page_with_name(self) -> None:
        def page(myferet, mysession) -> None:
            pass

        myferet = FeretUI()

        myferet.register_page(name='mypage')(page)
        assert myferet.pages['mypage'] is page

    def test_register_page_with_template(self) -> None:
        def page(myferet, mysession) -> None:
            pass

        myferet = FeretUI()
        session = Session()

        myferet.register_page(
            templates=["""
                <template id="test">
                  <div>test</div>
                </template>
            """],
        )(page)
        assert myferet.pages['page'] is page
        assert myferet.render_template(session, 'test')

    def test_register_page_with_forms(self) -> None:
        def page(myferet, mysession) -> None:
            pass

        myferet = FeretUI()

        myferet.register_page(forms=[FeretUIForm])(page)
        assert len(myferet.translation.forms) == 1

    def test_register_static_page(self) -> None:
        def page(myferet, mysession) -> None:
            pass

        myferet = FeretUI()
        session = Session()

        myferet.register_static_page('my-static-page', "<div>test</div>")
        assert myferet.pages['my-static-page']
        assert myferet.render_template(session, 'my-static-page')
        assert myferet.get_page('my-static-page')(myferet, session, {})

    def test_register_static_page2(self) -> None:
        def page(myferet, mysession) -> None:
            pass

        myferet = FeretUI()
        session = Session()

        myferet.register_static_page(
            'my-static-page',
            "<div>test</div>",
            templates=('<template id="test"><div>Test</div></template>',),
        )
        assert myferet.pages['my-static-page']
        assert myferet.render_template(session, 'my-static-page')
        assert myferet.get_page('my-static-page')(myferet, session, {})

    def test_get_page(self) -> None:
        myferet = FeretUI()
        assert myferet.get_page('homepage') is homepage

    def test_get_page_404(self) -> None:
        myferet = FeretUI()
        assert myferet.get_page('homepage2') is page_404

    def test_register_toolbar_left_menus_1(self) -> None:
        myferet = FeretUI()
        myferet.register_toolbar_left_menus([ToolBarMenu('Test', page='test')])
        assert len(myferet.menus['left']) == 1
        assert len(myferet.translation.menus) == 1

    def test_register_toolbar_left_menus_2(self) -> None:
        myferet = FeretUI()
        myferet.register_toolbar_left_menus([
            ToolBarMenu('Test', page='test'),
            ToolBarMenu('Test', page='test'),
        ])
        assert len(myferet.menus['left']) == 2
        assert len(myferet.translation.menus) == 2

    def test_register_toolbar_left_menus_with_not_ToolbarMenu(self) -> None:
        myferet = FeretUI()
        with pytest.raises(MenuError):
            myferet.register_toolbar_left_menus([Menu('Test', page='test')])

    def test_register_toolbar_left_menus_divider(self) -> None:
        myferet = FeretUI()
        with pytest.raises(MenuError):
            myferet.register_toolbar_left_menus([ToolBarDividerMenu()])

    def test_register_toolbar_left_menus_dropdown(self) -> None:
        myferet = FeretUI()
        myferet.register_toolbar_left_menus([
            ToolBarDropDownMenu(
                'Test', children=[ToolBarMenu('Test', page='test')]),
        ])
        assert len(myferet.menus['left']) == 1
        assert len(myferet.translation.menus) == 2

    def test_register_toolbar_right_menus_1(self) -> None:
        myferet = FeretUI()
        myferet.register_toolbar_right_menus(
            [ToolBarMenu('Test', page='test')])
        assert len(myferet.menus['right']) == 1
        assert len(myferet.translation.menus) == 1

    def test_register_toolbar_right_menus_2(self) -> None:
        myferet = FeretUI()
        myferet.register_toolbar_right_menus([
            ToolBarMenu('Test', page='test'),
            ToolBarMenu('Test', page='test'),
        ])
        assert len(myferet.menus['right']) == 2
        assert len(myferet.translation.menus) == 2

    def test_register_toolbar_right_menus_with_not_ToolbarMenu(self) -> None:
        myferet = FeretUI()
        with pytest.raises(MenuError):
            myferet.register_toolbar_right_menus([Menu('Test', page='test')])

    def test_register_toolbar_right_menus_divider(self) -> None:
        myferet = FeretUI()
        with pytest.raises(MenuError):
            myferet.register_toolbar_right_menus([ToolBarDividerMenu()])

    def test_register_toolbar_right_menus_dropdown(self) -> None:
        myferet = FeretUI()
        myferet.register_toolbar_right_menus([
            ToolBarDropDownMenu('Test', children=[
                ToolBarMenu('Test', page='test'),
            ]),
        ])
        assert len(myferet.menus['right']) == 1
        assert len(myferet.translation.menus) == 2

    def test_register_aside_menus_1(self) -> None:
        myferet = FeretUI()
        myferet.register_aside_menus(
            'my-aside',
            [AsideMenu('Test', page='test')])
        assert len(myferet.asides['my-aside']) == 1
        assert len(myferet.translation.menus) == 1

    def test_register_aside_menus_2(self) -> None:
        myferet = FeretUI()
        myferet.register_aside_menus(
            'my-aside',
            [
                AsideMenu('Test', page='test'),
                AsideMenu('Test', page='test'),
            ],
        )
        assert len(myferet.asides['my-aside']) == 2
        assert len(myferet.translation.menus) == 2

    def test_register_aside_menus_with_not_AsideMenu(self) -> None:
        myferet = FeretUI()
        with pytest.raises(MenuError):
            myferet.register_aside_menus(
                'my-aside',
                [Menu('Test', page='test')],
            )

    def test_register_aside_menus_header(self) -> None:
        myferet = FeretUI()
        myferet.register_aside_menus(
            'my-aside',
            [
                AsideHeaderMenu('Test', [
                    AsideMenu('Test', page='test'),
                ]),
            ],
        )
        assert len(myferet.asides['my-aside']) == 1
        assert len(myferet.translation.menus) == 2

    def test_register_form(self) -> None:
        myferet = FeretUI()

        @myferet.register_form()
        class MyForm(FeretUIForm):
            pass

        assert len(myferet.translation.forms) == 1

    def test_register_auth_menus_1(self, snapshot):
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)
        snapshot.assert_match(myferet.render(request).body, 'before.html')
        myferet.register_auth_menus([ToolBarButtonMenu('Test', page='test')])
        snapshot.assert_match(myferet.render(request).body, 'after.html')

    def test_register_auth_menus_2(self, snapshot):
        myferet = FeretUI()
        with pytest.raises(MenuError):
            myferet.register_auth_menus([ToolBarMenu('Test', page='test')])

    def test_register_user_menus_1(self) -> None:
        myferet = FeretUI()
        myferet.register_user_menus([ToolBarMenu('Test', page='test')])
        assert len(myferet.menus['user']) == 1
        assert len(myferet.translation.menus) == 1
