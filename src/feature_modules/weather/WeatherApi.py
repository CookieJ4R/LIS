from typing import Callable

from core_modules.eventing.TemporaryEventReceiver import TemporaryEventReceiver
from core_modules.logging.lis_logging import get_logger
from core_modules.rest.AbstractBaseApi import AbstractBaseApi
from core_modules.rest.RestServer import REST_METHOD_GET
from feature_modules.weather.WeatherEvents import CurrentWeatherResponseEvent, GetCurrentWeatherEvent


class WeatherApi(AbstractBaseApi):
    """
    API for all commands related to the weather service
    """

    log = get_logger(__name__)

    def __init__(self, put_event):
        self.put_event = put_event

    def register_endpoints(self, register_endpoint: Callable):
        self.log.debug("Registering api endpoints...")
        register_endpoint("/weather/current", REST_METHOD_GET, self._get_current_weather_data)

    async def _get_current_weather_data(self, _args):
        """
        Endpoint handler for the /weather/current endpoint.
        :param _args: contains the arguments of the request
        :return: Tuple containing the status_code and response
        """
        response_receiver = TemporaryEventReceiver(self.put_event, [CurrentWeatherResponseEvent])
        await response_receiver.start()
        await self.put_event(GetCurrentWeatherEvent())
        event: CurrentWeatherResponseEvent = await response_receiver.wait_for_event()
        return 200, event.current_weather.to_json()
