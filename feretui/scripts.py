# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Module feretui.scripts.

Console scripts for FeretUI

* :func:`export_catalog` : Export a catalog template for a specific addons
"""

import sys
from argparse import ArgumentParser
from importlib.metadata import version

from feretui.feretui import FeretUI


def client_path(import_definition: str) -> FeretUI:
    """Convert the string to class or instance."""
    if not isinstance(import_definition, str):
        return import_definition

    import_path, import_name = import_definition.split(":")
    module = __import__(import_path, fromlist=[import_name])
    if hasattr(module, import_name):
        return getattr(module, import_name)

    raise ImportError(f"{import_name} does not exist in {import_path}")


def export_catalog() -> None:
    """Console script function to export catalog."""
    parser = ArgumentParser(
        prog="Feretui.export_catalog",
        description="Export the catalog template on format POT",
    )
    parser.add_argument("output", help="The output file")
    parser.add_argument(
        "--client",
        default="feretui.feretui:FeretUI",
        type=client_path,
        help=(
            "Select a class or an instance of your client. "
            "By default it is the main class of FeretUI"
        ),
    )
    parser.add_argument("--version", help="The version of the catalog.")
    parser.add_argument(
        "--addons", default="feretui", help="The addons to export"
    )

    args = parser.parse_args(sys.argv[1:])
    version_ = args.version
    if version_ is None:
        version_ = version(args.addons)

    instance = args.client
    if isinstance(instance, FeretUI):
        pass
    elif issubclass(instance, FeretUI):
        instance = instance()

    instance.export_catalog(args.output, version_, addons=args.addons)
