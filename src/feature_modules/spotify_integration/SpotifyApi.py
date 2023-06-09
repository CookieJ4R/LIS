import json
from typing import Callable

from core_modules.eventing.TemporaryEventReceiver import TemporaryEventReceiver
from core_modules.logging.lis_logging import get_logger
from core_modules.rest.AbstractBaseApi import AbstractBaseApi
from core_modules.rest.RestServer import REST_METHOD_PUT, REST_METHOD_GET
from feature_modules.spotify_integration.SpotifyEvents import SpotifyStartResumePlaybackEvent, \
    SpotifyPausePlaybackEvent, SpotifyNextTrackEvent, SpotifyPreviousTrackEvent, SpotifyGetCurrentTrackEvent, \
    SpotifyGetCurrentTrackResponseEvent


class SpotifyApi(AbstractBaseApi):
    """
    API for all commands related to the spotify integration
    """

    log = get_logger(__name__)

    def __init__(self, put_event):
        self.put_event = put_event

    def register_endpoints(self, register_endpoint: Callable):
        self.log.debug("Registering api endpoints...")
        register_endpoint("/spotify/play", REST_METHOD_PUT, self._start_resume_playback)
        register_endpoint("/spotify/pause", REST_METHOD_PUT, self._pause_playback)
        register_endpoint("/spotify/next", REST_METHOD_PUT, self._next_track)
        register_endpoint("/spotify/previous", REST_METHOD_PUT, self._previous_track)
        register_endpoint("/spotify/current", REST_METHOD_GET, self._get_playback_state)

    async def _start_resume_playback(self, _args):
        """
        Endpoint handler for the /spotify/play endpoint.
        :param _args: contains the arguments of the request
        :return: Tuple containing the status_code and response
        """
        await self.put_event(SpotifyStartResumePlaybackEvent())
        return 200, ""

    async def _pause_playback(self, _args):
        """
        Endpoint handler for the /spotify/pause endpoint.
        :param _args: contains the arguments of the request
        :return: Tuple containing the status_code and response)
        """
        await self.put_event(SpotifyPausePlaybackEvent())
        return 200, ""

    async def _next_track(self, _args):
        """
        Endpoint handler for the /spotify/next endpoint.
        :param _args: contains the arguments of the request
        :return: Tuple containing the status_code and response
        """
        await self.put_event(SpotifyNextTrackEvent())
        return 200, ""

    async def _previous_track(self, _args):
        """
        Endpoint handler for the /spotify/previous endpoint.
        :param _args: contains the arguments of the request
        :return: Tuple containing the status_code and response
        """
        await self.put_event(SpotifyPreviousTrackEvent())
        return 200, ""

    async def _get_playback_state(self, _args):
        """
        Endpoint handler for the /spotify/current endpoint.
        :param _args: contains the arguments of the request
        :return: Tuple containing the status_code and the JSON string of the current playback
        """
        response_receiver = TemporaryEventReceiver(self.put_event, [SpotifyGetCurrentTrackResponseEvent])
        await response_receiver.start()
        await self.put_event(SpotifyGetCurrentTrackEvent())
        event: SpotifyGetCurrentTrackResponseEvent = await response_receiver.wait_for_event()
        return 200, event.playback_state.to_json()
