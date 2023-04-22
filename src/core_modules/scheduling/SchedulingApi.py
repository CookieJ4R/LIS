import json
from typing import Callable

from core_modules.logging.lis_logging import get_logger
from core_modules.rest.AbstractBaseApi import AbstractBaseApi
from core_modules.rest.RestServer import REST_METHOD_POST
from core_modules.rest.request_util import get_bool_from_args_obj, get_string_from_args_obj, get_int_from_args_obj
from core_modules.scheduling.SchedulableEvent import SchedulableEvent
from core_modules.scheduling.SchedulingEvents import ScheduleEventExecutionEvent
from datetime import datetime


# TODO add logging statements and simplify api call complexity
class SchedulingApi(AbstractBaseApi):
    """
    Api to schedule events for later execution via a request to the REST-Server.
    """

    log = get_logger(__name__)

    def __init__(self, put_event: Callable, get_registered_events: Callable):
        self.put_event = put_event
        self.get_registered_events = get_registered_events

    def register_endpoints(self, register_handler: Callable):
        self.log.debug("Registering api endpoints...")
        register_handler("/schedule", REST_METHOD_POST, self.handle_schedule_request)

    async def handle_schedule_request(self, args):
        """
        Endpoint handler for the /schedule endpoint.
        :param args: contains the arguments of the request
        :return: Tuple containing of (status_code, response)
        """
        self.log.info("Received request to schedule an event!")
        exec_time = get_string_from_args_obj("exec_time", args)
        if exec_time is not None:
            try:
                exec_time = datetime.strptime(exec_time, "%Y-%m-%dT%H:%M")
            except ValueError:
                return 400, f"Supplied exec_time is not parseable! {exec_time}"
        persist = get_bool_from_args_obj("persist_after_reboot", args)
        grace_period_minutes = get_int_from_args_obj("grace_period_in_minutes", args)
        event_json = get_string_from_args_obj("event", args)
        try:
            event_dict = json.loads(event_json)
        except json.decoder.JSONDecodeError:
            return 400, "Supplied event is not valid JSON!"
        event_to_schedule = None
        for event in self.get_registered_events():
            if issubclass(event, SchedulableEvent):
                try:
                    event_to_schedule = event.from_api_json(event_dict)
                    break
                except KeyError:
                    continue
        if event_to_schedule is None:
            return 400, "Event could not be mapped to registered event!"
        self.log.info("Sending event scheduling " + str(event_to_schedule) + " for " + str(exec_time))
        await self.put_event(ScheduleEventExecutionEvent(exec_time, event_to_schedule, persist, grace_period_minutes))
        return 200, ""
