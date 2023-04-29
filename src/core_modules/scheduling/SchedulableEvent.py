from abc import ABC, abstractmethod


EVENT_ID_DATA_FIELD = "event_id"


class SchedulableEvent(ABC):
    """
    Baseclass for Events that should be schedulable via the SchedulingApi as they need to be constructed from json
    passed via the api call.
    """

    @classmethod
    @abstractmethod
    def get_event_id(cls) -> str:
        """
        The event id of the event. Used to differentiate between events with the same parameters.
        Needs to be used during the from_api_json call
        :return: The event_id of the event usually corresponding to the class name.
        """
        ...

    @classmethod
    @abstractmethod
    def from_api_json(cls, parsed_json: dict):
        """
        Constructs an event instance from a parsed json dict (usually passed via the scheduling api)
        :param parsed_json: The parsed json as dict
        :return: An instance of the event
        :raises KeyError: If the json does not correspond to this Event.
        :raises ValueError: If the event_id does not match.
        """
        ...

    @abstractmethod
    def to_json(self):
        """
        Constructs a JSON representation of this event.
        :return: A JSON string of this event
        """
        ...
