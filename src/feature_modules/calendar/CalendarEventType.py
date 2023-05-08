from enum import auto

from core_modules.util.DescriptiveEnum import DescriptiveEnum


class CalendarEventType(DescriptiveEnum):
    TimeSlot = auto()
    DaySlot = auto()
