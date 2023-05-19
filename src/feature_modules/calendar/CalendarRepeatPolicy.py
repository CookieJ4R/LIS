from enum import auto

from core_modules.util.DescriptiveEnum import DescriptiveEnum


class CalendarRepeatPolicy(DescriptiveEnum):
    """
    Enum representing the possible repeat policies of calendar events in an ics file.
    """
    NoRepeat = auto()
    Daily = auto()
    Weekly = auto()
    Monthly = auto()
    Yearly = auto()

    @staticmethod
    def get_repeat_policy_from_name(repeat_policy_name: str):
        """
        Helper method to get a repeat policy by its name.
        :param repeat_policy_name: The name of the policy as stated in the ics format.
        :return: the enum value corresponding to the given name.
        """
        for field in CalendarRepeatPolicy:
            if field == repeat_policy_name.capitalize():
                return field
        return CalendarRepeatPolicy.NoRepeat
