from enum import auto

from core_modules.util.DescriptiveEnum import DescriptiveEnum


class EventRepeatPolicy(DescriptiveEnum):
    """
    Enum containing all event repetition modes
    """
    NoRepeat = auto()
    Hourly = auto()
    Daily = auto()
    Weekly = auto()
    Monthly = auto()
    Yearly = auto()

    @staticmethod
    def get_event_repeat_policy_from_name(repeat_policy_name: str):
        for field in EventRepeatPolicy:
            if field == repeat_policy_name:
                return field
        return EventRepeatPolicy.NoRepeat
