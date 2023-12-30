from bottle import request, HTTPResponse, route, run, static_file
from datetime import date
from os import path
import logging

logging.basicConfig(level=logging.DEBUG)

from feretui import (  # noqa: E402
    FeretUI, fields, Session, Request, menu_homepage, Actionset, Action,
    Resource, ListView, NewView, FormView, EditView, Filter, Dataset,
)


myferet = FeretUI()


menus = []


def is_auth(session):
    return True if session.user is None else False


@myferet.register_resource('r1', 'Resource 1', menus=menus, security=None)
class R1(Resource):
    code = fields.String(
        default=lambda: date.today().isoformat(),
        required=True,
    )
    label = fields.String(readonly=True, invisible=is_auth)
    comment = fields.String(default="A comment", invisible=['list', 'edit'])
    number = fields.Integer()

    _list_view = ListView(
        fields=[
            code,
            label,
            number,
            comment,
            Actionset(
                "Actions",
                [
                    Action("1", method="display_on_form"),
                    Action("2", method="display_on_form", invisible=True),
                    Action("3", method="display_on_form", invisible=True),
                    Action("4", method="display_on_form", invisible=True),
                    Action("5", method="display_on_form", invisible=True),
                    Action("6", method="display_on_form", invisible=True),
                ]
            )
        ],
        label="Resources 1",
        filters=[
            Filter(number),
            Filter(code),
            Filter(label),
            Filter(fields.String(label='plop'), code='code')],
        actions=[
            Actionset(
                "Group action 1",
                [
                    Action("Click sur moi 1", method="display_on_list", invisible=is_auth),
                    Action("Click sur moi 2", method="display_on_list"),
                    Action("Click sur moi 3", method="display_on_list"),
                    Action("Click sur moi 4", method="display_on_list"),
                    Action("Click sur moi 5", method="display_on_list"),
                    Action("Click sur moi 6", method="display_on_form"),
                ]
            ),
            Actionset(
                "Group action 2",
                [
                    Action("Click sur moi 1", method="display_on_list", invisible=True),
                    Action("Click sur moi 2", method="display_on_list", invisible=True),
                    Action("Click sur moi 3", method="display_on_list", invisible=True),
                ]
            ),
            Actionset(
                "Group action 3",
                [
                    Action("Click sur moi 4", method="display_on_list"),
                    Action("Click sur moi 5", method="display_on_list"),
                    Action("Click sur moi 6", method="display_on_list"),
                ]
            ),
        ],
    )
    _new_view = NewView(
        template_id=None,
        template_src=None,
        label="New resource 1",
    )
    _form_view = FormView(
        template_id=None,
        template_src=None,
        label="R1",
        actions=[
            Actionset(
                "Group action 1",
                [
                    Action("Click sur moi 1", method="display_on_form"),
                    Action("Click sur moi 2", method="display_on_form"),
                    Action("Click sur moi 3", method="display_on_form"),
                    Action("Click sur moi 4", method="display_on_form"),
                    Action("Click sur moi 5", method="display_on_form"),
                    Action("Click sur moi 6", method="display_on_list"),
                ]
            ),
            Actionset(
                "Group action 2",
                [
                    Action("Click sur moi 1", method="display_on_form"),
                    Action("Click sur moi 2", method="display_on_form"),
                    Action("Click sur moi 3", method="display_on_form"),
                ]
            ),
            Actionset(
                "Group action 3",
                [
                    Action("Click sur moi 4", method="display_on_form"),
                    Action("Click sur moi 5", method="display_on_form"),
                    Action("Click sur moi 6", method="display_on_form"),
                ]
            ),
        ],
    )
    _edit_view = EditView(
        template_id=None,
        template_src=None,
        label="R1",
    )

    DATA = [
        {
            'id': f'{x}',
            'code': f'Code{x}',
            'label': f'Label {x}',
            'comment': '',
            'number': x,
        }
        for x in range(102)
    ]

    def __init__(self, id=None):
        super().__init__(id=id)
        self.data = {}
        if id:
            self.data = [
                x
                for x in self.DATA
                if x['id'] == id
            ][0]

    def create(self, **kwargs):
        kwargs['id'] = str(len(self.DATA) + 1)
        self.DATA.append(kwargs)
        return kwargs['id']

    @classmethod
    def filtered_reads(cls, filters, fields, offset, limit):
        DATA = []
        # filter
        DATA.extend(cls.DATA)
        for fname, op, values in filters:
            DATA_ = []
            for data in DATA:
                val = data.get(fname)
                if op == 'eq' and val in values:
                    DATA_.append(data)
                elif op == 'like':
                    for values2 in values:
                        if values2 in val:
                            DATA_.append(data)

            DATA = DATA_

        # offset and limit
        DATA2 = DATA[offset:offset + limit]

        # create dataset
        datas = [
            (data['id'], {f: data[f] for f in fields})
            for data in DATA2
        ]
        return Dataset(
            data=datas,
            total=len(DATA),
        )

    def read(self, fields):
        return {
            field: self.data[field]
            for field in fields
        }

    def update(self, **kwargs):
        self.data.update(kwargs)

    def delete(self):
        self.DATA.remove(self.data)

    @classmethod
    def display_on_list(cls, feret, request):
        print(f"classmethod {cls} : do some thing")

    def display_on_form(self, feret, request):
        print(f"instance {self} : do some thing")


menus.extend([
    R1.get_navbar_menu(),
    menu_homepage,
    {
        'label': "Bulma",
        'url': "https://bulma.io/documentation",
    },
    {
        'label': "Other",
    },
    {
        'label': 'A menu',
        'children': [
            menu_homepage,
            R1.get_navbar_menu(),
            {
                'label': "Bulma",
                'url': "https://bulma.io/documentation",
            },
            {
                'label': "Other",
            },
        ],
    },
    {
        'label': 'A menu',
        'children': [
            {
                'label': 'A menu',
                'children': [
                    menu_homepage,
                    R1.get_navbar_menu(),
                    {
                        'label': "Bulma",
                        'url': "https://bulma.io/documentation",
                    },
                    {
                        'label': "Other",
                    },
                ],
            },
            menu_homepage,
            R1.get_navbar_menu(),
            {
                'label': "Bulma",
                'url': "https://bulma.io/documentation",
            },
            {
                'label': "Other",
            },
        ],
    },
])


@myferet.register_callback
def feretui_navbar_header_left(session):
    return [
        R1.get_navbar_menu(),
    ]


@myferet.register_callback
def feretui_navbar_header_right(session):
    return [
        R1.get_navbar_menu(),
        menu_homepage,
    ]


class Session(Session):
    def __init__(self):
        super().__init__()
        self.lang = 'fr'
        # self.theme = "darkly"
        # self.theme = "journal"
        # self.theme = "minty"


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


@route('/feretui/action/<action>', method=['GET', 'DELETE'])
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


if __name__ == "__main__":
    # myferet.export_catalog('.feretui.pot')
    myferet.load_catalog('./feretui/locale/fr.po', 'fr')
    run(host="localhost", port=8080)
