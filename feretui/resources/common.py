from markupsafe import Markup

from feretui.request import Request
from feretui.resources.actions import SelectedRowsAction
from feretui.response import Response


class MultiViewHeaderButtons:

    def get_header_buttons(self, feretui, session, options):
        res = []
        if self.create_button_redirect_to:
            res.append(
                Markup(feretui.render_template(
                    session,
                    'view-create-button',
                    create_view_qs=self.get_transition_querystring(
                        options,
                        view=self.create_button_redirect_to,
                    ),
                )),
            )

        return res


class ActionsMixinForView:

    actions: list = []

    def get_actions(self, feret, session):
        return [
            actionset.render(feret, session, self.resource.code, self.code)
            for actionset in self.actions
            if actionset.is_visible(session)
        ]

    def get_call_kwargs(self, params):
        return {}

    def call(self, feretui, request):
        if request.method is not Request.POST:
            raise Exception

        method = request.params.get('method')
        if isinstance(method, list):
            method = method[0]

        is_declared = False
        view_kwargs = {}
        for actionset in self.actions:
            for action in actionset.actions:
                if action.is_visible(request.session):
                    if action.method == method:
                        if isinstance(action, SelectedRowsAction):
                            view_kwargs.update(
                                self.get_call_kwargs(request.params),
                            )

                        is_declared = True
                        break

        if not is_declared:
            raise Exception

        func = getattr(self.resource, method)
        res = func(feretui, request, **view_kwargs)
        if res:
            if not isinstance(res, Response):
                res = Response(res)
        else:
            qs = request.get_query_string_from_current_url()
            res = Response(Markup(self.render(feretui, request.session, qs)))

        return res
