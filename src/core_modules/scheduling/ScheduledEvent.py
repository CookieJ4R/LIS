from core_modules.eventing.BaseEvent import BaseEvent


class ScheduledEvent:

    def __init__(self, event_to_exec: BaseEvent, grace_period_in_minutes: int):
        self.event_to_exec = event_to_exec
        self.grace_period_in_minutes = grace_period_in_minutes
