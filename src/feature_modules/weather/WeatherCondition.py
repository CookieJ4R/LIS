from enum import auto

from core_modules.util.DescriptiveEnum import DescriptiveEnum

FOGGY_CONDITIONS = ["Mist", "Smoke", "Haze", "Dust", "Fog", "Sand", "Dust", "Ash", "Squall", "Tornado"]


class WeatherCondition(DescriptiveEnum):
    """
    Enum containing all available weather conditions
    """
    Unknown = auto()
    Thunderstorm = auto()
    Drizzle = auto()
    Rain = auto()
    Snow = auto()
    Clear = auto()
    Clouds = auto()
    Fog = auto()

    @staticmethod
    def get_condition_from_weather_response(response_condition_field: str):
        """
        Returns a WeatherCondition based on the passed string value (extracted from the weather api response)
        :param response_condition_field: the condition from the api response
        :return: The WeatherCondition enum based on the passed string
        """
        if response_condition_field in FOGGY_CONDITIONS:
            return WeatherCondition.Fog

        for condition in WeatherCondition:
            if response_condition_field == condition:
                return condition

        return WeatherCondition.Unknown
