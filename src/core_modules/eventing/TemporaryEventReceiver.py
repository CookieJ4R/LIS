from typing import Callable

from core_modules.eventing.BaseEvent import BaseEvent
from core_modules.eventing.EventReceiver import EventReceiver
from core_modules.eventing.SystemEvents import RegisterTempReceiverEvent, UnregisterTempReceiverEvent
from core_modules.logging.lis_logging import get_logger


class TemporaryEventReceiver(EventReceiver):
    """
    Special EventReceiver that is used to listen to a ResponseEvent manually.
    """

    log = get_logger(__name__)

    def __init__(self, put_event: Callable, event_list: list[type(BaseEvent)]):
        self.log.debug("Starting TemporaryEventReceiver for events: " + str(event_list))
        super().__init__()
        self.put_event = put_event
        self.event_list = event_list

    async def start(self) -> None:
        """
        The TemporaryEventReceiver needs to be started manually to ensure that the registration with the event receiver
        goes through before the event it is waiting on is distributed to prevent "losing" the event.
        """
        self.log.debug("Registering with EventDistributor...")
        await self.put_event(RegisterTempReceiverEvent(self))

    async def _handle_events_task(self):
        """
        Overwrite _handle_events_task to do nothing as we want to manually wait for the event in this case.
        """
        ...

    def fetch_events_to_register(self) -> list[type[BaseEvent]]:
        """
        Overwritten to provide response event this TemporaryEventReceiver is listening to.
        :return: List containing the response events to register
        """
        return self.event_list

    async def wait_for_event(self, unregister_after_receive: bool = True):
        """
        Used to wait for a registered event without using the internal loop to allow better application flow control.
        :param unregister_after_receive: Whether to unregister the event receiver after receiving an event.
        :return: The event that was received.
        """
        self.log.debug("Waiting for Event...")
        event = await self._event_queue.get()
        if unregister_after_receive:
            self.log.debug("Unregistering with EventDistributor...")
            await self.put_event(UnregisterTempReceiverEvent(self))
        return event

