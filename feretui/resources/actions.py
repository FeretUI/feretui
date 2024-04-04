from markupsafe import Markup


class Action:
    template_id = 'feretui-page-resource-action'

    def __init__(
        self,
        label: str,
        method: str,
        visible_callback=None,
        tooltip=None,
    ):
        self.label = label
        self.method = method
        self.visible_callback = visible_callback
        self.tooltip = tooltip

    def get_label(self):
        return self.label

    def render(
        self,
        feret,
        session,
        resource_code,
        view_code,
    ):
        url = f'{feret.base_url}/action/resource?'
        url += f'action=call&method={self.method}'

        return Markup(feret.render_template(
            session,
            self.template_id,
            url=url,
            label=self.get_label(),
            tooltip=self.tooltip,
            rcode=resource_code,
            vcode=view_code,
        ))

    def is_visible(
        self,
        session,
    ) -> bool:
        return True


class SelectedRowsAction(Action):
    template_id = 'feretui-page-resource-action-for-selected-rows'


class Actionset:

    def __init__(self, label: str, actions: list[Action], tooltip=None):
        self.label = label
        self.actions = actions
        self.tooltip = tooltip

    def get_label(self):
        return self.label

    def render(
        self,
        feret,
        session,
        resource_code,
        view_code,
    ):
        return Markup(feret.render_template(
            session,
            'feretui-page-resource-action-set',
            label=self.get_label(),
            actions=[
                action.render(feret, session, resource_code, view_code)
                for action in self.actions
                if action.is_visible(session)
            ],
            tooltip=self.tooltip,
        ))

    def is_visible(
        self,
        session,
    ) -> bool:
        return all([
            action.is_visible(session)
            for action in self.actions
        ])
