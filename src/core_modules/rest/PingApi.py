from typing import Callable

from core_modules.logging.lis_logging import get_logger
from core_modules.rest.AbstractBaseApi import AbstractBaseApi
from core_modules.rest.RestServer import REST_METHOD_GET


class PingApi(AbstractBaseApi):
    """
    Simple api to test if the rest server is running.
    """

    log = get_logger(__name__)

    def register_endpoints(self, register_handler: Callable):
        self.log.debug("Registering api endpoints...")
        register_handler("/ping", REST_METHOD_GET, self._ping_response)

    async def _ping_response(self, _args):
        """
        Endpoint handler for the /ping endpoint.
        :param _args: contains the arguments of the request
        :return: Tuple containing of (status_code, response)
        """
        self.log.info("Received request - replying with pong!")
        return 200, "pong"
