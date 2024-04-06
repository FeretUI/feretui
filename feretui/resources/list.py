# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Module feretui.resource.

The resource is a set of View to représente one data.

* :class:`.Resource`

::

    myferet.register_resource(
        'code of the resource',
        'label',
    )
    class MyResource(Resource):
        pass
"""
from typing import TYPE_CHECKING

from markupsafe import Markup
from polib import POFile
from wtforms.fields import Field

from feretui.resources.common import MultiView

# from feretui.exceptions import ResourceError
# from feretui.request import Request
# from feretui.response import Response
# from feretui.session import Session
from feretui.resources.view import View
# from feretui.response import Response
from feretui.thread import local

from .resource import Resource

if TYPE_CHECKING:
    # from feretui.feretui import FeretUI
    from feretui.translation import Translation


def span_widget(field):
    data = field.data
    if hasattr(field, 'choices'):
        for choice in field.choices:
            if choice[0] == data:
                data = choice[1]
                break

    return Markup(f'<span>{ data }</span>')


class DefaultViewList:
    label: str = None
    limit: int = 20
    create_button_redirect_to: str = None
    delete_button_redirect_to: str = None
    do_click_on_entry_redirect_to: str = None


class ListView(MultiView, View):
    code: str = 'list'
    WIDGETS: dict[str, Field] = {}

    def get_label(self: "View") -> str:
        """Return the translated label."""
        if not self.label:
            return super().get_label()

        return local.feretui.translation.get(
            local.lang, f'{self.context}:label', self.label,
        )

    def export_catalog(
        self: "Resource",
        translation: "Translation",
        po: POFile,
    ) -> None:
        """Export the translations in the catalog.

        :param translation: The translation instance to add also inside it.
        :type translation: :class:`.Translation`
        :param po: The catalog instance
        :type po: PoFile_
        """
        if self.label:
            po.append(translation.define(f'{self.context}:label', self.label))

    def widget(self, field, **kwargs):
        return self.WIDGETS.get(field.__class__, span_widget)(field, **kwargs)

    def get_call_kwargs(self, params):
        res = super().get_call_kwargs(params)
        key = f'selected-rows-resource-{self.resource.code}-view-{self.code}'
        if key in params:
            res['pks'] = params[key]

        return res

    def get_header_buttons(self, feretui, session, options):
        res = super().get_header_buttons(feretui, session, options)
        if self.delete_button_redirect_to:
            res.append(
                Markup(feretui.render_template(
                    session,
                    'view-delete-button',
                    delete_view_qs=self.get_transition_querystring(
                        options,
                        view=self.delete_button_redirect_to,
                    ),
                    rcode=self.resource.code,
                    vcode=self.code,
                )),
            )

        return res

    def render(
        self,
        feretui,
        session,
        options: dict,
    ) -> str:
        return feretui.render_template(
            session,
            'feretui-resource-list',
            widget=self.widget,
            **self.render_kwargs(feretui, session, options)
        )


class LResource:
    default_view = 'list'

    MetaViewList = DefaultViewList

    def build_view(
        self: "LResource",
        view_cls_name: str,
    ) -> Resource:
        if view_cls_name.startswith('MetaViewList'):
            meta_view_cls = self.get_meta_view_class(view_cls_name)
            meta_view_cls.append(ListView)
            view_cls = type(
                'ListView',
                tuple(meta_view_cls),
                {},
            )
            if not self.default_view:
                self.default_view = view_cls.code

            return view_cls(self)

        return super().build_view(view_cls_name, view_cls)
