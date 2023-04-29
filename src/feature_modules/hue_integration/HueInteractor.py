from typing import Callable

import aiohttp

from core_modules.eventing.BaseEvent import BaseEvent
from core_modules.eventing.EventReceiver import EventReceiver
from core_modules.logging.lis_logging import get_logger
from core_modules.rest.RestServer import REST_METHOD_PUT, REST_METHOD_GET
from core_modules.storage.StorageManager import StorageManager
from feature_modules.hue_integration.HueConfig import HueConfig
from feature_modules.hue_integration.HueEvents import HueGetLampsEvent, HueGetLampsResponseEvent, HueLampSetStateEvent
from feature_modules.hue_integration.HueLamp import HueLamp
from feature_modules.hue_integration.HueSSEReceiver import HueSSEReceiver

SECTION_HEADER_HUE = "PHILIPPS_HUE"

FIELD_HUE_BRIDGE_IP = "HUE_BRIDGE_IP"
FIELD_HUE_CLIENT_KEY = "HUE_CLIENT_KEY"


class HueInteractor(EventReceiver):
    """
    Class responsible for interfacing with the Hue-Bridge REST Api.
    """

    log = get_logger(__name__)

    def __init__(self, storage: StorageManager, put_event: Callable):
        super().__init__()
        self.put_event = put_event
        self.hue_config = HueConfig(storage.get(FIELD_HUE_BRIDGE_IP, SECTION_HEADER_HUE),
                                    storage.get(FIELD_HUE_CLIENT_KEY, SECTION_HEADER_HUE))
        self.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False),
                                             headers={"hue-application-key": self.hue_config.client_key,
                                                      "Content-Type": "application/json"})
        self.hue_sse_receiver = HueSSEReceiver(put_event, self.hue_config)

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
        :return: status, response json
        """
        self.log.debug("Sending " + method + " request to Hue-Bridge endpoint " + str(endpoint) + " with " + str(data))
        if method == REST_METHOD_PUT:
            async with await self.session.put('https://' + self.hue_config.bridge_ip + "/clip/v2/" +
                                              endpoint, data=data) as response:
                return response.status, await response.json()
        elif method == REST_METHOD_GET:
            async with await self.session.get('https://' + self.hue_config.bridge_ip + "/clip/v2/" +
                                              endpoint) as response:
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
        status, resp = await self._send_request(REST_METHOD_GET, "resource/light")
        lamps = []
        if status == 200:
            lights = resp["data"]
            for light in lights:
                lamps.append(HueLamp(light["metadata"]["name"], light["id"], light["on"]))
        return lamps
