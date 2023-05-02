from core_modules.eventing.BaseEvent import BaseEvent
from core_modules.scheduling.SimpleSchedulableEvent import SimpleSchedulableEvent
from feature_modules.weather.WeatherData import WeatherData


class GetCurrentWeatherEvent(BaseEvent):
    """
    Event to get the current weather.
    """


class CurrentWeatherResponseEvent(BaseEvent):
    """
    Response event for the GetCurrentWeatherEvent.
    """
    current_weather: WeatherData

    def __init__(self, current_weather: WeatherData):
        self.current_weather = current_weather


class RefreshWeatherEvent(BaseEvent, SimpleSchedulableEvent):
    """
    Event to refresh the current WeatherData object.
    """
