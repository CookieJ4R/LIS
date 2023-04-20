"""
Class containing all Events used for RestServer components.
"""
from core_modules.eventing.BaseEvent import BaseEvent


class SSEDataEvent(BaseEvent):
    """
    Class for sending data to the SSERequestHandler. Each SSEDataEvent will be written as a singular event to the
    event-stream.
    """

    def __init__(self, event: str, data: str):
        self.event = event
        self.data = data

    def get_data(self):
        """
        Method to return the data of this event as an SSE formatted string that can directly be written to the output
        buffer.
        :return: event-stream formatted text containing event and data.
        """
        return "event: " + self.event + "\ndata: " + self.data + "\n\n"
