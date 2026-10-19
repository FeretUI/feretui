.. This file is a part of the FeretUI project
..
..    Copyright (C) 2026 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

Widgets and Form Components
===========================

FeretUI provides a comprehensive system of widgets and reactive forms built around `WTForms <https://wtforms.readthedocs.io/>`_, **Pico CSS v2**, and **HTMX**.

This architecture powers rich ERP and business web applications:

* **Zero custom client-side JavaScript**: all validation, recalculation, and workflow logic is written in pure Python.
* **Instant Reactivity (@onchange)**: server-side recomputation with targeted updates via HTMX Out-Of-Band swaps (``hx-swap-oob="true"``).
* **Native Accessibility (RGAA 11.5)**: systematic semantic markup (``<fieldset>``, ``<legend>``, ``<nav>``, ARIA attributes).
* **Visual indicator for required fields**: automatic styling matching the primary theme color (via the ``is-link`` class).

---

1. Base Reactive Form: ``FeretUIForm``
--------------------------------------

All FeretUI forms inherit from the base class :class:`feretui.form.FeretUIForm` (which extends ``wtforms.form.Form``).

This class enhances WTForms with:

1. Automatic multilingual translation via FeretUI's translation catalogs.
2. Automatic field wrapping with semantic labels and error containers.
3. The reactive event engine :func:`~feretui.form.onchange`.
4. Dynamic warning messages (``onchange_warning``).

Simple Form Example::

    from feretui.form import FeretUIForm
    from wtforms import StringField, DecimalField, IntegerField
    from wtforms.validators import InputRequired, NumberRange

    class ProductForm(FeretUIForm):
        code = StringField("Product Code", validators=[InputRequired()])
        label = StringField("Description", validators=[InputRequired()])
        unit_price = DecimalField("Unit Price (€)", validators=[InputRequired(), NumberRange(min=0)])
        stock_qty = IntegerField("Initial Stock", default=0)

---

2. Workflow Pipeline: ``StatusBarWidget`` & ``StatusBarField``
--------------------------------------------------------------

The :class:`~feretui.form.StatusBarField` field and its companion widget :class:`~feretui.form.StatusBarWidget` render an ERP workflow stage banner (e.g. *Draft* → *Confirmed* → *Processing* → *Delivered*).

.. code-block:: python

    from feretui.form import FeretUIForm, StatusBarField
    from wtforms import StringField

    class SaleOrderForm(FeretUIForm):
        status = StatusBarField(
            "Workflow Status",
            choices=[
                ("draft", "Draft"),
                ("confirmed", "Confirmed"),
                ("processing", "Processing"),
                ("delivered", "Delivered"),
                ("cancelled", "Cancelled"),
            ],
            default="draft",
            clickable=True,
        )
        notes = StringField("Internal Notes")

Visual States and CSS Classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The widget dynamically calculates the position of each stage relative to the active stage:

.. list-table::
   :widths: 25 25 50
   :header-rows: 1

   * - State
     - Applied CSS Classes
     - Description and ARIA
   * - Active stage
     - ``.is-current``, ``.current``
     - Currently active stage, marked with ``aria-current="step"``.
   * - Passed stages
     - ``.is-passed``, ``.passed``
     - Previous stages already completed in the sequence.
   * - Future stages
     - ``.is-future``, ``.future``
     - Upcoming stages in the workflow pipeline.

Read vs Edit Behavior
~~~~~~~~~~~~~~~~~~~~~~

* **In read-only mode** (:class:`~feretui.resources.read.ReadView` or ``clickable=False``):
  Stages appear as sequential non-clickable badges (``<button disabled>``).
* **In edit mode** (:class:`~feretui.resources.create.CreateView` or :class:`~feretui.resources.update.UpdateView`):
  Each stage acts as an interactive button. Clicking a step updates the hidden ``<input type="hidden">`` and dispatches a standard JavaScript ``change`` event intercepted by HTMX.

---

3. Relational Fields: ``Many2OneField`` & ``One2ManyField``
-----------------------------------------------------------

FeretUI provides first-class relational fields designed for business ERP applications:

* :class:`~feretui.form.Many2OneField`: Foreign-key style field pointing to another resource.
  - **In Read Mode**: Renders a clickable navigation link with an external arrow icon (``<i class="ti ti-arrow-up-right"></i>``) taking the user directly to the target record's read view.
  - **In Edit Mode**: Renders a dropdown ``<select>`` accompanied by a quick jump button (``↗``) to inspect the selected record.
* :class:`~feretui.form.One2ManyField`: One-to-Many or Many-to-Many relationship rendered as an embedded interactive sub-table.
  - Takes a list of column tuples ``[("field_name", "Header Label"), ...]``.
  - Connects to a ``target_resource`` to provide direct navigation links on each row.
  - Automatically adapts to both lists of dictionaries and lists of ORM objects.
* :class:`~feretui.form.HiddenField`: Renders directly as ``<input type="hidden">`` without surrounding labels or wrapper divs, ideal for primary keys (``pk``).

Relational Form Example::

    from feretui.form import FeretUIForm, Many2OneField, One2ManyField, HiddenField
    from wtforms import StringField

    class SaleOrderForm(FeretUIForm):
        pk = HiddenField("ID")
        order_ref = StringField("Order Reference")
        customer_id = Many2OneField(
            "Customer",
            resource="customers",
            choices=get_customer_choices,
        )
        lines = One2ManyField(
            "Order Lines",
            columns=[
                ("product_name", "Product"),
                ("qty", "Qty"),
                ("unit_price", "Unit Price (€)"),
                ("subtotal", "Subtotal (€)"),
            ],
            target_resource="products",
        )

---

4. Reactive Calculations with ``@onchange`` & Out-Of-Band Swaps
---------------------------------------------------------------

The :func:`feretui.form.onchange` decorator synchronizes and recalculates form fields on the server whenever an observed field value changes in the browser.

How It Works
~~~~~~~~~~~~

1. The user changes an input field in the browser (e.g. quantity or unit price).
2. The ``change`` event triggers an HTMX request to ``/feretui/action/onchange``.
3. FeretUI runs the decorated Python method on the server.
4. Only fields whose values were modified by the method are returned with ``hx-swap-oob="true"``.
5. The browser DOM is updated instantly without a full-page reload.

Complete Recalculation and Warning Example::

    from feretui.form import FeretUIForm, onchange
    from wtforms import DecimalField, IntegerField, StringField
    from wtforms.validators import InputRequired

    class OrderLineForm(FeretUIForm):
        quantity = IntegerField("Quantity", default=1, validators=[InputRequired()])
        unit_price = DecimalField("Unit Price", default=0.0)
        discount_rate = DecimalField("Discount (%)", default=0.0)
        total_amount = DecimalField("Total (€)", default=0.0)
        warning_msg = StringField("Warning")

        @onchange("quantity", "unit_price", "discount_rate")
        def _calc_total(self) -> None:
            qty = self.quantity.data or 0
            price = self.unit_price.data or 0.0
            discount = self.discount_rate.data or 0.0

            subtotal = float(qty) * float(price)
            if discount > 0:
                subtotal *= (1.0 - (float(discount) / 100.0))

            self.total_amount.data = round(subtotal, 2)

            if discount > 50:
                self.onchange_warning = "Warning: granted discount exceeds 50%!"

---

5. Field Wrappers & RGAA 11.5 Accessibility
--------------------------------------------

In FeretUI, each WTForms field is rendered through a dedicated wrapper function configured in ``FeretUIForm.WRAPPERS``.

Wrappers Table
~~~~~~~~~~~~~~

.. list-table::
   :widths: 30 25 45
   :header-rows: 1

   * - Wrapper Function
     - Associated Field Type
     - Role and Behavior
   * - :func:`~feretui.form.wrap_input`
     - *(default)*, ``StringField``, ``IntegerField``, ``DateField``, etc.
     - Wraps widget in a field container with label, description, and errors. Adds ``is-link`` if required.
   * - :func:`~feretui.form.wrap_bool`
     - ``BooleanField``
     - Checkbox rendering with adjacent label.
   * - :func:`~feretui.form.wrap_radio`
     - ``RadioField``
     - Radio button list for mutually exclusive choices.
   * - :func:`~feretui.form.wrap_fieldset`
     - ``FormField``
     - Groups nested sub-fields inside a ``<fieldset>`` with a ``<legend>``.
   * - :func:`~feretui.form.wrap_select_multiple`
     - ``SelectMultipleField``
     - Displays multiple choices as a checklist of checkboxes inside a ``<fieldset>``.
   * - :func:`~feretui.form.wrap_status_bar`
     - :class:`~feretui.form.StatusBarField`
     - Wraps the workflow pipeline with support for Out-Of-Band swaps.
   * - :func:`~feretui.form.wrap_many2one`
     - :class:`~feretui.form.Many2OneField`
     - Clickable link with navigation arrow in read mode; select + jump button in edit mode.
   * - :func:`~feretui.form.wrap_one2many`
     - :class:`~feretui.form.One2ManyField`
     - Embedded sub-table with row navigation.
   * - :func:`~feretui.form.wrap_hidden`
     - ``HiddenField``
     - Invisible input rendered without label or wrapper div.
   * - :func:`~feretui.form.no_wrap`
     - ``SelectFieldBase._Option``
     - Renders raw widget without wrapper div.

RGAA 11.5 Compliance (Field Grouping)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The **RGAA 11.5** accessibility criterion requires that groups of related form controls must be grouped inside a ``<fieldset>`` element with an explicit ``<legend>``.

FeretUI enforces this rule automatically:
* For nested forms using ``FormField``.
* For multi-select checkbox lists using ``SelectMultipleField``.

---

6. Supported Field Types and Validators
---------------------------------------

FeretUI supports all standard WTForms fields as well as custom business fields:

Text and Secure Inputs
~~~~~~~~~~~~~~~~~~~~~~

* ``StringField``: Single-line text input.
* ``TextAreaField``: Multi-line text input (notes, comments).
* ``PasswordField``: Obfuscated password input.
* ``HiddenField``: Hidden technical input (e.g. primary key ``pk``).

Robust Password Validator: :class:`~feretui.form.Password`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FeretUI provides a password validator enforcing cybersecurity standards:

.. code-block:: python

    from feretui.form import FeretUIForm, Password
    from wtforms import PasswordField

    class UserCredentialsForm(FeretUIForm):
        password = PasswordField(
            "Password",
            validators=[Password(min=12, max=64)],
        )

The validator verifies that passwords contain:
* Minimum length (12 characters by default).
* Both uppercase and lowercase letters.
* Numbers (0-9).
* Symbols or special characters.

Numeric, Dates, and Choice Fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``IntegerField``, ``FloatField``, ``DecimalField``: Numbers with range validation (``NumberRange``).
* ``DateField``, ``DateTimeLocalField``: HTML5 date and datetime pickers.
* ``SelectField``: Dropdown menu for single selection.
* ``RadioField``: Radio buttons for exclusive selection.
* ``BooleanField``: Boolean checkbox.
* ``StatusBarField``: Interactive workflow pipeline.
* ``Many2OneField``: Foreign key relational field with link navigation.
* ``One2ManyField``: Embedded sub-table for related records.
* ``WYSIWYGField`` (aliases: ``RichTextField``, ``HtmlField``): Built-in rich-text / HTML editor.

WYSIWYG and Rich-Text Editor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For CMS, descriptions, email bodies, and formatted content, FeretUI includes a lightweight, native WYSIWYG editor :class:`~feretui.form.WYSIWYGField` (also accessible via aliases ``RichTextField`` and ``HtmlField``).

.. code-block:: python

    from feretui.form import FeretUIForm, WYSIWYGField

    class ArticleForm(FeretUIForm):
        content = WYSIWYGField(
            "Article Body",
            min_height="300px",
            placeholder="Compose your rich text here...",
        )

Key Features:

* **Zero external runtime dependency**: 100% theme-aware using Pico CSS v2 and Tabler icons.
* **Formatting toolbar**: Bold, Italic, Underline, Strikethrough, Headings (H1, H2, H3), Paragraph, Bullet / Numbered lists, Blockquotes, Preformatted code, and Links.
* **Seamless sync**: Updates an underlying hidden ``<textarea>`` automatically on change and blur, integrating with standard form POST and HTMX triggers.
* **Read-only preview**: Renders formatted HTML securely inside a styled container when the view is in read-only mode.

---

7. Business Actions and Action Widgets
--------------------------------------

In resource views, actions represent buttons that trigger Python methods or navigation.

.. list-table::
   :widths: 35 65
   :header-rows: 1

   * - Action Class
     - Description and Role
   * - :class:`~feretui.resources.actions.Action`
     - Button triggering a Python method on the resource object via HTMX.
   * - :class:`~feretui.resources.actions.Actionset`
     - Dropdown menu grouping multiple actions under a single label.
   * - :class:`~feretui.resources.actions.GotoViewAction`
     - Button navigating to a specific view (e.g. print or duplicate).
   * - :class:`~feretui.resources.actions.SelectedRowsAction`
     - Batch action in :class:`~feretui.resources.list.ListView`, enabled only when rows are selected.

Example Declaration in ``MetaViewRead``::

    from feretui.resources.actions import Action, Actionset, GotoViewAction

    class MetaViewRead:
        actions = [
            Action("Confirm Order", "action_confirm", icon="ti ti-check"),
            Actionset("Advanced Options", [
                GotoViewAction("Duplicate", "duplicate", icon="ti ti-copy"),
                Action("Send by Email", "send_email", icon="ti ti-mail"),
            ]),
        ]

---

8. ERP Keyboard Shortcuts
-------------------------

FeretUI includes global keyboard shortcuts to speed up routine tasks:

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Shortcut
     - Associated Action
   * - ``Alt + N``
     - **New**: Opens the creation form for the active resource.
   * - ``Ctrl + S``
     - **Save**: Submits and saves the active form.
   * - ``Alt + F``
     - **Search / Filter**: Immediately focuses the search input.
   * - ``Escape`` (Échap)
     - **Cancel / Return**: Cancels current editing and returns to the previous view.
