import json

from core_modules.scheduling.SchedulableEvent import SchedulableEvent, EVENT_ID_DATA_FIELD


class SimpleSchedulableEvent(SchedulableEvent):
    """
    Implementation for events that carry no data to simplify the boilerplate code for them.
    """

    @classmethod
    def get_event_id(cls) -> str:
        return cls.__name__

    @classmethod
    def from_api_json(cls, parsed_json: dict):
        """
        Will just check for the EVENT_ID_DATA_FIELD as no data needs to be mapped
        :param parsed_json:
        :return:
        """
        if parsed_json[EVENT_ID_DATA_FIELD] != cls.get_event_id():
            raise ValueError
        return cls()

    def to_json(self):
        """
        Will create a simple dict containing only the EVENT_ID_DATA_FIELD as not data needs to be stored.
        :return: The json of the corresponding event.
        """
        return json.dumps({EVENT_ID_DATA_FIELD: self.__class__.get_event_id()})
