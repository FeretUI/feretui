import pytest
from feretui.exceptions import ActionError
from feretui.feretui import FeretUI
from feretui.session import Session
from feretui.actions import render, goto
from feretui.pages import homepage
from feretui.request import Request


class TestAction:

    def test_render(self):
        myferet = FeretUI()
        session = Session()
        request = Request(method=Request.GET, session=session)
        res = render(myferet, request)
        assert res.body == homepage(myferet, session, {})

    def test_goto(self):
        myferet = FeretUI()
        session = Session()
        request = Request(
            method=Request.GET,
            session=session,
            querystring="page=homepage",
            headers={
                'Hx-Current-Url': '/'
            }
        )
        res = goto(myferet, request)
        assert res.body == homepage(myferet, session, {})
        assert res.headers['HX-Push-Url'] == "/?page=homepage"

    def test_goto_without_page(self):
        myferet = FeretUI()
        session = Session()
        request = Request(method=Request.GET, session=session)
        with pytest.raises(ActionError):
            goto(myferet, request)
