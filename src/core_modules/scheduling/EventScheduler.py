import asyncio
import json
from datetime import datetime, timedelta
from typing import Callable

from core_modules.eventing.BaseEvent import BaseEvent
from core_modules.eventing.EventReceiver import EventReceiver
from core_modules.logging.lis_logging import get_logger
from core_modules.scheduling.ScheduledEvent import ScheduledEvent, EXEC_DATETIME_FORMAT
from core_modules.scheduling.SchedulingEvents import ScheduleEventExecutionEvent
from core_modules.storage.StorageManager import StorageManager

STORAGE_PERSISTENT_EVENTS_FIELD = "SCHEDULED_EVENTS"
STORAGE_PERSISTENT_EVENTS_SECTION = "SCHEDULING"

PERSISTENT_EVENT_FIELD_EXEC_TIME = "exec_time"
PERSISTENT_EVENT_FIELD_EVENT = "event"
PERSISTENT_EVENT_FIELD_GRACE_PERIOD = "grace_period_in_minutes"


class EventScheduler(EventReceiver):
    """
    Class containing the scheduling engine for planing Events to be executed at a later date.
    """

    _event_execution_map = {}
    log = get_logger(__name__)

    def __init__(self, storage: StorageManager, put_event: Callable):
        super().__init__()
        self.storage = storage
        self.put_event = put_event
        asyncio.create_task(self._scheduling_engine_task())

    def fetch_events_to_register(self) -> list[type[BaseEvent]]:
        return [ScheduleEventExecutionEvent]

    def load_persistent_events(self, event_mapping_func: Callable):
        """
        Load all persistent events that were written to disk prior.
        :param event_mapping_func: The function to use to map an events json representation back to an Event instance.
        """
        self.log.info("Loading scheduled events from storage.")
        events_to_load = self.storage.get(STORAGE_PERSISTENT_EVENTS_FIELD, STORAGE_PERSISTENT_EVENTS_SECTION, [])
        for stored_event in events_to_load:
            ev = event_mapping_func(json.loads(stored_event[PERSISTENT_EVENT_FIELD_EVENT]))
            exec_time = datetime.strptime(stored_event[PERSISTENT_EVENT_FIELD_EXEC_TIME], EXEC_DATETIME_FORMAT)
            grace_time_in_minutes = stored_event[PERSISTENT_EVENT_FIELD_GRACE_PERIOD]
            self._add_event_to_execution_map(exec_time, ScheduledEvent(exec_time, ev, grace_time_in_minutes))

    def _add_event_to_execution_map(self, exec_time: datetime, scheduled_event: ScheduledEvent):
        """
        Add an event to the execution map to schedule it for execution.
        :param exec_time: The time the event will be executed at.
        :param scheduled_event: The event to schedule.
        """
        self.log.info("Scheduling " + str(scheduled_event) + " for execution at " + str(exec_time))
        if exec_time in self._event_execution_map:
            self._event_execution_map[exec_time].append(scheduled_event)
        else:
            self._event_execution_map[exec_time] = [scheduled_event]

    def _handle_scheduling_event(self, scheduling_event):
        """
        Handles a scheduling event and stores the event in the scheduling map. Also writes persistent events to disk.
        :param scheduling_event: The scheduling event that is being handled.
        """
        exec_time = scheduling_event.exec_time.replace(second=0, microsecond=0)
        scheduled_event = ScheduledEvent(exec_time, scheduling_event.event, scheduling_event.grace_period_in_minutes)
        if scheduling_event.persist_after_reboot:
            self.log.debug(f"Writing persistent event {str(scheduled_event)} to storage.")
            self.storage.append_or_add(scheduled_event.to_obj_rep(),
                                       STORAGE_PERSISTENT_EVENTS_FIELD,
                                       STORAGE_PERSISTENT_EVENTS_SECTION)
        self._add_event_to_execution_map(exec_time, scheduled_event)

    async def handle_specific_event(self, event: BaseEvent):
        if isinstance(event, ScheduleEventExecutionEvent):
            self._handle_scheduling_event(event)

    def _get_events_to_execute_now(self, now: datetime):
        """
        Method for fetching all events that should be executed at this point in time and removed from the internal map.
        :param now: The time the event checking was performed (=> when the async sleep ended).
        :return: all previously scheduled events that should be forwarded to the event bus now.
        """
        events_to_schedule = []
        exec_times_to_remove = []
        for exec_date in self._event_execution_map:
            if now >= exec_date:
                events_in_datetime = self._event_execution_map[exec_date]
                exec_times_to_remove.append(exec_date)
                for event in events_in_datetime:
                    if now >= exec_date + timedelta(minutes=event.grace_period_in_minutes):
                        self.log.info(f"Event {str(event)} has passed an is past its grace period - skipping!")
                        continue
                    else:
                        events_to_schedule.append(event.event_to_exec)
        for exec_time in exec_times_to_remove:
            executed_events = self._event_execution_map.pop(exec_time)
            for event in executed_events:
                # not called on events_to_schedule to also removed events past their grace period from persistence
                self.storage.remove_obj_from_list(event.to_obj_rep(),
                                                  STORAGE_PERSISTENT_EVENTS_FIELD,
                                                  STORAGE_PERSISTENT_EVENTS_SECTION)
        return events_to_schedule

    async def _scheduling_engine_task(self):
        """
        Task for checking which events to execute at the given time. Will always fire around XX:XX:00.
        """
        while True:
            now = datetime.now()
            events = self._get_events_to_execute_now(now)
            for event in events:
                self.log.info(f"Executing prior scheduled event {event}")
                await self.put_event(event)
            now = datetime.now()
            await asyncio.sleep(60 - now.second)
