.. This file is a part of the FeretUI project
..
..    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

Serve FeretUI with starlette
----------------------------

Starlette is a lightweight ASGI framework/toolkit, which is ideal for 
building async web services in Python.

See the `starlette documentation <https://www.starlette.io/>`_.

For this example you need  to install some additional package

::

    pip install starlette uvicorn python-multipart itsdangerous

::

    import logging
    from contextlib import contextmanager

    from starlette.applications import Starlette
    from starlette.responses import HTMLResponse, FileResponse, Response
    from starlette.routing import Route
    from starlette.middleware import Middleware
    from starlette.middleware.sessions import SessionMiddleware

    from multidict import MultiDict
    import uvicorn

    logging.basicConfig(level=logging.DEBUG)


    @contextmanager
    def feretui_session(request, cls):
        session = None
        try:
            session = cls(**request.session)
            yield session
        finally:
            if session:
                request.session.update(session.to_dict())


    myferet = FeretUI()

    # Here define your feretui stuff.


    async def index(request):
        with feretui_session(request, MySession) as session:
            frequest = Request(
                method=Request.GET,
                querystring=request.scope['query_string'].decode('utf-8'),
                headers=request.headers,
                session=session,
            )
            res = myferet.render(frequest)
            return HTMLResponse(res.body, headers=res.headers)


    async def feretui_static_file(request):
        filepath = myferet.get_static_file_path(request.path_params['filepath'])
        if filepath:
            return FileResponse(filepath)

        return Response('', status_code=404)


    async def get_params(request):
        res = {}
        res.update({
            key: request.query_params.getlist(key)
            for key in request.query_params.keys()
            if request.query_params.get(key)
        })

        form = await request.form()
        res.update({
            key: form.getlist(key)
            for key in form.keys()
            if form.get(key)
        })

        return res


    async def call_action(request):
        with feretui_session(request, MySession) as session:
            form = await request.form()
            frequest = Request(
                method=getattr(Request, request.method),
                querystring=request.scope['query_string'].decode('utf-8'),
                form=MultiDict(form),
                params=await get_params(request),
                headers=request.headers,
                session=session,
            )
            res = myferet.execute_action(frequest, request.path_params['action'])
            return HTMLResponse(res.body, headers=res.headers)


    if __name__ == "__main__":
        app = Starlette(
            debug=True,
            routes=[
                Route('/', index),
                Route('/feretui/static/{filepath:path}', feretui_static_file),
                Route(
                    '/feretui/action/{action:str}',
                    call_action,
                    methods=['GET', 'POST']),
            ],
            middleware=[
                Middleware(SessionMiddleware, secret_key="secret"),
            ],
        )
        uvicorn.run(app, port=8080, log_level="info")
