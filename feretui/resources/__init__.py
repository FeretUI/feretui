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

* :class:`.LCRUDResource`

The decorator :meth:`feretui.feretui.FeretUI.register_resource` call the
:meth:`feretui.resources.resource.Resource.build` method and register
the resource in feretui.

::

    @myferet.register_resource()
    class MyResource(Resource):
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
from feretui.resources.resource import Resource  # noqa: F401


class LCRUDResource:
    """LCRUDResource class.

    This class is a mixin, it inherit the mixins:

    *

    """
