"""Unit tests for CalendarView and CalResource."""

from datetime import date, datetime

import pytest
from wtforms import DateField, StringField

from feretui.context import cvar_feretui, cvar_request
from feretui.form import FeretUIForm
from feretui.request import Request
from feretui.resources import CalCRUD, CalResource, Resource
from feretui.resources.calendar import CalendarView


class TestCalendar:
    """Test suite for Calendar view."""

    def test_cal_resource_build(self) -> None:
        """Verify CalResource builds with default_view='calendar'."""

        class TaskForm(FeretUIForm):
            pk = StringField()
            name = StringField()
            deadline = DateField()

        class TaskResource(CalResource, Resource):
            code = "tasks"
            label = "Tasks"
            default_view = None
            Form = TaskForm

            def filtered_reads(self, form_cls, filters, offset, limit):
                return {"forms": [], "total": 0}

        res = TaskResource.build()
        assert res.default_view == "calendar"
        assert "calendar" in res.views
        view = res.views["calendar"]
        assert isinstance(view, CalendarView)
        assert view.code == "calendar"

    def test_calendar_date_parsing_and_events(self) -> None:
        """Verify _parse_date and extract_events handling."""
        view = CalendarView.__new__(CalendarView)
        view.date_start_field = "deadline"
        view.date_stop_field = "end_date"
        view.title_field = "name"
        view.color_field = "priority"

        assert view._parse_date(None) is None
        assert view._parse_date(date(2026, 10, 15)) == date(2026, 10, 15)
        dt = datetime(2026, 10, 15, 14, 30)
        assert view._parse_date(dt) == date(2026, 10, 15)
        assert view._parse_date("2026-10-15") == date(2026, 10, 15)
        assert view._parse_date("2026-10-15 10:00:00") == date(2026, 10, 15)
        assert view._parse_date("invalid-date") is None

        class DummyForm:
            class pk:
                data = "task-1"

            class deadline:
                data = "2026-10-19"

            class end_date:
                data = "2026-10-21"

            class name:
                data = "Deliver Milestone 3"

            class priority:
                data = "done"

        class DummyFormNoDate:
            class pk:
                data = "task-2"

            class deadline:
                data = None

            class end_date:
                data = None

            class name:
                data = "Task without date"

            class priority:
                data = None

        events = view.extract_events([DummyForm(), DummyFormNoDate()])
        assert len(events) == 1
        ev = events[0]
        assert ev["pk"] == "task-1"
        assert ev["title"] == "Deliver Milestone 3"
        assert ev["start_date"] == date(2026, 10, 19)
        assert ev["stop_date"] == date(2026, 10, 21)
        assert ev["color"] == "done"

    def test_calendar_build_month_grid(self) -> None:
        """Verify month grid matrix generation."""
        view = CalendarView.__new__(CalendarView)
        events = [
            {
                "pk": "1",
                "title": "Launch",
                "start_date": date(2026, 10, 19),
                "stop_date": None,
                "color": "green",
            }
        ]
        weeks = view.build_month_grid(2026, 10, events)
        assert len(weeks) >= 4
        # Every week has 7 days
        for week in weeks:
            assert len(week) == 7

        # Find October 19, 2026
        oct_19 = None
        for week in weeks:
            for day_cell in week:
                if day_cell["date"] == date(2026, 10, 19):
                    oct_19 = day_cell
                    break
        assert oct_19 is not None
        assert oct_19["day"] == 19
        assert oct_19["is_current_month"] is True
        assert len(oct_19["events"]) == 1
        assert oct_19["events"][0]["title"] == "Launch"

    def test_calendar_render(self, feretui, session) -> None:
        """Verify calendar rendering and navigation URLs."""
        cvar_feretui.set(feretui)
        cvar_request.set(Request(session=session))

        class EventForm(FeretUIForm):
            pk = StringField()
            name = StringField()
            date = StringField()

        class EventResource(CalCRUD, Resource):
            code = "events"
            label = "Events"
            Form = EventForm

            def filtered_reads(self, form_cls, filters, offset, limit):
                f1 = form_cls()
                f1.pk.data = "101"
                f1.name.data = "Sprint Planning"
                f1.date.data = "2026-10-15"
                return {"forms": [f1], "total": 1}

        res = EventResource.build()
        view = res.views["calendar"]

        html = view.render(feretui, session, {"year": "2026", "month": "10"})
        assert "feretui-calendar-view" in html
        assert "October 2026" in html
        assert "Mon" in html and "Sun" in html
        assert "Sprint Planning" in html
        assert "year=2026&amp;month=9" in html
        assert "year=2026&amp;month=11" in html

        # Test January rollback to December of previous year
        html_jan = view.render(feretui, session, {"year": "2026", "month": "1"})
        assert "January 2026" in html_jan
        assert "year=2025&amp;month=12" in html_jan
        assert "year=2026&amp;month=2" in html_jan

        # Test December rollover to January of next year
        html_dec = view.render(feretui, session, {"year": "2026", "month": "12"})
        assert "December 2026" in html_dec
        assert "year=2026&amp;month=11" in html_dec
        assert "year=2027&amp;month=1" in html_dec
