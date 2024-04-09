# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Module feretui.resources.list.

The List resource represent data under html table.

* :class:`.ReadView`
* :class:`.RResource`

::

    myferet.register_resource()
    class MyResource(RResource, Resource):
        code = 'code of the resource',
        label = 'label',

        class MetaViewRead:
            pass
"""
from typing import TYPE_CHECKING

from lxml.etree import SubElement
from markupsafe import Markup

from feretui.request import Request
from feretui.resources.common import (
    ActionsMixinForView,
    TemplateMixinForView,
)
from feretui.resources.view import View
from feretui.session import Session

from .resource import Resource

if TYPE_CHECKING:
    from feretui.feretui import FeretUI


class DefaultViewRead:
    """Default value for the view read."""

    label: str = None
    limit: int = 20
    create_button_redirect_to: str = None
    delete_button_redirect_to: str = None
    edit_button_redirect_to: str = None
    return_button_redirect_to: str = None

    header_template: str = """
    <div class="columns">
      <div class="column is-3">
        <h1>User : {{ form.pk.data }}</h1>
      </div>
      <div class="column">
        <div class="buttons is-centered">
          {% for button in header_buttons %}
          {{ button }}
          {% endfor %}
        </div>
      </div>
      <div class="column is-3">
      other
      </div>
    </div>
    """

    body_template = """
    <div class="container">
      {% for field in form %}
      {{ field(readonly=True) }}
      {% endfor %}
    </div>
    """

    footer_template: str = """
    <div class="buttons is-centered">
       {% for button in header_buttons %}
       {{ button }}
       {% endfor %}
    </div>
    """


class ReadView(ActionsMixinForView, TemplateMixinForView, View):
    """List view."""

    code: str = 'read'

    def set_body_template(self, feretui, form) -> None:
        root = SubElement(form, 'div')
        root.set('class', 'columns')
        div = SubElement(root, 'div')
        div.set('class', 'column')
        super().set_body_template(feretui, div)
        if len(self.actions):
            div = SubElement(root, 'div')
            div.set('class', 'column is-2')
            div.text = """
                {% for action in actions %}
                {{ action }}
                {% endfor %}
            """

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
        res = super().render_kwargs(feretui, session, options)
        pk = options.get('pk')
        if isinstance(pk, list):
            pk = pk[0]

        # if not pk:
        #     raise ViewError()

        res.update({
            'actions': self.get_actions(feretui, session),
            'form': self.resource.read(self.form_cls, pk),
        })
        return res

    def get_header_buttons(
        self: "ReadView",
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
                        pk=None,
                        view=self.create_button_redirect_to,
                    ),
                )),
            )
        if self.edit_button_redirect_to:
            res.append(
                Markup(feretui.render_template(
                    session,
                    'view-goto-edit-button',
                    edit_view_qs=self.get_transition_querystring(
                        options,
                        view=self.edit_button_redirect_to,
                    ),
                )),
            )
        if self.delete_button_redirect_to:
            res.append(
                Markup(feretui.render_template(
                    session,
                    'view-goto-delete-button',
                    delete_view_qs=self.get_transition_querystring(
                        options,
                        view=self.delete_button_redirect_to,
                    ),
                )),
            )
        if self.return_button_redirect_to:
            res.append(
                Markup(feretui.render_template(
                    session,
                    'view-goto-return-button',
                    return_view_qs=self.get_transition_querystring(
                        options,
                        pk=None,
                        view=self.return_button_redirect_to,
                    ),
                )),
            )

        return res

    def get_call_kwargs(self: "ReadView", request: Request) -> dict:
        """Return the kwargs of the call method."""
        res = super().get_call_kwargs(request)
        qs = request.get_query_string_from_current_url()
        pks = qs.get('pk')
        if not pks:
            raise Exception

        res['pks'] = pks
        return res


class RResource:
    """LResource class."""

    MetaViewRead = DefaultViewRead

    def build_view(
        self: "RResource",
        view_cls_name: str,
    ) -> Resource:
        """Return the view instance in fonction of the MetaView attributes.

        :param view_cls_name: name of the meta attribute
        :type view_cls_name: str
        :return: An instance of the view
        :rtype: :class:`feretui.resources.view.View`
        """
        if view_cls_name.startswith('MetaViewRead'):
            meta_view_cls = self.get_meta_view_class(view_cls_name)
            meta_view_cls.append(ReadView)
            view_cls = type(
                'ReadView',
                tuple(meta_view_cls),
                {},
            )
            if not self.default_view:
                self.default_view = view_cls.code

            return view_cls(self)

        return super().build_view(view_cls_name)
