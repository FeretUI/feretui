# This file is a part of the FeretUI project
#
#    Copyright (C) 2023-2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Feretui.

Small web client to build an admin user interface without any link with a
framework.

This project is not a nodejs project. The client is generated with static
templates. The javascrip library `htmx <https://htmx.org>`_ to improve the
capability to manipulate the DOM and to add HTTP verb (DELETE, PUT, PATCH).

The client is not a Framework, and don't use any web-server, orm, connector
Frameworks. The goal is to separate the concept between both.

In a classical project the database, the ORM model's and the user interface
is declared on the same place. They are both the same configuration. But It is
a mistake, because that limit the possibility and force to have only entry
point by the user interface. The rules as *required*, *readonly*, ... should
be depending only on the user-interface. It is possible to define an interface
based on more than one Model, or with another constraints.

To isolate it about the web-server projects, This project add objects to do
absctract with web server:

* :class:`feretui.response.Response`: It is the class object used by FeretUI
  to respond at the client query.

::

    from feretui import FeretUI


    myferet = FeretUI()


"""
from feretui.response import Response  # noqa : F401
