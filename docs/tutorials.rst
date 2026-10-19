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

FeretUI is **100% pure Python** and requires zero Node.js or npm dependencies.
Styling is powered by **Pico CSS v2** with a built-in Python CSS compressor and Tabler Icons.

Install FeretUI from source or via pip::

    pip install .

Installation will add the ``feretui`` commands to the environment.

.. note:: FeretUI requires Python >= 3.10


--------------------------------
Install your favorite web server
--------------------------------

FeretUI come without any web server. The web serving is not this job.

.. include:: routes.rst
.. include:: bottle.rst
.. include:: flask.rst
.. include:: pyramid.rst
.. include:: django-routes.rst
.. include:: starlette.rst

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
.. include:: kanban.rst
.. include:: status.rst
.. include:: translation.rst


-------------------------
Install your favorite ORM
-------------------------

FeretUI come without any ORM. It is not this job, It not required to have an ORM.
You can do without directly with SQL or just with full static page.

.. include:: sqlalchemy.rst
.. include:: django-orm.rst

--------
Examples
--------

Mini-ERP
--------

A complete **Mini-ERP** demonstration application is provided in the repository under ``examples/mini_erp/``:

* Shows **SQLAlchemyResource** automated CRUD and filtering.
* Demonstrates **Kanban view** with drag-and-drop powered by SortableJS.
* Demonstrates **StatusBarField** workflow pipelines.
* Demonstrates reactive **@onchange** recalculations with HTMX.
* Demonstrates **Universal Exports** (CSV and Excel XLSX).
* Demonstrates **Starlette** ASGI integration.

For a full step-by-step walkthrough and architectural details, see the `Mini-ERP README <https://github.com/FeretUI/feretui/blob/main/examples/mini_erp/README.md>`_ (local file: `examples/mini_erp/README.md <../examples/mini_erp/README.md>`_).

To run the Mini-ERP locally:

.. code-block:: bash

    cd examples/mini_erp
    python app.py

Then open your browser at ``http://localhost:8000``.

Mini-CMS
--------

A complete **Mini-CMS** demonstration application is provided in the repository under ``examples/mini_cms/``:

* Shows **WYSIWYGField** rich-text editing with a native toolbar and clean HTML output.
* Demonstrates an **Editorial Kanban Desk** grouping articles by publication status (*Draft* → *Under Review* → *Published* → *Archived*).
* Demonstrates reactive **@onchange** auto-slugification from article titles.
* Demonstrates **One2ManyField** articles sub-tables and **Many2OneField** category links.
* Demonstrates **Category Stat / Smart Buttons** on form headers.

For the full step-by-step tutorial, see :doc:`how_to_make_a_cms` or the `Mini-CMS README <https://github.com/FeretUI/feretui/blob/main/examples/mini_cms/README.md>`_.

To run the Mini-CMS locally:

.. code-block:: bash

    cd examples/mini_cms
    python app.py

Then open your browser at ``http://localhost:8000``.


