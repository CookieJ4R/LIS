from datetime import datetime

from core_modules.scheduling.SchedulableEvent import SchedulableEvent

EXEC_DATETIME_FORMAT = "%Y-%m-%dT%H:%M"


class ScheduledEvent:
    """
    Helper class to be stored as object in the EventScheduler internal map to provide access to fields beyond the event
    to execute at the given time.
    """

    def __init__(self, exec_time: datetime, event_to_exec: SchedulableEvent, grace_period_in_minutes: int):
        self.exec_time = exec_time
        self.event_to_exec = event_to_exec
        self.grace_period_in_minutes = grace_period_in_minutes

    def to_obj_rep(self):
        return {"exec_time": self.exec_time.strftime(EXEC_DATETIME_FORMAT),
                "grace_period_in_minutes": self.grace_period_in_minutes,
                "event": self.event_to_exec.to_json()}
