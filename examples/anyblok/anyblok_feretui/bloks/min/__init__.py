from importlib import import_module
from logging import getLogger

from anyblok.blok import Blok

logger = getLogger(__name__)


class FeretUIMin(Blok):
    version = "0.1.0"
    author = "Jean-Sébastien Suzanne"
    required = ["anyblok-core", "pyramid", "feretui-base"]

    def load(self):
        import_module(
            '.myferet',
            'anyblok_feretui.bloks.min'
        )
