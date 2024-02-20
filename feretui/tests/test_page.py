import pytest
from feretui.feretui import FeretUI
from feretui.session import Session
from feretui.pages import page_404, page_forbidden, homepage


class TestPage:

    def test_404(self):
        myferet = FeretUI()
        session = Session()
        res = page_404(myferet, session, {'page': 'test'})
        assert res

    def test_forbidden(self):
        myferet = FeretUI()
        session = Session()
        res = page_forbidden(myferet, session, {'page': 'test'})
        assert res

    def test_homepage(self):
        myferet = FeretUI()
        session = Session()
        res = homepage(myferet, session, {})
        assert res
