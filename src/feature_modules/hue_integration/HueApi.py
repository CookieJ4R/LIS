from typing import Callable

from core_modules.eventing.ResponseEventReceiver import ResponseEventReceiver
from core_modules.rest.AbstractBaseApi import AbstractBaseApi
from core_modules.rest.RestServer import REST_METHOD_PUT, REST_METHOD_GET
from core_modules.rest.request_util import get_bool_from_args_obj, get_string_from_args_obj
from feature_modules.hue_integration.HueEvents import HueLampSetStateEvent, HueGetLampsEvent, HueGetLampsResponseEvent


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

    async def _get_connected_lamps(self, _args):
        """
        Endpoint handler to get all connected lamps. Returned info will contain the lamp name as well as the
        light service id.
        :param _args: The args passed to the request.
        :return: Status code 200, JSON containing all registered lamps
        """
        response_receiver = ResponseEventReceiver(self.put_event, [HueGetLampsResponseEvent])
        await response_receiver.start()
        await self.put_event(HueGetLampsEvent())
        event: HueGetLampsResponseEvent = await response_receiver.wait_for_response_event()
        return 200, event.get_lamp_json()
