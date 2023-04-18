from typing import Callable

from core_modules.eventing.BaseEvent import BaseEvent
from core_modules.eventing.EventReceiver import EventReceiver
from core_modules.eventing.SystemEvents import RegisterResponseReceiverEvent, UnregisterResponseReceiverEvent
from core_modules.logging.lis_logging import get_logger


class ResponseEventReceiver(EventReceiver):
    """
    Special EventReceiver that is used to listen to a ResponseEvent manually.
    """

    log = get_logger(__name__)

    def __init__(self, put_event: Callable, response_events: list[type(BaseEvent)]):
        self.log.info("Starting ResponseReceiver for events: " + str(response_events))
        super().__init__()
        self.put_event = put_event
        self.response_events = response_events

    async def start(self) -> None:
        """
        The ResponseEventReceivers needs to be started to ensure that the registration with the event receiver goes
        through before the event it is waiting on is distributed to prevent "losing" the event.
        """
        self.log.info("Registering with EventDistributor...")
        await self.put_event(RegisterResponseReceiverEvent(self))

    async def _handle_events_task(self):
        """
        Overwrite _handle_events_task to do nothing as we want to manually wait for the event in this case.
        """
        ...

    def fetch_events_to_register(self) -> list[type[BaseEvent]]:
        """
        Overwritten to provide response event this ResponseEventReceiver is listening to.
        :return: List containing the response events to register
        """
        return self.response_events

    async def wait_for_response_event(self, unregister_after_response: bool = True):
        """
        Used to wait for a response event without using the internal loop to allow better application flow control.
        :param unregister_after_response: Whether to unregister the event receiver after receiving an event.
        :return: The response event this receiver is waiting on.
        """
        self.log.info("Waiting for response Event...")
        event = await self._event_queue.get()
        if unregister_after_response:
            self.log.info("Unregistering with EventDistributor...")
            await self.put_event(UnregisterResponseReceiverEvent(self))
        return event

