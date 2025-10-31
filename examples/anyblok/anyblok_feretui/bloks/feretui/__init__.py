from importlib import import_module
from logging import getLogger
from contextlib import contextmanager
from multidict import MultiDict
from pyramid.response import FileResponse, Response
from pyramid.httpexceptions import exception_response

from anyblok.blok import Blok
from feretui import FeretUI, Request

logger = getLogger(__name__)


@contextmanager
def feretui_session(feretui_session_cls, pyramid_session, anyblok):
    fsession = None
    try:
        fsession = feretui_session_cls(**pyramid_session)
        fsession.anyblok = anyblok
        yield fsession
    finally:
        if fsession:
            fsession.anyblok = None
            pyramid_session.update(fsession.to_dict())
            pyramid_session.save()


def feretui_index(request):
    anyblok = request.anyblok.registry
    myferet = anyblok.Pyramid.myferet
    MySession = anyblok.Pyramid.MySession
    with feretui_session(MySession, request.session, anyblok) as session:
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


def feretui_static_file(request):
    myferet = request.anyblok.registry.Pyramid.myferet
    filepath = myferet.get_static_file_path(
        '/'.join(request.matchdict['filepath']),
    )
    if filepath:
        return FileResponse(filepath)

    raise exception_response(404)


def call_action(request):
    action = request.matchdict['action']
    anyblok = request.anyblok.registry
    myferet = anyblok.Pyramid.myferet
    MySession = anyblok.Pyramid.MySession
    with feretui_session(MySession, request.session, anyblok) as session:
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


class FeretUI(Blok):
    version = "0.1.0"
    author = "Jean-Sébastien Suzanne"
    required = ["anyblok-core", "pyramid"]

    def load(self):
        myferet = import_module(
            '.myferet',
            'anyblok_feretui.bloks.feretui'
        )
        self.anyblok.Pyramid.myferet = myferet.myferet
        self.anyblok.Pyramid.MySession = myferet.MySession
    
    @classmethod
    def pyramid_load_config(cls, config):
        config.add_view(
            view=feretui_index,
            route_name='feretui',
            request_method='GET',
        )
        config.add_view(
            view=feretui_static_file,
            route_name='feretui_static_file',
            request_method='GET',
        )
        config.add_view(
            view=call_action,
            route_name='call_action',
            request_method=('DELETE', 'GET', 'POST'),
        )

        config.add_route('feretui', '/')
        config.add_route('feretui_static_file', '/feretui/static/*filepath')
        config.add_route('call_action', '/feretui/action/{action}')
