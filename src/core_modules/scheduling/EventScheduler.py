import asyncio
from datetime import datetime, timedelta
from typing import Callable

from core_modules.eventing.BaseEvent import BaseEvent
from core_modules.eventing.EventReceiver import EventReceiver
from core_modules.logging.lis_logging import get_logger
from core_modules.scheduling.ScheduledEvent import ScheduledEvent
from core_modules.scheduling.SchedulingEvents import ScheduleEventExecutionEvent


class EventScheduler(EventReceiver):

    _event_execution_map = {}
    log = get_logger(__name__)

    def __init__(self, put_event: Callable):
        super().__init__()
        self.put_event = put_event
        # TODO: load persist events from disk

    def fetch_events_to_register(self) -> list[type[BaseEvent]]:
        return [ScheduleEventExecutionEvent]

    async def handle_specific_event(self, scheduling_event: BaseEvent):
        if isinstance(scheduling_event, ScheduleEventExecutionEvent):
            exec_time = scheduling_event.exec_time
            exec_time = exec_time.replace(second=0, microsecond=0)
            scheduled_event = ScheduledEvent(scheduling_event.event, scheduling_event.grace_period_in_minutes)
            # TODO: if should persist, write to disk here
            if exec_time in self._event_execution_map:
                self._event_execution_map[exec_time].append(scheduled_event)
            else:
                self._event_execution_map[exec_time] = [scheduled_event]

    def start_scheduling_engine(self):
        asyncio.create_task(self._scheduling_engine_task())

    def _get_event_to_execute_now(self, now: datetime):
        # TODO add rescheduling for repeating events
        events_to_schedule = []
        exec_times_to_remove = []
        for exec_date in self._event_execution_map:
            if now >= exec_date:
                events_in_datetime = self._event_execution_map[exec_date]
                exec_times_to_remove.append(exec_date)
                for event in events_in_datetime:
                    if now >= exec_date + timedelta(minutes=event.grace_period_in_minutes):
                        continue
                    else:
                        events_to_schedule.append(event.event_to_exec)
        for exec_time in exec_times_to_remove:
            self._event_execution_map.pop(exec_time)
        return events_to_schedule

    async def _scheduling_engine_task(self):
        while True:
            now = datetime.now()
            events = self._get_event_to_execute_now(now)
            for event in events:
                await self.put_event(event)
            now = datetime.now()
            await asyncio.sleep(60 - now.second)
