.. This file is a part of the FeretUI project
..
..    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

Getting Started
===============

------------
Installation
------------

FeretUI needs some dependencies system::

    sudo npm install -g less


Install released versions of FeretUI from the Python package index with
`pip <http://pypi.python.org/pypi/pip>`_ or a similar tool::

    pip install feretui (Not ready yet)

Installation via source distribution is via the ``pyproject.toml`` script::

    pip install .

Installation will add the ``feretui`` commands to the environment.

.. note:: FeretUI use Python version >= 3.10


--------------------------------
Install your favorite web server
--------------------------------

FeretUI come without any web server. The web serving is not this job.

.. include:: routes.rst
.. include:: bottle.rst
.. include:: flask.rst
.. include:: pyramid.rst

---------------------------------------
Defined the content of your application
---------------------------------------

It is the FeretUI stuff for your project.

You may defined

* Menu
* page (with form or not)
* action
* resource (set of page and action for a database entries)

.. include:: menus.rst
.. include:: form_page_action.rst
.. include:: resource.rst
.. include:: translation.rst


-------------------------
Install your favorite ORM
-------------------------

FeretUI come without any ORM. It is not this job, It not required to have an ORM.
You can do without directly with SQL or just with full static page.

.. include:: sqlalchemy.rst

--------
Examples
--------

Some `examples <https://github.com/FeretUI/feretui/tree/main/examples>`_ exist.
