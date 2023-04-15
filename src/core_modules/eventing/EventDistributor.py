import asyncio

from core_modules.eventing.BaseEvent import BaseEvent
from core_modules.eventing.EventReceiver import EventReceiver


class EventDistributor(EventReceiver):
    """
    Central event distribution center. Responsible for registering handler for events and
    distributing the arriving events to all registered handlers.
    """

    def __init__(self):
        self._event_queue = asyncio.Queue()
        self.event_distribution_map = {}
        super().__init__()

    def register_for_events(self, event_receiver: EventReceiver, events: list[type[BaseEvent]]):
        """
        Method to register an event_receiver for a list of event types.
        :param event_receiver: The EventReceiver to register.
        :param events: List of Event types to register.
        """
        for event in events:
            if event in self.event_distribution_map:
                self.event_distribution_map[event] = self.event_distribution_map[event].append(event_receiver)
            else:
                self.event_distribution_map[event] = [event_receiver]

    async def _handle_events_task(self):
        """
        Overrides the default _handle_events_task of the EventReceiver to distribute the events instead of
        handling them directly. While this could also be done by implementing the handle_specific_event method
        this approach was chosen to prevent possible complications if more logic was added to the
        EventReceiver _handle_events_task
        """
        while True:
            event = await self._event_queue.get()
            print(event)
            print(type(event))
            print(self.event_distribution_map)
            if type(event) in self.event_distribution_map:
                receivers = self.event_distribution_map[type(event)]
                for r in receivers:
                    await r.put_event(event)
            else:
                print("received event " + str(event) + " but no event receivers where registered")
