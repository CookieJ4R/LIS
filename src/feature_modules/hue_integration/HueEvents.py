"""
File containing all the Events used by the HueInteractor and HueApi
"""
import json

from core_modules.eventing.BaseEvent import BaseEvent
from core_modules.scheduling.SchedulableEvent import SchedulableEvent, EVENT_ID_DATA_FIELD
from feature_modules.hue_integration.HueLamp import HueLamp


class HueLampSetStateEvent(BaseEvent, SchedulableEvent):
    """
    Event for changing the on/off state of a specific lamp.
    """

    def __init__(self, lamp_id: str, on: bool):
        self.lamp_id = lamp_id
        self.on = on

    @classmethod
    def get_event_id(cls) -> str:
        return HueLampSetStateEvent.__name__

    @classmethod
    def from_api_json(cls, parsed_json: dict):
        if parsed_json[EVENT_ID_DATA_FIELD] != HueLampSetStateEvent.get_event_id():
            raise ValueError
        return HueLampSetStateEvent(parsed_json["lamp_id"], parsed_json["on"])

    def to_json(self):
        obj = self.__dict__
        obj[EVENT_ID_DATA_FIELD] = HueLampSetStateEvent.get_event_id()
        return json.dumps(obj)


class HueGetLampsEvent(BaseEvent):
    """
    Event for getting all lamps
    """


class HueGetLampsResponseEvent(BaseEvent):
    """
    Response event for listing all lamps and their id
    """

    def __init__(self, lamps: list[HueLamp]):
        self.lamps = lamps

    def get_lamp_json(self):
        """
        Helper method to return JSON containing all lamp objects
        :return: JSON describing all connected lamps
        """
        return json.dumps({"lamps": [lamp.__dict__ for lamp in self.lamps]})
