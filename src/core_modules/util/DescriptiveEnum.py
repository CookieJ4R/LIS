from enum import StrEnum


class DescriptiveEnum(StrEnum):
    """
    Metaclass for string based enums to allow automatic value assignment via auto() based on the field name
    """

    def _generate_next_value_(name, start, count, last_values):
        """
        Overwrites the enum method to allow automatic name assigning via auto()
        """
        return name
