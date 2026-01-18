# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Asset management for FeretUI."""

from logging import getLogger
from pathlib import Path

logger = getLogger(__name__)


class AssetManager:
    """Manage static assets (JS, CSS, Images, Themes, Fonts)."""

    def __init__(self, base_url: str) -> None:
        """Initialize the manager.

        :param base_url: The prefix of the url for all internal api
        :type base_url: str
        """
        self.base_url = base_url
        self.statics: dict[str, str | Path] = {}
        self.js_import: list[str] = []
        self.css_import: list[tuple[bool, str]] = []
        self.images: dict[str, str] = {}
        self.themes: dict[str, str] = {}
        self.fonts: dict[str, str] = {}

    def register_js(self, name: str, filepath: str | Path) -> None:
        """Register a javascript file to import in the client.

        :param name: name of the file see in the html url
        :type name: str
        :param filepath: Path in server file system
        :type filepath: str | Path
        """
        if name in self.statics:
            logger.warning("The js script %s is overwriting", name)
        else:
            logger.debug("Add the js script %s", name)
            self.js_import.append(name)

        self.statics[name] = filepath

    def register_css(
        self,
        name: str,
        filepath: str | Path,
        compress: bool = True,
    ) -> None:
        """Register a stylesheet file to import in the client.

        :param name: name of the file see in the html url
        :type name: str
        :param filepath: Path in server file system
        :type filepath: str | Path
        :param compress: if True compress the csv
        :type compress: bool
        """
        if name in self.statics:
            logger.warning("The stylesheet %s is overwriting", name)
        else:
            url = f"{self.base_url}/static/{name}"
            logger.debug("Add the stylesheet %s", url)
            if compress:
                self.css_import.append((compress, name))
            else:
                self.css_import.append((compress, url))

        self.statics[name] = filepath

    def register_image(self, name: str, filepath: str | Path) -> None:
        """Register an image file to use it in the client.

        :param name: name of the image see in the html url
        :type name: str
        :param filepath: Path in server file system
        :type filepath: str | Path
        """
        if name in self.statics:
            logger.warning("The image %s is overwriting", name)
        else:
            url = f"{self.base_url}/static/{name}"
            logger.debug("Add the image %s", url)
            self.images[name] = url

        self.statics[name] = filepath

    def register_theme(self, name: str, filepath: str | Path) -> None:
        """Register a theme file to use it in the client.

        :param name: name of the theme see in the html url
        :type name: str
        :param filepath: Path in server file system
        :type filepath: str | Path
        """
        if name in self.statics:
            logger.warning("The theme %s is overwriting", name)
        else:
            logger.debug("Add the available theme %s", name)
            self.themes[name] = name

        self.statics[name] = filepath

    def register_font(self, name: str, filepath: str | Path) -> None:
        """Register a theme file to use it in the client.

        :param name: name of the font see in the html url
        :type name: str
        :param filepath: Path in server file system
        :type filepath: str | Path
        """
        if name in self.statics:
            logger.warning("The font %s is overwriting", name)
        else:
            url = f"{self.base_url}/static/{name}"
            logger.debug("Add the available font %s", url)
            self.fonts[name] = url

        self.statics[name] = filepath

    def get_theme_url(self, theme: str) -> str:
        """Return the theme url.

        :param theme: The theme name
        :type theme: str
        :return: the url to import stylesheet
        :rtype: str
        """
        return self.themes.get(theme, self.themes.get("default"))

    def get_image_url(self, name: str) -> str:
        """Get the url for a picture.

        :param name: The name of the picture
        :type name: str
        :return: The url to get it
        :rtype: str
        """
        return self.images.get(name)

    def get_static_file_path(self, filename: str) -> str | Path | None:
        """Get the path in the filesystem for static file name.

        :param filename: The name of the static
        :type filename: str
        :return: The filesystem path
        :rtype: str | Path | None
        """
        return self.statics.get(filename)
