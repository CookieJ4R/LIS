import os

import aiohttp

from core_modules.eventing.BaseEvent import BaseEvent
from core_modules.eventing.EventReceiver import EventReceiver
from core_modules.rest.RestServer import REST_METHOD_PUT, REST_METHOD_GET
from feature_modules.hue_integration.HueApi import HueLampSetStateEvent


class HueInteractor(EventReceiver):
    """
    Class responsible for interfacing with the Hue-Bridge REST Api.
    """

    def __init__(self):
        super().__init__()
        self.hue_bridge_api = os.getenv("HUE_BRIDGE_IP")
        self.hue_client_key = os.getenv("HUE_CLIENT_KEY")

    def fetch_events_to_register(self) -> list[type[BaseEvent]]:
        return [HueLampSetStateEvent]

    async def handle_specific_event(self, event: BaseEvent):
        if isinstance(event, HueLampSetStateEvent):
            await self.set_state_of_lamp(event.lamp_id, event.on)

    async def _send_request(self, method, endpoint, data=None):
        """
        Internal method to send an asynchronous request to the Hue-Bridge.
        :param method: The method to use (GET, PUT)
        :param endpoint: The endpoint that will be appended to the main url (e.g. resource/light/<ID>)
        :param data: The data to send (used for PUT requests)
        """
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False),
                                         headers={"hue-application-key": self.hue_client_key,
                                                  "Content-Type": "application/json"}) as session:
            if method == REST_METHOD_PUT:
                await session.put('https://' + self.hue_bridge_api + "/clip/v2/" + endpoint,
                                  data=data)
            elif method == REST_METHOD_GET:
                await session.get('https://' + self.hue_bridge_api + "/clip/v2/" + endpoint)

    async def set_state_of_lamp(self, lamp_id: str, on: bool):
        """
        Method for switching the state of a specific lamp
        :param lamp_id: The id of the lamp to change the state off.
        :param on: The value to set the state to (true = on, false = off)
        """
        await self._send_request(REST_METHOD_PUT, "resource/light/" + lamp_id,
                                 b'{"on": {"on": true}}' if on else b'{"on": {"on": false}}')
