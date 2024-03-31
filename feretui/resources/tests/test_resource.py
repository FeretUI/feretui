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

from feretui.exceptions import ResourceError
from feretui.resources.resource import Resource


class TestResource:

    def test_without_code(self) -> None:

        class MyResource(Resource):
            label = 'Test'

        with pytest.raises(ResourceError):
            MyResource.build()

    def test_without_label(self) -> None:

        class MyResource(Resource):
            code = 'test'

        with pytest.raises(ResourceError):
            MyResource.build()
