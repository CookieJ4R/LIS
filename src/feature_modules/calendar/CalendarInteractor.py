import asyncio
from datetime import datetime, date, time, timezone
from enum import auto, Enum
from typing import Callable

import aiohttp
import tzlocal
from icalendar import Calendar

from core_modules.eventing.BaseEvent import BaseEvent
from core_modules.eventing.EventReceiver import EventReceiver
from core_modules.logging.lis_logging import get_logger
from core_modules.rest.RestServerEvents import SSEDataEvent
from core_modules.scheduling.EventRepeatPolicy import EventRepeatPolicy
from core_modules.scheduling.SchedulingEvents import ScheduleEventExecutionEvent, UnscheduleEventExecutionEvent
from core_modules.scheduling.scheduling_helper import get_next_week_for_date, get_next_day_for_date, \
    get_next_year_for_date, get_next_month_for_date, get_next_quarter_hour
from core_modules.storage.StorageManager import StorageManager
from feature_modules.calendar.CalendarEventSchedule import CalendarEventSchedule
from feature_modules.calendar.CalendarEventType import CalendarEventType
from feature_modules.calendar.CalendarEvents import CalendarRefreshEvent, CalendarFetchNextEvent, \
    CalendarFetchNextResponseEvent, CalendarFetchTodayEvent, CalendarFetchTodayResponseEvent
from feature_modules.calendar.CalendarRepeatPolicy import CalendarRepeatPolicy
from feature_modules.calendar.SpecificCalendarEvent import SpecificCalendarEvent


class CalendarEventOrdering(Enum):
    EARLIEST_START = auto()
    EARLIEST_END = auto()


CALENDAR_URL_FIELD = "CALENDAR_URL"
CALENDAR_SECTION = "CALENDAR"

CALENDAR_EVENT_MARKER = "VEVENT"
CALENDAR_COMPONENT_DTSTART = "dtstart"
CALENDAR_COMPONENT_DTEND = "dtend"
CALENDAR_COMPONENT_SUMMARY = "summary"
CALENDAR_COMPONENT_RRULE = "rrule"
CALENDAR_COMPONENT_RRULE_FREQ = "FREQ"
CALENDAR_COMPONENT_RRULE_UNTIL = "UNTIL"


class CalendarInteractor(EventReceiver):
    """
    Class containing all logic for integrating an ical Calendar into LIS.
    """
    log = get_logger(__name__)

    def __init__(self, put_event: Callable, storage: StorageManager):
        super().__init__()
        self.put_event = put_event
        self.calendar_url = storage.get(CALENDAR_URL_FIELD, CALENDAR_SECTION)
        self.last_fetched_events = []
        self.current_expire_refresh_event = None
        self.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False))
        asyncio.create_task(self.fetch_and_schedule_refresh_task())
        asyncio.create_task(self.schedule_auto_refresh_task())

    def fetch_events_to_register(self) -> list[type[BaseEvent]]:
        return [CalendarRefreshEvent, CalendarFetchNextEvent, CalendarFetchTodayEvent]

    async def handle_specific_event(self, event: BaseEvent):
        if isinstance(event, CalendarRefreshEvent):
            await self.fetch_and_schedule_refresh_task()
        elif isinstance(event, CalendarFetchNextEvent):
            next_events = self.get_next_events(await self.fetch_events_and_refresh(), limit=event.limit)
            next_events_json = list(map(lambda ev: ev.to_dict(), next_events))
            await self.put_event(CalendarFetchNextResponseEvent(next_events_json))
        elif isinstance(event, CalendarFetchTodayEvent):
            today_events = self.get_events_for_today(await self.fetch_events_and_refresh(), limit=event.limit)
            today_events_json = list(map(lambda ev: ev.to_dict(), today_events))
            await self.put_event(CalendarFetchTodayResponseEvent(today_events_json))

    async def fetch_and_schedule_refresh_task(self):
        """
        Fetches all events and schedules a refresh for end of the first calendar event. Also puts an update indicator
        onto the SSE stream, signalising the frontend that new data may be available.
        """
        events = await self._fetch_calendar_events()
        next_events = self.get_next_events(events, limit=1, order_by=CalendarEventOrdering.EARLIEST_END)
        if len(next_events) > 0 and events != self.last_fetched_events:
            # schedule refresh for end of first "next event"
            next_event = next_events[0]
            if len(self.last_fetched_events) == 0 or next_event != self.last_fetched_events[0]:
                self.log.debug("Scheduling refresh event for next event at " + str(next_event.end.replace(tzinfo=None)))
                if self.current_expire_refresh_event is not None:
                    await self.put_event(UnscheduleEventExecutionEvent(self.current_expire_refresh_event))
                event_expire_to_schedule = CalendarRefreshEvent()
                await self.put_event(ScheduleEventExecutionEvent(next_event.end.replace(tzinfo=None),
                                                                 event_expire_to_schedule))
                self.current_expire_refresh_event = event_expire_to_schedule
                # output signal to SSE for client to trigger a re-fetch
                # no calendar events are sent over sse as the client should decide how many events to fetch
                await self.put_event(SSEDataEvent("calendar/update", ""))
        self.last_fetched_events = events

    async def schedule_auto_refresh_task(self):
        """
        Schedules an event on startup that runs every quarter of an hour to trigger the refresh task in case new events
        have been added to the calendar during that time.
        """
        self.log.debug("Scheduling refresh event for auto refresh at " + str(get_next_quarter_hour()))
        await self.put_event(ScheduleEventExecutionEvent(get_next_quarter_hour(),
                                                         CalendarRefreshEvent(),
                                                         repeat_policy=EventRepeatPolicy.QuarterHourly))

    @staticmethod
    def _get_next_valid_event(original_event_schedule: CalendarEventSchedule, specific_event: SpecificCalendarEvent,
                              already_scheduled_events_list, next_schedule_func):
        """
        Internal method to get the next valid event for a specified event schedule and a specific event in the past.
        :param original_event_schedule: The original schedule to calculate the specific event on.
        :param specific_event: The specific event that has happened in the past. (the only one present in the ics file)
        :param already_scheduled_events_list: a list of already scheduled event
        (to prevent only getting the next possible event)
        :param next_schedule_func: The helper func to calculate the next event with (e.g. get_next_day_for_date)
        :return: The specific event if an event in the future complies with the schedule, else None
        """
        while (specific_event.start < datetime.now(tzlocal.get_localzone()) or
               specific_event in already_scheduled_events_list):
            specific_event = SpecificCalendarEvent(next_schedule_func(specific_event.start),
                                                   next_schedule_func(specific_event.end),
                                                   specific_event.summary, specific_event.type)
            # return this event if it is an event that spans the whole day and its next occurrence is today
            if specific_event.type == CalendarEventType.DaySlot and specific_event.start.date() == date.today():
                break
        if original_event_schedule.repeat_until is not None and (
                original_event_schedule.repeat_until > specific_event.start):
            return specific_event
        return None

    def get_events_for_today(self, events, limit=3):
        """
        Returns the events scheduled for today
        :param events: All events in the calendar
        :param limit: How many events will be returned for today at maximum.
        :return: A list containing up to *limit* calendar events that are scheduled for today.
        """
        self.log.info("Fetching events for today...")
        next_events = self.get_next_events(events, limit)
        today_events = []
        for event in next_events:
            if event.start.date() == date.today():
                today_events.append(event)
            else:
                break
        return today_events

    def get_next_events(self, events: list[CalendarEventSchedule], limit=3,
                        order_by: CalendarEventOrdering = CalendarEventOrdering.EARLIEST_START):
        """
        Returns the next x calendar events.
        :param events: All unordered calendar event schedules.
        :param limit: How many events should be returned at maximum.
        :param order_by: defines in which order the next events will be returned.
        :return: A list containing up to *limit* calendar events that will take place next.
        """
        next_events = []
        for _ in range(limit):
            potential_events = []
            for ev in events:
                # non repeating
                if ev.repeat_policy is CalendarRepeatPolicy.NoRepeat:
                    if ev.start >= datetime.now(tzlocal.get_localzone()):
                        potential_events.append(SpecificCalendarEvent(ev.start, ev.end, ev.summary, ev.type))
                    elif ev.type == CalendarEventType.DaySlot and ev.start.date() == date.today():
                        potential_events.append(SpecificCalendarEvent(ev.start, ev.end, ev.summary, ev.type))
                # repeating
                else:
                    # repeating but first start in the future
                    specific_event = SpecificCalendarEvent(ev.start, ev.end, ev.summary, ev.type)
                    if specific_event.start >= datetime.now(
                            tzlocal.get_localzone()) and specific_event not in next_events:
                        if ev.repeat_until is not None:
                            if ev.repeat_until > specific_event.start:
                                potential_events.append(specific_event)
                        else:
                            potential_events.append(specific_event)
                    # repeating but start in the past (e.g. already repeated event)
                    else:
                        specific_event = SpecificCalendarEvent(ev.start, ev.end, ev.summary, ev.type)
                        if ev.repeat_policy == CalendarRepeatPolicy.Daily:
                            specific_event = self._get_next_valid_event(ev, specific_event, next_events,
                                                                        get_next_day_for_date)
                        elif ev.repeat_policy == CalendarRepeatPolicy.Weekly:
                            specific_event = self._get_next_valid_event(ev, specific_event, next_events,
                                                                        get_next_week_for_date)
                        elif ev.repeat_policy == CalendarRepeatPolicy.Monthly:
                            specific_event = self._get_next_valid_event(ev, specific_event, next_events,
                                                                        get_next_month_for_date)
                        elif ev.repeat_policy == CalendarRepeatPolicy.Yearly:
                            specific_event = self._get_next_valid_event(ev, specific_event, next_events,
                                                                        get_next_year_for_date)
                        if specific_event is not None:
                            potential_events.append(specific_event)
            if order_by is CalendarEventOrdering.EARLIEST_START:
                potential_events = sorted(potential_events, key=lambda potential_event: potential_event.start)
            elif order_by is CalendarEventOrdering.EARLIEST_END:
                potential_events = sorted(potential_events, key=lambda potential_event: potential_event.end)
            for p_ev in potential_events:
                if p_ev not in next_events:
                    next_events.append(p_ev)
                    break
        return next_events

    async def _fetch_calendar_events(self):
        """
        Method to extract calendar schedules from an online ics source.
        :return: The event schedules extracted.
        """
        events = []
        tmp_events = []
        async with await self.session.get(self.calendar_url) as response:
            if response.status == 200:
                cal = Calendar.from_ical(await response.text())
                for component in cal.walk():
                    # get event components from the ical
                    if component.name == CALENDAR_EVENT_MARKER:
                        ev = CalendarEventSchedule(component.get(CALENDAR_COMPONENT_DTSTART).dt,
                                                   component.get(CALENDAR_COMPONENT_DTEND).dt,
                                                   str(component.get(CALENDAR_COMPONENT_SUMMARY)),
                                                   CalendarRepeatPolicy.get_repeat_policy_from_name(
                                                       component.get(CALENDAR_COMPONENT_RRULE)[
                                                           CALENDAR_COMPONENT_RRULE_FREQ][0]) if
                                                   CALENDAR_COMPONENT_RRULE in component
                                                   else CalendarRepeatPolicy.NoRepeat,
                                                   component.get(CALENDAR_COMPONENT_RRULE)[
                                                       CALENDAR_COMPONENT_RRULE_UNTIL][0]
                                                   if (CALENDAR_COMPONENT_RRULE in component and
                                                       CALENDAR_COMPONENT_RRULE_UNTIL in component.get(
                                                               CALENDAR_COMPONENT_RRULE)) else None)
                        tmp_events.append(ev)
        now = datetime.now(tz=tzlocal.get_localzone())
        for ev in tmp_events:
            if type(ev.start) is date:
                # filter out all "whole day events" in the ical that are in the past and have no repeat policy
                if ev.start < now.date() and ev.repeat_policy is None:
                    continue
                else:
                    # update timezone which is not contained in ical for events that span the whole day
                    ev.start = datetime.combine(ev.start, time.min, tzinfo=tzlocal.get_localzone())
                    ev.end = datetime.combine(ev.end, time.min, tzinfo=tzlocal.get_localzone())
                    ev.type = CalendarEventType.DaySlot
            elif type(ev.start) is datetime:
                # filter out all events that are in the past and have no repeat policy
                if ev.start < now and ev.repeat_policy is None:
                    continue
            # filter out all events that have a repeat policy which has already expired
            if ev.repeat_policy is not None and ev.repeat_until is not None and ev.repeat_until < datetime.now(
                    tz=timezone.utc):
                continue
            events.append(ev)
        return events

    async def fetch_events_and_refresh(self):
        """
        Fetches calendar events and sends a CalenderRefresh event
        :return: The fetched calendar events.
        """
        events = await self._fetch_calendar_events()
        await self.put_event(CalendarRefreshEvent())
        return events
