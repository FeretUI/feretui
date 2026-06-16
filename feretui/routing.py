"""Refactor routing logic of FeretUI."""

from collections.abc import Callable, Iterable
from logging import getLogger
from typing import TYPE_CHECKING

from feretui.context import set_context
from feretui.exceptions import UnexistingActionError
from feretui.pages import static_page
from feretui.request import Request
from feretui.response import Response
from feretui.session import Session

if TYPE_CHECKING:
    from feretui.feretui import FeretUI
    from feretui.form import FeretUIForm

logger = getLogger(__name__)


class RouteRegistry:
    """RouteRegistry class.

    Manage pages and actions.
    """

    def __init__(self, feretui: "FeretUI") -> None:
        self.feretui = feretui
        self.actions: dict[str, Callable] = {}
        self.pages: dict[str, Callable] = {}

    def register_action(
        self,
        function: Callable[["FeretUI", Request], Response],
    ) -> Callable[["FeretUI", Request], Response]:
        """Register an action."""
        if function.__name__ in self.actions:
            logger.info("Overload action %r", function.__name__)

        self.actions[function.__name__] = function
        return function

    def execute_action(
        self,
        request: Request,
        action_name: str,
    ) -> Response:
        """Execute a stored action."""
        if action_name not in self.actions:
            raise UnexistingActionError(action_name)

        with set_context(self.feretui, request):
            function = self.actions[action_name]
            return function(self.feretui, request)

    def register_page(
        self,
        name: str = None,
        templates: Iterable[str] = None,
        forms: Iterable["FeretUIForm"] = None,
        addons: str = None,
    ) -> Callable:
        """Register a page."""
        if isinstance(templates, Iterable):
            for template in templates:
                self.feretui.register_template_from_str(template, addons=addons)

        if isinstance(forms, Iterable):
            register = self.feretui.register_form(addons=addons)
            for form in forms:
                register(form)

        default_name = name

        def register_page_callback(
            func: Callable[["FeretUI", Session, dict], str],
        ) -> Callable[["FeretUI", Session, dict], str]:
            name = default_name if default_name else func.__name__

            if name in self.pages:
                logger.info("Overload page %r", name)

            self.pages[name] = func
            return func

        return register_page_callback

    def register_static_page(
        self,
        name: str,
        template: str,
        templates: Iterable[str] = None,
        addons: str = None,
    ) -> None:
        """Register a page."""
        if templates is None:
            templates = []
        if not isinstance(templates, list) and isinstance(templates, Iterable):
            templates = list(templates)

        templates.append(f'<template id="{name}">{template}</template>')
        self.register_page(
            name=name,
            templates=templates,
            addons=addons,
        )(
            static_page(name),
        )

    def get_page(
        self,
        pagename: str,
    ) -> Callable[["FeretUI", Session, dict], str]:
        """Return the page callable."""
        if pagename not in self.pages:
            return self.get_page("404")

        return self.pages[pagename]
