# feretui
[![Documentation Status](https://readthedocs.org/projects/feretui/badge/?version=latest)](https://feretui.readthedocs.io/en/latest/?badge=latest)
[![Python linting](https://github.com/FeretUI/feretui/actions/workflows/lint.yaml/badge.svg)](https://github.com/FeretUI/feretui/actions/workflows/lint.yaml)
[![Tests](https://github.com/FeretUI/feretui/actions/workflows/tests.yaml/badge.svg)](https://github.com/FeretUI/feretui/actions/workflows/tests.yaml)
[![Coverage Status](https://coveralls.io/repos/github/FeretUI/feretui/badge.svg?branch=main)](https://coveralls.io/github/FeretUI/feretui?branch=main)

small web client to build an admin interface or a little backoffice

The goal of this project is to give developers the possibility to
create an admin interface for any project.

On the web, we often need to create an user interface for the configuration or the 
administration of a project. It's not the core of the project but we don't 
want to add this part to the main user interface.

**django_admin** is a solution for django developer, but not for the others.

I don't want to link this project with a framework. I really want to create an admin
backoffice available for any framework.

## Installation

### Installation of the dependencies

* `lessc` is a tools need for the minification of the static

```commandline
sudo npm install -g less
```

### Installation of the project

Install released versions of FeretUI from the Python package index with
[pip](http://pypi.python.org/pypi/pip) or a similar tool:

```commandline
pip install feretui
```

Installation via source distribution via the `pyproject.toml` script:

```commandline
pip install .
```

### Running tests

If you want to run the tests, 
first install the test dependencies:
```commandline
pip install '.[test,bottle]'
```

Then simply run:
```commandline
pytest
```

## web server

You can use your favorite web server.

* tutorial with [bottle](https://feretui.readthedocs.io/en/latest/tutorials.html#serve-feretui-with-bottle)
* tutorial with [flask](https://feretui.readthedocs.io/en/latest/tutorials.html#serve-feretui-with-flask)
* tutorial with [pyramid](https://feretui.readthedocs.io/en/latest/tutorials.html#serve-feretui-with-pyramid)
* tutorial with [django's views](https://feretui.readthedocs.io/en/latest/tutorials.html#serve-feretui-with-django)
* tutorial with [starlette](https://feretui.readthedocs.io/en/latest/tutorials.html#serve-feretui-with-starlette)

## the ORM.

You can use your favorite ORM.

* tutorial with [SQLAlchemy](https://feretui.readthedocs.io/en/latest/tutorials.html#sqlalchemy)
* tutorial with [django's ORM](https://feretui.readthedocs.io/en/latest/tutorials.html#django)
