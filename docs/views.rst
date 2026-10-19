.. This file is a part of the FeretUI project
..
..    Copyright (C) 2026 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

Views and Business Resources
============================

FeretUI organizes data access into **Resources** composed of multiple coordinated **Views**. Each view corresponds to a specific interaction mode (tabular list, detailed card, input form, confirmation dialog, or Kanban board).

---

1. View Architecture and Mixins
-------------------------------

A resource combines one or more views by inheriting from dedicated mixins:

.. list-table::
   :widths: 20 20 25 35
   :header-rows: 1

   * - Mixin
     - View Class
     - View Code
     - Role
   * - :class:`~feretui.resources.list.LResource`
     - :class:`~feretui.resources.list.ListView`
     - ``"list"``
     - Paginated table with search, filters, and export.
   * - :class:`~feretui.resources.create.CResource`
     - :class:`~feretui.resources.create.CreateView`
     - ``"create"``
     - Form to create a new record.
   * - :class:`~feretui.resources.read.RResource`
     - :class:`~feretui.resources.read.ReadView`
     - ``"read"``
     - Read-only record display with an action bar.
   * - :class:`~feretui.resources.update.UResource`
     - :class:`~feretui.resources.update.UpdateView`
     - ``"update"``
     - Form to edit and update a record.
   * - :class:`~feretui.resources.delete.DResource`
     - :class:`~feretui.resources.delete.DeleteView`
     - ``"delete"``
     - Confirmation screen to delete records.
   * - :class:`~feretui.resources.kanban.KResource`
     - :class:`~feretui.resources.kanban.KanbanView`
     - ``"kanban"``
     - Kanban stage board with SortableJS drag-and-drop.
   * - :class:`~feretui.resources.LCRUDResource`
     - *(shortcut)*
     - *(all)*
     - Shortcut combining List, Create, Read, Update, and Delete.

Example declaration with SQLAlchemy::

    from feretui import FeretUI
    from feretui.contrib.sqla import SQLAlchemyResource
    from feretui.resources.kanban import KResource

    myferet = FeretUI(title="ERP Application")

    @myferet.register_resource()
    class OrderResource(KResource, SQLAlchemyResource):
        code = "orders"
        label = "Orders"
        model = SaleOrder
        session_factory = SessionLocal
        default_view = "kanban"

---

2. List View (ListView) & ``MetaViewList`` Configuration
--------------------------------------------------------

The list view displays records in a responsive table with pagination, sorting, multiple row selection, and filters.

Configurable Options in ``MetaViewList``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 30 20 50
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``limit``
     - ``int``
     - Number of records displayed per page (default: ``20``).
   * - ``enable_export``
     - ``bool``
     - Enables the export button and action (default: ``False``).
   * - ``export_formats``
     - ``list[str]``
     - Supported formats: ``["csv"]`` or ``["csv", "xlsx"]``.
   * - ``do_click_on_entry_redirect_to``
     - ``str``
     - Target view when double-clicking a row (e.g. ``"read"``).
   * - ``create_button_redirect_to``
     - ``str``
     - Target view for the "New" button (default: ``"create"``).
   * - ``Filter``
     - ``class``
     - WTForms subclass defining filter inputs.

Example::

    class MetaViewList:
        limit = 50
        enable_export = True
        export_formats = ["csv", "xlsx"]
        do_click_on_entry_redirect_to = "read"

        class Filter:
            status = SelectField(choices=[("draft", "Draft"), ("done", "Done")])
            customer = StringField("Customer")

---

3. Read View (ReadView) & ``MetaViewRead`` Configuration
--------------------------------------------------------

Displays details of a record in read-only mode.

Configurable Options in ``MetaViewRead``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``actions`` (list): List of business action buttons (:class:`~feretui.resources.actions.Action`, :class:`~feretui.resources.actions.Actionset`, :class:`~feretui.resources.actions.GotoViewAction`).
* ``update_button_redirect_to`` (str): Target view for the "Edit" button (default: ``"update"``).
* ``delete_button_redirect_to`` (str): Target view for the "Delete" button (default: ``"delete"``).
* ``create_button_redirect_to`` (str): Target view for the "New" button (default: ``"create"``).

Example::

    class MetaViewRead:
        actions = [
            Actionset("Actions", [
                GotoViewAction("Duplicate", "duplicate"),
                GotoViewAction("Print", "print_invoice"),
            ]),
        ]

---

4. Form Views: Creation & Update
--------------------------------

* **CreateView** (:class:`~feretui.resources.create.CreateView`):
  * Configured via ``MetaViewCreate``.
  * Options: ``after_create_redirect_to`` (target view after successful creation, e.g. ``"read"``), ``cancel_button_redirect_to`` (target view upon cancellation).
* **UpdateView** (:class:`~feretui.resources.update.UpdateView`):
  * Configured via ``MetaViewUpdate``.
  * Options: ``after_update_redirect_to``, ``cancel_button_redirect_to``.

Example::

    class MetaViewCreate:
        after_create_redirect_to = "read"
        cancel_button_redirect_to = "list"

    class MetaViewUpdate:
        after_update_redirect_to = "read"
        cancel_button_redirect_to = "read"

---

5. Kanban View (KanbanView) & ``MetaViewKanban`` Configuration
--------------------------------------------------------------

The Kanban view tracks a workflow visually through stage columns with drag-and-drop ergonomics.

Configurable Options in ``MetaViewKanban``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``column_field`` (str): Form field name used to group cards into stage columns (default: ``"status"``).
* ``columns`` (list[tuple[str, str]] | None): Explicit list of stages ``[(stage_key, stage_label)]``. Discovered dynamically from field choices or data if omitted.
* ``card_title_field`` (str | None): Form field used as card header title. Defaults to the first non-pk field.
* ``card_body_fields`` (list[str] | None): List of form fields displayed inside the card body.
* ``do_click_on_entry_redirect_to`` (str | None): View code to navigate to upon double-clicking a card (e.g. ``"read"``).

Interactivity and Persistence (SortableJS + HTMX)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a card is moved to a new column:

1. SortableJS intercepts the drop event in the browser.
2. An HTMX HTTP call ``POST /feretui/action/resource?action=move_card`` is sent with ``pk`` and ``stage``.
3. The Python method ``move_card(pk, stage, index)`` on the resource updates the database.
4. **Zero custom JavaScript business logic**.

Example::

    class MetaViewKanban:
        column_field = "status"
        card_title_field = "order_ref"
        card_body_fields = ["customer_name", "total_amount"]
        do_click_on_entry_redirect_to = "read"

---

6. Delete View (DeleteView) & ``MetaViewDelete`` Configuration
--------------------------------------------------------------

The delete view (:class:`~feretui.resources.delete.DeleteView`) renders a confirmation screen listing the records to delete (identified by their primary keys ``pk``).

Configurable Options in ``MetaViewDelete``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``label`` (str): Title of the delete confirmation screen (default: ``"Delete"``).
* ``after_delete_redirect_to`` (str | None): Target view after successful deletion (typically ``"list"``).

Example::

    class MetaViewDelete:
        after_delete_redirect_to = "list"

---

7. Multi-Views & View Switching (MultiView)
-------------------------------------------

A resource can combine multiple display views (for example, a tabular list view and a Kanban board view).

* The ``default_view`` attribute defines the initial view opened by default (e.g. ``default_view = "kanban"`` or ``default_view = "list"``).
* Header buttons generated by :class:`~feretui.resources.common.MultiView` allow instant view switching via HTMX without full-page reloads.

Example::

    @myferet.register_resource()
    class ProjectTaskResource(KResource, LCRUDResource, SQLAlchemyResource):
        code = "tasks"
        label = "Tasks"
        model = ProjectTask
        session_factory = SessionLocal
        default_view = "kanban"

---

8. Form Declaration and Inheritance in Views
--------------------------------------------

In FeretUI, each resource and view can declare its fields via an inner ``Form`` class:

1. **Global Resource Form**: defined at the resource class level (shared fields across all views).
2. **View-Specific Form**: defined inside the ``MetaView*`` class (adds or overrides fields for that specific view).
3. **Filter Form**: defined via ``Filter`` inside ``MetaViewList`` for multi-criteria searching.

Example::

    class TaskResource(LCRUDResource, SQLAlchemyResource):
        code = "tasks"
        label = "Tasks"

        # Common fields across all views (Create, Read, Update, List)
        class Form:
            title = StringField("Title", validators=[InputRequired()])
            description = TextAreaField("Description")
            status = StatusBarField("Status", choices=[
                ("draft", "Draft"),
                ("in_progress", "In Progress"),
                ("done", "Done"),
            ])

        # Customization for the list view
        class MetaViewList:
            limit = 25
            class Filter:
                status = SelectField("Status", choices=[("", "All"), ("in_progress", "In Progress")])

---

9. Custom Views
---------------

Entirely custom views can be implemented by subclassing :class:`feretui.resources.view.View` or :class:`~feretui.resources.update.DefaultViewUpdate`:

.. code-block:: python

    from feretui.resources.update import DefaultViewUpdate

    class MetaViewUpdatePassword(DefaultViewUpdate):
        code = "update_password"
        after_update_redirect_to = "read"
        cancel_button_redirect_to = "read"

        header_template = """
        <h1>Update Password for {{ form.pk.data }}</h1>
        """

        body_template = """
        <div class="container mb-4">
          {{ form.password }}
          {{ form.password_confirm }}
        </div>
        """

---

10. Modern ERP Sheet Forms & Smart Buttons
------------------------------------------

FeretUI introduces dedicated ERP sheet templates that present records as cohesive, paper-like cards:

* ``body_template_id = "view-sheet-readonly-form"``: Read-only sheet layout.
* ``body_template_id = "view-sheet-readwrite-form"``: Editable sheet layout.

Key Features of the Sheet Layout:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Hides Technical IDs**: Technical primary keys (``pk`` or ``HiddenField``) are hidden from the visual interface (kept in hidden inputs during editing for seamless form submission).
2. **Human Record Header**: The header displays the record's natural identity (e.g. order reference, title, or customer name) rather than an arbitrary integer ID.
3. **Smart Stat Buttons**: Resources can define a ``get_smart_buttons()`` method to render clickable badge counters at the top right of the sheet (e.g. linked orders, invoices, or delivery slips).
4. **Responsive 2-Column Grid**: Standard inputs (strings, numbers, selects, many2one relations) are neatly organized side by side in a responsive 2-column grid (``.feretui-form-grid``).
5. **Full-Width Relational Sub-Tables**: Notes, textareas, and embedded ``One2ManyField`` sub-tables automatically stretch across the full width below the grid.

Example Configuration::

    @myferet.register_resource()
    class CustomerResource(SQLAlchemyResource):
        code = "customers"
        label = "Customers"
        model = Customer
        Form = CustomerForm

        class MetaViewRead:
            body_template_id = "view-sheet-readonly-form"

        class MetaViewEdit:
            body_template_id = "view-sheet-readwrite-form"

        def get_smart_buttons(self, form, feretui, session):
            return [
                {
                    "label": "Orders",
                    "count": len(form.orders.data or []),
                    "icon": "ti ti-shopping-cart",
                    "url": "/?page=resource&resource=orders&view=list",
                },
            ]

