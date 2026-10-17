.. This file is a part of the FeretUI project
..
..    Copyright (C) 2026 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

Kanban View & KResource
-----------------------

FeretUI provides an ERP-style Kanban board view using :class:`feretui.resources.kanban.KanbanView` and the mixin :class:`feretui.resources.kanban.KResource`.

~~~~~~~~
Features
~~~~~~~~

* **Semantic Stage Columns**: Cards grouped automatically by stage (e.g. ``status`` or custom stage field).
* **Drag-and-Drop Ergonomics**: Fluid card movement powered by `SortableJS <https://sortablejs.github.io/Sortable/>`_.
* **Strict Separation of Concerns**: Zero business logic in JavaScript. Dragging a card triggers an HTMX POST to FeretUI's Python backend: ``POST /feretui/action/resource?action=move_card``.
* **Configurable MetaView**: Define column field, card title field, and body fields declaratively.

~~~~~
Usage
~~~~~

To enable Kanban on a resource, inherit from :class:`~feretui.resources.kanban.KResource` and declare ``MetaViewKanban``::

    from feretui import FeretUI, LCRUDResource
    from feretui.resources.kanban import KResource
    from feretui.contrib.sqla import SQLAlchemyResource

    myferet = FeretUI(title="My ERP")

    @myferet.register_resource()
    class TaskResource(KResource, SQLAlchemyResource):
        code = "tasks"
        label = "Tasks"
        model = Task
        session_factory = SessionLocal
        default_view = "kanban"

        class MetaViewKanban:
            column_field = "status"
            card_title_field = "title"
            card_body_fields = ["assignee", "due_date"]
            do_click_on_entry_redirect_to = "read"

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Configuration Options in ``MetaViewKanban``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``column_field`` (str): Form field name used to group cards into stage columns (default: ``"status"``).
* ``columns`` (list[tuple[str, str]] | None): Explicit list of ``(stage_key, stage_label)`` stages. If omitted, stages are extracted from the field's choices or discovered dynamically from data.
* ``card_title_field`` (str | None): Form field used as card header title. Defaults to the first non-pk field.
* ``card_body_fields`` (list[str] | None): List of form fields displayed inside the card body.
* ``do_click_on_entry_redirect_to`` (str | None): View code to navigate to upon double-clicking a card (e.g. ``"read"`` or ``"update"``).

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Persistence of Card Movements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a card is dragged from one column to another, FeretUI calls the resource's ``move_card`` method:

.. code-block:: python

    def move_card(self, pk: str, stage: str, index: int | None = None) -> None:
        # Update stage in database
        ...

When using :class:`~feretui.contrib.sqla.SQLAlchemyResource`, ``move_card`` is implemented automatically.
