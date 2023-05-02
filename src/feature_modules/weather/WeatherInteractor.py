import asyncio
from typing import Callable

import aiohttp

from core_modules.eventing.BaseEvent import BaseEvent
from core_modules.eventing.EventReceiver import EventReceiver
from core_modules.logging.lis_logging import get_logger
from core_modules.storage.StorageManager import StorageManager
from feature_modules.weather.WeatherData import WeatherData
from feature_modules.weather.WeatherEvents import GetCurrentWeatherEvent, CurrentWeatherResponseEvent, \
    RefreshWeatherEvent

WEATHER_STORAGE_SECTION = "WEATHER"
API_TOKEN_FIELD = "OPEN_WEATHERMAP_API_TOKEN"
LOC_LONGITUDE_FIELD = "LONGITUDE"
LOC_LATITUDE_FIELD = "LATITUDE"

BASE_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


class WeatherInteractor(EventReceiver):
    """
    Class responsible for interacting with the openweathermap api.
    """
    log = get_logger(__name__, "DEBUG")

    def __init__(self, put_event: Callable, storage: StorageManager):
        super().__init__()
        self.put_event = put_event
        self.storage = storage
        self.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False))

        self.cur_weather_data = None
        asyncio.create_task(self.get_current_weather_data())

    def fetch_events_to_register(self) -> list[type[BaseEvent]]:
        return [GetCurrentWeatherEvent]

    async def handle_specific_event(self, event: BaseEvent):
        if isinstance(event, GetCurrentWeatherEvent):
            if self.cur_weather_data is None:
                await self.get_current_weather_data()
            await self.put_event(CurrentWeatherResponseEvent(self.cur_weather_data))
        elif isinstance(event, RefreshWeatherEvent):
            await self.get_current_weather_data()

    def _get_weather_params(self) -> dict:
        """
        Internal method to get the query params for the openweathermap api.
        :return: The dictionary that contains the query params.
        """
        params = {
            "lat": str(self.storage.get(LOC_LATITUDE_FIELD, WEATHER_STORAGE_SECTION, "")),
            "lon": str(self.storage.get(LOC_LONGITUDE_FIELD, WEATHER_STORAGE_SECTION, "")),
            "appid": str(self.storage.get(API_TOKEN_FIELD, WEATHER_STORAGE_SECTION, "")),
            "units": "metric"
         }
        self.log.debug("Querying weather with params: " + str(params))
        return params

    async def get_current_weather_data(self):
        """
        Gets the current weather data by sending a get request to the open weathermap api and updates the internal
        representation.
        """
        params = self._get_weather_params()
        async with await self.session.get(BASE_WEATHER_URL, params=params) as response:
            if response.content_type == "application/json":
                self.cur_weather_data = WeatherData.from_json(await response.json())
