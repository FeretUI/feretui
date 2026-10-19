.. This file is a part of the FeretUI project
..
..    Copyright (C) 2026 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

CSS Architecture & Style Guide
==============================

FeretUI uses an ultra-lightweight, professional CSS micro-framework designed specifically for business applications, back-offices, and ERP systems.

It is structured as a **curated overlay on top of Pico CSS v2**, combining the semantic power of Pico with the specialized patterns of enterprise management software (inspired by modern Odoo interfaces).

Philosophy & Comparison with Bulma
----------------------------------

Before version 0.2, FeretUI relied on Bulma. The transition to **Pico CSS + ``feretui.css``** brings major benefits:

.. list-table::
   :widths: 25 35 40
   :header-rows: 1

   * - Aspect
     - Legacy Bulma
     - FeretUI (Pico CSS + ``feretui.css``)
   * - **Weight & Performance**
     - ~500 KB uncompressed, requires SCSS/lessc
     - **~105 KB total** (Pico: 82 KB, FeretUI overlay: 23 KB), zero Node.js
   * - **DOM Cleanliness**
     - Heavy wrapper nesting (``div.field > div.control > input``)
     - **Clean, semantic HTML5** (native ``<label>``, ``<input>``, ``<dialog>``)
   * - **Dark / Light Mode**
     - Manual theming, bulky CSS swaps
     - **Native automatic dark mode** via ``prefers-color-scheme`` or user session
   * - **ERP Ergonomics**
     - Generic website styling, unsuited for forms
     - **Native ERP Sheet, Workflow Status Bar, Smart Buttons, Kanban**

---

1. Page Layout & Form Sheet (Fiche Papier ERP)
----------------------------------------------

In business applications, data forms must not be stretched across an entire ultra-wide monitor. FeretUI provides an Odoo-like "sheet" container with a clean elevation shadow, optimal max-width, and responsive margins.

Containers
~~~~~~~~~~

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Class
     - Description and Context of Use
   * - ``.feretui-form-sheet``
     - White card sheet container mimicking a physical paper document with a subtle border and shadow (max-width: 1140px, centered). Used for Form views (``ReadView``, ``EditView``, ``CreateView``).
   * - ``.feretui-form-grid``
     - Responsive two-column form grid (``grid-template-columns: 1fr 1fr`` on desktop, 1 column on mobile) to display fields side by side cleanly.
   * - ``.feretui-fullwidth-field``
     - Applied to a field inside ``.feretui-form-grid`` so it spans across both columns (e.g., long descriptions, addresses, or child tables).
   * - ``.container.is-fluid``
     - Removes default max-width limits to let wide tables or Kanban boards utilize 100% of the screen width.

Form Layout Example::

    <div class="feretui-form-sheet">
      <!-- Top header with smart buttons & status bar -->
      ...
      <!-- Two-column form grid -->
      <div class="feretui-form-grid">
        <div>
          <label for="name">Customer Name</label>
          <input type="text" id="name" name="name">
        </div>
        <div>
          <label for="email">Email Address</label>
          <input type="email" id="email" name="email">
        </div>
        <div class="feretui-fullwidth-field">
          <label for="notes">Internal Notes</label>
          <textarea id="notes" name="notes"></textarea>
        </div>
      </div>
    </div>

Columns Flexbox (Bulma Compatibility)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For custom layouts, FeretUI preserves an intuitive flexbox grid:

* ``.columns``: Flex container with uniform gaps (``gap: 1.5rem``).
* ``.columns > .column``: Auto-expanding column (``flex: 1``).
* ``.column.is-narrow``: Column sized to fit its content without expanding.
* ``.column.is-half``: 50% width column.
* ``.column.is-one-third``: 33.3% width column.
* ``.column.is-two-thirds``: 66.6% width column.

---

2. Form Headers, Workflow Pipeline & Smart Buttons
--------------------------------------------------

Workflow Pipeline (StatusBar)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :class:`~feretui.form.StatusBarField` renders an interactive workflow chevron bar:

* ``.feretui-status-bar``: Pipeline bar container.
* ``.status-bar-steps``: Ordered list of stages.
* ``.status-step``: Individual stage step (clickable button or span).
* ``.status-step.is-current``: Current active state (accent color).
* ``.status-step.is-passed``: Previously completed state.
* ``.status-step.is-future``: Upcoming future stage.

Smart Buttons (Stat Boxes)
~~~~~~~~~~~~~~~~~~~~~~~~~~

Stat boxes at the top-right of a form sheet linking to related records (e.g. "5 Orders", "2 Invoices"):

* ``.feretui-smart-buttons``: Flex container in the top-right header aligning smart buttons.
* ``.feretui-smart-button``: Compact card button displaying an icon, count number, and text label.

Example::

    <div class="feretui-smart-buttons">
      <button class="feretui-smart-button" hx-get="/action/orders">
        <i class="ti ti-receipt"></i>
        <div>
          <strong>12</strong>
          <small>Orders</small>
        </div>
      </button>
    </div>

---

3. Form Fields & Relational Widgets
-----------------------------------

Input Controls & States
~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Class / Attribute
     - Description and Context of Use
   * - ``[required]`` / ``label small``
     - Indicates a mandatory field. The asterisk ``*`` or ``(required)`` label is styled automatically in the primary theme color.
   * - ``aria-invalid="true"``
     - Added automatically when form validation fails. Colors the input border in red.
   * - ``small#invalid-helper``
     - Error message displayed immediately below the invalid field (styled in danger red).
   * - ``.input.is-static``
     - **Read-only plain-text field**. Strips away borders, backgrounds, and shadows, allowing read-only forms to present information like natural text without disabled input boxes.

Read-only Plain-text Example::

    <!-- Read-only field renders as clean flat text -->
    <input type="text" class="input is-static" value="Acme Corporation" readonly>

Relational Widgets (Many2One & One2Many)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``.feretui-many2one-wrapper``: Wrapper for Many2One foreign key links.
* ``.feretui-many2one-link``: Clean clickable link directing to the related record's read view.
* ``.feretui-one2many-wrapper``: Container holding a sub-table of related rows.
* ``.feretui-one2many-table``: Bordered table for embedded child records (e.g. sale order lines).

---

4. Buttons & Action Bars
------------------------

Button Containers
~~~~~~~~~~~~~~~~~

* ``.buttons``: Flexbox container aligning buttons with uniform spacing (``gap: 0.5rem``).
* ``.buttons.is-centered``: Horizontally centers the button group.
* ``.field.is-grouped``: Horizontally aligns form inputs and action buttons side by side.
* ``.field.is-grouped-multiline``: Allows grouped items to wrap onto the next line gracefully on smaller viewports.

Button Variants
~~~~~~~~~~~~~~~

Applied to ``<button>`` or ``<a role="button">``:

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Class
     - Description and Context of Use
   * - *(default)*
     - Solid theme button (primary color). Used for main actions (Save, Create).
   * - ``.secondary`` / ``.outline``
     - Neutral bordered button with transparent background. Used for secondary actions (Return, Cancel).
   * - ``.button.is-danger``
     - Destructive action button (red). Used for Delete actions.
   * - ``.button.is-ghost``
     - Borderless, transparent button that highlights on hover. Used for subtle icon actions.
   * - ``.is-fullwidth``
     - Expands the button across 100% of the container width.

---

5. Data Tables & Pagination
---------------------------

List View Tables
~~~~~~~~~~~~~~~~

* ``.table-container.overflow-auto``: Responsive wrapper enabling smooth horizontal scrolling on narrow screens without breaking page layout.
* ``table.striped``: Native Pico CSS striped rows for effortless scanning of dense data.
* ``th.is-narrow``: Column constrained to its minimal required width (e.g. checkbox column).

Pagination Bar
~~~~~~~~~~~~~~

* ``.pagination``: Right-aligned pagination toolbar.
* ``.pagination-list``: Flex list of page buttons.
* ``.pagination-link``: Numbered page button.
* ``.pagination-link.is-current``: Highlighted active page button.
* ``.pagination-previous`` / ``.pagination-next``: Previous and next buttons.

---

6. Kanban Board
---------------

Used by :class:`~feretui.resources.kanban.KanbanView` for stage-based pipeline cards:

* ``.feretui-kanban-board``: Horizontal scroll container holding stage columns.
* ``.feretui-kanban-column``: Fixed-width column (290px) representing a stage.
* ``.feretui-kanban-column-header``: Header with stage title and counter badge (``.badge``).
* ``.feretui-kanban-cards-container``: Drag-and-drop container powered by SortableJS.
* ``.feretui-kanban-card``: Interactive card with hover elevation and cursor pointer.
* ``.kanban-card-ghost``: Dotted preview placeholder shown while dragging a card.
* ``.card-header`` & ``.card-body``: Structured zones inside a card.

---

7. Tags, Badges & Filter Pills
------------------------------

* ``.tags``: Flexbox container aligning badges.
* ``.tags.has-addons``: Combines adjacent tags into a single unified pill (label + value + close button).
* ``.tag``: Rounded badge component.
* Color variants: ``.tag.is-info`` (blue), ``.tag.is-success`` (green), ``.tag.is-warning`` (yellow), ``.tag.is-danger`` (red), ``.tag.is-dark`` (charcoal).
* ``.delete``: Small circular cross icon to dismiss a filter pill or close a modal dialog.

---

8. Notifications & Alerts
-------------------------

* ``.notification``: Alert box with padding and rounded corners.
* ``.notification.is-info``: Neutral informational message.
* ``.notification.is-success``: Confirmation alert.
* ``.notification.is-danger``: Critical warning or error alert.

---

9. Utility Classes & Accessibility
----------------------------------

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Class
     - Description and Context of Use
   * - ``.is-sr-only``
     - Visually hides text while keeping it available for screen readers (accessibility RGAA 11.5).
   * - ``.is-hidden-print``
     - Completely hides elements (navbar, buttons, sidebar) when printing invoices or reports.
   * - ``.has-text-centered``
     - Centers text horizontally.
   * - ``.has-text-right``
     - Right-aligns text (ideal for monetary numbers, subtotals, and timestamps).
   * - ``.is-pulled-right`` / ``.is-pulled-left``
     - Floats an element to the right or left.
   * - ``.is-clearfix``
     - Clears floated children.
