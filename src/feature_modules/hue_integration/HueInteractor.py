from typing import Callable

import aiohttp

from core_modules.eventing.BaseEvent import BaseEvent
from core_modules.eventing.EventReceiver import EventReceiver
from core_modules.logging.lis_logging import get_logger
from core_modules.rest.RestServer import REST_METHOD_PUT, REST_METHOD_GET
from core_modules.storage.StorageManager import StorageManager, FIELD_HUE_BRIDGE_IP, SECTION_HEADER_HUE, \
    FIELD_HUE_CLIENT_KEY
from feature_modules.hue_integration.HueApi import HueLampSetStateEvent
from feature_modules.hue_integration.HueEvents import HueGetLampsEvent, HueGetLampsResponseEvent
from feature_modules.hue_integration.HueLamp import HueLamp


class HueInteractor(EventReceiver):
    """
    Class responsible for interfacing with the Hue-Bridge REST Api.
    """

    log = get_logger(__name__)

    def __init__(self, storage: StorageManager, put_event: Callable):
        super().__init__()
        self.put_event = put_event
        self.hue_bridge_api = storage.get(FIELD_HUE_BRIDGE_IP, SECTION_HEADER_HUE)
        self.hue_client_key = storage.get(FIELD_HUE_CLIENT_KEY, SECTION_HEADER_HUE)

    def fetch_events_to_register(self) -> list[type[BaseEvent]]:
        return [HueLampSetStateEvent, HueGetLampsEvent]

    async def handle_specific_event(self, event: BaseEvent):
        self.log.info("Handling " + str(event))
        if isinstance(event, HueLampSetStateEvent):
            await self.set_state_of_lamp(event.lamp_id, event.on)
        elif isinstance(event, HueGetLampsEvent):
            lamps = await self.get_lamps()
            await self.put_event(HueGetLampsResponseEvent(lamps))

    async def _send_request(self, method, endpoint, data=None):
        """
        Internal method to send an asynchronous request to the Hue-Bridge.
        :param method: The method to use (GET, PUT)
        :param endpoint: The endpoint that will be appended to the main url (e.g. resource/light/<ID>)
        :param data: The data to send (used for PUT requests)
        """
        self.log.debug("Sending " + method + " request to Hue-Bridge endpoint " + str(endpoint) + " with " + str(data))
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False),
                                         headers={"hue-application-key": self.hue_client_key,
                                                  "Content-Type": "application/json"}) as session:
            if method == REST_METHOD_PUT:
                async with await session.put('https://' + self.hue_bridge_api + "/clip/v2/" + endpoint,
                                             data=data) as response:
                    return response.status, await response.json()
            elif method == REST_METHOD_GET:
                async with await session.get('https://' + self.hue_bridge_api + "/clip/v2/" + endpoint) as response:
                    return response.status, await response.json()

    async def set_state_of_lamp(self, lamp_id: str, on: bool):
        """
        Method for switching the state of a specific lamp
        :param lamp_id: The id of the lamp to change the state off.
        :param on: The value to set the state to (true = on, false = off)
        """
        self.log.info("Setting state of lamp " + lamp_id + " to " + str(on) + " via Hue-Bridge REST-Api")
        await self._send_request(REST_METHOD_PUT, "resource/light/" + lamp_id,
                                 b'{"on": {"on": true}}' if on else b'{"on": {"on": false}}')

    async def get_lamps(self) -> list[HueLamp]:
        """
        Method for getting all lights registered with the hue bridge. Will ignore other devices like switches
        or the bridge itself.
        :return: List containing a HueLamp object for each connected lamp.
        Empty list if no lamp is connected or an error occurred.
        """
        self.log.info("Getting connected lights via Hue-Bridge REST-Api")
        status, resp = await self._send_request(REST_METHOD_GET, "resource/device")
        lamps = []
        if status == 200:
            devices = resp["data"]
            for device in devices:
                light_service = self._get_light_service_of_device(device["services"])
                if light_service is not None:
                    lamps.append(HueLamp(device["metadata"]["name"], light_service["rid"]))
        return lamps

    @staticmethod
    def _get_light_service_of_device(services_list: list):
        """
        Helper method to discern which devices are lamps.
        :param services_list: service list of a hue device.
        :return: The light service if present {"rid": xxx, "rtype": light}, None otherwise
        """
        for service in services_list:
            if service["rtype"] == "light":
                return service
        return None
