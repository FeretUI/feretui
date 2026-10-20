# This file is a part of the FeretUI project
#
#    Copyright (C) 2024-2026 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Tests for ProgressBarWidget, ProgressBarField, and progress_bar_widget."""

from typing import Any

from feretui.form import (
    FeretUIForm,
    ProgressBarField,
    ProgressBarWidget,
    wrap_progress_bar,
)
from feretui.resources.list import progress_bar_widget


class ProjectForm(FeretUIForm):
    """Test form with progress bar field."""

    progress = ProgressBarField(
        "Progress",
        max_value=100.0,
        show_label=True,
    )
    quota = ProgressBarField(
        "Quota",
        max_value=50.0,
        label_template="{value}/{max_value} units ({percent}%)",
    )


class TestProgressBar:
    """Test suite for ProgressBarWidget and ProgressBarField."""

    def test_widget_direct_call(self) -> None:
        """Test ProgressBarWidget __call__ formatting."""
        widget = ProgressBarWidget(max_value=100.0)

        class DummyField:
            data = 75.0
            max_value = 100.0
            show_label = True
            label_template = None

        html = widget(DummyField())
        assert 'class="feretui-progress-bar"' in html
        assert '<progress value="75.0" max="100.0">75%</progress>' in html
        assert "75%" in html

    def test_widget_custom_label_template(self) -> None:
        """Test ProgressBarWidget with custom label_template."""
        widget = ProgressBarWidget(
            max_value=50.0,
            label_template="{value}/{max_value} ({percent}%)",
        )

        class DummyField:
            data = "25"
            max_value = 50.0
            show_label = True
            label_template = "{value}/{max_value} ({percent}%)"

        html = widget(DummyField())
        assert "25.0/50.0 (50%)" in html

    def test_widget_invalid_data_and_clamping(self) -> None:
        """Test ProgressBarWidget with invalid, negative, or exceeding values."""
        widget = ProgressBarWidget(max_value=100.0)

        class DummyField:
            data = "invalid"
            max_value = 100.0
            show_label = False
            label_template = None

        html = widget(DummyField())
        assert '<progress value="0.0" max="100.0">0%</progress>' in html
        assert 'class="progress-label"' not in html

    def test_field_in_form(self, feretui: Any, session: Any, frequest: Any) -> None:  # noqa: ARG002
        """Test ProgressBarField rendering within FeretUIForm."""
        form = ProjectForm(data={"progress": 45.0, "quota": 10.0})
        html = form.progress()
        assert "feretui-progress-bar-wrapper" in html
        assert "Progress" in html
        assert '<progress value="45.0" max="100.0">45%</progress>' in html

        html_quota = form.quota()
        assert "10.0/50.0 units (20%)" in html_quota

    def test_process_formdata(self) -> None:
        """Test process_formdata parsing numeric strings or empty submissions."""
        form = ProjectForm()
        form.progress.process_formdata(["82.5"])
        assert form.progress.data == 82.5

        form.progress.process_formdata(["bad_val"])
        assert form.progress.data is None

        form.progress.process_formdata([])
        assert form.progress.data is None

    def test_wrap_progress_bar_with_wrapper_id(
        self, feretui: Any, session: Any, frequest: Any  # noqa: ARG002
    ) -> None:
        """Test wrap_progress_bar with wrapper_id and OOB swap attributes."""
        form = ProjectForm(data={"progress": 60.0})
        html = wrap_progress_bar(
            feretui,
            session,
            form.progress,
            wrapper_id="pbar-container",
            oob=True,
            nolabel=True,
        )
        assert 'id="pbar-container"' in html
        assert 'hx-swap-oob="true"' in html

    def test_list_progress_bar_widget(self) -> None:
        """Test progress_bar_widget for list view table columns."""
        field = ProgressBarField()
        field.data = 80.0
        field.max_value = 100.0

        html = progress_bar_widget(field)
        assert "<progress" in html
        assert 'value="80.0"' in html
        assert "80%" in html

        # With empty / invalid data
        field.data = None
        html_empty = progress_bar_widget(field)
        assert 'value="0.0"' in html_empty
        assert "0%" in html_empty

        field.data = "not-a-number"
        html_invalid = progress_bar_widget(field)
        assert 'value="0.0"' in html_invalid

