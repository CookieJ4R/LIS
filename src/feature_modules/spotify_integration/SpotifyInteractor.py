import aiohttp

from core_modules.eventing.BaseEvent import BaseEvent
from core_modules.eventing.EventReceiver import EventReceiver
from core_modules.logging.lis_logging import get_logger
from core_modules.rest.RestServer import REST_METHOD_PUT, REST_METHOD_GET, REST_METHOD_POST
from core_modules.storage.StorageManager import StorageManager
from feature_modules.spotify_integration.SpotifyEvents import SpotifyPausePlaybackEvent, SpotifyStartResumePlaybackEvent


class SpotifyInteractor(EventReceiver):
    """
    Class responsible for interacting with the spotify REST api.
    """
    log = get_logger(__name__, "DEBUG")

    def __init__(self, storage: StorageManager):
        super().__init__()
        self.storage = storage
        self.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False))

    def fetch_events_to_register(self) -> list[type[BaseEvent]]:
        return [SpotifyPausePlaybackEvent, SpotifyStartResumePlaybackEvent]

    async def handle_specific_event(self, event: BaseEvent):
        if isinstance(event, SpotifyPausePlaybackEvent):
            await self._pause_playback()
        elif isinstance(event, SpotifyStartResumePlaybackEvent):
            await self._start_resume_playback()

    async def _start_resume_playback(self):
        """
        Method to start or resume the current playback by sending a request to the spotify web api.
        """
        await self._send_request_with_token_retry(REST_METHOD_PUT,
                                                  "https://api.spotify.com/v1/me/player/play",
                                                  headers={
                                                      "Authorization": "Bearer " + self.storage.get(
                                                          "ACCESS_TOKEN",
                                                          "SPOTIFY", "")})

    async def _pause_playback(self):
        """
        Method to pause the current playback by sending a request to the spotify web api.
        """
        await self._send_request_with_token_retry(REST_METHOD_PUT,
                                                  "https://api.spotify.com/v1/me/player/pause",
                                                  headers={
                                                      "Authorization": "Bearer " + self.storage.get(
                                                          "ACCESS_TOKEN",
                                                          "SPOTIFY", "")})

    async def _refresh_access_token(self):
        """
        Method to refresh and update the access_token by sending a request with the refresh_token.
        """
        status, response = await self._send_request(REST_METHOD_POST, "https://accounts.spotify.com/api/token",
                                                    data={"grant_type": "refresh_token",
                                                          "refresh_token": self.storage.get(
                                                              "REFRESH_TOKEN", "SPOTIFY", "")
                                                          },
                                                    headers={"Authorization": "Basic " + self.storage.get("AUTH_CODE",
                                                                                                          "SPOTIFY",
                                                                                                          ""),
                                                             "Content-Type": "application/x-www-form-urlencoded"})
        if status == 200:
            self.storage.update(response["access_token"], "ACCESS_TOKEN", "SPOTIFY")

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
                return response.status, None
        elif method == REST_METHOD_POST:
            async with await self.session.post(url, headers=headers, data=data) as response:
                self.log.debug(await response.json())
                return response.status, await response.json()

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
        if status in [400, 401]:
            await self._refresh_access_token()
            headers["Authorization"] = "Bearer " + self.storage.get("ACCESS_TOKEN", "SPOTIFY", "")
            status, response = await self._send_request(method, url, headers, data)
            return status, response
        return 500, None
