import asyncio
from typing import Callable

import aiohttp

from core_modules.eventing.BaseEvent import BaseEvent
from core_modules.eventing.EventReceiver import EventReceiver
from core_modules.logging.lis_logging import get_logger
from core_modules.rest.RestServer import REST_METHOD_PUT, REST_METHOD_GET, REST_METHOD_POST
from core_modules.storage.StorageManager import StorageManager
from feature_modules.spotify_integration.SpotifyCurrentPlaybackSSEProvider import SpotifyCurrentPlaybackSSEProvider
from feature_modules.spotify_integration.SpotifyEvents import SpotifyPausePlaybackEvent, \
    SpotifyStartResumePlaybackEvent, SpotifyPreviousTrackEvent, SpotifyNextTrackEvent, SpotifyGetCurrentTrackEvent, \
    SpotifyGetCurrentTrackResponseEvent
from feature_modules.spotify_integration.SpotifyPlaybackState import SpotifyPlaybackState, SpotifyPlayback
from feature_modules.spotify_integration.SpotifyTrack import SpotifyTrack

WEB_API_BASE_URL = "https://api.spotify.com/v1"
TOKEN_URL = "https://accounts.spotify.com/api/token"
PLAYER_BASE_ENDPOINT = "/me/player"

ACCESS_TOKEN_FIELD = "ACCESS_TOKEN"
SPOTIFY_STORAGE_SECTION = "SPOTIFY"


class SpotifyInteractor(EventReceiver):
    # TODO: add method for fetching current track (including api endpoint) as well as a fetch loop every x seconds
    #  (since spotify api does not provide an event stream for "normal" api users...) and forward the result to the
    #  LIS sse output
    """
    Class responsible for interacting with the spotify REST api.
    """
    log = get_logger(__name__)

    def __init__(self, put_event: Callable, storage: StorageManager):
        super().__init__()
        self.put_event = put_event
        self.storage = storage
        self.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False))
        self.current_playback_sse_provider = SpotifyCurrentPlaybackSSEProvider(put_event)

    def fetch_events_to_register(self) -> list[type[BaseEvent]]:
        return [SpotifyPausePlaybackEvent,
                SpotifyStartResumePlaybackEvent,
                SpotifyNextTrackEvent,
                SpotifyPreviousTrackEvent,
                SpotifyGetCurrentTrackEvent]

    async def handle_specific_event(self, event: BaseEvent):
        self.log.info("Received event: " + str(event))
        if isinstance(event, SpotifyPausePlaybackEvent):
            await self._pause_playback()
        elif isinstance(event, SpotifyStartResumePlaybackEvent):
            await self._start_resume_playback()
        elif isinstance(event, SpotifyNextTrackEvent):
            await self._next_track()
        elif isinstance(event, SpotifyPreviousTrackEvent):
            await self._prev_track()
        elif isinstance(event, SpotifyGetCurrentTrackEvent):
            playback_state = await self._get_current_track()
            await self.put_event(SpotifyGetCurrentTrackResponseEvent(playback_state))

    def _get_bearer_auth_header(self):
        """
        Construct a dictionary containing the auth header for the spotify web api
        :return: The constructed header dictionary
        """
        return {"Authorization": "Bearer " + self.storage.get(ACCESS_TOKEN_FIELD, SPOTIFY_STORAGE_SECTION, "")}

    async def _start_resume_playback(self):
        """
        Method to start or resume the current playback by sending a request to the spotify web api.
        """
        await self._send_request_with_token_retry(REST_METHOD_PUT,
                                                  WEB_API_BASE_URL + PLAYER_BASE_ENDPOINT + "/play",
                                                  headers=self._get_bearer_auth_header()
                                                  )

    async def _pause_playback(self):
        """
        Method to pause the current playback by sending a request to the spotify web api.
        """
        await self._send_request_with_token_retry(REST_METHOD_PUT,
                                                  WEB_API_BASE_URL + PLAYER_BASE_ENDPOINT + "/pause",
                                                  headers=self._get_bearer_auth_header())

    async def _next_track(self):
        """
        Method to skip to the next track by sending a request to the spotify web api.
        """
        await self._send_request_with_token_retry(REST_METHOD_POST,
                                                  WEB_API_BASE_URL + PLAYER_BASE_ENDPOINT + "/next",
                                                  headers=self._get_bearer_auth_header())

    async def _prev_track(self):
        """
        Method to return to the previous track by sending a request to the spotify web api
        """
        await self._send_request_with_token_retry(REST_METHOD_POST,
                                                  WEB_API_BASE_URL + PLAYER_BASE_ENDPOINT + "/previous",
                                                  headers=self._get_bearer_auth_header())

    async def _get_current_track(self):
        """
        Method to get the currently playing track as well as the playback state
        """
        status, response = await self._send_request_with_token_retry(REST_METHOD_GET,
                                                                     WEB_API_BASE_URL + PLAYER_BASE_ENDPOINT +
                                                                     "/currently-playing",
                                                                     headers=self._get_bearer_auth_header())
        if status == 200:
            try:
                track = SpotifyTrack(response["item"]["name"],
                                     response["item"]["artists"][0]["name"],
                                     response["item"]["album"]["images"][1]["url"])
            except KeyError:
                track = None
            try:
                playback = SpotifyPlayback.PLAYING if response["is_playing"] else SpotifyPlayback.STOPPED
            except KeyError:
                playback = SpotifyPlayback.NONE
            return SpotifyPlaybackState(playback, track)
        return SpotifyPlaybackState(None, None)

    async def _refresh_access_token(self):
        """
        Method to refresh and update the access_token by sending a request with the refresh_token.
        """
        status, response = await self._send_request(REST_METHOD_POST, TOKEN_URL,
                                                    data={"grant_type": "refresh_token",
                                                          "refresh_token": self.storage.get(
                                                              "REFRESH_TOKEN", SPOTIFY_STORAGE_SECTION, "")
                                                          },
                                                    headers={
                                                        "Authorization": "Basic " + self.storage.get(
                                                            "AUTH_CODE",
                                                            SPOTIFY_STORAGE_SECTION,
                                                            ""),
                                                        "Content-Type": "application/x-www-form-urlencoded"})
        if status == 200:
            self.storage.update(response["access_token"], ACCESS_TOKEN_FIELD, SPOTIFY_STORAGE_SECTION)

    async def _send_request(self, method, url, headers=None, data=None):
        """
        Internal method to send an asynchronous request to the Spotify-Api.
        :param method: The method to use (GET, PUT, POST)
        :param url: The url the request will be sent to
        :param headers: The headers to add to the request.
        :param data: The data to send.
        :return: status, response json or None
        """
        self.log.debug("Sending " + method + " request to " + str(url) + " with " + str(data))
        if method == REST_METHOD_PUT:
            async with await self.session.put(url, headers=headers, data=data) as response:
                return response.status, None
        elif method == REST_METHOD_GET:
            async with await self.session.get(url, headers=headers) as response:
                json = None
                if response.status == 200:
                    json = await response.json()
                return response.status, json
        elif method == REST_METHOD_POST:
            async with await self.session.post(url, headers=headers, data=data) as response:
                if response.content_type == "application/json":
                    self.log.debug(await response.json())
                    return response.status, await response.json()
                else:
                    return response.status, await response.text()

    async def _send_request_with_token_retry(self, method, url, headers=None, data=None):
        """
        Wraps the _send_request method to retry after a failure related to a wrong or expired access token by
        refreshing it and repeating the request.
        :param method: The method to use (GET, PUT, POST)
        :param url: The url the request will be sent to
        :param headers: The headers to add to the request.
        :param data: The data to send.
        :return: status, response json or None
        """
        status, response = await self._send_request(method, url, headers, data)
        if status == 200:
            return status, response
        if status in [400, 401]:  # status codes that may indicate an expired access token
            await self._refresh_access_token()
            headers["Authorization"] = "Bearer " + self.storage.get(ACCESS_TOKEN_FIELD, SPOTIFY_STORAGE_SECTION, "")
            status, response = await self._send_request(method, url, headers, data)
            return status, response
        return 500, None
