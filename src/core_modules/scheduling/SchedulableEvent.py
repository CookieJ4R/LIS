from abc import ABC, abstractmethod


class SchedulableEvent(ABC):
    """
    Baseclass for Events that should be schedulable via the SchedulingApi as they need to be constructed from json
    passed via the api call.
    """

    @staticmethod
    @abstractmethod
    def from_api_json(parsed_json: dict):
        """
        Constructs an event instance from a parsed json dict (usually passed via the scheduling api=
        :param parsed_json: The parsed json as dict
        :return: An instance of the event
        :raises KeyError: If the json does not correspond to this Event.
        """
        ...
