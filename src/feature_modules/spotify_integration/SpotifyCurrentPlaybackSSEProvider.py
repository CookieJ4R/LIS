import asyncio
from typing import Callable

from core_modules.eventing.TemporaryEventReceiver import TemporaryEventReceiver
from core_modules.logging.lis_logging import get_logger
from core_modules.rest.RestServerEvents import SSEDataEvent
from feature_modules.spotify_integration.SpotifyEvents import SpotifyGetCurrentTrackResponseEvent, \
    SpotifyGetCurrentTrackEvent

SPOTIFY_CURRENT_SSE_ENDPOINT = "spotify/current"
SPOTIFY_SECONDS_BETWEEN_PLAYBACK_STATE_QUERIES = 2


class SpotifyCurrentPlaybackSSEProvider:
    """
    Class containing the spotify current playback to SSE bridge.
    """
    log = get_logger(__name__)

    def __init__(self, put_event: Callable):
        self.put_event = put_event
        asyncio.create_task(self._spotify_playback_provider_task())

    async def _spotify_playback_provider_task(self):
        """
        Infinite task that is responsible for periodically query the spotify api for the current playback state and
        forward it to the LIS eventbus
        """
        response_receiver = TemporaryEventReceiver(self.put_event, [SpotifyGetCurrentTrackResponseEvent])
        await response_receiver.start()
        self.log.debug("Started current playback provider task.")
        while True:
            await self.put_event(SpotifyGetCurrentTrackEvent())
            event: SpotifyGetCurrentTrackResponseEvent = await response_receiver.wait_for_event(
                unregister_after_receive=False)
            self.log.debug("Received response - forwarding to SSE")
            await self.put_event(SSEDataEvent(SPOTIFY_CURRENT_SSE_ENDPOINT, event.playback_state.to_json()))
            await asyncio.sleep(SPOTIFY_SECONDS_BETWEEN_PLAYBACK_STATE_QUERIES)
