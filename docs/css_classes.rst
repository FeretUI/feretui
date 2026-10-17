.. This file is a part of the FeretUI project
..
..    Copyright (C) 2026 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

CSS Classes and Usage in FeretUI
================================

FeretUI is built on a modern, semantic, and ultra-lightweight CSS foundation powered by **Pico CSS v2**, enriched by the companion ERP stylesheet ``feretui.css``.

This architecture provides:

* **Zero Node.js / npm / lessc dependencies**: Pure CSS compiled and minified on-the-fly in Python via ``PurePythonCSSCompressor``.
* **Semantic HTML**: Native tags (``<button>``, ``<dialog>``, ``<table>``, ``<nav>``, ``<input>``) are elegantly styled out of the box.
* **Ergonomic compatibility**: Preserves proven utility and semantic classes (tags, buttons, notifications, columns).
* **Native Dark / Light mode**: Automatic OS-level adaptation or configurable via ``session.color_scheme``.

---

1. Buttons & Button Groups
--------------------------

Button Containers
~~~~~~~~~~~~~~~~~

* ``.buttons``: Flexbox container aligning buttons with uniform spacing (``gap: 0.5rem``).
* ``.buttons.is-centered``: Horizontally centers the button group.
* ``#buttons``: Resource view header container for pagination and actions, maintaining buttons on a single line on desktop while remaining responsive on mobile.

Button Style Variants
~~~~~~~~~~~~~~~~~~~~~

Classes apply to ``<button>``, ``<a role="button">``, or ``<input type="button|submit">`` tags:

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Class
     - Description and Usage
   * - *(default)*
     - Solid button using the theme's primary color (``--pico-primary``).
   * - ``.secondary``
     - Soft secondary button with a neutral background.
   * - ``.contrast``
     - High-contrast button (inverted black/white).
   * - ``.button.is-danger`` / ``button.is-danger``
     - Destructive action button (danger red, e.g. delete).
   * - ``.button.is-ghost`` / ``button.is-ghost``
     - Transparent borderless button, ideal for subtle toolbar actions.
   * - ``.is-fullwidth``
     - Expands the button across 100% of its container width.

Example::

    <div class="buttons">
      <button type="submit">Save</button>
      <button type="button" class="secondary">Cancel</button>
      <button type="button" class="button is-danger">Delete</button>
    </div>

---

2. Tags, Badges & Filters
-------------------------

FeretUI retains an elegant and semantic syntax for tags (filter pills, statuses, badges).

Tag Containers
~~~~~~~~~~~~~~

* ``.tags``: Flex container aligning tags side by side.
* ``.tags.has-addons``: Merges adjacent tags into a single continuous pill (e.g. label + delete button).

Tag Styles
~~~~~~~~~~

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Class
     - Rendering and Use Case
   * - ``.tag``
     - Standard rounded badge (2em height, 0.75rem text).
   * - ``.tag.is-rounded``
     - Fully rounded pill badge.
   * - ``.tag.is-primary``
     - Primary theme colored tag.
   * - ``.tag.is-info``
     - Information tag (blue).
   * - ``.tag.is-success``
     - Success or validation tag (green).
   * - ``.tag.is-warning``
     - Warning tag (yellow / amber).
   * - ``.tag.is-danger``
     - Error or blocking status tag (red).
   * - ``.tag.is-dark`` / ``.tag.is-light``
     - Dark and light neutral variants.
   * - ``.tag.is-medium`` / ``.tag.is-large``
     - Larger text sizes (1rem and 1.25rem).
   * - ``.delete`` / ``button.delete``
     - Circular button with integrated cross icon to remove a filter or close a modal dialog.

Example of an active filter with a remove button::

    <div class="tags has-addons">
      <span class="tag is-info">Status: In Progress</span>
      <button class="tag delete" hx-post="/feretui/action/remove_filter"></button>
    </div>

---

3. Forms & Validation
---------------------

* ``.is-required`` or ``label small[aria-hidden="true"]``: Required field indicator (asterisk ``*``). Automatically styled with the primary theme color (``--pico-primary``) for instant visual recognition.
* ``.table-container`` / ``.overflow-auto``: Container providing smooth horizontal scrolling on smaller screens for wide data tables.

Example::

    <label for="name">
      Customer Name <small aria-hidden="true">*</small>
    </label>
    <input type="text" id="name" name="name" required>

---

4. Notifications & Alerts
-------------------------

To display status, error, or confirmation messages:

* ``.notification``: Alert box with margins and rounded corners.
* ``.notification.is-info``: Informational message.
* ``.notification.is-success``: Successful operation confirmation.
* ``.notification.is-danger``: Blocking error or critical warning.

Example::

    <div class="notification is-success">
      Order #SO-0042 has been confirmed successfully.
    </div>

---

5. Status Bar / Workflow Pipeline (StatusBar)
---------------------------------------------

The :class:`~feretui.form.StatusBarField` component and its template generate a responsive workflow bar:

* ``.feretui-status-bar``: Right-aligned container with automatic horizontal scrolling.
* ``.status-bar-steps``: Ordered list of workflow stages.
* ``.status-step``: Transition button or read-only stage step.
* ``.is-current``: Active stage (highlighted with the primary theme color).
* ``.is-passed``: Completed stage (soft, muted appearance).

Generated HTML Example::

    <nav class="feretui-status-bar" aria-label="Workflow Status">
      <ul class="status-bar-steps">
        <li class="is-passed"><button type="button" class="status-step">Draft</button></li>
        <li class="is-current"><button type="button" class="status-step" aria-current="step">In Progress</button></li>
        <li><button type="button" class="status-step">Done</button></li>
      </ul>
    </nav>

---

6. Kanban Board
---------------

The :class:`~feretui.resources.kanban.KanbanView` structures cards and stage columns using:

* ``.feretui-kanban-board``: Horizontal flexboard layout with smooth scrolling.
* ``.feretui-kanban-column``: Column representing a stage (fixed 290px width).
* ``.feretui-kanban-column-header``: Column header with title and counter badge (``.badge``).
* ``.feretui-kanban-cards-container``: Droppable area holding cards (SortableJS interactivity).
* ``.feretui-kanban-card``: Draggable card with shadow and drag cursor.
* ``.kanban-card-ghost``: Dotted preview placeholder during drag-and-drop.
* ``.kanban-card-chosen``: Dynamic subtle tilt on the dragged card.
* ``.card-header`` & ``.card-body``: Card header and body field content.

---

7. Pagination
-------------

* ``.pagination``: Right-aligned pagination toolbar.
* ``.pagination-list``: List of page numbers.
* ``.pagination-link``: Link / button to a given page.
* ``.pagination-link.is-current``: Active page (styled with ``--pico-primary-background``).
* ``.pagination-previous`` & ``.pagination-next``: Previous and next buttons (disabled via ``[disabled]``).

---

8. Navigation & Header Menus
----------------------------

* ``header.is-hidden-print``: Sticky header with a subtle box shadow.
* ``details.dropdown``: Customized native Pico CSS dropdown menu.
* ``details.dropdown.is-right``: Aligns dropdown menu to the right edge (for profile / user menu).
* ``hr.navbar-divider``: Subtle horizontal divider separating menu action groups.

---

9. Accessibility & Utilities
----------------------------

* ``.is-sr-only``: Visually hides an element while preserving accessibility for screen readers (RGAA 11.5).
* ``.is-hidden-print``: Hides components during printing (menus, action buttons).
* ``.has-text-centered``: Centers text.
* ``.has-text-right``: Right-aligns text (useful for amounts and numeric totals).
* ``.container.is-fluid``: Removes maximum width constraints to fill 100% of available screen width (ERP fullscreen mode).
* ``.columns.is-desktop``, ``.column``, ``.column.is-narrow``: Flexbox grid to separate forms and side panels.
