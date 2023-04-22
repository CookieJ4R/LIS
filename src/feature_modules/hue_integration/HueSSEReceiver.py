import asyncio
import json
from typing import Callable

import aiohttp

from core_modules.logging.lis_logging import get_logger
from core_modules.rest.RestServerEvents import SSEDataEvent
from feature_modules.hue_integration.BridgeEvents.HueBridgeBrightnessChangeEvent import HueBridgeBrightnessChangeEvent
from feature_modules.hue_integration.BridgeEvents.HueBridgeColorChangeEvent import HueBridgeColorChangeEvent
from feature_modules.hue_integration.BridgeEvents.HueBridgeStateChangeEvent import HueBridgeStateChangeEvent
from feature_modules.hue_integration.HueConfig import HueConfig

EVENT_STATE_CHANGE_MARKER = "on"
EVENT_COLOR_CHANGE_MARKER = "color"
EVENT_BRIGHTNESS_CHANGE_MARKER = "dimming"

HUE_SSE_EVENT_PREFIX = "hue"

SSE_EVENT_ID_STATE_CHANGE = HUE_SSE_EVENT_PREFIX + "/state_changed"
SSE_EVENT_ID_COLOR_CHANGE = HUE_SSE_EVENT_PREFIX + "/color_changed"
SSE_EVENT_ID_BRIGHTNESS_CHANGE = HUE_SSE_EVENT_PREFIX + "/brightness_changed"


class HueSSEReceiver:
    """
    Class responsible for receiving and filtering SSEs from the Hue-Bridge as well as forwarding them to the outward
    facing SSE-Stream (-> Frontend)
    """

    log = get_logger(__name__)

    def __init__(self, put_event: Callable, hue_config: HueConfig):
        self.put_event = put_event
        self.hue_config = hue_config
        asyncio.create_task(self.receive_hue_events())

    async def _parse_and_forward_hue_event(self, event: dict):
        """
        Parses the arriving event to one of the known internal HueBridge Event Types and forwards it to the
        outward facing SSE-Stream (-> Frontend) if the parsing succeeded.
        :param event: The event to parse and potentially forward
        """
        self.log.info(f"Received {str(event)} from Hue Bridge. Forwarding to connected clients.")
        ev = None
        event_id = ""
        if EVENT_STATE_CHANGE_MARKER in event:
            ev = HueBridgeStateChangeEvent.from_dict(event)
            event_id = SSE_EVENT_ID_STATE_CHANGE
        elif EVENT_COLOR_CHANGE_MARKER in event:
            ev = HueBridgeColorChangeEvent.from_dict(event)
            event_id = SSE_EVENT_ID_COLOR_CHANGE
        elif EVENT_BRIGHTNESS_CHANGE_MARKER in event:
            ev = HueBridgeBrightnessChangeEvent.from_dict(event)
            event_id = SSE_EVENT_ID_BRIGHTNESS_CHANGE
        if ev is not None:
            await self.put_event(SSEDataEvent(event_id, ev.to_json()))
        else:
            self.log.warning(f"Received event {str(event)} could not be mapped to known event type")

    async def handle_event_stream_packet(self, data_packet):
        """
        Handles an arriving SSE on the HueBridge Eventstream. May contain more than one individual event.
        Will extract the wanted events ("light"), parse and forward them.
        :param data_packet: The event packet to handle
        """
        data_packet = data_packet.decode("utf-8").split("\n")
        for line in data_packet:
            line = line.strip()
            if line:
                if line.startswith("data:"):
                    data_split = line.split("data: ")
                    json_line = "{\"events\": " + data_split[1] + "}"
                    self.log.debug("Decoding SSE: " + json_line)
                    obj = json.loads(json_line)
                    for ev in obj["events"]:
                        for e in ev["data"]:
                            if e["type"] == "light":
                                await self._parse_and_forward_hue_event(e)
                            else:
                                self.log.debug("Ignoring Hue Bridge event " + str(e) +
                                               "as it is not a light event")

    async def receive_hue_events(self):
        """
        Client Session connecting to the SSE-Stream of the HueBridge to receive update events without recurring
        GET-Request.
        Timeout is set to None to prevent a timeout if no event arrives in a given time.
        """
        timeout = aiohttp.ClientTimeout(total=None, connect=None, sock_connect=None, sock_read=None)
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False),
                                         headers={"hue-application-key": self.hue_config.client_key,
                                                  "Accept": "text/event-stream"}, timeout=timeout) as session:
            async with await session.get('https://' + self.hue_config.bridge_ip + "/eventstream/clip/v2/") as response:
                async for data, _ in response.content.iter_chunks():
                    await self.handle_event_stream_packet(data)
