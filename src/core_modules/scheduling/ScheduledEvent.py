from core_modules.eventing.BaseEvent import BaseEvent


class ScheduledEvent:
    """
    Helper class to be stored as object in the EventScheduler internal map to provide access to fields beyond the event
    to execute at the given time.
    """

    def __init__(self, event_to_exec: BaseEvent, grace_period_in_minutes: int):
        self.event_to_exec = event_to_exec
        self.grace_period_in_minutes = grace_period_in_minutes
