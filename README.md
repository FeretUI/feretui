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

```pip install bottle BottleSessions```

```
import logging
from contextlib import contextmanager
from os import path

from bottle import (
    abort, app, debug, request, response, route, run, static_file
)
from BottleSessions import BottleSessions
from multidict import MultiDict

from feretui import (
    AsideHeaderMenu,
    AsideMenu,
    FeretUI,
    Request,
    Session,
    ToolBarDropDownMenu,
    ToolBarMenu,
)

logging.basicConfig(level=logging.DEBUG)


@contextmanager
def feretui_session(cls):
    session = None
    try:
        session = cls(**request.session)
        yield session
    finally:
        if session:
            request.session.update(session.to_dict())


def add_response_headers(headers) -> None:
    for k, v in headers.items():
        response.set_header(k, v)


class MySession(Session):

    def __init__(self, **options) -> None:
        options.setdefault('theme', 'minty')
        options.setdefault('lang', 'fr')
        super().__init__(**options)


myferet = FeretUI()
myferet.load_internal_catalog('fr')


@route('/')
def index():
    with feretui_session(MySession) as session:
        frequest = Request(
            method=Request.GET,
            querystring=request.query_string,
            headers=dict(request.headers),
            session=session,
        )
        res = myferet.render(frequest)
        add_response_headers(res.headers)
        return res.body


@route('/feretui/static/<filepath:path>')
def feretui_static_file(filepath):
    filepath = myferet.get_static_file_path(filepath)
    if filepath:
        root, name = path.split(filepath)
        return static_file(name, root)

    abort(404)


@route('/feretui/action/<action>', method=['GET'])
def get_action(action):
    with feretui_session(MySession) as session:
        frequest = Request(
            method=Request.GET,
            querystring=request.query_string,
            headers=dict(request.headers),
            session=session,
        )
        res = myferet.execute_action(frequest, action)
        add_response_headers(res.headers)
        return res.body


@route('/feretui/action/<action>', method=['POST'])
def post_action(session, action):
    with feretui_session(MySession) as session:
        frequest = Request(
            method=Request.POST,
            form=MultiDict(request.forms),
            headers=dict(request.headers),
            session=session,
        )
        res = myferet.execute_action(frequest, action)
        add_response_headers(res.headers)
        return res.body


if __name__ == "__main__":
    app = app()
    cache_config = {
        'cache_type': 'FileSystem',
        'cache_dir': './sess_dir',
        'threshold': 2000,
    }
    BottleSessions(
        app, session_backing=cache_config, session_cookie='appcookie')
    debug(True)
    run(host="localhost", port=8080)
```
