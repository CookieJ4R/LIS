from datetime import datetime

from core_modules.eventing.BaseEvent import BaseEvent
from core_modules.scheduling.EventRepeatPolicy import EventRepeatPolicy
from core_modules.scheduling.SchedulableEvent import SchedulableEvent


class ScheduleEventExecutionEvent(BaseEvent):
    """
    Event for scheduling another event at a given time.
    """

    def __init__(self, exec_time: datetime, event: SchedulableEvent, persist_after_reboot: bool = False,
                 repeat_policy: EventRepeatPolicy = EventRepeatPolicy.NoRepeat, grace_period_in_minutes: int = 0):
        """
        Constructor of ScheduleEventExecutionEvent
        :param datetime exec_time: The time the passed event will be executed at.
        :param SchedulableEvent event: The event to execute at the given time.
        :param bool persist_after_reboot: Whether the event will persist after a system reboot.
        :param EvenRepeatPolicy repeat_policy: How often the event will be re-scheduled after execution.
        :param int grace_period_in_minutes: Grace period after which the event will no longer be executed.
        Useful for persistent events that have long passed after a reboot and should no longer be executed or for the
        exact opposite - for events that have long since passed but need to be executed anyway!
        """
        self.event = event
        self.exec_time = exec_time
        self.persist_after_reboot = persist_after_reboot
        self.repeat_policy = repeat_policy
        self.grace_period_in_minutes = grace_period_in_minutes
