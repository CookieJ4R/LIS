import json
from typing import Callable, Union

from core_modules.logging.lis_logging import get_logger
from core_modules.rest.AbstractBaseApi import AbstractBaseApi
from core_modules.rest.RestServer import REST_METHOD_POST
from core_modules.rest.request_util import get_bool_from_args_obj, get_string_from_args_obj, get_int_from_args_obj
from core_modules.scheduling.EventRepeatPolicy import EventRepeatPolicy
from core_modules.scheduling.ScheduledEvent import EXEC_DATETIME_FORMAT
from core_modules.scheduling.SchedulingEvents import ScheduleEventExecutionEvent, DEFAULT_GRACE_PERIOD_IN_MINUTES
from datetime import datetime


class SchedulingApi(AbstractBaseApi):
    """
    Api to schedule events for later execution via a request to the REST-Server.
    """

    log = get_logger(__name__)

    def __init__(self, put_event: Callable, event_mapping_func: Callable):
        self.put_event = put_event
        self._event_mapping_func = event_mapping_func

    def register_endpoints(self, register_handler: Callable):
        self.log.debug("Registering api endpoints...")
        register_handler("/schedule", REST_METHOD_POST, self.handle_schedule_request)

    def _parse_exec_time(self, exec_time: str) -> Union[datetime | None]:
        """
        Parses the exec_time param of the schedule request to a datetime object.
        :param exec_time: The exec_time str to parse.
        :return: The parsed datetime if the str is valid, None otherwise
        """
        if exec_time is not None:
            try:
                exec_time = datetime.strptime(exec_time, EXEC_DATETIME_FORMAT)
                return exec_time
            except ValueError:
                self.log.error(f"Supplied time {exec_time} did not conform to format {EXEC_DATETIME_FORMAT}")
                return None
        return None

    def _load_event_json(self, event_json: str) -> Union[dict | None]:
        """
        Loads the event_json str into a dict
        :param event_json: The json string to parse
        :return: The parsed dict if valid, None otherwise
        """
        try:
            return json.loads(event_json)
        except json.decoder.JSONDecodeError:
            self.log.error(f"Supplied event {event_json} is not valid JSON!")
            return None

    async def handle_schedule_request(self, args):
        """
        Endpoint handler for the /schedule endpoint.
        :param args: contains the arguments of the request
        :return: Tuple containing of (status_code, response)
        """
        self.log.info("Received request to schedule an event!")
        exec_time = get_string_from_args_obj("exec_time", args)
        persist = get_bool_from_args_obj("persist_after_reboot", args, False)
        repeat_policy = get_string_from_args_obj("repeat_policy", args)
        grace_period_minutes = get_int_from_args_obj("grace_period_in_minutes", args, DEFAULT_GRACE_PERIOD_IN_MINUTES)

        event_json = get_string_from_args_obj("event", args)

        exec_time = self._parse_exec_time(exec_time)
        if exec_time is None:
            return 400, f"Supplied exec_time is not parseable! {exec_time}"

        event_dict = self._load_event_json(event_json)
        if event_dict is None:
            return 400, "Supplied event is not valid JSON!"

        repeat_policy = EventRepeatPolicy.get_event_repeat_policy_from_name(repeat_policy)

        event_to_schedule = self._event_mapping_func(event_dict)
        if event_to_schedule is None:
            return 400, "Event could not be mapped to registered event!"

        self.log.info("Sending event to schedule " + str(event_to_schedule) + " for execution at " + str(exec_time))
        await self.put_event(ScheduleEventExecutionEvent(exec_time, event_to_schedule, persist,
                                                         repeat_policy, grace_period_minutes))
        return 200, ""
