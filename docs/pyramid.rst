.. This file is a part of the FeretUI project
..
..    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

Serve FeretUI with pyramid
--------------------------

Pyramid is a small, fast, down-to-earth, open source Python web framework. 
It makes real-world web application development and deployment more fun, more 
predictable, and more productive. Try Pyramid, browse its add-ons and documentation, 
and get an overview.

See the `pyramid documentation <https://docs.pylonsproject.org/projects/pyramid/en/latest/index.html#>`_.

For this example you need  to install some additional package

::

    pip install pyramid, pyramid_beaker

::

    import logging
    from contextlib import contextmanager
    from wsgiref.simple_server import make_server

    from multidict import MultiDict
    from pyramid.config import Configurator
    from pyramid.httpexceptions import exception_response
    from pyramid.response import FileResponse, Response
    from pyramid.view import view_config
    from pyramid_beaker import session_factory_from_settings

    from feretui import FeretUI, Request, Session

    logging.basicConfig(level=logging.DEBUG)


    @contextmanager
    def feretui_session(feretui_session_cls, pyramid_session):
        fsession = None
        try:
            fsession = feretui_session_cls(**pyramid_session)
            yield fsession
        finally:
            if fsession:
                pyramid_session.update(fsession.to_dict())
                pyramid_session.save()


    myferet = FeretUI()

    # Here define your feretui stuff.


    @view_config(route_name='feretui', request_method='GET')
    def feretui(request):
        with feretui_session(Session, request.session) as session:
            frequest = Request(
                method=Request.GET,
                querystring=request.query_string,
                headers=dict(request.headers),
                session=session,
            )
            response = myferet.render(frequest)
            return Response(
                response.body,
                headers=response.headers,
            )


    @view_config(route_name='feretui_static_file', request_method='GET')
    def feretui_static_file(request):
        filepath = myferet.get_static_file_path(
            '/'.join(request.matchdict['filepath']),
        )
        if filepath:
            return FileResponse(filepath)

        raise exception_response(404)


    @view_config(
        route_name='call_action',
        request_method=('DELETE', 'GET', 'POST'),
    )
    def call_action(request):
        action = request.matchdict['action']
        with feretui_session(Session, request.session) as session:
            frequest = Request(
                method=getattr(Request, request.method),
                querystring=request.query_string,
                form=MultiDict(request.POST),
                params=request.params.dict_of_lists(),
                headers=dict(request.headers),
                session=session,
            )
            response = myferet.execute_action(frequest, action)
            return Response(
                response.body,
                headers=response.headers,
            )


    if __name__ == "__main__":
        session_factory = session_factory_from_settings({})
        with Configurator() as config:
            config.include('pyramid_beaker')
            config.set_session_factory(session_factory)
            config.add_route('feretui', '/')
            config.add_route('feretui_static_file', '/feretui/static/*filepath')
            config.add_route('call_action', '/feretui/action/{action}')
            config.scan()
            app = config.make_wsgi_app()

        with make_server('', 8080, app) as httpd:
            logging.info("Serving on port 8080...")
            httpd.serve_forever()
