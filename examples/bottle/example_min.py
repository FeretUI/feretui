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


@route('/feretui/action/<action>', method=['GET'])
def get_action(session, action):
    frequest = Request(
        method=Request.GET,
        querystring=request.query_string,
        headers=dict(request.headers),
        session=session,
    )
    response = myferet.do_action(frequest, action)
    return HTTPResponse(
        body=response.body,
        status=response.status_code,
        headers=response.headers
    )


@route('/feretui/action/<action>', method=['POST'])
def post_action(session, action):
    frequest = Request(
        method=Request.POST,
        body=request.body.read(),
        headers=dict(request.headers),
        session=session,
    )
    response = myferet.do_action(frequest, action)
    return HTTPResponse(
        body=response.body,
        status=response.status_code,
        headers=response.headers
    )


if __name__ == "__main__":
    app = app()
    plugin = MySessionPlugin(cookie_lifetime=600)
    app.install(plugin)
    debug(True)
    run(host="localhost", port=8080)