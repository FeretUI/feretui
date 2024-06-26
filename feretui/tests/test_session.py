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

from feretui.session import Session


def test_session() -> None:
    """Test session."""
    session = Session()
    assert session.user is None
    assert session.to_dict() == {
        'user': None,
        'lang': 'en',
        'theme': 'default',
    }
