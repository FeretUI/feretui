from feretui.schema import LoginValidator, SignupValidator


class Session:

    def __init__(self):
        self.user = None
        self.lang = 'en'
        self.theme = None

    LoginValidator = LoginValidator

    def login(self, login: str = None, password: str = None):
        self.user = login

    SignupValidator = SignupValidator

    def signup(
        self,
        login: str = None,
        lang: str = None,
        password: str = None,
        confirm_password: str = None,
    ):
        pass

    def logout(self):
        self.user = None
