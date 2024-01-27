# feretui
[![Documentation Status](https://readthedocs.org/projects/feretui/badge/?version=latest)](https://feretui.readthedocs.io/en/latest/?badge=latest)
[![Python linting](https://github.com/FeretUI/feretui/actions/workflows/lint.yaml/badge.svg)](https://github.com/FeretUI/feretui/actions/workflows/lint.yaml)
[![Tests](https://github.com/FeretUI/feretui/actions/workflows/tests.yaml/badge.svg)](https://github.com/FeretUI/feretui/actions/workflows/tests.yaml)
[![Coverage Status](https://coveralls.io/repos/github/FeretUI/feretui/badge.svg?branch=main)](https://coveralls.io/github/FeretUI/feretui?branch=main)

small web client to build an admin interface or a little backoffice


The goal of this project is to give at the developper the possibility to
create an admin interface for any project.

In the web we often need to create an user interface to the configuration or the 
administration of the project. It is not the core of the project but we don't 
want to add this part in the main user interface.

**django_admin** is a solution for the django developper, but not for the other one.


I don't want to link this project with a framework. I really want to create an admin
backoffice availlable for any framework.

## Installation

Install released versions of FeretUI from the Python package index with
`pip <http://pypi.python.org/pypi/pip>`_ or a similar tool:

```
pip install feretui (Not ready yet)
```

Installation via source distribution is via the ``pyproject.toml`` script:

```
pip install .
```

Installation will add the ``feretui`` commands to the environment.

## Example with bottle

For this example you need  to install some additional package

```pip install bottle bottle_session redis```

```
import inspect
import logging
from os import path

import redis
from bottle import HTTPResponse, app, debug, request, route, run, static_file
from bottle_session import Session as BottleSession
from bottle_session import SessionPlugin

from feretui import FeretUI, Request, Session

logging.basicConfig(level=logging.DEBUG)


class MySessionPlugin(SessionPlugin):

    def apply(self, callback, context):
        context.config.get('session')
        try:
            args = inspect.signature(context.callback).parameters
        except AttributeError:
            args = inspect.getargspec(context.callback)[0]

        if self.keyword not in args:
            return callback

        def wrapper(*args, **kwargs):
            r = redis.Redis(connection_pool=self.connection_pool)
            kwargs[self.keyword] = MySession(
                r,
                self.cookie_name,
                self.cookie_lifetime,
                self.cookie_secure,
                self.cookie_httponly
            )
            rv = callback(*args, **kwargs)
            return rv

        return wrapper


class MySession(Session, BottleSession):

    def __init__(
        self,
        rdb,
        cookie_name='bottle.session',
        cookie_lifetime=None,
        cookie_secure=False,
        cookie_httponly=False
    ):
        Session.__init__(self)
        BottleSession.__init__(
            self,
            rdb,
            cookie_name,
            cookie_lifetime,
            cookie_secure,
            cookie_httponly
        )


myferet = FeretUI()


@route('/')
def index(session):
    frequest = Request(
        method=Request.GET,
        querystring=request.query_string,
        headers=dict(request.headers),
        session=session,
    )
    response = myferet.render(frequest)
    return HTTPResponse(
        body=response.body,
        status=response.status_code,
        headers=response.headers
    )


@route('/feretui/static/<filename>')
def feretui_static_file(session, filename):
    filepath = myferet.get_static_file_path(filename)
    if filepath:
        root, name = path.split(filepath)
        return static_file(name, root)

    return None


if __name__ == "__main__":
    app = app()
    plugin = MySessionPlugin(cookie_lifetime=600)
    app.install(plugin)
    debug(True)
    run(host="localhost", port=8080)
```
