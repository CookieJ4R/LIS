from typing import Callable

from core_modules.rest.AbstractBaseApi import AbstractBaseApi
from core_modules.rest.RestServer import REST_METHOD_GET


class PingApi(AbstractBaseApi):
    """
    Simple api to test if the rest server is running.
    """

    def register_endpoints(self, register_handler: Callable):
        register_handler("/ping", REST_METHOD_GET, self._ping_response)

    @staticmethod
    async def _ping_response(_args):
        """
        Endpoint handler for the /ping endpoint.
        :param _args: contains the arguments of the request
        :return: Tuple containing of (status_code, response)
        """
        return 200, "pong"
