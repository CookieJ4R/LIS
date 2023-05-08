from enum import auto

from core_modules.util.DescriptiveEnum import DescriptiveEnum


class CalendarRepeatPolicy(DescriptiveEnum):
    NoRepeat = auto()
    Daily = auto()
    Weekly = auto()
    Monthly = auto()
    Yearly = auto()

    @staticmethod
    def get_repeat_policy_from_name(repeat_policy_name: str):
        for field in CalendarRepeatPolicy:
            if field == repeat_policy_name.capitalize():
                return field
        return CalendarRepeatPolicy.NoRepeat
