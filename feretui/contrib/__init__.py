# This file is a part of the FeretUI project
#
#    Copyright (C) 2026 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""FeretUI Contrib extensions (ORM helpers, integrations)."""

from feretui.contrib.sqla import SQLAlchemyResource, model_to_form

__all__ = ["SQLAlchemyResource", "model_to_form"]
