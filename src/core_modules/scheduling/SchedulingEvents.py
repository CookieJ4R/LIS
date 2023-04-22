from datetime import datetime

from core_modules.eventing.BaseEvent import BaseEvent
from core_modules.scheduling.SchedulableEvent import SchedulableEvent


class ScheduleEventExecutionEvent(BaseEvent):
    """
    Event for scheduling another event at a given time.
    """

    def __init__(self, exec_time: datetime, event: SchedulableEvent, persist_after_reboot: bool = None,
                 grace_period_in_minutes: int = None):
        """
        Constructor of ScheduleEventExecutionEvent
        :param datetime exec_time: The time the passed event will be executed at.
        :param SchedulableEvent event: The event to execute at the given time.
        :param bool persist_after_reboot: Whether the event will persist after a system reboot.
        :param int grace_period_in_minutes: Grace period after which the event will no longer be executed.
        Useful for persistent events that have long passed after a reboot and should no longer be executed or for the
        exact opposite - for events that have long since passed but need to be executed anyway!
        """

        if persist_after_reboot is None:
            persist_after_reboot = False
        if grace_period_in_minutes is None:
            grace_period_in_minutes = 1

        self.event = event
        self.exec_time = exec_time
        self.persist_after_reboot = persist_after_reboot
        self.grace_period_in_minutes = grace_period_in_minutes
