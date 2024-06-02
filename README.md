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

### Installation of the dependencies

* lessc is a tools need for the minification of the static

```
sudo npm install -g less
```

### Installation of the project

Install released versions of FeretUI from the Python package index with
[pip](http://pypi.python.org/pypi/pip) or a similar tool:

```
pip install feretui (Not ready yet)
```

Installation via source distribution is via the ``pyproject.toml`` script:

```
pip install .
```

## web server

You can use your favorite web server.

* tutorial with [bottle](https://feretui.readthedocs.io/en/latest/tutorials.html#serve-feretui-with-bottle)
* tutorial with [flask](https://feretui.readthedocs.io/en/latest/tutorials.html#serve-feretui-with-flask)
* tutorial with [pyramid](https://feretui.readthedocs.io/en/latest/tutorials.html#serve-feretui-with-pyramid)

## the ORM.

You can use your favorite ORM.

* tutorial with [SQLAlchemy](https://feretui.readthedocs.io/en/latest/tutorials.html#sqlalchemy)
