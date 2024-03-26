import urllib
from wtforms.fields.core import UnboundField
from feretui.form import FeretUIForm
from markupsafe import Markup


class ViewError(Exception):
    pass


class Action:

    def __init__(
        self,
        label: str,
        method: str,
        visible_callback=None,
        css_class=None,
        tooltip=None,
    ):
        self.label = label
        self.method = method
        self.visible_callback = visible_callback
        self.tooltip = tooltip
        if css_class is None:
            css_class = []

        self.css_class = css_class

    def get_label(self):
        return self.label

    def render(
        self,
        feret,
        session,
        pk=False,
    ):
        url = f'{feret.base_url}/action/resource?'
        url += f'action=call&method={self.method}'
        if pk:
            url += '&pk={pk}'

        return Markup(feret.render_template(
            session,
            'feretui-page-resource-action',
            url=url,
            label=self.get_label(),
            css_class=' '.join(self.css_class),
            tooltip=self.tooltip,
        ))

    def is_visible(
        self,
        session,
    ) -> bool:
        return True


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
    ):
        return Markup(feret.render_template(
            session,
            'feretui-page-resource-action-set',
            label=self.get_label(),
            actions=[
                action.render(feret, session)
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


class View:

    def __init__(
        self,
        label: str = None,
    ):
        self.label = label

    def render(
        self,
        resource_cls,
        feret,
        session,
        options: dict[str, list[str]],
    ) -> str:
        raise ViewError('render must be overwriting')

    def get_label(self, resource_cls):
        return self.label or resource_cls._label

    def get_transition_querystring(
        self,
        options: dict,
        **kwargs: dict[str, str],
    ):
        options = options.copy()
        for key, value in kwargs.items():
            if value is None:
                options.pop(key, None)
            elif isinstance(value, list):
                options[key] = value
            else:
                options[key] = [value]

        return urllib.parse.urlencode(options, doseq=True)


class ActionsMixinForView:

    def __init__(
        self,
        actions: list[Actionset] = None,
    ):
        if actions is None:
            actions = []

        self.actions = actions

    def get_actions(
        self,
        feret,
        session,
    ):
        return [
            actionset.render(
                feret,
                session,
            )
            for actionset in self.actions
            if actionset.is_visible(session)
        ]


class ListView(ActionsMixinForView, View):

    def __init__(
        self,
        fields: list[str] = None,
        # filters: list[Filter] = None,
        limit: int = 15,
        label: str = None,
        actions: list[Actionset] = None,
    ):
        View.__init__(self, label=label)
        ActionsMixinForView.__init__(self, actions=actions)
        self.fields = fields
        # self.filters = filters
        self.limit = limit

    def render(
        self,
        resource_cls,
        feret,
        session,
        options: dict,
    ) -> str:
        properties = {}

        if self.fields:
            for attr in dir(resource_cls.Form):
                field = getattr(resource_cls.Form, attr)
                if isinstance(field, UnboundField):
                    if attr not in self.fields:
                        properties[attr] = None
        else:
            self.fields = [
                attr
                for attr in dir(resource_cls.Form)
                if isinstance(getattr(resource_cls.Form, attr), UnboundField)
            ]

        form_cls = type(
            f'{resource_cls._code}__list',
            (resource_cls.Form, FeretUIForm),
            properties,
        )

        offset = options.get('offset', 0)
        if isinstance(offset, list):
            offset = offset[0]

        offset = int(offset)
        dataset = resource_cls.filtered_reads(
            form_cls,
            None,  # filters,
            offset,
            self.limit,
        )
        paginations = range(0, dataset['total'], self.limit)

        create_view_qs = self.get_transition_querystring(
            options,
            view=resource_cls.on_list_create_button_redirect_to,
        )

        open_view_qs = self.get_transition_querystring(
            options,
            id=None,
            view=resource_cls.on_list_do_click_on_row_redirect_to,
        )

        return feret.render_template(
            session,
            'feretui-page-resource-list',
            label=self.get_label(resource_cls),
            form=form_cls(),
            fields=self.fields,
            offset=offset,
            limit=self.limit,
            paginations=paginations,
            dataset=dataset,
            actions=self.get_actions(feret, session),
            create_view_qs=create_view_qs,
            open_view_qs=open_view_qs,
        )
