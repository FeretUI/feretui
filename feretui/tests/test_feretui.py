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
