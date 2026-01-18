
import pytest
from wtforms import FormField, SelectMultipleField, StringField, widgets
from wtforms.validators import InputRequired
from feretui.form import FeretUIForm

class TestRGAA115Grouping:
    def test_form_field_render(self, snapshot, feretui, frequest) -> None:
        class SubForm(FeretUIForm):
            sub_name = StringField("Sub Name")

        class MyForm(FeretUIForm):
            sub = FormField(SubForm, label="My Sub Form")

        myform = MyForm()
        # Verify if FormField is wrapped in fieldset
        snapshot.assert_match(myform.sub(), "snapshot_form_field.html")

    def test_select_multiple_checkbox_render(self, snapshot, feretui, frequest) -> None:
        class MyForm(FeretUIForm):
            # SelectMultipleField rendered as a list of checkboxes MUST be grouped
            options = SelectMultipleField(
                "Options",
                choices=[('a', 'A'), ('b', 'B')],
                option_widget=widgets.CheckboxInput(),
                widget=widgets.ListWidget(prefix_label=False)
            )

        myform = MyForm()
        # Verify if SelectMultipleField (checkboxes) is wrapped in fieldset
        snapshot.assert_match(myform.options(), "snapshot_select_multiple.html")

    def test_form_field_render_readonly(self, snapshot, feretui, frequest) -> None:
        class SubForm(FeretUIForm):
            sub_name = StringField("Sub Name")

        class MyForm(FeretUIForm):
            sub = FormField(
                SubForm,
                label="My Sub Form",
                render_kw={"readonly": True},
            )

        myform = MyForm()
        # Verify if FormField is wrapped in fieldset
        snapshot.assert_match(myform.sub(), "snapshot_form_field_readonly.html")

    def test_select_multiple_render(self, snapshot, feretui, frequest) -> None:
        class MyForm(FeretUIForm):
            # SelectMultipleField rendered as a list of checkboxes MUST be grouped
            options = SelectMultipleField(
                "Options",
                choices=[('a', 'A'), ('b', 'B')],
            )

        myform = MyForm()
        # Verify if SelectMultipleField (checkboxes) is wrapped in fieldset
        snapshot.assert_match(
            myform.options(),
            "snapshot_select_multiple_no_list_widget.html",
        )

    def test_select_multiple_required(self, snapshot, feretui, frequest) -> None:
        class MyForm(FeretUIForm):
            options = SelectMultipleField(
                "Options",
                choices=[('a', 'A'), ('b', 'B')],
                option_widget=widgets.CheckboxInput(),
                widget=widgets.ListWidget(prefix_label=False),
                validators=[InputRequired()]
            )

        myform = MyForm()
        # Verify if SelectMultipleField is wrapped in fieldset and shows required
        snapshot.assert_match(myform.options(), "snapshot_select_multiple_required.html")
