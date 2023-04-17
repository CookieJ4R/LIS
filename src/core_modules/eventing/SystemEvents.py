from core_modules.eventing.BaseEvent import BaseEvent


class SystemEvent(BaseEvent):
    """
    Base class for all system events that should be handled by the EventDistributor itself.
    """
    ...


class RegisterResponseReceiverEvent(SystemEvent):
    """
    Event to register a temporary ResponseReceiver
    """
    def __init__(self, response_receiver):
        self.response_receiver = response_receiver


class UnregisterResponseReceiverEvent(SystemEvent):
    """
    Event to unregister a temporary ResponseReceiver
    """
    def __init__(self, response_receiver):
        self.response_receiver = response_receiver
