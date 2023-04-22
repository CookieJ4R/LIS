from datetime import datetime

from core_modules.eventing.BaseEvent import BaseEvent


class ScheduleEventExecutionEvent(BaseEvent):

    def __init__(self, exec_time: datetime, event: BaseEvent, persist_after_reboot: bool = None,
                 grace_period_in_minutes: int = None):

        if persist_after_reboot is None:
            persist_after_reboot = False
        if grace_period_in_minutes is None:
            grace_period_in_minutes = 1

        self.event = event
        self.exec_time = exec_time
        self.persist_after_reboot = persist_after_reboot
        self.grace_period_in_minutes = grace_period_in_minutes
