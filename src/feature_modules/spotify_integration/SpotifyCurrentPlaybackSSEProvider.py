import asyncio
from typing import Callable

from core_modules.eventing.TemporaryEventReceiver import TemporaryEventReceiver
from core_modules.logging.lis_logging import get_logger
from core_modules.rest.RestServerEvents import SSEDataEvent
from feature_modules.spotify_integration.SpotifyEvents import SpotifyGetCurrentTrackResponseEvent, \
    SpotifyGetCurrentTrackEvent


class SpotifyCurrentPlaybackSSEProvider:

    log = get_logger(__name__)

    def __init__(self, put_event: Callable):
        self.put_event = put_event
        asyncio.create_task(self._spotify_playback_provider_task())

    async def _spotify_playback_provider_task(self):
        response_receiver = TemporaryEventReceiver(self.put_event, [SpotifyGetCurrentTrackResponseEvent])
        await response_receiver.start()
        while True:
            await self.put_event(SpotifyGetCurrentTrackEvent())
            event: SpotifyGetCurrentTrackResponseEvent = await response_receiver.wait_for_event(
                unregister_after_receive=False)
            await self.put_event(SSEDataEvent("spotify/current", event.playback_state.to_json()))
            await asyncio.sleep(2)
