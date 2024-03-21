# This file is a part of the FeretUI project
#
#    Copyright (C) 2023-2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""The thread behaviours.

Some part of information is given in local thread.

It is the case of the
* lang
* feretui instance
* feretui request instance

This is very helpfull for the translation and to distribute the instance
of the client and the request every where during the execution

::

    from feretui.thread import local

    feretui = local.feretui
    request = local.request
    lang = local.lang
"""
from threading import local as localthreading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from feretui.feretui import FeretUI
    from feretui.request import Request


class LocalThreading(localthreading):
    """LocalThread class.

    It is a thread safe store point for:

    * lang
    * feretui instance
    * feretui request instance
    """

    lang: str = 'en'
    """The language code of the thread"""

    feretui: "FeretUI" = None
    """The feretui instane of the thread."""

    request: "Request" = None
    """The feretui request instane of the thread."""


local = LocalThreading()
"""A thread safe local store. [:class:`.LocalThreading`]"""
