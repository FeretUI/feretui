from typing import TYPE_CHECKING

from feretui.session import Session

if TYPE_CHECKING:
    from feretui.feretui import FeretUI


def page_404(feretui: "FeretUI", session: Session, options: dict):
    page = options.get('page', '')
    if isinstance(page, list):
        page = page[0]

    return feretui.render_template(session, 'feretui-page-404', page=page)


def page_forbidden(feret: "FeretUI", session: Session, options: dict):
    page = options.get('page', '')
    if isinstance(page, list):
        page = page[0]

    return feret.render_template(
        session, 'feretui-page-forbidden', page=page)


def homepage(feret: "FeretUI", session: Session, options: dict):
    return feret.render_template(session, 'feretui-page-homepage')
