from core_modules.eventing.BaseEvent import BaseEvent


class SystemEvent(BaseEvent):
    """
    Base class for all system events that should be handled by the EventDistributor itself.
    """
    ...


class RegisterTempReceiverEvent(SystemEvent):
    """
    Event to register a TemporaryEventReceiver
    """
    def __init__(self, event_receiver):
        self.event_receiver = event_receiver


class UnregisterTempReceiverEvent(SystemEvent):
    """
    Event to unregister a TemporaryEventReceiver
    """
    def __init__(self, event_receiver):
        self.event_receiver = event_receiver
