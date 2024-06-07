.. This file is a part of the FeretUI project
..
..    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

Serve FeretUI with django
-------------------------

Django is a high-level Python web framework that encourages rapid development and clean, 
pragmatic design. Built by experienced developers, it takes care of much of the hassle 
of web development, so you can focus on writing your app without needing to reinvent 
the wheel. It’s free and open source.

See the `django's documentation <https://www.djangoproject.com>`_.

For this example you need  to install some additional package

::

    pip install django

Create your app and install it.

Update the urls.py to add a new path::

    from django.urls import path

    from . import views

    urlpatterns = [
        path("", views.index, name="feretui-index"),
        path("feretui/static/<filepath>", views.feretui_static_file, name="feretui-static"),
        path("feretui/action/<action>", views.call_action, name="feretui-action"),
    ]

Updated the views.py::

    from contextlib import contextmanager
    from django.http import FileResponse, HttpResponse, HttpResponseNotFound
    from feretui import Session, Request
    from multidict import MultiDict
    from .feret import myferet


    class MySession(Session):

        def __init__(self, **options) -> None:
            options.setdefault('theme', 'minty')
            options.setdefault('lang', 'fr')
            super().__init__(**options)


    @contextmanager
    def feretui_session(request, cls):
        session = None
        try:
            session = cls(**request.session)
            yield session
        finally:
            if session:
                request.session.update(session.to_dict())


    def index(request):
        with feretui_session(request, MySession) as session:
            frequest = Request(
                method=Request.GET,
                querystring=request.GET.urlencode(),
                headers=dict(request.headers),
                session=session,
            )
            res = myferet.render(frequest)
            return HttpResponse(res.body, headers=res.headers)


    def feretui_static_file(request, filepath):
        filepath = myferet.get_static_file_path(filepath)
        if filepath:
            return FileResponse(open(filepath, 'rb'))

        return HttpResponseNotFound("404")


    def call_action(request, action):
        with feretui_session(request, MySession) as session:
            params = dict()
            params.update(request.GET)
            params.update(request.POST)
            frequest = Request(
                method=getattr(Request, request.method),
                querystring=request.GET.urlencode(),
                form=MultiDict(request.POST),
                params=params,
                headers=dict(request.headers),
                session=session,
            )
            res = myferet.execute_action(frequest, action)
            return HttpResponse(res.body, headers=res.headers)
