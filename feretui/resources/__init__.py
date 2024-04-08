# This file is a part of the FeretUI project
#
#    Copyright (C) 2023-2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Resource modules.

The resource is generally a set of views (page and form). This view construct
the page and define the render and the action for the resource.

To help the contruction of the view some mixins exist:

* :class:`feretui.resources.list.LResource`
* :class:`feretui.resources.read.RResource`
* :class:`.LCRUDResource`

The decorator :meth:`feretui.feretui.FeretUI.register_resource` call the
:meth:`feretui.resources.resource.Resource.build` method and register
the resource in feretui.

::

    @myferet.register_resource()
    class MyResource(LResouce, Resource):
        code = 'the identifier of the resource'
        label = 'The label'


To add the resource in the toolbar menu, an attribute exist in the Resource
class (only if build).

::

    myferet.register_toolbar_left_menus([
        MyResource.menu,
    ])
"""
from feretui.resources.actions import (  # noqa: F401
    Action,
    Actionset,
    SelectedRowsAction,
)
from feretui.resources.list import LResource  # noqa: F401
from feretui.resources.read import RResource  # noqa: F401
from feretui.resources.resource import Resource  # noqa: F401


class LCRUDResource(LResource, RResource):
    """LCRUDResource class.

    This class is a mixin, it inherit the mixins:

    *

    """

    default_view = 'list'

    class MetaViewList:
        """Meta view class for list."""

        create_button_redirect_to: str = 'create'
        delete_button_redirect_to: str = 'delete'
        do_click_on_entry_redirect_to: str = 'read'

    class MetaViewRead:
        """Meta view class for list."""

        create_button_redirect_to: str = 'create'
        delete_button_redirect_to: str = 'delete'
        edit_button_redirect_to: str = 'edit'
        return_button_redirect_to: str = 'list'
