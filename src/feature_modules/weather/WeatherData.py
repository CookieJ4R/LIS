import json
from dataclasses import dataclass

from feature_modules.weather.WeatherCondition import WeatherCondition


@dataclass
class WeatherData:
    """
    Dataclass containing all information regarding the current weather.
    """
    condition: WeatherCondition
    temperature: float
    humidity: float
    wind_speed: float
    sunrise: int
    sunset: int

    @staticmethod
    def from_json(parsed_json: dict):
        """
        Returns a WeatherData object based on a passed parsed_json dictionary
        :param parsed_json: The parsed json string as a dictionary.
        :return: WeatherData object based on the values contained in the passed json dict.
        """
        return WeatherData(
            WeatherCondition.get_condition_from_weather_response(parsed_json["weather"][0]["main"]),
            parsed_json["main"]["temp"],
            parsed_json["main"]["humidity"],
            parsed_json["wind"]["speed"],
            parsed_json["sys"]["sunrise"],
            parsed_json["sys"]["sunset"])

    def to_json(self):
        """
        Returns a json string representation of the WeatherData object.
        :return: The json representation.
        """
        return json.dumps(self.__dict__)
