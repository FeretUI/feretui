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

    """

    def __init__(self):
        """FeretUI session."""
        self.user: str = None
        self.lang: str = 'en'
