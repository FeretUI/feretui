# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.

import pytest
from feretui.thread import local


@pytest.fixture(scope="function", autouse=True)
def clean_local():
    local.feretui = None
    local.lang = 'en'
    local.request = None
