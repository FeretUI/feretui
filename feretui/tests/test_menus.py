import pytest
from feretui.exceptions import MenuError
from feretui.feretui import FeretUI
from feretui.menus import (
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
        assert ToolBarDividerMenu().render(myferet, session)

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
        ).render(myferet, session)

    def test_ToolBarDropDownMenu_tooltip(self):
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)
        local.request = request
        assert ToolBarDropDownMenu(
            'Test',
            tooltip='Test',
            children=[ToolBarMenu('Test', page='test')]
        ).render(myferet, session)

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
        assert ToolBarMenu('Test', page='test').render(myferet, session)

    def test_ToolBarMenu_tooltip(self):
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)
        local.request = request
        assert ToolBarMenu(
            'Test', page='test', tooltip="Test").render(myferet, session)

    def test_ToolBarMenu_with_children_kwargs(self):
        with pytest.raises(MenuError):
            ToolBarMenu('Test', page='test', children=[])

    def test_ToolBarUrlMenu(self):
        myferet = FeretUI()
        session = Session()
        assert ToolBarUrlMenu(
            'Test',
            'https://feretui.readthedocs.io/en/latest/',
        ).render(myferet, session)

    def test_ToolBarUrlMenu_tooltip(self):
        myferet = FeretUI()
        session = Session()
        assert ToolBarUrlMenu(
            'Test',
            'https://feretui.readthedocs.io/en/latest/',
            tooltip='Test',
        ).render(myferet, session)
