# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Module feretui.exceptions.

Get the exceptions known by FeretUI:

* :class:`.FeretUIError`
* :class:`.RequestError`
* :class:`.TemplateError`
* :class:`.TranslationError`
"""


class FeretUIError(Exception):
    """Main exception of FeretUI."""


class RequestError(FeretUIError):
    """Exception raised by Request object.

    Inherits :class:`.FeretUIError`.
    """


class TemplateError(FeretUIError):
    """Exception raised by Template object.

    Inherits :class:`.FeretUIError`.
    """


class TranslationError(FeretUIError):
    """Exception raised by Translation object.

    Inherits :class:`.FeretUIError`.
    """


class ActionError(FeretUIError):
    """Exception raised by Request object.

    Inherits :class:`.FeretUIError`.
    """


class UnexistingAction(ActionError):
    """Exception raised by Request object.

    Inherits :class:`.ActionError`.
    """


class ActionValidatorError(ActionError):
    """Exception raised by Request object.

    Inherits :class:`.ActionError`.
    """
