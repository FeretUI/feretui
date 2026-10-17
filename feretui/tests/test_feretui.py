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

from feretui.exceptions import (
    MenuError,
    UnexistingActionError,
    UnexistingResourceError,
)
from feretui.feretui import FeretUI
from feretui.form import FeretUIForm
from feretui.menus import (
    AsideHeaderMenu,
    AsideMenu,
    Menu,
    ToolBarButtonMenu,
    ToolBarDividerMenu,
    ToolBarDropDownMenu,
    ToolBarMenu,
)
from feretui.pages import homepage, page_404
from feretui.request import Request
from feretui.resources.resource import Resource
from feretui.response import Response
from feretui.session import Session
from feretui.helper import menu_for_unauthenticated_user


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

    def test_get_title_static(self) -> None:
        """Test get_title with static string."""
        myferet = FeretUI(title="Custom Title")
        assert myferet.get_title() == "Custom Title"

    def test_get_title_callable(self) -> None:
        """Test get_title with callable."""
        def dynamic_title(feret: FeretUI, request: Request | None) -> str:
            if request and "page" in request.query:
                return f"{request.query['page'][0]} - My App"
            return "Default Title"

        myferet = FeretUI(title=dynamic_title)
        assert myferet.get_title() == "Default Title"
        session = Session()
        req = Request(session=session, querystring="page=login")
        assert myferet.get_title(req) == "login - My App"
        res = myferet.render(req)
        assert "login - My App" in res.body

    def test_get_static_file_path(self) -> None:
        """Test get_static_file_path."""
        myferet = FeretUI()
        assert (
            myferet.get_static_file_path('pico.css')
            == myferet.statics['pico.css']
        )

    def test_theme_url_and_static_file_path(self) -> None:
        """Test theme registration, URL resolution, and static files."""
        myferet = FeretUI()
        session_orange = Session(theme='orange')
        assert myferet.get_theme_url(session_orange) == "/feretui/static/orange.css"
        assert myferet.get_static_file_path("orange.css") == myferet.statics["orange.css"]
        assert myferet.get_static_file_path("orange") == myferet.statics["orange"]

        session_unknown = Session(theme='unknown_theme')
        assert myferet.get_theme_url(session_unknown) == "/feretui/static/default.css"

        # Test overwriting existing theme logs warning
        myferet.register_theme('orange', myferet.statics['orange'])

    def test_render_with_color_scheme(self) -> None:
        """Test rendering with explicit color_scheme."""
        myferet = FeretUI()
        session_light = Session(color_scheme='light')
        req_light = Request(session=session_light)
        res_light = myferet.render(req_light)
        assert '<html data-theme="light" lang="en">' in res_light.body

        session_dark = Session(color_scheme='dark')
        req_dark = Request(session=session_dark)
        res_dark = myferet.render(req_dark)
        assert '<html data-theme="dark" lang="en">' in res_dark.body

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

    def test_register_auth_menus_1(self, snapshot) -> None:
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)
        snapshot.assert_match(myferet.render(request).body, 'before.html')
        myferet.register_auth_menus([ToolBarButtonMenu(
            'Test', page='test', visible_callback=menu_for_unauthenticated_user
        )])
        snapshot.assert_match(myferet.render(request).body, 'after.html')

    def test_register_auth_menus_2(self, snapshot) -> None:
        myferet = FeretUI()
        with pytest.raises(MenuError):
            myferet.register_auth_menus([ToolBarMenu('Test', page='test')])

    def test_register_user_menus_1(self) -> None:
        myferet = FeretUI()
        myferet.register_user_menus([ToolBarMenu('Test', page='test')])
        assert len(myferet.menus['user']) == 1
        assert len(myferet.translation.menus) == 1

    def test_register_resource(self) -> None:
        myferet = FeretUI()

        class Test(Resource):
            code = 'test'
            label = 'Test'

        myferet.register_resource()(Test)
        assert myferet.resources['test']
        assert len(myferet.translation.resources) == 1

    def test_get_resource_1(self) -> None:
        myferet = FeretUI()
        myferet.resources['test'] = 'test'
        assert myferet.get_resource('test') == 'test'

    def test_get_resource_2(self) -> None:
        myferet = FeretUI()
        with pytest.raises(UnexistingResourceError):
            myferet.get_resource('test')

    def test_pure_python_css_compressor(self) -> None:
        from io import StringIO
        from feretui.feretui import PurePythonCSSCompressor

        css = "/* comment */ body { color: red; margin: 0px ; } "
        compressed = PurePythonCSSCompressor.compile(css)
        assert compressed == "body{color:red;margin:0px;}"

        stream = StringIO("/* header */ h1 { font-size: 2rem ; }")
        compressed_stream = PurePythonCSSCompressor.compile(stream)
        assert compressed_stream == "h1{font-size:2rem;}"

        debug_css = "/* keep */ a { color: blue; }"
        assert PurePythonCSSCompressor.compile(debug_css, debug=True) == debug_css

    def test_register_plugins_from_entrypoint(self, monkeypatch) -> None:
        """Test plugin auto-discovery via entry points."""

        class MockEntryPoint:
            def __init__(self, name, target):
                self.name = name
                self.target = target

            def load(self):
                return self.target

        class SetupPlugin:
            def setup(self, feretui):
                self.called = True

        def callable_plugin(feretui):
            return "callable_loaded"

        plain_plugin = "plain_value"

        eps = [
            MockEntryPoint("setup_plugin", SetupPlugin),
            MockEntryPoint("callable_plugin", callable_plugin),
            MockEntryPoint("plain_plugin", plain_plugin),
        ]

        def fake_entry_points(group=None):
            if group == "feretui.plugins":
                return eps
            return []

        monkeypatch.setattr("feretui.feretui.entry_points", fake_entry_points)
        feret = FeretUI()
        assert "setup_plugin" in feret.plugins
        assert feret.plugins["setup_plugin"].called is True
        assert feret.plugins["callable_plugin"] == "callable_loaded"
        assert feret.plugins["plain_plugin"] == "plain_value"


