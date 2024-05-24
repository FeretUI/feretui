.. This file is a part of the FeretUI project
..
..    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

Translation
-----------

~~~~~~~~~~~~~~~~~~~~~~
Export the translation
~~~~~~~~~~~~~~~~~~~~~~

The translation is saved in po file.

A console script exist to export the translation in the pofile template.

::

    export-feretui-catalog --version 0.1.0 my/file.pot


All the entry with translation have **addons** named argument to give context.
You can filter only on one of these addons.

~~~~~~~~~
Translate
~~~~~~~~~

to translate use `poedit <https://poedit.net/>`_.

~~~~~~~~~~~~~~~~~~~~~~
Import the translation
~~~~~~~~~~~~~~~~~~~~~~

The import of the translation is done in the project and by instance. Two instance can live in 
the same project with two diferent translation.

Internal translations
~~~~~~~~~~~~~~~~~~~~~

::

    myferet.load_internal_catalog('fr')


.. warning::

    If your lang is not defined in the project, you can use the pot file
    save in the project.

Another translations
~~~~~~~~~~~~~~~~~~~~

::

    myferet.load_catalog('my/file.po', 'fr')
