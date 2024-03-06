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
from wtforms import Form, PasswordField, StringField
from wtforms.validators import InputRequired
from wtforms.widgets import PasswordInput, TextInput


class WrapInput:
    def __init__(self, widget):
        super(WrapInput, self).__init__()
        self.widget = widget

    def __call__(self, field, **kwargs):
        from markupsafe import Markup

        from feretui.thread import local

        myferet = local.feretui
        session = local.request.session

        input_class = ["input"]
        if field.errors:
            input_class.append("is-danger")
        else:
            for validator in field.validators:
                if isinstance(validator, InputRequired):
                    input_class.append("is-link")

        c = kwargs.pop('class', '') or kwargs.pop('class_', '')
        kwargs['class'] = '%s %s' % (' '.join(input_class), c)
        return Markup(myferet.render_template(
            session,
            "feretui-input-field",
            label=field.label,
            widget=self.widget(field, **kwargs),
            error=', '.join(field.errors),
        ))


class FeretUIStringField(StringField):
    widget = WrapInput(TextInput())


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

    class LoginForm(Form):
        login = FeretUIStringField(validators=[InputRequired()])
        password = PasswordField(
            validators=[InputRequired()],
            widget=WrapInput(PasswordInput()),
        )

    def __init__(self: "Session") -> "Session":
        """FeretUI session."""
        self.user: str = None
        self.lang: str = 'en'
        self.theme: str = 'default'

    def login(self, login=None, password=None):
        self.user = login
