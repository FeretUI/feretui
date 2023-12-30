from typing import TYPE_CHECKING

from feretui.helper import unauthenticated_or_forbidden
from feretui.session import Session

if TYPE_CHECKING:
    from feretui.feretui import FeretUI


def page_404(feret: "FeretUI", session: Session, options: dict):
    page = options.get('page', '')
    if isinstance(page, list):
        page = page[0]

    return feret.load_page_template(session, 'feretui-page-404', page=page)


def page_forbidden(feret: "FeretUI", session: Session, options: dict):
    page = options.get('page', '')
    if isinstance(page, list):
        page = page[0]

    return feret.load_page_template(
        session, 'feretui-page-forbidden', page=page)


def page_homepage(feret: "FeretUI", session: Session, options: dict):
    return feret.load_page_template(session, 'feretui-page-homepage')


@unauthenticated_or_forbidden
def page_login(feret: "FeretUI", session: Session, options: dict):
    return feret.load_page_template(session, 'feretui-page-login')


@unauthenticated_or_forbidden
def page_signup(feret: "FeretUI", session: Session, options: dict):
    return feret.load_page_template(session, 'feretui-page-signup')


def page_resource(feret: "FeretUI", session: Session, options: dict):
    resourcecode = options['resource']
    if isinstance(resourcecode, list):
        resourcecode = resourcecode[0]

    Resource = feret.get_resource(resourcecode)

    def render(feret, session, options):
        left_menus = Resource.render_menus()
        actions = Resource.get_actions(feret, session, options)
        template_id = 'feretui-page-resource'
        if left_menus:
            template_id += '-left'
        if actions:
            template_id += '-right'

        return feret.load_page_template(
            session,
            template_id,
            resource=resourcecode,
            resource_url=Resource.get_view_url_from_options(options),
            left_menus=left_menus,
            actions=actions,
        )

    if Resource._security:
        render = Resource._security(render)

    new_options = options.copy()
    new_options['page'] = [Resource.get_label()]
    return render(feret, session, new_options)
