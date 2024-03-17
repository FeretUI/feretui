import pytest

from feretui.actions import goto
from feretui.exceptions import ActionError
from feretui.feretui import FeretUI
from feretui.pages import homepage
from feretui.request import Request
from feretui.session import Session


class TestAction:

    def test_goto(self) -> None:
        myferet = FeretUI()
        session = Session()
        request = Request(
            method=Request.GET,
            session=session,
            querystring="page=homepage",
            headers={
                'Hx-Current-Url': '/',
            },
        )
        res = goto(myferet, request)
        assert res.body == homepage(myferet, session, {})
        assert res.headers['HX-Push-Url'] == "/?page=homepage"

    def test_goto_without_page(self) -> None:
        myferet = FeretUI()
        session = Session()
        request = Request(method=Request.GET, session=session)
        with pytest.raises(ActionError):
            goto(myferet, request)

    def test_goto_with_in_aside(self) -> None:
        myferet = FeretUI()
        session = Session()
        request = Request(
            method=Request.GET,
            session=session,
            querystring="in-aside=test&page=homepage",
            headers={
                'Hx-Current-Url': '/',
            },
        )
        res = goto(myferet, request)
        assert res.body == homepage(myferet, session, {})
        assert (
            res.headers['HX-Push-Url']
            == "/?page=aside-menu&aside=test&aside_page=homepage"
        )
