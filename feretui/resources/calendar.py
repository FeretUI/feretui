# This file is a part of the FeretUI project
#
#    Copyright (C) 2024 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""Module feretui.resources.calendar.

The Calendar resource displays data organized on a date calendar grid.

* :class:`.CalendarView`
* :class:`.CalResource`
"""

import calendar
from datetime import date, datetime
from typing import TYPE_CHECKING, Any

from markupsafe import Markup

from feretui.form import FeretUIForm
from feretui.resources.common import LabelMixinForView, MultiView
from feretui.resources.view import View
from feretui.session import Session

from .resource import Resource

if TYPE_CHECKING:
    from feretui.feretui import FeretUI


class DefaultViewCalendar:
    """Default value for the view calendar."""

    label: str = None
    limit: int = 500
    create_button_redirect_to: str = None
    delete_button_redirect_to: str = None
    do_click_on_entry_redirect_to: str = None
    date_start_field: str = "date"
    date_stop_field: str | None = None
    title_field: str = "name"
    color_field: str | None = None
    mode: str = "month"
    quick_filters: list = []


class CalendarView(MultiView, LabelMixinForView, View):
    """Calendar view for date-based scheduling and planning."""

    code: str = "calendar"
    limit: int = 500
    create_button_redirect_to: str = None
    delete_button_redirect_to: str = None
    do_click_on_entry_redirect_to: str = None
    date_start_field: str = "date"
    date_stop_field: str | None = None
    title_field: str = "name"
    color_field: str | None = None
    mode: str = "month"

    def _parse_date(self, val: object) -> date | None:
        """Parse a date, datetime, or date string into a date object."""
        if not val:
            return None
        if isinstance(val, datetime):
            return val.date()
        if isinstance(val, date):
            return val
        if isinstance(val, str):
            clean_val = val[:19]
            try:
                return datetime.fromisoformat(clean_val).date()
            except ValueError:
                pass
            try:
                return datetime.strptime(clean_val, "%d/%m/%Y").date()
            except ValueError:
                pass
        return None

    def extract_events(
        self: "CalendarView",
        forms: list[FeretUIForm],
    ) -> list[dict[str, Any]]:
        """Extract events from forms."""
        events = []
        for form in forms:
            pk = getattr(getattr(form, "pk", None), "data", None)

            start_field = getattr(form, self.date_start_field, None)
            start_raw = getattr(start_field, "data", None)
            start_date = self._parse_date(start_raw)
            if not start_date:
                continue

            stop_date = None
            if self.date_stop_field:
                stop_field = getattr(form, self.date_stop_field, None)
                stop_raw = getattr(stop_field, "data", None)
                stop_date = self._parse_date(stop_raw)

            title_field = getattr(form, self.title_field, None)
            title = getattr(title_field, "data", "") or str(pk)

            color = None
            if self.color_field:
                color_field = getattr(form, self.color_field, None)
                color = getattr(color_field, "data", None)

            events.append(
                {
                    "pk": pk,
                    "title": title,
                    "start_date": start_date,
                    "stop_date": stop_date,
                    "color": color,
                    "form": form,
                }
            )
        return events

    def build_month_grid(
        self: "CalendarView",
        year: int,
        month: int,
        events: list[dict[str, Any]],
    ) -> list[list[dict[str, Any]]]:
        """Build the month weeks matrix with events assigned to days."""
        cal = calendar.Calendar(firstweekday=0)
        today = date.today()
        weeks: list[list[dict[str, Any]]] = []

        for week_dates in cal.monthdatescalendar(year, month):
            week_days: list[dict[str, Any]] = []
            for d in week_dates:
                is_current_month = d.month == month
                is_today = d == today
                day_events = [
                    ev
                    for ev in events
                    if (
                        ev["start_date"]
                        <= d
                        <= (ev["stop_date"] or ev["start_date"])
                    )
                ]
                week_days.append(
                    {
                        "date": d,
                        "date_str": d.isoformat(),
                        "day": d.day,
                        "is_current_month": is_current_month,
                        "is_today": is_today,
                        "events": day_events,
                    }
                )
            weeks.append(week_days)
        return weeks

    def render(
        self: "CalendarView",
        feretui: "FeretUI",
        session: Session,
        options: dict,
    ) -> str:
        """Render calendar view."""
        kwargs = self.render_kwargs(feretui, session, options)
        dataset = kwargs.get("dataset", {})
        forms = dataset.get("forms", [])

        today = date.today()
        year_opt = options.get("year")
        month_opt = options.get("month")

        year = (
            int(year_opt[0] if isinstance(year_opt, list) else year_opt)
            if year_opt
            else today.year
        )
        month = (
            int(month_opt[0] if isinstance(month_opt, list) else month_opt)
            if month_opt
            else today.month
        )

        # Month Navigation
        if month == 1:
            prev_year, prev_month = year - 1, 12
        else:
            prev_year, prev_month = year, month - 1

        if month == 12:
            next_year, next_month = year + 1, 1
        else:
            next_year, next_month = year, month + 1

        events = self.extract_events(forms)
        weeks = self.build_month_grid(year, month, events)
        month_name = calendar.month_name[month]

        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        base_goto = (
            f"{feretui.base_url}/action/goto?page=resource"
            f"&resource={self.resource.code}&view={self.code}"
        )
        prev_url = f"{base_goto}&year={prev_year}&month={prev_month}"
        next_url = f"{base_goto}&year={next_year}&month={next_month}"
        today_url = f"{base_goto}&year={today.year}&month={today.month}"

        return Markup(
            feretui.render_template(
                session,
                "feretui-resource-calendar",
                year=year,
                month=month,
                month_name=month_name,
                day_names=day_names,
                weeks=weeks,
                prev_url=prev_url,
                next_url=next_url,
                today_url=today_url,
                **kwargs,
            ),
        )


class CalResource:
    """CalResource class mixin."""

    default_view: str = "calendar"
    MetaViewCalendar = DefaultViewCalendar

    def build_view(
        self: "CalResource",
        view_cls_name: str,
    ) -> Resource:
        """Return view instance for MetaViewCalendar."""
        if view_cls_name.startswith("MetaViewCalendar"):
            meta_view_cls = self.get_meta_view_class(view_cls_name)
            meta_view_cls.append(CalendarView)
            view_cls = type(
                "CalendarView",
                tuple(meta_view_cls),
                {},
            )
            if not self.default_view:
                self.default_view = view_cls.code

            return view_cls(self)

        return super().build_view(view_cls_name)
