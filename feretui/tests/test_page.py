# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest

from feretui.exceptions import PageError, UnexistingResourceError
from feretui.helper import page_for_authenticated_user_or_goto
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
from feretui.menus import AsideMenu, ToolBarMenu
from feretui.resources.resource import Resource


class TestPage:

    def test_404(self, snapshot, feretui, session) -> None:
        snapshot.assert_match(
            page_404(feretui, session, {'page': ['test']}),
            'snapshot.html',
        )

    def test_forbidden(self, snapshot, feretui, session) -> None:
        snapshot.assert_match(
            page_forbidden(feretui, session, {'page': ['test']}),
            'snapshot.html',
        )

    def test_homepage(self, snapshot, feretui, session) -> None:
        snapshot.assert_match(
            homepage(feretui, session, {}),
            'snapshot.html',
        )

    def test_sitemap_1(self, snapshot, feretui, session) -> None:
        feretui.register_aside_menus(
            'my-aside',
            [AsideMenu('Test', page='test')])
        feretui.register_toolbar_left_menus([
            ToolBarMenu(
                'Test',
                page='aside-menu',
                aside='my-aside',
                aside_page='test'
            )
        ])
        snapshot.assert_match(
            sitemap(feretui, session, {}),
            'snapshot.html',
        )

    def test_sitemap_2(self, snapshot, feretui, authenticated_session) -> None:
        feretui.register_aside_menus(
            'my-aside',
            [AsideMenu('Test', page='test')])
        feretui.register_toolbar_left_menus([
            ToolBarMenu(
                'Test',
                page='aside-menu',
                aside='my-aside',
                aside_page='test'
            )
        ])
        snapshot.assert_match(
            sitemap(feretui, authenticated_session, {}),
            'snapshot.html',
        )

    def test_static_page(self, feretui, session) -> None:
        feretui.register_template_from_str(
            '''
                <template id="my-static-page">
                    <div>Test</div>
                </template>
            ''',
        )
        res = static_page('my-static-page')(feretui, session, {})
        assert res == '<div>\n Test\n</div>'

    def test_static_page_ko(self, feretui, session) -> None:
        with pytest.raises(PageError):
            static_page('my-static_page')(feretui, session, {})

    def test_aside(self, snapshot, feretui, session) -> None:
        snapshot.assert_match(aside_menu(
            feretui, session, {'aside': ['test']}),
            'snapshot.html',
        )

    def test_aside_without_requiremend(self, feretui, session) -> None:
        with pytest.raises(PageError):
            aside_menu(feretui, session, {})

    def test_login_1(self, snapshot, feretui, session, frequest) -> None:
        snapshot.assert_match(login(feretui, session, {}), 'snapshot.html')

    def test_login_2(self, feretui, authenticated_session) -> None:
        assert (
            login(feretui, authenticated_session, {})
            == page_forbidden(feretui, authenticated_session, {})
        )

    def test_signup_1(self, snapshot, feretui, session, frequest) -> None:
        snapshot.assert_match(signup(feretui, session, {}), 'snapshot.html')

    def test_signup_2(self, feretui, authenticated_session) -> None:
        assert (
            signup(feretui, authenticated_session, {})
            == page_forbidden(feretui, authenticated_session, {})
        )

    def test_resource_1(self, feretui, session) -> None:
        with pytest.raises(PageError):
            resource_page(feretui, session, {})

    def test_resource_2(self, feretui, session) -> None:
        with pytest.raises(UnexistingResourceError):
            resource_page(feretui, session, {'resource': ['test']})

    def test_resource_3(self, snapshot, feretui, session) -> None:

        @feretui.register_resource()
        class MyResource(Resource):
            code = 'test'
            label = 'Test'

        snapshot.assert_match(
            resource_page(feretui, session, {'resource': ['test']}),
            'snapshot.html',
        )

    def test_resource_4(self, snapshot, feretui, session) -> None:

        @feretui.register_resource()
        class MyResource(Resource):
            code = 'test'
            label = 'Test'
            page_visibility = staticmethod(
                page_for_authenticated_user_or_goto(page_forbidden))

        snapshot.assert_match(
            resource_page(feretui, session, {'resource': ['test']}),
            'snapshot.html',
        )

    def test_resource_5(self, snapshot, feretui, session) -> None:

        @feretui.register_resource()
        class MyResource(Resource):
            code = 'test'
            label = 'Test'
            page_visibility = None

        snapshot.assert_match(
            resource_page(
                feretui,
                session,
                {'resource': ['test'], 'view': ['test']},
            ),
            'snapshot.html',
        )
