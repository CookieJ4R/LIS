from enum import auto

from core_modules.util.DescriptiveEnum import DescriptiveEnum


class CalendarEventType(DescriptiveEnum):
    """
    Enum representing all possible types of calendar events.
    """
    TimeSlot = auto()
    DaySlot = auto()
