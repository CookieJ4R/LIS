from core_modules.eventing.BaseEvent import BaseEvent
from core_modules.scheduling.SimpleSchedulableEvent import SimpleSchedulableEvent
from feature_modules.calendar.SpecificCalendarEvent import SpecificCalendarEvent


class CalendarRefreshEvent(BaseEvent, SimpleSchedulableEvent):
    """
    Event to trigger a refresh of the calendar events
    """


class CalendarFetchNextEvent(BaseEvent):
    """
    Event to fetch the next x events.
    """
    def __init__(self, limit: int):
        self.limit = limit


class CalendarFetchNextResponseEvent(BaseEvent):
    """
    Event containing the response of the FetchNext event
    """
    def __init__(self, next_events: list[SpecificCalendarEvent]):
        self.next_events = next_events


class CalendarFetchTodayEvent(BaseEvent):
    """
    Event to fetch the next x events of today.
    """
    def __init__(self, limit: int):
        self.limit = limit


class CalendarFetchTodayResponseEvent(BaseEvent):
    """
    Event containing the response of the FetchToday event
    """
    def __init__(self, today_events: list[SpecificCalendarEvent]):
        self.today_events = today_events
