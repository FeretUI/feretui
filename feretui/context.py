# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Module feretui.context.

defined the contextvar used by FeretUI client

"""
from contextlib import contextmanager
from contextvars import ContextVar
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from feretui.feretui import FeretUI
    from feretui.request import Request

cvar_feretui: ContextVar["FeretUI"] = ContextVar('feretui')
cvar_request: ContextVar["Request"] = ContextVar('request')


@contextmanager
def set_context(feretui: "FeretUI", request: "Request"):
    """Context manager to tokenize contextvar."""
    token_feretui = cvar_feretui.set(feretui)
    token_request = cvar_request.set(request)
    try:
        yield
    finally:
        cvar_feretui.reset(token_feretui)
        cvar_request.reset(token_request)


class ContextProperties:
    """ContextProperties class.

    used to get the contextvar in class.
    """

    def __getattr__(self: "ContextProperties", attribute: str) -> None:
        """Getter."""
        if attribute == 'feretui':
            return cvar_feretui.get()

        if attribute == 'request':
            return cvar_request.get()

        return super().__getattr__(attribute)
