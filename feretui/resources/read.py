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

    myferet.register_resource(
    )
    class MyResource(LResource, Resource):
        code = 'code of the resource',
        label = 'label',

        class MetaViewList:
            pass
"""
from lxml.etree import SubElement
from typing import TYPE_CHECKING

# from markupsafe import Markup
# from polib import POFile

from feretui.resources.common import (
    ActionsMixinForView,
    TemplateMixinForView,
)
from feretui.resources.view import View
from feretui.session import Session

# from feretui.thread import local

from .resource import Resource

if TYPE_CHECKING:
    from feretui.feretui import FeretUI
    # from feretui.translation import Translation


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

    def set_body_template(self, feretui, form):
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
        res.update({
            'actions': self.get_actions(feretui, session)
        })
        return res

    # def export_catalog(
    #     self: "ListView",
    #     translation: "Translation",
    #     po: POFile,
    # ) -> None:
    #     """Export the translations in the catalog.

    #     :param translation: The translation instance to add also inside it.
    #     :type translation: :class:`.Translation`
    #     :param po: The catalog instance
    #     :type po: PoFile_
    #     """
    #     super().export_catalog(translation, po)

    # def get_call_kwargs(self: "ListView", params: dict) -> dict:
    #     """Return the kwargs of the call method."""
    #     res = super().get_call_kwargs(params)
    #     key = f'selected-rows-resource-{self.resource.code}-view-{self.code}'
    #     if key in params:
    #         res['pks'] = params[key]

    #     return res

    # def render(
    #     self: "ListView",
    #     feretui: "FeretUI",
    #     session: Session,
    #     options: dict,
    # ) -> str:
    #     """Render the view.

    #     :param feretui: The feretui client
    #     :type feretui: :class:`feretui.feretui.FeretUI`
    #     :param session: The Session
    #     :type session: :class:`feretui.session.Session`
    #     :param options: The options come from the body or the query string
    #     :type options: dict
    #     :return: The html page in
    #     :rtype: str.
    #     """
    #     return feretui.render_template(
    #         session,
    #         'feretui-resource-list',
    #         widget=self.widget,
    #         **self.render_kwargs(feretui, session, options),
    #     )


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
