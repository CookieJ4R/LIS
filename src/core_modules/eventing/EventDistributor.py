from typing import Union

from core_modules.eventing.BaseEvent import BaseEvent
from core_modules.eventing.EventReceiver import EventReceiver
from core_modules.eventing.SystemEvents import SystemEvent, RegisterTempReceiverEvent, \
    UnregisterTempReceiverEvent
from core_modules.logging.lis_logging import get_logger
from core_modules.scheduling.SchedulableEvent import SchedulableEvent


class EventDistributor(EventReceiver):
    """
    Central event distribution center. Responsible for registering handler for events and
    distributing the arriving events to all registered handlers.
    """

    log = get_logger(__name__)

    def __init__(self):
        self.event_distribution_map = {}
        super().__init__()

    def get_registered_events(self) -> list[type[BaseEvent]]:
        """
        Get all events registered with the event distributor.
        :return: all registered events as a list.
        """
        return list(self.event_distribution_map.keys())

    def register_event_receivers(self, event_receivers: list[EventReceiver]):
        """
        Method to register an event_receiver for a list of event types.
        :param event_receivers: The EventReceivers to register.
        """
        for ev_receiver in event_receivers:
            events = ev_receiver.fetch_events_to_register()
            for event in events:
                self.log.debug("Registering " + ev_receiver.__class__.__name__ + " for event " + str(event))
                if event in self.event_distribution_map:
                    self.event_distribution_map[event].append(ev_receiver)
                else:
                    self.event_distribution_map[event] = [ev_receiver]

    def unregister_event_receivers(self, event_receivers: list[EventReceiver]):
        """
        Method to remove a list of event receivers from all events. Mostly used for TemporaryEventReceiver.
        :param event_receivers: The EventReceivers to unregister.
        """
        modified_events = []
        for event_receiver in event_receivers:
            for event in self.event_distribution_map:
                if event_receiver in self.event_distribution_map[event]:
                    self.log.info("Unregistering " + event_receiver.__class__.__name__ + " for event " + str(event))
                    self.event_distribution_map[event].remove(event_receiver)
                    modified_events.append(event)
        for modified_event in modified_events:
            if len(self.event_distribution_map[modified_event]) == 0:
                self.event_distribution_map.pop(modified_event)

    async def _handle_system_event(self, event: SystemEvent):
        """
        Method to handle SystemEvents. These are special events that influence the System and the EventDistributor as
        a whole and should not be forwarded to other receivers.
        :param event: The SystemEvent to handle.
        """
        self.log.debug("Handling SystemEvent " + str(event))
        if isinstance(event, RegisterTempReceiverEvent):
            self.register_event_receivers([event.event_receiver])
        elif isinstance(event, UnregisterTempReceiverEvent):
            self.unregister_event_receivers([event.event_receiver])

    async def _handle_events_task(self):
        """
        Overrides the default _handle_events_task of the EventReceiver to distribute the events instead of
        handling them directly. While this could also be done by implementing the handle_specific_event method
        this approach was chosen to prevent possible complications if more logic was added to the
        EventReceiver _handle_events_task
        """
        while True:
            event = await self._event_queue.get()
            if isinstance(event, SystemEvent):
                await self._handle_system_event(event)
            elif type(event) in self.event_distribution_map:
                receivers = self.event_distribution_map[type(event)]
                for recv in receivers:
                    self.log.debug("Forwarding event " + str(event) + " to " + str(recv))
                    await recv.put_internal(event)
            else:
                self.log.warning("Received event " + str(event) + " but no event receivers were registered")

    def map_to_schedulable_event(self, event_dict: dict) -> Union[SchedulableEvent | None]:
        """
        Tries to map the event json dict to an event registered with the EventDistributor.
        :param event_dict: The dict to map to a known Event.
        :return: The SchedulableEvent the dict was mapped to if it exists, None otherwise
        """
        for event in self.get_registered_events():
            if issubclass(event, SchedulableEvent):
                try:
                    self.log.debug(f"mapping {event_dict} to {event}")
                    return event.from_api_json(event_dict)
                except (KeyError, ValueError):
                    self.log.debug(f"{event_dict} is not mappable to event {event} - skipping!")
                    continue
        self.log.error(f"Event {event_dict} could not be mapped to registered event!")
        return None
