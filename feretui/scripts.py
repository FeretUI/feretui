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


def export_catalog():
    """Console script function to export catalog."""
    parser = ArgumentParser(
        prog="Feretui.export_catalog",
        description="Export the catalog template on format POT",
    )
    parser.add_argument('output', help="The output file")
    parser.add_argument('--version', help="The version of the catalog.")
    parser.add_argument(
        '--addons', default="feretui", help="The addons to export")

    args = parser.parse_args(sys.argv[1:])
    version_ = args.version
    if version_ is None:
        version_ = version(args.addons)

    FeretUI.export_catalog(args.output, version_, addons=args.addons)
