import dataclasses
from datetime import datetime

from feature_modules.calendar.CalendarEventType import CalendarEventType

DATETIME_FORMAT = "%Y-%m-%dT%H:%M"


@dataclasses.dataclass
class SpecificCalendarEvent:
    """
    Class representing a specific calendar event as determined by an event schedule.
    For a repeating calendar event, there exists a specific calendar event for each iteration whereas there will
    always only ever be one calendar event schedule.
    """
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
        """
        Helper method to parse this specific calendar event to a dict for better parsing and transfering.
        :return: This SpecificCalendarEvent as a dict.
        """
        return {"start": self.start.strftime(DATETIME_FORMAT),
                "end": self.end.strftime(DATETIME_FORMAT),
                "type": self.type.value,
                "summary": self.summary}
