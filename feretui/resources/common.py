# This file is a part of the FeretUI project
#
#    Copyright (C) 2023-2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""feretui.resources.common's module.

* :class:`.ActionsMixinForView`
* :class:`.MultiView`
* :class:`.TemplateMixinForView`
"""

from typing import TYPE_CHECKING

from lxml.etree import Element, SubElement, tostring
from lxml.html import fromstring
from markupsafe import Markup
from polib import POFile

from feretui.exceptions import ViewActionError, ViewError
from feretui.form import FeretUIForm
from feretui.request import Request
from feretui.resources.actions import Actionset
from feretui.resources.view import view_action_validator
from feretui.response import Response
from feretui.session import Session
from feretui.template import Template, decode_html
from feretui.translation import Translation

if TYPE_CHECKING:
    from feretui.feretui import FeretUI


class LabelMixinForView:
    """LabelMixinForView class."""

    label: str = None

    def export_catalog(
        self: "LabelMixinForView",
        translation: Translation,
        po: POFile,
    ) -> None:
        """Export the translations in the catalog.

        :param translation: The translation instance to add also inside it.
        :type translation: :class:`.Translation`
        :param po: The catalog instance
        :type po: PoFile_
        """
        super().export_catalog(translation, po)
        if self.label:
            po.append(translation.define(f"{self.context}:label", self.label))

    def get_label(
        self: "LabelMixinForView",
        feretui: "FeretUI",
        session: Session,
    ) -> str:
        """Return the translated label.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The Session
        :type session: :class:`feretui.session.Session`
        :rtype: str.
        """
        if not self.label:
            return super().get_label(feretui, session)

        return feretui.translation.get(
            session.lang,
            f"{self.context}:label",
            self.label,
        )


class ActionsMixinForView:
    """ActionsMixinForView class.

    Render the actions buttons aside
    """

    actions: list[Actionset] = []

    def __init__(
        self: "ActionsMixinForView",
        *args: tuple,
        **kwargs: dict,
    ) -> None:
        """ActionsMixinForView constructor."""
        super().__init__(*args, **kwargs)
        for actionset in self.actions:
            actionset.context = f"{self.context}:actionset"
            for action in actionset.actions:
                action.context = f"{self.context}:action:{action.method}"

    def export_catalog(
        self: "ActionsMixinForView",
        translation: "Translation",
        po: POFile,
    ) -> None:
        """Export the translations in the catalog.

        :param translation: The translation instance to add also inside it.
        :type translation: :class:`.Translation`
        :param po: The catalog instance
        :type po: PoFile_
        """
        super().export_catalog(translation, po)
        for actionset in self.actions:
            actionset.export_catalog(translation, po)

    def get_actions(
        self: "ActionsMixinForView",
        feretui: "FeretUI",
        session: Session,
        options: dict,
    ) -> list[Markup]:
        """Return the actionset list renderer.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The Session
        :type session: :class:`feretui.session.Session`
        :param options: The querystring
        :type options: dict
        :return: The html pages
        :rtype: list[str]
        """
        return [
            actionset.render(
                feretui,
                session,
                options,
                self.resource.code,
                self.code,
            )
            for actionset in self.actions
            if actionset.is_visible(session)
        ]

    def get_call_kwargs(
        self: "ActionsMixinForView",
        request: Request,  # noqa: ARG002
    ) -> dict:
        """Return the kwargs for the call with this view.

        :param request: request params
        :type request: :class:`feretui.request.Request`
        :return: the kwargs from params
        :rtype: dict
        """
        return {}

    @view_action_validator(methods=Request.POST)
    def call(
        self: "ActionsMixinForView",
        feretui: "FeretUI",
        request: Request,
    ) -> Response:
        """Call a method on the resource.

        .. note::

            If the method called return None then the
            view is rerendering

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param request: The request
        :type request: :class:`feretui.request.Request`
        :return: The page to display
        :rtype: :class:`feretui.response.Response`
        :exception: ViewActionError
        """
        method = request.params.get("method")
        if isinstance(method, list):
            method = method[0]

        is_declared = False
        view_kwargs = {}
        for actionset in self.actions:
            for action in actionset.actions:
                if (
                    action.is_visible(request.session)
                    and action.method == method
                ):
                    view_kwargs.update(self.get_call_kwargs(request))
                    is_declared = True
                    break

        if not is_declared:
            raise ViewActionError(
                f"The method {method} is not declared in the {self}",
            )

        func = getattr(self.resource, method)
        res = func(feretui, request, **view_kwargs)
        if not res:
            qs = request.get_query_string_from_current_url()
            res = Response(Markup(self.render(feretui, request.session, qs)))

        if not isinstance(res, Response):
            res = Response(res)

        return res


class MultiView(ActionsMixinForView):
    """MultiView class.

    Render the buttons for view multi.
    """

    class Filter:
        """Filter's Form."""

    def __init__(self: "MultiView", *args: tuple, **kwargs: dict) -> None:
        """MultiView constructor."""
        super().__init__(*args, **kwargs)
        if not hasattr(self, "limit"):
            raise ViewError("The view has not a 'limit : int' class attribute")

        if not hasattr(self, "do_click_on_entry_redirect_to"):
            raise ViewError(
                "The view has not a 'do_click_on_entry_redirect_to : str' "
                "class attribute",
            )

        if not hasattr(self, "create_button_redirect_to"):
            raise ViewError(
                "The view has not a 'create_button_redirect_to : str' "
                "class attribute",
            )

        if not hasattr(self, "delete_button_redirect_to"):
            raise ViewError(
                "The view has not a 'delete_button_redirect_to : str' "
                "class attribute",
            )

        if not hasattr(self.resource, "filtered_reads"):
            raise ViewError(
                "The resource has not a 'filtered_reads' method\n"
                "def filtered_reads(self, form_cls, filters, offset, limit):\n"
                "    return {'total': 0, 'forms': []}",
            )

        self.filter_cls = self.get_filter_cls()

    def export_catalog(
        self: "MultiView",
        translation: "Translation",
        po: POFile,
    ) -> None:
        """Export the translations in the catalog.

        :param translation: The translation instance to add also inside it.
        :type translation: :class:`.Translation`
        :param po: The catalog instance
        :type po: PoFile_
        """
        super().export_catalog(translation, po)
        self.filter_cls.export_catalog(translation, po)

    def get_filter_cls(self: "MultiView") -> FeretUIForm:
        """Return the Filter Form for the view."""
        return type(
            f"Filter_{self.resource.code}_{self.code}",
            (self.Filter, self.form_cls),
            {"view": self},
        )

    # ---------- Render -------------------

    def get_header_buttons(
        self: "MultiView",
        feretui: "FeretUI",
        session: Session,
        options: dict,
    ) -> list[Markup]:
        """Return the buttons for the multi view.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The Session
        :type session: :class:`feretui.session.Session`
        :param options: The options come from the body or the query string
        :type options: dict
        :return: The html pages
        :rtype: list[Markup]
        """
        res = []
        if self.create_button_redirect_to:
            res.append(
                Markup(
                    feretui.render_template(
                        session,
                        "view-goto-create-button",
                        url=self.get_transition_url(
                            feretui,
                            options,
                            view=self.create_button_redirect_to,
                        ),
                    ),
                ),
            )
        if self.delete_button_redirect_to:
            res.append(
                Markup(
                    feretui.render_template(
                        session,
                        "view-goto-selected-delete-button",
                        rcode=self.resource.code,
                        vcode=self.code,
                    ),
                ),
            )

        return res

    def get_actions(
        self: "MultiView",
        feretui: "FeretUI",
        session: Session,
        options: dict,
    ) -> list[Markup]:
        """Return the actionset list renderer.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The Session
        :type session: :class:`feretui.session.Session`
        :param options: The querystring
        :type options: dict
        :return: The html pages
        :rtype: list[str]
        """
        res = [
            Markup(
                feretui.render_template(
                    session,
                    "view-filter",
                    form=self.filter_cls(),
                    hx_post=f"{feretui.base_url}/action/resource?action=filters",
                ),
            ),
        ]
        res.extend(super().get_actions(feretui, session, options))
        return res

    def render_kwargs(
        self: "MultiView",
        feretui: "FeretUI",
        session: Session,
        options: dict,
    ) -> dict:
        """Return the dict of parameter need for  the muti view.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The Session
        :type session: :class:`feretui.session.Session`
        :param options: The options come from the body or the query string
        :type options: dict
        :return: the named attributes
        :rtype: dict
        """
        filters = [
            (key[7:-1], values)
            for key, values in options.items()
            if (key.startswith("filter[") and key[-1] == "]")
        ]
        offset = options.get("offset", 0)
        if isinstance(offset, list):
            offset = offset[0]

        offset = int(offset)
        dataset = self.resource.filtered_reads(
            self.form_cls,
            filters,
            offset,
            self.limit,
        )
        paginations = range(0, dataset["total"], self.limit)

        open_view_url = (
            self.get_transition_url(
                feretui,
                options,
                pk=None,
                view=self.do_click_on_entry_redirect_to,
            )
            if self.do_click_on_entry_redirect_to
            else None
        )
        return {
            "rcode": self.resource.code,
            "vcode": self.code,
            "label": self.get_label(feretui, session),
            "form": self.form_cls(),
            "offset": offset,
            "limit": self.limit,
            "paginations": paginations,
            "dataset": dataset,
            "filters": filters,
            "open_view_url": open_view_url,
            "header_buttons": self.get_header_buttons(
                feretui,
                session,
                options,
            ),
            "actions": self.get_actions(feretui, session, options),
        }

    # ---------------- View actions -------------------------

    @view_action_validator(methods=[Request.GET])
    def pagination(
        self: "MultiView",
        feretui: "FeretUI",
        request: Request,
    ) -> Response:
        """Change the pagination call by the resource router.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param request: The request
        :type request: :class:`feretui.request.Request`
        :return: The page to display
        :rtype: :class:`feretui.response.Response`
        """
        newqs = request.get_query_string_from_current_url().copy()
        base_url = request.get_base_url_from_current_url()
        newqs["offset"] = request.query["offset"]
        return Response(
            self.render(feretui, request.session, newqs),
            headers={
                "HX-Push-Url": request.get_url_from_dict(base_url, newqs),
            },
        )

    @view_action_validator(methods=[Request.POST, Request.DELETE])
    def filters(
        self: "MultiView",
        feretui: "FeretUI",
        request: Request,
    ) -> Response:
        """Change the filters and rerender.

        The type of modification of the filter depend of the request method:

        * POST : add a filter
        * DELETE : remove a filter

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param request: The request
        :type request: :class:`feretui.request.Request`
        :return: The page to display
        :rtype: :class:`feretui.response.Response`
        """
        qs = request.get_query_string_from_current_url()
        qs["offset"] = 0

        for param, values in request.params.items():
            if param == "action":
                continue

            existing = qs.setdefault(f"filter[{param}]", [])
            if request.method == Request.POST:
                for value in values:
                    if value not in existing:
                        existing.append(value)
            elif request.method == Request.DELETE:
                for value in values:
                    if value in existing:
                        existing.remove(value)

                if not existing:
                    del qs[f"filter[{param}]"]

        base_url = request.get_base_url_from_current_url()
        url = request.get_url_from_dict(base_url=base_url, querystring=qs)
        return Response(
            self.render(feretui, request.session, qs),
            headers={
                "HX-Push-Url": url,
            },
        )

    @view_action_validator(methods=[Request.POST])  # USE POST cause of params
    def goto_delete(
        self: "MultiView",
        feretui: "FeretUI",
        request: Request,
    ) -> Response:
        """Goto the delete page.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param request: The request
        :type request: :class:`feretui.request.Request`
        :return: The page to display
        :rtype: :class:`feretui.response.Response`
        """
        view_kwargs = self.get_call_kwargs(request)
        newqs = request.get_query_string_from_current_url().copy()
        base_url = request.get_base_url_from_current_url()
        newqs.update(
            {
                "view": self.delete_button_redirect_to,
                "pk": view_kwargs["pks"],
            },
        )
        return Response(
            self.resource.views[self.delete_button_redirect_to].render(
                feretui, request.session, newqs,
            ),
            headers={
                "HX-Push-Url": request.get_url_from_dict(base_url, newqs),
            },
        )


class TemplateMixinForView:
    """TemplateMixinForView class."""

    header_template_id: str = "view-buttons-header"
    header_template: str = None
    body_template_id: str = "view-readwrite-form"
    body_template: str = None
    footer_template_id: str = "view-buttons-header"
    footer_template: str = None

    # ----- translation ------
    def export_catalog(
        self: "ActionsMixinForView",
        translation: "Translation",
        po: POFile,
    ) -> None:
        """Export the translations in the catalog.

        :param translation: The translation instance to add also inside it.
        :type translation: :class:`.Translation`
        :param po: The catalog instance
        :type po: PoFile_
        """
        super().export_catalog(translation, po)
        template_id = f"resource-{self.resource.code}-view-{self.code}"
        tmpls = Template(Translation(translation.feretui))
        tmpls.load_template_from_str(
            self.get_compiled_template(
                translation.feretui,
                Session(),
                template_id,
            ),
        )
        tmpls.export_catalog(po)

    # ----- templating ------
    def compile(self: "TemplateMixinForView", node: Element) -> Element:
        """Transform the template to add some javascript behaviours.

        :param node: The main node to transform
        :type node: HtmlElement_
        :return: new node
        :rtype: HtmlElement_
        """
        return node

    def set_header_template(
        self: "TemplateMixinForView",
        feretui: "FeretUI",
        session: Session,
        parent: Element,
    ) -> None:
        """Add the header template.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The feretui session
        :type session: :class:`feretui.session.Session`
        :param parent: The parent node
        :type parent: HtmlElement_
        """
        header = None
        if self.header_template:
            header = fromstring(decode_html(self.header_template))
        elif self.header_template_id:
            header = feretui.template.get_template(
                self.header_template_id,
                session.lang,
                tostring=False,
            )

        if header is not None:
            header = self.compile(header)
            parent.append(header)

    def set_form_template(
        self: "TemplateMixinForView",
        feretui: "FeretUI",  # noqa: ARG002
        session: Session,  # noqa: ARG002
        parent: Element,
    ) -> Element:
        """Add the form node in the template.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The feretui session
        :type session: :class:`feretui.session.Session`
        :param parent: The parent node
        :type parent: HtmlElement_
        """
        return SubElement(parent, "form")

    def set_body_template(
        self: "TemplateMixinForView",
        feretui: "FeretUI",  # noqa: ARG002
        session: Session,
        parent: Element,
    ) -> Element:
        """Add the body template.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The feretui session
        :type session: :class:`feretui.session.Session`
        :param parent: The parent node
        :type parent: HtmlElement_
        """
        body = None
        if self.body_template:
            body = fromstring(self.body_template)
        elif self.body_template_id:
            body = feretui.template.get_template(
                self.body_template_id,
                session.lang,
                tostring=False,
            )

        if body is not None:
            body = self.compile(body)
            parent.append(body)

    def set_footer_template(
        self: "TemplateMixinForView",
        feretui: "FeretUI",  # noqa: ARG002
        session: Session,
        parent: Element,
    ) -> Element:
        """Add the footer template.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The feretui session
        :type session: :class:`feretui.session.Session`
        :param parent: The parent node
        :type parent: HtmlElement_
        """
        footer = None
        if self.footer_template:
            footer = fromstring(self.footer_template)
        elif self.footer_template_id:
            footer = feretui.template.get_template(
                self.footer_template_id,
                session.lang,
                tostring=False,
            )

        if footer is not None:
            footer = self.compile(footer)
            parent.append(footer)

    def get_compiled_template(
        self: "TemplateMixinForView",
        feretui: "FeretUI",
        session: Session,
        template_id: str,
    ) -> str:
        """Get the template for this view.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The feretui session
        :type session: :class:`feretui.session.Session`
        :param template_id: The id of the template
        :type template_id: str
        """
        template = Element("template")
        template.set("id", template_id)
        div = SubElement(template, "div")
        div.set("id", template_id)
        div.set("class", "container is-fluid content")
        form = self.set_form_template(feretui, session, div)
        self.set_header_template(feretui, session, form)
        self.set_body_template(feretui, session, form)
        self.set_footer_template(feretui, session, form)
        return tostring(template)

    # ----- render -----
    def render_kwargs(
        self: "TemplateMixinForView",
        feretui: "FeretUI",
        session: Session,
        options: dict,
    ) -> dict:
        """Get kwarg of the view for render.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The Session
        :type session: :class:`feretui.session.Session`
        :param options: The options come from the body or the query string
        :type options: dict
        :return: The kwargs
        :rtype: dict.
        """
        return {
            "resource": self.resource,
            "header_buttons": self.get_header_buttons(
                feretui,
                session,
                options,
            ),
            "rcode": self.resource.code,
            "vcode": self.code,
        }

    def get_header_buttons(
        self: "TemplateMixinForView",
        feretui: "FeretUI",  # noqa: ARG002
        session: Session,  # noqa: ARG002
        options: dict,  # noqa: ARG002
    ) -> list[Markup]:
        """Return the buttons for the multi view.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The Session
        :type session: :class:`feretui.session.Session`
        :param options: The options come from the body or the query string
        :type options: dict
        :return: The html pages
        :rtype: list[Markup].
        """
        return []

    def render(
        self: "TemplateMixinForView",
        feretui: "FeretUI",
        session: Session,
        options: dict,
    ) -> str:
        """Render the view.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The Session
        :type session: :class:`feretui.session.Session`
        :param options: The options come from the body or the query string
        :type options: dict
        :return: The html page in
        :rtype: str.
        """
        template_id = f"resource-{self.resource.code}-view-{self.code}"
        if not feretui.template.has_template(template_id):
            feretui.template.load_template_from_str(
                self.get_compiled_template(feretui, session, template_id),
            )

        return feretui.render_template(
            session,
            template_id,
            **self.render_kwargs(feretui, session, options),
        )
