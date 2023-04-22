from typing import Callable

from tornado.iostream import StreamClosedError

from core_modules.eventing.TemporaryEventReceiver import TemporaryEventReceiver
from core_modules.eventing.SystemEvents import UnregisterTempReceiverEvent
from core_modules.logging.lis_logging import get_logger
from core_modules.rest.BaseRequestHandler import BaseRequestHandler
from core_modules.rest.RestServerEvents import SSEDataEvent


class SSERequestHandler(BaseRequestHandler):
    """
    Request handler for SSE (/sse). All Server sent events will be served over this endpoint.
    The frontend is responsible for registering EventListeners for the events it is interested in on the specific route.
    """

    log = get_logger(__name__)
    put_event: Callable
    _sse_event_receiver: TemporaryEventReceiver

    def initialize(self, put_event: Callable):
        """
        Initialize method called by tornado during each request.
        :param put_event: The callable for sending an Event to the EventDistributor
        """
        self.put_event = put_event
        self._sse_event_receiver = TemporaryEventReceiver(put_event, [SSEDataEvent])

    async def get(self):
        """
        GET endpoint with keep-alive event stream for Server-Sent Events
        """
        self.log.debug("Received SSE Request")
        self.add_header("Content-Type", "text/event-stream")
        self.add_header("Cache-Control", "no-store")
        await self._sse_event_receiver.start()
        while True:
            event: SSEDataEvent = await self._sse_event_receiver.wait_for_event(
                unregister_after_receive=False)
            self.log.debug("Received SSEDataEvent: " + str(event))
            self.log.debug("Writing SSE response...")
            self.write(event.get_data())
            try:
                await self.flush()
            except StreamClosedError as e:
                self.log.warning("Lost connection to client - unregistering sse event receiver: " + str(e))
                await self.put_event(UnregisterTempReceiverEvent(self._sse_event_receiver))
                break
