.. This file is a part of the FeretUI project
..
..    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

CHANGELOG
=========

0.2.0 (unreleased)
------------------

* Next-Gen ERP: Added social Chatter & Activity Timeline via :class:`~feretui.resources.chatter.HasChatterMixin`.
* Next-Gen ERP: Added tabbed form layout organization via :class:`~feretui.form.Notebook` and :class:`~feretui.form.Page`.
* Next-Gen ERP: Added interactive monthly Calendar view via :class:`~feretui.resources.calendar.CalendarView` and :class:`~feretui.resources.calendar.CalResource`.
* Next-Gen ERP: Added dynamic View Switcher toolbar with state preservation across List, Kanban, and Calendar views.
* Next-Gen ERP: Added multi-level stackable modal dialogs via :class:`~feretui.resources.actions.OpenModalAction`.
* Next-Gen ERP: Added 1-click Quick Filters via :class:`~feretui.resources.common.QuickFilter`.
* Next-Gen ERP: Added rich text WYSIWYG editor via :class:`~feretui.form.WYSIWYGField`.
* Next-Gen ERP: Added relational navigation via :class:`~feretui.form.Many2OneField` and embedded sub-tables via :class:`~feretui.form.One2ManyField`.
* Next-Gen ERP: Added workflow stage status bar via :class:`~feretui.form.StatusBarField`.
* Security: Fixed unescaped user markup and hardened against XSS injections.
* Assets: Upgraded HTMX to 2.0.4 with SSE support, _hyperscript to 0.9.14, and Alpine.js to 3.14.8.

0.1.1 (unreleased)
------------------

* Refactor: Extracted asset management into `AssetManager` class.
* Accessibility: Updated `RadioField` templates to use `<fieldset>` and `<legend>` (Issue #92).
* Accessibility: Implemented keyboard accessibility for tooltips (RGAA 12.11) (Issue #107).
* Accessibility: Implemented grouping for FormField and SelectMultipleField (RGAA 11.5) (Issue #123).
* Documentation: Added Troubleshooting guide.
* Dev: Added pre-commit configuration.
* Dev: Added GitHub Issue templates.

0.1.0 (31-10-2025)
------------------

Main version of FeretUI, based on the POC

* Added Request object
* Added Response object
* Added Session object
* Added templating
* Added actions callbacks mechanism.
* Added pages callbacks mechanism.
* Added WTForm 
* Added menus
* Added Resource (list, create, read, update, delete, actions)
* Added static file register
* Added themes
* Added translation behaviours
* Added authentification
