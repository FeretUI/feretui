# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Conftest for pytest."""

import pytest

from feretui.context import cvar_feretui, cvar_request
from feretui.feretui import FeretUI
from feretui.request import Request
from feretui.session import Session


@pytest.fixture(scope="function")
def feretui() -> FeretUI:
    """Return a feretui."""
    feretui = FeretUI()
    cvar_feretui.set(feretui)
    return feretui


@pytest.fixture(scope="function")
def session() -> Session:
    """Return a session."""
    return Session()


@pytest.fixture(scope="function")
def authenticated_session() -> Session:
    """Return a session."""
    return Session(user='test')


@pytest.fixture(scope="function")
def frequest(session: Session) -> Request:
    """Return a request."""
    request = Request(session=session)
    cvar_request.set(request)
    return request
