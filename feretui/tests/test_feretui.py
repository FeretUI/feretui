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

from feretui.exceptions import UnexistingAction
from feretui.feretui import FeretUI
from feretui.request import Request
from feretui.response import Response
from feretui.session import Session


class TestFeretUI:
    """Test of FeretUI class."""

    def test_render(self):
        """Test the main render without any options."""
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)
        response = myferet.render(request)
        assert isinstance(response, Response)

    def test_get_static_file_path(self):
        """Test get_static_file_path."""
        myferet = FeretUI()
        assert (
            myferet.get_static_file_path('bulma.css')
            == myferet.statics['bulma.css']
        )

    def test_register_and_execute_action(self):
        """Test get_static_file_path."""
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)

        @myferet.register_action
        def my_action(feretui, request):
            return id(feretui)

        assert myferet.execute_action(request, 'my_action') == id(myferet)

    def test_execute_unexisting_action(self):
        """Test get_static_file_path."""
        myferet = FeretUI()
        session = Session()
        request = Request(session=session)

        with pytest.raises(UnexistingAction):
            myferet.execute_action(request, 'my_action')
