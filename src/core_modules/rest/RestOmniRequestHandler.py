from typing import Callable

from core_modules.logging.lis_logging import get_logger
from core_modules.rest.BaseRequestHandler import BaseRequestHandler
from core_modules.rest.request_util import remap_request_args


class RestOmniRequestHandler(BaseRequestHandler):
    """
    Extension of the tornado BaseRequestHandler which forwards all api calls to the RestServer handle_request method.
    This is used because we want to register api Objects that are instantiated before and register themselves with the
    RestServer. Therefore, tornado only takes care of asynchronously receiving the request and forwarding the result
    of the registered endpoint handler in the specific apis.
    """
    log = get_logger(__name__)
    request_handle_callable: Callable = None

    def initialize(self, request_handle_callable: Callable):
        """
        Initialize method called by tornado during each request.
        :param request_handle_callable: The callable responsible for handling and distributing the requests as this
        Handler accepts all requests.
        """
        self.request_handle_callable = request_handle_callable

    async def get(self):
        """ Handler to forward get requests """
        await self._forward_request()

    async def post(self):
        """ Handler to forward post requests """
        await self._forward_request()

    async def put(self):
        """ Handler to forward put requests """
        await self._forward_request()

    async def delete(self):
        """ Handler to forward delete requests """
        await self._forward_request()

    async def _forward_request(self):
        """
        Forwards the request and all additional information like args and method to the handler callable.
        This method is also responsible for actually returning the response to the request containing the response and
         status of the handler which actually handles the request in the end.
        """
        method = self.request.method
        path = self.request.path
        parameters = remap_request_args(self.request.arguments)
        self.log.info("Received " + method + " request on endpoint " + path)
        status, response = await self.request_handle_callable(path, parameters, method)
        self.set_status(status)
        self.write(response)
        await self.flush()
