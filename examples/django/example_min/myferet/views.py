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
