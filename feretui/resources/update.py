# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Module feretui.resources.list.

The List resource represent data under html table.

* :class:`.CreateView`
* :class:`.CResource`

::

    myferet.register_resource()
    class MyResource(CResource, Resource):
        code = 'code of the resource',
        label = 'label',

        class MetaViewCreate:
            pass
"""
from typing import TYPE_CHECKING

from lxml.etree import Element
from markupsafe import Markup

from feretui.form import FeretUIForm
from feretui.request import Request
from feretui.resources.common import TemplateMixinForView
from feretui.resources.view import View, view_action_validator
from feretui.response import Response
from feretui.session import Session

from .resource import Resource

if TYPE_CHECKING:
    from feretui.feretui import FeretUI


class DefaultViewUpdate:
    """Default value for the view read."""

    after_update_redirect_to: str = None
    cancel_button_redirect_to: str = None

    body_template_id: str = "view-readwrite-form"


class EditView(TemplateMixinForView, View):
    """Create view."""

    code: str = 'edit'

    def set_form_template(
        self: "EditView",
        feretui: "FeretUI",  # noqa: ARG002
        parent: Element,
    ) -> Element:
        """Add the form node in the template.

        :param feretui: The feretui client
        :type feretui: :class:`feretui.feretui.FeretUI`
        :param parent: The parent node
        :type parent: HtmlElement_
        """
        form = super().set_form_template(feretui, parent)
        form.set(
            'hx-post',
            f'{feretui.base_url}/action/resource?action=save',
        )
        return form

    def get_header_buttons(
        self: "EditView",
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
        options = options.copy()
        options.pop('error', None)
        options.pop('form', None)
        res = super().get_header_buttons(feretui, session, options)
        res.append(
            Markup(feretui.render_template(
                session,
                'view-do-save-button',
            )),
        )
        if self.cancel_button_redirect_to:
            res.append(
                Markup(feretui.render_template(
                    session,
                    'view-goto-edit-cancel-button',
                    url=self.get_transition_url(
                        feretui,
                        options,
                        view=self.cancel_button_redirect_to,
                    ),
                )),
            )
        return res

    def render_kwargs(
        self: "EditView",
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
        res = super().render_kwargs(feretui, session, options)
        pk = options.get('pk')
        if isinstance(pk, list):
            pk = pk[0]

        res.update({
            'form': options.pop('form', self.resource.read(self.form_cls, pk)),
            'error': options.get('error'),
        })
        return res

    @view_action_validator(methods=[Request.POST])
    def save(
        self: "EditView",
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
        options = request.get_query_string_from_current_url().copy()
        pk = options.get('pk')
        if isinstance(pk, list):
            pk = pk[0]

        form = self.form_cls(request.form)
        if form.validate():
            try:
                self.resource.update([form])
                if self.after_update_redirect_to:
                    base_url = request.get_base_url_from_current_url()
                    options.update({
                        'view': self.after_update_redirect_to,
                        'pk': pk,
                    })
                    url = request.get_url_from_dict(
                        base_url=base_url,
                        querystring=options,
                    )
                    return Response(
                        self.resource.views[
                            self.after_update_redirect_to
                        ].render(feretui, request.session, options),
                        headers={
                            'HX-Push-Url': url,
                        },
                    )
            except Exception as e:
                options['error'] = str(e)

        options['form'] = form
        return Response(self.render(feretui, request.session, options))


class UResource:
    """UResource class."""

    MetaViewUpdate = DefaultViewUpdate

    def build_view(
        self: "UResource",
        view_cls_name: str,
    ) -> Resource:
        """Return the view instance in fonction of the MetaView attributes.

        :param view_cls_name: name of the meta attribute
        :type view_cls_name: str
        :return: An instance of the view
        :rtype: :class:`feretui.resources.view.View`
        """
        if view_cls_name.startswith('MetaViewUpdate'):
            meta_view_cls = self.get_meta_view_class(view_cls_name)
            meta_view_cls.append(EditView)
            view_cls = type(
                'EditView',
                tuple(meta_view_cls),
                {},
            )
            if not self.default_view:
                self.default_view = view_cls.code

            return view_cls(self)

        return super().build_view(view_cls_name)

    def read(self: "UResource", form_cls: FeretUIForm, pk: str) -> FeretUIForm:
        """Return an intance of the form.

        .. warning:: must be overwriting

        :param form_cls: Form of the list view
        :type form_cls: :class:`feretui.form.FeretUIForm`
        :param pk: The primary key
        :type pk: str
        :return: the form instance
        :type form_cls: :class:`feretui.form.FeretUIForm`
        """

    def update(self: "UResource", forms: list[FeretUIForm]) -> None:
        """Update an object from the form and return the primary key.

        .. warning:: must be overwriting

        :param form: The instance of Form
        :type form: :class:`feretui.form.FeretUIForm`
        """
