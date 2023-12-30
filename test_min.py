from bottle import request, HTTPResponse, route, run, static_file
from os import path
from feretui import FeretUI, Session, Request
import logging
logging.basicConfig(level=logging.DEBUG)


myferet = FeretUI()
session = Session()


@route('/')
def index():
    frequest = Request(
        method=Request.GET,
        querystring=request.query_string,
        headers=dict(request.headers),
        request=request,
        session=session,
    )
    return myferet.render(frequest)


@route('/feretui/static/<filename>')
def feretui_static_file(filename):
    filepath = myferet.get_static_file_path(filename)
    if filepath:
        root, name = path.split(filepath)
        return static_file(name, root)

    return None


@route('/feretui/action/<action>', method=['GET'])
def get_action(action):
    frequest = Request(
        method=Request.GET,
        querystring=request.query_string,
        headers=dict(request.headers),
        request=request,
        session=session,
    )
    response = myferet.do_action(frequest, action)
    return HTTPResponse(
        body=response.body,
        status=response.status_code,
        headers=response.headers
    )


@route('/feretui/action/<action>', method=['POST'])
def post_action(action):
    frequest = Request(
        method=Request.POST,
        body=request.body.read(),
        headers=dict(request.headers),
        request=request,
        session=session,
    )
    response = myferet.do_action(frequest, action)
    return HTTPResponse(
        body=response.body,
        status=response.status_code,
        headers=response.headers
    )


if __name__ == "__main__":
    run(host="localhost", port=8080)
