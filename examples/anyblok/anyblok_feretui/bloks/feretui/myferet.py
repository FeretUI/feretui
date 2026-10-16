from feretui import FeretUI, Session

myferet = FeretUI()
myferet.load_internal_catalog('fr')
Session.SignUpForm.lang.kwargs['choices'].append(('fr', 'Français'))


class MySession(Session):

    def __init__(self, **options) -> None:
        options.setdefault('theme', 'default')
        options.setdefault('lang', 'fr')
        super().__init__(**options)
