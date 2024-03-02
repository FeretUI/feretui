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
    aside_menu, page_404, page_forbidden, homepage, static_page
)
from feretui.session import Session


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

    def test_static_page(self):
        myferet = FeretUI()
        session = Session()
        myferet.register_template_from_str(
            '''
                <template id="my-static-page">
                    <div>Test</div>
                </template>
            '''
        )
        res = static_page('my-static-page')(myferet, session, {})
        assert res == '<div>\n Test\n</div>'

    def test_static_page_ko(self):
        myferet = FeretUI()
        session = Session()
        with pytest.raises(PageError):
            static_page('my-static_page')(myferet, session, {})

    def test_aside(self):
        myferet = FeretUI()
        session = Session()
        res = aside_menu(myferet, session, {'aside': ['test']})
        assert res

    def test_aside_without_requiremend(self):
        myferet = FeretUI()
        session = Session()
        with pytest.raises(PageError):
            aside_menu(myferet, session, {})
