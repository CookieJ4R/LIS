from abc import ABC, abstractmethod


class HueBridgeBaseEvent(ABC):
    """
    Baseclass to provide some common methods for all HueBridgeEvents.
    """

    @staticmethod
    @abstractmethod
    def from_dict(json_parsed_obj: dict):
        """
        Method to obtain a specific event from an already parsed json string
        :param json_parsed_obj: The parsed json obj to convert to this event
        :return: A instance of this event with the values of the provided parsed json object.
        """
        ...

    @abstractmethod
    def to_json(self) -> str:
        """
        Method to obtain a JSON representation of this event.
        :return: JSON representation of this object.
        """
        ...
