import urllib
from wtforms.fields.core import UnboundField
from feretui.form import FeretUIForm


class ViewError(Exception):
    pass


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

    def get_label(self):
        return self.label or 'List'

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


class ListView(View):
    template_type: str = 'list'

    def __init__(
        self,
        fields: list[str] = None,
        # filters: list[Filter] = None,
        limit: int = 15,
        label: str = None,
        # actions: list[Actionset] = None,
    ):
        View.__init__(self, label=label)
        # ActionsMixinForView.__init__(self, actions=actions)
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
            label=self.get_label(),
            fields=self.fields,
            form=form_cls(),
            # filters=filters,
            offset=offset,
            limit=self.limit,
            paginations=paginations,
            dataset=dataset,
            create_view_qs=create_view_qs,
            open_view_qs=open_view_qs,
        )
