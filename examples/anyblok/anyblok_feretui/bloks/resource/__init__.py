from importlib import import_module
from logging import getLogger

from anyblok.blok import Blok

logger = getLogger(__name__)


class FeretUIResource(Blok):
    version = "0.1.0"
    author = "Jean-Sébastien Suzanne"
    required = ["anyblok-core", "pyramid", "feretui-base", "auth-password"]

    def load(self):
        myferet = import_module(
            '.myferet',
            'anyblok_feretui.bloks.resource',
        )
        self.anyblok.Pyramid.MySession = myferet.MySession

    @classmethod
    def import_declaration_module(cls):
        from . import model  # noqa

    def update(self, latest_version):
        if latest_version is not None:
            return

        User = self.anyblok.Pyramid.User
        Credential = self.anyblok.Pyramid.CredentialStore

        User.insert(login='admin', name='Adminstrator')
        Credential.insert(login='admin', password='admin')

        for x in range(100):
            User.insert(login=f'foo{x}', name=f'Foo {x}')
            Credential.insert(login=f'foo{x}', password=f'bar{x}')
