import asyncio

from core_modules.eventing.BaseEvent import BaseEvent
from core_modules.logging.lis_logging import get_logger


class EventReceiver:
    """
    Base class for classes that need to receive events distributed by the central EventDistributor.
    """

    log = get_logger(__name__)

    def __init__(self):
        self.log.info("Starting...")
        self._event_queue = asyncio.Queue()
        # schedule _handle_events_task for execution
        asyncio.create_task(self._handle_events_task())

    def fetch_events_to_register(self) -> list[type[BaseEvent]]:
        """
        Method to collect Events this EventReceiver is interested in.
        Called by the EventDistributor during registration.
        :return: A list containing all Events the EventReceiver wants to receive.
        """
        return []

    async def put_internal(self, event: BaseEvent):
        """
        Method that enqueues the event to the internal _event_queue
        :param event: The event to add to the event queue.
        """
        self.log.debug("Adding " + str(type(event)) + " to internal event queue.")
        await self._event_queue.put(event)

    async def _handle_events_task(self):
        """
        Loop that is run in an async task to watch the internal event queue and handle events accordingly.
        """
        while True:
            event = await self._event_queue.get()
            await asyncio.create_task(self.handle_specific_event(event))

    async def handle_specific_event(self, event: BaseEvent):
        """
        Base method that gets called for each event received on the event queue.
        Should be overriden by child classes to provide the wanted event handling for each event the class
        subscribed to.
        :param event: The event that was received and that will be handled.
        """
        ...
