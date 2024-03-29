# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest

from feretui.exceptions import PageError
from feretui.feretui import FeretUI
from feretui.pages import (
    aside_menu,
    homepage,
    login,
    page_404,
    page_forbidden,
    signup,
    static_page,
)
from feretui.session import Session


class TestPage:

    def test_404(self, snapshot) -> None:
        myferet = FeretUI()
        session = Session()
        snapshot.assert_match(
            page_404(myferet, session, {'page': ['test']}),
            'snapshot.html',
        )

    def test_forbidden(self, snapshot) -> None:
        myferet = FeretUI()
        session = Session()
        snapshot.assert_match(
            page_forbidden(myferet, session, {'page': ['test']}),
            'snapshot.html',
        )

    def test_homepage(self, snapshot) -> None:
        myferet = FeretUI()
        session = Session()
        snapshot.assert_match(
            homepage(myferet, session, {}),
            'snapshot.html',
        )

    def test_static_page(self) -> None:
        myferet = FeretUI()
        session = Session()
        myferet.register_template_from_str(
            '''
                <template id="my-static-page">
                    <div>Test</div>
                </template>
            ''',
        )
        res = static_page('my-static-page')(myferet, session, {})
        assert res == '<div>\n Test\n</div>'

    def test_static_page_ko(self) -> None:
        myferet = FeretUI()
        session = Session()
        with pytest.raises(PageError):
            static_page('my-static_page')(myferet, session, {})

    def test_aside(self, snapshot) -> None:
        myferet = FeretUI()
        session = Session()
        snapshot.assert_match(aside_menu(
            myferet, session, {'aside': ['test']}),
            'snapshot.html',
        )

    def test_aside_without_requiremend(self) -> None:
        myferet = FeretUI()
        session = Session()
        with pytest.raises(PageError):
            aside_menu(myferet, session, {})

    def test_login_1(self, snapshot) -> None:
        myferet = FeretUI()
        session = Session()
        snapshot.assert_match(login(myferet, session, {}), 'snapshot.html')

    def test_login_2(self) -> None:
        myferet = FeretUI()
        session = Session(user='test')
        res = login(myferet, session, {})
        assert res == page_forbidden(myferet, session, {})

    def test_signup_1(self, snapshot) -> None:
        myferet = FeretUI()
        session = Session()
        snapshot.assert_match(signup(myferet, session, {}), 'snapshot.html')

    def test_signup_2(self) -> None:
        myferet = FeretUI()
        session = Session(user='test')
        res = signup(myferet, session, {})
        assert res == page_forbidden(myferet, session, {})
