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
* :class:`.RequestFormError`
* :class:`.RequestSessionError`
* :class:`.RequestNoSessionError`
* :class:`.RequestWrongSessionError`
* :class:`.TemplateError`
* :class:`.TranslationError`
* :class:`.TranslationMenuError`
* :class:`.TranslationFormError`
* :class:`.TranslationResourceError`
* :class:`.PageError`
* :class:`.ActionError`
* :class:`.UnexistingActionError`
* :class:`.ActionValidatorError`
* :class:`.ActionAuthenticationError`
* :class:`.ActionUserIsNotAuthenticatedError`
* :class:`.ActionUserIsAuthenticatedError`
* :class:`.MenuError`
* :class:`.ResourceError`
* :class:`.UnexistingResourceError`
* :class:`.ViewError`
* :class:`.ViewActionError`
* :class:`.ViewFormError`
"""


class FeretUIError(Exception):
    """Main exception of FeretUI."""


class RequestError(FeretUIError):
    """Exception raised by Request object.

    Inherits :class:`.FeretUIError`.
    """


class RequestFormError(RequestError):
    """Exception raised by Request object.

    Inherits :class:`.RequestError`.
    """


class RequestSessionError(RequestError):
    """Exception raised by Request object.

    Inherits :class:`.RequestError`.
    """


class RequestNoSessionError(RequestSessionError):
    """Exception raised by Request object.

    Inherits :class:`.RequestSessionError`.
    """


class RequestWrongSessionError(RequestSessionError):
    """Exception raised by Request object.

    Inherits :class:`.RequestSessionError`.
    """


class TemplateError(FeretUIError):
    """Exception raised by Template object.

    Inherits :class:`.FeretUIError`.
    """


class TranslationError(FeretUIError):
    """Exception raised by Translation object.

    Inherits :class:`.FeretUIError`.
    """


class TranslationMenuError(TranslationError):
    """Exception raised by Translation object.

    Inherits :class:`.TranslationError`.
    """


class TranslationFormError(TranslationError):
    """Exception raised by Translation object.

    Inherits :class:`.TranslationError`.
    """


class TranslationResourceError(TranslationError):
    """Exception raised by Translation object.

    Inherits :class:`.TranslationError`.
    """


class PageError(FeretUIError):
    """Exception raised by page mecanism in FeretUI object.

    Inherits :class:`.FeretUIError`.
    """


class ActionError(FeretUIError):
    """Exception raised by action mecanism in FeretUI object.

    Inherits :class:`.FeretUIError`.
    """


class UnexistingActionError(ActionError):
    """Exception raised by action mecanism in FeretUI object.

    Inherits :class:`.ActionError`.
    """


class ActionValidatorError(ActionError):
    """Exception raised by action mecanism in FeretUI object.

    Inherits :class:`.ActionError`.
    """


class ActionAuthenticationError(ActionError):
    """Exception raised by action mecanism in FeretUI object.

    Inherits :class:`.ActionError`.
    """


class ActionUserIsAuthenticatedError(ActionAuthenticationError):
    """Exception raised by action mecanism in FeretUI object.

    Inherits :class:`.ActionAuthenticationError`.
    """


class ActionUserIsNotAuthenticatedError(ActionAuthenticationError):
    """Exception raised by action mecanism in FeretUI object.

    Inherits :class:`.ActionAuthenticationError`.
    """


class MenuError(FeretUIError):
    """Exception raised by menu mecanism in FeretUI object.

    Inherits :class:`.FeretUIError`.
    """


class ResourceError(FeretUIError):
    """Exception raised by resource mecanism in FeretUI object.

    Inherits :class:`.FeretUIError`.
    """


class UnexistingResourceError(FeretUIError):
    """Exception raised by resource mecanism in FeretUI object.

    Inherits :class:`.ResourceError`.
    """


class ViewError(FeretUIError):
    """Exception raised by resource mecanism in FeretUI object.

    Inherits :class:`.ResourceError`.
    """


class ViewActionError(FeretUIError):
    """Exception raised by resource mecanism in FeretUI object.

    Inherits :class:`.ViewError`.
    """


class ViewFormError(FeretUIError):
    """Exception raised by resource mecanism in FeretUI object.

    Inherits :class:`.ViewError`.
    """
