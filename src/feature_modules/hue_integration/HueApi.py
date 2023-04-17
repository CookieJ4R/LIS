from typing import Callable

from core_modules.rest.AbstractBaseApi import AbstractBaseApi
from core_modules.rest.RestServer import REST_METHOD_PUT, REST_METHOD_GET
from core_modules.rest.request_util import get_bool_from_args_obj, get_string_from_args_obj
from feature_modules.hue_integration.HueEvents import HueLampSetStateEvent


class HueApi(AbstractBaseApi):
    """
    API for all commands related to the philipps hue integration
    """

    def __init__(self, put_event):
        self.put_event = put_event

    def register_endpoints(self, register_endpoint: Callable):
        register_endpoint("/hue/state", REST_METHOD_PUT, self._toggle_lamp_state)
        register_endpoint("/hue/lights", REST_METHOD_GET, self._get_connected_lamps)

    async def _toggle_lamp_state(self, args):
        """
        Endpoint handler to set the state of a specific lamp
        :param args: The args passed to the request.
        :return: 200 after the event was sent. Note that this also returns 200 when the changing of the state
        does not happen. The 200 only signifies, that the request has reached the REST server.
        """
        lamp_id = get_string_from_args_obj("id", args)
        on = get_bool_from_args_obj("on", args)
        await self.put_event(HueLampSetStateEvent(lamp_id, on))
        return 200, ""

    async def _get_connected_lamps(self, args):
        """
        Endpoint handler to get all connected lamps. Returned info will contain the lamp name as well as the
        light service id.
        :param args: The args passed to the request.
        :return:
        """
        # TODO: register temporary EventResponse receiver to listen to the response event containing
        #  the data after sending the initial get event
        #  should take the Events to listen in the constructor, overwrite handle event by forwarding it and unregister
        #  itself afterwards. Only problem is, that it needs access to the EventCenter, this could be solved by sending
        #  a "registertempreceiverevent" internally, that is handled by the EventCenter itself
        pass