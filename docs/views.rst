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
   * - :class:`~feretui.resources.calendar.CalResource`
     - :class:`~feretui.resources.calendar.CalendarView`
     - ``"calendar"``
     - Interactive monthly calendar for deadlines, events, and bookings.
   * - :class:`~feretui.resources.chatter.HasChatterMixin`
     - *(mixin)*
     - *(form)*
     - Social collaboration, internal notes, activity timeline, and message posting.
   * - :class:`~feretui.resources.grid.GridResource`
     - :class:`~feretui.resources.grid.GridView`
     - ``"grid"``
     - Responsive card gallery / mosaic view with search and pagination.
   * - :class:`~feretui.resources.graph.GResource`
     - :class:`~feretui.resources.graph.GraphView`
     - ``"graph"``
     - Interactive analytics charts (bar, line, pie) and summary pivot table.
   * - :class:`~feretui.resources.LCRUDResource`
     - *(shortcut)*
     - *(all)*
     - Shortcut combining List, Create, Read, Update, and Delete.
   * - :class:`~feretui.resources.KCRUDResource`
     - *(shortcut)*
     - *(all)*
     - Shortcut combining Kanban, Create, Read, Update, and Delete.
   * - :class:`~feretui.resources.LKCRUDResource`
     - *(shortcut)*
     - *(all)*
     - Shortcut combining List, Kanban, and full CRUD.
   * - :class:`~feretui.resources.CalCRUDResource`
     - *(shortcut)*
     - *(all)*
     - Shortcut combining Calendar and full CRUD.
   * - :class:`~feretui.resources.GCRUDResource`
     - *(shortcut)*
     - *(all)*
     - Shortcut combining Graph and full CRUD.

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

---

11. Calendar View: Planning and Deadlines
-----------------------------------------

The Calendar view (:class:`~feretui.resources.calendar.CalendarView`, enabled via :class:`~feretui.resources.calendar.CalResource` or :class:`~feretui.resources.CalCRUDResource`) presents business records as interactive events placed upon a monthly calendar grid.

Key Capabilities:
~~~~~~~~~~~~~~~~~

* **Month Navigation**: Year and month switcher with rollover between adjacent years.
* **Date Parsing**: Automatically handles ``datetime``, ``date``, and standard ISO string formats (``YYYY-MM-DD``).
* **Click-to-Read Navigation**: Clicking an event badge directly opens the record in read mode via HTMX.
* **Configurable Metadata**:

.. code-block:: python

    from feretui import FeretUIForm
    from feretui.resources import CalCRUDResource
    from feretui.contrib.sqla import SQLAlchemyResource
    from wtforms import StringField, DateField

    class TaskForm(FeretUIForm):
        name = StringField("Task Name")
        deadline = DateField("Deadline")
        priority = StringField("Priority")

    @myferet.register_resource()
    class TaskResource(CalCRUDResource, SQLAlchemyResource):
        code = "tasks"
        label = "Task Planning"
        model = Task
        Form = TaskForm

        class MetaViewCalendar:
            date_start_field = "deadline"
            date_stop_field = None          # Optional end date for multi-day events
            title_field = "name"            # Label displayed in the event chip
            color_field = "priority"        # Badge color modifier

---

12. Multi-View Switcher and Top Control Panel
---------------------------------------------

When a resource provides more than one collection view (e.g. List, Kanban, and Calendar), FeretUI automatically generates a responsive **View Switcher** toolbar on the top-right of the control panel:

.. code-block:: html

    <div class="feretui-view-switcher">
      <a class="feretui-view-button is-active" href="/?page=resource&resource=orders&view=kanban">...</a>
      <a class="feretui-view-button" href="/?page=resource&resource=orders&view=list">...</a>
      <a class="feretui-view-button" href="/?page=resource&resource=orders&view=calendar">...</a>
    </div>

Features:
~~~~~~~~~

1. **State Preservation**: Switching views preserves the active filters, search keywords, and pagination limits across view types.
2. **Context-Aware Visibility**: Views whose ``is_visible(session)`` method returns ``False`` are automatically omitted from the switcher.
3. **Deep Linking & HTMX**: Navigation updates the browser address bar with ``hx-push-url="true"`` while updating only the central ``#body`` container.

---

13. Quick Filters and Faceted Search
------------------------------------

The :class:`~feretui.resources.common.QuickFilter` class provides declarative, single-click filter buttons rendered at the top of collection views (List and Kanban).

.. code-block:: python

    from feretui import QuickFilter

    class MetaViewList:
        quick_filters = [
            QuickFilter("In Progress", "status", "in_progress", icon="ti ti-clock"),
            QuickFilter("Done", "status", "done", icon="ti ti-check"),
            QuickFilter("High Priority", "priority", "urgent", icon="ti ti-alert-triangle"),
        ]

Features:
~~~~~~~~~

* **One-Click Toggle**: Clicking an inactive filter adds ``filter[field]=value`` via HTMX POST. Clicking an active filter removes it via HTMX DELETE.
* **Badge Highlighting**: Active filter buttons are styled with primary theme contrast (``.is-active``).
* **Flexible Declarations**: Supports :class:`~feretui.resources.common.QuickFilter` instances, 4-tuples ``("Label", "field", "value", "icon")``, or dictionaries.

---

14. Social Collaboration & Activity Timeline: Chatter
-----------------------------------------------------

The :class:`~feretui.resources.chatter.HasChatterMixin` mixin equips any resource with an integrated communication hub directly underneath the form sheet.

Activating the Chatter:
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from feretui.resources import HasChatterMixin, LCRUDResource
    from feretui.contrib.sqla import SQLAlchemyResource

    @myferet.register_resource()
    class OrderResource(HasChatterMixin, LCRUDResource, SQLAlchemyResource):
        code = "orders"
        label = "Orders"
        model = SaleOrder
        chatter = True  # Activates the chatter panel on readonly & edit sheets

Programmatic Notes & History:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can programmatically record internal notes and activity log entries using :meth:`~feretui.resources.chatter.HasChatterMixin.add_chatter_message`:

.. code-block:: python

    order_resource = myferet.get_resource("orders")

    # Record an automated system audit entry
    order_resource.add_chatter_message(
        pk="101",
        body="Order confirmed and sent to logistics warehouse.",
        author="System",
        msg_type="note",
    )

    # Record a customer communication note
    order_resource.add_chatter_message(
        pk="101",
        body="Customer phoned requesting express Saturday delivery.",
        author="Alice Smith",
        msg_type="message",
    )

Interactive Client Features:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Rich Scribe Area**: Toggle between *Internal Note* (yellow background highlight) and *Public Message*.
2. **Instant HTMX Post**: Submissions hit ``/action/resource?action=chatter_post&pk=...`` and seamlessly prepend the new note to the timeline without page reload.
3. **Audit Trail**: Every message displays the author's initials, name, publication date/time, and icon badge.

---

15. Stackable Modal Dialogs
---------------------------

FeretUI provides a multi-level modal dialog system built on the HTML5 ``<dialog>`` standard and Pico CSS:

Opening a Modal via Action:
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from feretui import OpenModalAction, Actionset

    class MetaViewList:
        actions = [
            Actionset("Quick Create", [
                OpenModalAction(
                    "New Customer",
                    resource="customers",
                    view="create",
                    title="Quick Add Customer",
                    modal_size="normal",  # "small" | "normal" | "large" | "full"
                    icon="ti ti-user-plus",
                ),
            ]),
        ]

Features:
~~~~~~~~~

* **Modal Stacking**: Modals are appended to the root ``#feretui-modal-stack`` container, allowing child dialogs to stack over parent dialogs with automatically managed ``z-index``.
* **Fluid Sizing**: Supports four responsive size variants: ``small`` (450px), ``normal`` (640px), ``large`` (900px), and ``full`` (95vw).
* **Keyboard & Backdrop Closing**: Pressing ``Escape`` or clicking the dark backdrop smoothly closes the topmost modal dialog.
* **Server-Triggered Dismissal**: Backend controllers can emit the ``HX-Trigger: closeModal`` header to instruct the client to dismiss the active dialog after successful creation.

---

16. Graph and Analytics View (GraphView)
----------------------------------------

FeretUI includes built-in business intelligence and reporting through :class:`~feretui.resources.graph.GraphView` and the :class:`~feretui.resources.graph.GResource` mixin.

It generates server-side SVG charts (Bar, Line, Pie) with no heavy front-end charting dependencies, paired with a dynamic summary Pivot Table.

Declaration Example:
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from feretui.resources.graph import GResource
    from feretui.contrib.sqla import SQLAlchemyResource

    class SalesAnalyticsResource(GResource, SQLAlchemyResource):
        code = "sales_analytics"
        label = "Sales Analytics"
        model = SaleOrder
        default_view = "graph"

        class MetaViewGraph:
            graph_type = "bar"  # "bar" | "line" | "pie"
            group_by = "status"
            measure = "total_amount"
            measure_operator = "sum"  # "sum" | "avg" | "count"
            group_by_fields = [
                ("status", "Status"),
                ("salesperson", "Salesperson"),
            ]

Key Capabilities:
~~~~~~~~~~~~~~~~~

* **Instant Chart Switching**: Switch between Bar, Line, and Pie charts directly from the view toolbar.
* **Aggregations**: Automatically computes ``sum``, ``avg``, and ``count`` operations across grouped records.
* **Pivot Table**: Renders an interactive breakdown table detailing each dimension's value, record count, and percentage share.
* **Control Panel Compatibility**: Seamlessly integrated with the real-time search box and dynamic *Group by* dropdown.

---

17. Interactive Assistants and Batch Wizards (WizardResource)
-------------------------------------------------------------

FeretUI provides ephemeral, transient assistants called **Wizards** via :class:`~feretui.resources.wizard.WizardResource`.
Wizards are rendered inside HTML5 ``<dialog>`` stackable modals and enable multi-step workflows, confirmation dialogues, and bulk batch actions across records selected in a list view.

Declaration Example:
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from wtforms import StringField
    from wtforms.validators import InputRequired
    from feretui import FeretUIForm, Response, Session, WizardResource

    class BatchCancelOrderForm(FeretUIForm):
        reason = StringField("Cancellation Reason", validators=[InputRequired()])

    class BatchCancelOrderWizard(WizardResource):
        code = "batch_cancel_orders"
        label = "Cancel Orders"
        title = "Cancel Selected Orders"
        Form = BatchCancelOrderForm
        icon = "ti ti-ban"
        confirm_label = "Confirm Cancellation"
        confirm_icon = "ti ti-ban"

        def get_defaults(self, session: Session, active_ids: list[str]) -> dict[str, Any]:
            return {
                "reason": f"Cancellation requested for {len(active_ids)} order(s)",
            }

        def execute(
            self,
            form: FeretUIForm,
            session: Session,
            active_ids: list[str],
        ) -> Response | None:
            # Execute business logic on selected active_ids...
            return Response(
                "<!-- modal-closed -->",
                status_code=200,
                headers={"HX-Trigger": "closeModal", "HX-Refresh": "true"},
            )

Wiring into a List View:
~~~~~~~~~~~~~~~~~~~~~~~~

To attach a wizard to a list view as a batch action for selected rows, use :class:`~feretui.resources.actions.OpenWizardAction`:

.. code-block:: python

    from feretui import Actionset, OpenWizardAction

    class OrderResource(SQLAlchemyResource):
        ...
        class MetaViewList:
            actions = [
                Actionset(
                    "Batch Actions",
                    [
                        OpenWizardAction(
                            "Batch Cancel",
                            wizard="batch_cancel_orders",
                            title="Cancel Selected Orders",
                            icon="ti ti-ban",
                            for_selected_rows=True,
                        ),
                    ],
                ),
            ]

When users select multiple rows using row checkboxes in the list view and click the batch action button, FeretUI packages the selected IDs into ``active_ids`` and opens the wizard modal with pre-populated contextual defaults.


8. Grid View (Gallery / Mosaic Cards)
--------------------------------------

The :class:`~feretui.resources.grid.GridResource` and :class:`~feretui.resources.grid.GridView` provide a modern, responsive card-based mosaic layout for resources where visual browsing is preferred over tabular density (such as product catalogs, customer directories, employee cards, or asset inventories).

Key Features:
* **Responsive CSS Grid Layout**: Automatically wraps cards using CSS grid with min-card sizing (``grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))``).
* **Direct Navigation**: Clicking any card navigates to the record's detail read/edit view.
* **Integrated View Switcher**: Seamlessly toggles between List, Grid, Kanban, and Calendar views without losing search queries or active filters.
* **Search and Pagination**: Inherits FeretUI's unified ``MultiView`` search, filtering, and page navigation.

Example Declaration::

    from feretui.resources.grid import GridCRUDResource
    from feretui.resources.resource import Resource
    from wtforms import StringField, DecimalField

    class ProductResource(GridCRUDResource, Resource):
        code = "products"
        label = "Products"

        class Form:
            pk = StringField("ID")
            name = StringField("Product Name")
            sku = StringField("SKU")
            price = DecimalField("Unit Price")

        class MetaViewGrid:
            limit = 24




