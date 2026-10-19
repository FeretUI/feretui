.. This file is a part of the FeretUI project
..
..    Copyright (C) 2026 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

StatusBar & Reactive @onchange
------------------------------

FeretUI provides workflow widgets and reactive client-server recalculations with zero custom JavaScript.

~~~~~~~~~~~~~~~~~~~~~~~~
StatusBar Widget & Field
~~~~~~~~~~~~~~~~~~~~~~~~

:class:`feretui.form.StatusBarField` renders an ERP workflow pipeline banner (e.g. *Draft* → *In Progress* → *Done* → *Cancelled*).

.. code-block:: python

    from feretui.form import FeretUIForm, StatusBarField
    from wtforms import StringField

    class OrderForm(FeretUIForm):
        status = StatusBarField(
            "Workflow Status",
            choices=[
                ("draft", "Draft"),
                ("in_progress", "In Progress"),
                ("done", "Done"),
                ("cancelled", "Cancelled"),
            ],
            default="draft",
        )
        notes = StringField("Notes")

In read mode, stages appear as sequential badges highlighting the active stage. In edit mode, stages act as interactive state-transition buttons.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Reactive Calculations with ``@onchange``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FeretUI supports reactive form recalculations using the :func:`feretui.form.onchange` decorator.
When an observed field changes in the browser, HTMX automatically posts to ``/feretui/action/onchange``, runs the decorated Python method, and updates only the modified fields using out-of-band swaps (``hx-swap-oob="true"``).

.. code-block:: python

    from feretui.form import FeretUIForm, onchange
    from wtforms import FloatField, IntegerField

    class LineItemForm(FeretUIForm):
        qty = IntegerField("Quantity", default=1)
        unit_price = FloatField("Unit Price", default=0.0)
        total_amount = FloatField("Total", default=0.0)

        @onchange("qty", "unit_price")
        def _recalculate_total(self) -> None:
            q = int(self.qty.data or 0)
            p = float(self.unit_price.data or 0.0)
            self.total_amount.data = round(q * p, 2)

Benefits:

1. **Python Single Source of Truth**: Calculation and business logic live strictly on the server in Python.
2. **Instant User Feedback**: UI is refreshed automatically via HTMX without full-page reloads.
3. **No custom client-side JavaScript**: WTForms and FeretUI manage all input binding and validation.
