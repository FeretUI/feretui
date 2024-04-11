.. This file is a part of the FeretUI project
..
..    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

The routes to serve FeretUI
---------------------------

We need 3 routes :

* [GET] client route
* [GET] static files route
* [GET, POST, PATCH, PUT, DELETE] action route.

.. note::

    The GET, POST, DELETE is the minimum method to use the actions.
    The other is to add only if you need custom form with theses methods.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Request, Response and Session
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The objects Request, Response and Session are wrapper class. The goal is to
séparate and link the three object come from web server to FeretUI.

FeretUI can not know all the web server and can not be adapted for each. We need
a link between them. The responsability to do the link is yours.

Some exemple exist and can copy it or adapt it for your projects.

* :class:`feretui.request.Request`
* :class:`feretui.response.Response`
* :class:`feretui.session.Session`

~~~~~~~~~~~~
Client route
~~~~~~~~~~~~

The client route is the route that return the FeretUI client. the route (name and url) is free.

The route should ::

    session = ...  # get the feretui session
    myferet = ...  # get the instance client
    request = Request(session=session, ...)  # get the feretui request
    response = myferet.render(request)  # get the client page
    # return the response formated for the web server

~~~~~~~~~~~~~~~~~~
static files route
~~~~~~~~~~~~~~~~~~

The static files  route is the route that return the javascript, css, font, images.

the url is /*feretui base url*/static/*filepath*

The route should ::

    filepath = ...  # get the file path
    myferet = ...  # get the instance client
    return myferet.get_static_file_path(filepath)  # return the static file

~~~~~~~~~~~~
Action route
~~~~~~~~~~~~

The action route is used to do action on and with the FeretUI client.

* render page
* execute a page
* ...

the url is /*feretui base url*/static/*action*

The route should ::

    action = ...  # get the action to call
    session = ...  # get the feretui session
    myferet = ...  # get the instance client
    request = Request(session=session, ...)  # get the feretui request
    response = myferet.execute_action(request, action)  # execute the action
    # return the response formated for the web server
