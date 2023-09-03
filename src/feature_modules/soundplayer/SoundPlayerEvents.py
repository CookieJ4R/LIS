import json

from core_modules.eventing.BaseEvent import BaseEvent
from core_modules.scheduling.SchedulableEvent import SchedulableEvent, EVENT_ID_DATA_FIELD


class SoundPlayerPlayEvent(BaseEvent, SchedulableEvent):
    """
    Event to play a sound by id.
    """

    def __init__(self, sound_id: str):
        self.sound_id = sound_id

    @classmethod
    def get_event_id(cls) -> str:
        return SoundPlayerPlayEvent.__name__

    @classmethod
    def from_api_json(cls, parsed_json: dict):
        if parsed_json[EVENT_ID_DATA_FIELD] != SoundPlayerPlayEvent.get_event_id():
            raise ValueError
        return SoundPlayerPlayEvent(parsed_json["sound_id"])

    def to_json(self):
        obj = self.__dict__
        obj[EVENT_ID_DATA_FIELD] = SoundPlayerPlayEvent.get_event_id()
        return json.dumps(obj)


class SoundPlayerPlayFromPoolEvent(BaseEvent, SchedulableEvent):
    """
    Event to play a sound from a specific sound pool.
    """

    def __init__(self, pool_id: str):
        self.sound_id = pool_id

    @classmethod
    def get_event_id(cls) -> str:
        return SoundPlayerPlayFromPoolEvent.__name__

    @classmethod
    def from_api_json(cls, parsed_json: dict):
        if parsed_json[EVENT_ID_DATA_FIELD] != SoundPlayerPlayFromPoolEvent.get_event_id():
            raise ValueError
        return SoundPlayerPlayFromPoolEvent(parsed_json["pool_id"])

    def to_json(self):
        obj = self.__dict__
        obj[EVENT_ID_DATA_FIELD] = SoundPlayerPlayFromPoolEvent.get_event_id()
        return json.dumps(obj)
