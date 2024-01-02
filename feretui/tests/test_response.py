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

from feretui.response import Response


def test_response():
    """Test Response."""
    response = Response('<div>Response</div>')
    assert response.body == '<div>Response</div>'
    assert response.content_type == 'text/html'
    assert response.status_code == 200
    assert response.headers == {}
