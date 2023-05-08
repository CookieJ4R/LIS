import dataclasses
from datetime import datetime

from feature_modules.calendar.CalendarEventType import CalendarEventType
from feature_modules.calendar.CalendarRepeatPolicy import CalendarRepeatPolicy


@dataclasses.dataclass
class CalendarEventSchedule:
    start: datetime
    end: datetime
    summary: str
    repeat_policy: CalendarRepeatPolicy
    repeat_until: datetime
    type: CalendarEventType = CalendarEventType.TimeSlot

    def __eq__(self, other):
        if isinstance(other, CalendarEventSchedule):
            return self.start == other.start and self.end == other.end and self.summary == other.summary
        return False

    def __hash__(self):
        return hash(str(self.start) + str(self.end) + self.summary + self.repeat_policy + str(self.repeat_until))