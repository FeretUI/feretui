from bottle import request, HTTPResponse, route, run, static_file
from os import path
import logging
logging.basicConfig(level=logging.DEBUG)

from feretui import (  # noqa: E402
    FeretUI, Session, Request, authenticated_or_login, authenticated_or_404,
    menu_login, menu_signup, menu_homepage
)


myferet = FeretUI()


@myferet.register_page
@authenticated_or_login
def toto(feret, session, options):
    """
        <template id="my-feret-toto">
            <p>Toto</p>
        </template>
    """
    return feret.load_page_template(session, 'my-feret-toto')


@myferet.register_page
@authenticated_or_404
def titi(feret, session, options):
    """
        <template id="my-feret-titi">
            <p>Titi</p>
        </template>
    """
    return feret.load_page_template(session, 'my-feret-titi')


@myferet.register_callback
def feretui_navbar_header_left(session):
    menus = [
        {
            'label': "Bulma",
            'url': "https://bulma.io/documentation",
        },
        {
            'code': "toto",
            'label': "Toto",
        },
        {
            'code': "titi",
            'label': "Titi",
        },
    ]
    if session.user:
        menus.append(menu_homepage)

    return menus


@myferet.register_callback
def feretui_navbar_header_right(session):
    return [
        {
            'code': "homepage",
            'label': "Home",
        },
    ]


@myferet.register_callback
def feretui_navbar_authentications():
    return [menu_signup, menu_login]


class Session(Session):
    def __init__(self):
        super().__init__()
        self.lang = 'fr'
        self.theme = "minty"


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
    # myferet.export_catalog('./feretui/locale/feretui.pot')
    myferet.load_catalog('./feretui/locale/fr.po', 'fr')
    run(host="localhost", port=8080)
