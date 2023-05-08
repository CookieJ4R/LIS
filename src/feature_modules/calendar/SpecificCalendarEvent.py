import dataclasses
import json
from datetime import datetime
from enum import auto

from core_modules.util.DescriptiveEnum import DescriptiveEnum
from feature_modules.calendar.CalendarEventType import CalendarEventType

DATETIME_FORMAT = "%Y-%m-%dT%H:%M"


@dataclasses.dataclass
class SpecificCalendarEvent:
    start: datetime
    end: datetime
    summary: str
    type: CalendarEventType

    def __eq__(self, other):
        if isinstance(other, SpecificCalendarEvent):
            return self.start == other.start and self.end == other.end and self.summary == other.summary
        return False

    def __hash__(self):
        return hash(str(self.start) + str(self.end) + self.summary)

    def to_dict(self):
        return {"start": self.start.strftime(DATETIME_FORMAT),
                "end": self.end.strftime(DATETIME_FORMAT),
                "type": self.type.value,
                "summary": self.summary}
