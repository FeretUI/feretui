# This file is a part of the FeretUI project
#
#    Copyright (C) 2023-2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""feretui.resources.common's module."""
from typing import TYPE_CHECKING

from markupsafe import Markup
from polib import POFile

from feretui.exceptions import ViewActionError, ViewError
from feretui.form import FeretUIForm
from feretui.request import Request
from feretui.resources.actions import Actionset, SelectedRowsAction
from feretui.response import Response
from feretui.session import Session

if TYPE_CHECKING:
    from feretui.feretui import FeretUI
    from feretui.translation import Translation


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
            actionset.context = f'{self.context}:actionset'
            for action in actionset.actions:
                action.context = f'{self.context}:action:{action.method}'

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
    ) -> list[Markup]:
        """Return the actionset list renderer.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The Session
        :type session: :class:`feretui.session.Session`
        :return: The html pages
        :rtype: list[str]
        """
        return [
            actionset.render(feretui, session, self.resource.code, self.code)
            for actionset in self.actions
            if actionset.is_visible(session)
        ]

    def get_call_kwargs(
        self: "ActionsMixinForView",
        params: dict,  # noqa: ARG002
    ) -> dict:
        """Return the kwargs for the call with this view.

        :param params: request params
        :type params: dict
        :return: the kwargs from params
        :rtype: dict
        """
        return {}

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
        if request.method is not Request.POST:
            raise ViewActionError(f'{request.method} is not the POST method')

        method = request.params.get('method')
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
                    if isinstance(action, SelectedRowsAction):
                        view_kwargs.update(self.get_call_kwargs(request.params))

                    is_declared = True
                    break

        if not is_declared:
            raise ViewActionError(
                f'The method {method} is not declared in the {self}',
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
        if not hasattr(self, 'limit'):
            raise ViewError("The view has not a 'limit : int' class attribute")

        if not hasattr(self, 'do_click_on_entry_redirect_to'):
            raise ViewError(
                "The view has not a 'do_click_on_entry_redirect_to : str' "
                "class attribute",
            )

        if not hasattr(self, 'create_button_redirect_to'):
            raise ViewError(
                "The view has not a 'create_button_redirect_to : str' "
                "class attribute",
            )

        if not hasattr(self, 'delete_button_redirect_to'):
            raise ViewError(
                "The view has not a 'delete_button_redirect_to : str' "
                "class attribute",
            )

        if not hasattr(self.resource, 'filtered_reads'):
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
            f'Filter_{self.resource.code}_{self.code}',
            (self.Filter, self.form_cls),
            {'view': self},
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
                Markup(feretui.render_template(
                    session,
                    'view-goto-create-button',
                    create_view_qs=self.get_transition_querystring(
                        options,
                        view=self.create_button_redirect_to,
                    ),
                )),
            )
        if self.delete_button_redirect_to:
            res.append(
                Markup(feretui.render_template(
                    session,
                    'view-goto-selected-delete-button',
                    delete_view_qs=self.get_transition_querystring(
                        options,
                        view=self.delete_button_redirect_to,
                    ),
                    rcode=self.resource.code,
                    vcode=self.code,
                )),
            )

        return res

    def get_actions(
        self: "MultiView",
        feretui: "FeretUI",
        session: Session,
    ) -> list[Markup]:
        """Return the actionset list renderer.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param session: The Session
        :type session: :class:`feretui.session.Session`
        :return: The html pages
        :rtype: list[str]
        """
        res = [
            Markup(feretui.render_template(
                session,
                'view-filter',
                form=self.filter_cls(),
                hx_post=f'{feretui.base_url}/action/resource?action=filters',
            )),
        ]
        res.extend(super().get_actions(feretui, session))
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
            if (
                key.startswith('filter[')
                and key[-1] == ']'
            )
        ]
        offset = options.get('offset', 0)
        if isinstance(offset, list):
            offset = offset[0]

        offset = int(offset)
        dataset = self.resource.filtered_reads(
            self.form_cls,
            filters,
            offset,
            self.limit,
        )
        paginations = range(0, dataset['total'], self.limit)

        open_view_qs = (
            self.get_transition_querystring(
                options,
                pk=None,
                view=self.do_click_on_entry_redirect_to,
            ) if self.do_click_on_entry_redirect_to
            else None
        )
        return {
            "rcode": self.resource.code,
            "vcode": self.code,
            "label": self.get_label(),
            "form": self.form_cls(),
            "offset": offset,
            "limit": self.limit,
            "paginations": paginations,
            "dataset": dataset,
            "filters": filters,
            "open_view_qs": open_view_qs,
            "header_buttons": self.get_header_buttons(
                feretui,
                session,
                options,
            ),
            "actions": self.get_actions(feretui, session),
        }

    # ---------------- View actions -------------------------

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
        newqs['offset'] = request.query['offset']
        return Response(
            self.render(feretui, request.session, newqs),
            headers={
                'HX-Push-Url': request.get_url_from_dict(base_url, newqs),
            },
        )

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
        qs['offset'] = 0

        for param, values in request.params.items():
            if param == 'action':
                continue

            existing = qs.setdefault(f'filter[{param}]', [])
            if request.method == Request.POST:
                for value in values:
                    if value not in existing:
                        existing.append(value)
            elif request.method == Request.DELETE:
                for value in values:
                    if value in existing:
                        existing.remove(value)

                if not existing:
                    del qs[f'filter[{param}]']

        base_url = request.get_base_url_from_current_url()
        url = request.get_url_from_dict(base_url=base_url, querystring=qs)
        return Response(
            self.render(feretui, request.session, qs),
            headers={
                'HX-Push-Url': url,
            },
        )
