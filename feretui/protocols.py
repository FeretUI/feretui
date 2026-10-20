# This file is a part of the FeretUI project
#
#    Copyright (C) 2024-2026 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Module feretui.protocols.

Formal Protocol definitions and structural typing contracts for FeretUI.
Enables static analysis under mypy --strict and runtime verification.

* :class:`.SessionProtocol`
* :class:`.RequestProtocol`
* :class:`.ResponseProtocol`
* :class:`.FormProtocol`
* :class:`.ViewProtocol`
* :class:`.ResourceProtocol`
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class SessionProtocol(Protocol):
    """Structural typing contract for user session objects."""

    user: Any
    lang: str
    theme: str
    color_scheme: str | None

    def to_dict(self) -> dict[str, Any]:
        """Return the value of the session as a dict."""
        ...  # pragma: no cover


@runtime_checkable
class RequestProtocol(Protocol):
    """Structural typing contract for HTTP request abstraction."""

    session: Any
    method: Any
    query: dict[str, Any]
    params: Any
    headers: dict[str, str]


@runtime_checkable
class ResponseProtocol(Protocol):
    """Structural typing contract for HTTP response abstraction."""

    body: str
    status_code: int
    headers: dict[str, str]


@runtime_checkable
class FormProtocol(Protocol):
    """Structural typing contract for form objects."""

    errors: dict[str, list[str]]

    def validate(self) -> bool:
        """Validate form data."""
        ...  # pragma: no cover

    @property
    def data(self) -> dict[str, Any]:
        """Return dict of form field data."""
        ...  # pragma: no cover


@runtime_checkable
class ViewProtocol(Protocol):
    """Structural typing contract for resource views."""

    code: str

    def render(
        self,
        feretui: object,
        session: SessionProtocol,
        options: dict[str, object],
    ) -> object:
        """Render the view."""
        ...  # pragma: no cover


@runtime_checkable
class ResourceProtocol(Protocol):
    """Structural typing contract for resources."""

    code: str
    label: str
    default_view: str | None
    views: dict[str, Any]
