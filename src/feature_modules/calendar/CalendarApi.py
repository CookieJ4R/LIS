import json
from typing import Callable

from core_modules.eventing.TemporaryEventReceiver import TemporaryEventReceiver
from core_modules.logging.lis_logging import get_logger
from core_modules.rest.AbstractBaseApi import AbstractBaseApi
from core_modules.rest.RestServer import REST_METHOD_GET
from core_modules.rest.request_util import get_int_from_args_obj
from feature_modules.calendar.CalendarEvents import CalendarFetchNextEvent, CalendarFetchNextResponseEvent, \
    CalendarFetchTodayResponseEvent, CalendarFetchTodayEvent


class CalendarApi(AbstractBaseApi):
    """
    API for all commands related to the calendar integration
    """

    log = get_logger(__name__)

    def __init__(self, put_event):
        self.put_event = put_event

    def register_endpoints(self, register_endpoint: Callable):
        self.log.debug("Registering api endpoints...")
        register_endpoint("/calendar/next", REST_METHOD_GET, self._get_next_events)
        register_endpoint("/calendar/today", REST_METHOD_GET, self._get_today_events)

    async def _get_next_events(self, args):
        """
        Endpoint handler to get the next x calendar events
        :param args: The args passed to the request.
        :return: The appropriate status code (400 on error, 200 success) as well as the next events as json.
        """
        limit = get_int_from_args_obj("limit", args)
        if limit is None:
            return 400, "Malformed or missing limit parameter!"
        self.log.info(f"Received request - getting {limit} next events")
        response_receiver = TemporaryEventReceiver(self.put_event, [CalendarFetchNextResponseEvent])
        await response_receiver.start()
        await self.put_event(CalendarFetchNextEvent(limit))
        response_event: CalendarFetchNextResponseEvent = await response_receiver.wait_for_event()
        return 200, json.dumps({"events": response_event.next_events})

    async def _get_today_events(self, args):
        """
        Endpoint handler to get today´s events
        :param args: The args passed to the request.
        :return: The appropriate status code (400 on error, 200 success) as well as today´s events as json.
        """
        limit = get_int_from_args_obj("limit", args)
        if limit is None:
            return 400, "Malformed or missing limit parameter!"
        self.log.info(f"Received request - getting {limit} events for today")
        response_receiver = TemporaryEventReceiver(self.put_event, [CalendarFetchTodayResponseEvent])
        await response_receiver.start()
        await self.put_event(CalendarFetchTodayEvent(limit))

        response_event: CalendarFetchTodayResponseEvent = await response_receiver.wait_for_event()
        return 200, json.dumps({"events": response_event.today_events})
