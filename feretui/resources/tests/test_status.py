"""Tests for StatusBarWidget and StatusBarField."""

from wtforms import StringField
from wtforms.validators import InputRequired

from feretui.form import FeretUIForm, onchange
from feretui.resources.status import (
    StatusBarField,
    StatusBarWidget,
    wrap_status_bar,
)


class TestStatusBar:
    """Test suite for StatusBarWidget and StatusBarField."""

    def test_widget_standalone_render(self) -> None:
        widget = StatusBarWidget()
        stages = [("draft", "Draft"), ("in_progress", "In Progress"), ("done", "Done")]

        # Render with active middle step, interactive
        html = widget.render(
            stages=stages,
            current="in_progress",
            readonly=False,
            field_id="wf-status",
            field_name="status",
        )
        assert 'class="feretui-status-bar"' in html
        assert 'aria-label="Workflow Status"' in html
        assert 'value="in_progress"' in html
        assert 'id="wf-status"' in html
        assert 'name="status"' in html

        # Check passed step (Draft)
        assert '<li class="is-passed passed">' in html
        assert 'onclick="var el=document.getElementById(\'wf-status\');' in html

        # Check current step (In Progress)
        assert '<li class="is-current current">' in html
        assert 'aria-current="step"' in html
        assert "<button " in html

        # Check future step (Done)
        assert '<li class="is-future future">' in html

    def test_widget_readonly_render(self) -> None:
        widget = StatusBarWidget(clickable=False)
        stages = [("draft", "Draft"), ("done", "Done")]

        html = widget.render(
            stages=stages,
            current="draft",
            readonly=True,
        )
        # All buttons must be disabled when readonly
        assert 'onclick="' not in html
        assert html.count("disabled") == 2

    def test_widget_current_not_in_stages(self) -> None:
        widget = StatusBarWidget()
        stages = [("a", "Stage A"), ("b", "Stage B")]
        html = widget.render(stages=stages, current="unknown")
        # All items are treated as future
        assert 'class="is-future future"' in html
        assert "is-current" not in html
        assert "is-passed" not in html

    def test_widget_call_via_field(self, feretui, frequest) -> None:
        class OrderForm(FeretUIForm):
            status = StatusBarField(
                "Status",
                choices=[("draft", "Draft"), ("confirmed", "Confirmed")],
                default="draft",
            )

        form = OrderForm()
        widget = StatusBarWidget()
        html = widget(form.status, readonly=True)
        assert 'name="status"' in html
        assert 'value="draft"' in html

    def test_status_bar_field_in_form(self, feretui, frequest) -> None:
        class TaskForm(FeretUIForm):
            pk = StringField()
            state = StatusBarField(
                "Task State",
                choices=[("todo", "To Do"), ("done", "Done")],
                default="todo",
                description="Current workflow stage",
            )

        form = TaskForm()
        html = form.state()
        assert 'class="feretui-status-bar-wrapper"' in html
        assert "Task State" in html
        assert "Current workflow stage" in html
        assert 'value="todo"' in html

    def test_wrap_status_bar_options(self, feretui, frequest) -> None:
        class DocForm(FeretUIForm):
            pk = StringField()
            status = StatusBarField(
                "Status",
                choices=[("new", "New"), ("signed", "Signed")],
                validators=[InputRequired()],
            )

        form = DocForm()
        form.validate()  # Triggers error since no input

        # Test with wrapper_id and oob=True
        html = wrap_status_bar(
            feretui,
            frequest.session,
            form.status,
            wrapper_id="status-wrapper",
            oob=True,
            nolabel=True,
        )
        assert 'id="status-wrapper"' in html
        assert 'hx-swap-oob="true"' in html
        assert "status-bar-label" not in html
        assert 'id="invalid-helper"' in html

        # Test with wrapper_id and oob=False without nolabel
        html2 = wrap_status_bar(
            feretui,
            frequest.session,
            form.status,
            wrapper_id="status-wrapper-2",
            oob=False,
            nolabel=False,
        )
        assert 'id="status-wrapper-2"' in html2
        assert 'hx-swap-oob="true"' not in html2
        assert "status-bar-label" in html2

    def test_status_bar_onchange_integration(self, feretui, frequest) -> None:
        class PipelineForm(FeretUIForm):
            pk = StringField()
            stage = StatusBarField(
                "Stage",
                choices=[("step1", "Step 1"), ("step2", "Step 2")],
                default="step1",
            )
            note = StringField()

            @onchange("stage")
            def _stage_changed(self) -> None:
                if self.stage.data == "step2":
                    self.note.data = "Advanced to step 2"

        form = PipelineForm()
        form.stage.data = "step2"
        modified = form.process_onchange("stage")
        assert "note" in modified
        assert form.note.data == "Advanced to step 2"
