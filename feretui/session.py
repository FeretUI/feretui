# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Module feretui.session.

This is a internal session, it represent the session of the web-server but
with only the entry need by the client

The session can be overwritting by the developper::

    from feretui import Session


    session = Session()
"""
from wtforms import PasswordField, RadioField, StringField
from wtforms.validators import EqualTo, InputRequired

from feretui.form import FeretUIForm, Password
from feretui.thread import local


class LoginForm(FeretUIForm):
    login = StringField(validators=[InputRequired()])
    password = PasswordField(validators=[InputRequired()])


def get_langs():
    return local.feretui.get_langs()


class SignUpForm(FeretUIForm):
    login = StringField(validators=[InputRequired()])
    lang = RadioField(
        label='Language',
        choices=get_langs,
        validators=[InputRequired()],
    )
    password = PasswordField(validators=[Password()])
    password_confirm = PasswordField(
        validators=[InputRequired(), EqualTo('password')],
    )


class Session:
    """Description of the session.

    The session can be overwritting by the developper::

        from feretui import Session


        class MySession(Session):
            pass

    Attributes
    ----------
    * [user: str = None] : User name of the session
    * [lang: str = 'en'] : The language use by the user session
    * [theme: str = 'default'] : The ui theme use by the user session

    """

    LoginForm: FeretUIForm = LoginForm
    SignUpForm: FeretUIForm = SignUpForm

    def __init__(self: "Session") -> "Session":
        """FeretUI session."""
        self.user: str = None
        self.lang: str = 'en'
        self.theme: str = 'default'

    def login(self, login=None, password=None) -> None:
        self.user = login

    def logout(self) -> None:
        self.user = None

    def signup(self, **kwargs) -> None:
        self.user = kwargs['login']
        for key, value in kwargs.items():
            if key in ('login', 'password', 'password_confirm'):
                continue

            setattr(self, key, value)
