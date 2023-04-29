import datetime
from typing import Callable

from core_modules.logging.lis_logging import get_logger
from core_modules.rest.AbstractBaseApi import AbstractBaseApi
from core_modules.rest.RestServer import REST_METHOD_GET


class SysInfoApi(AbstractBaseApi):
    """
    Api to get information about the LIS system.
    """

    log = get_logger(__name__)

    def register_endpoints(self, register_handler: Callable):
        self.log.debug("Registering api endpoints...")
        register_handler("/sysinfo", REST_METHOD_GET, self._sysinfo_response)

    async def _sysinfo_response(self, _args):
        """
        Endpoint handler for the /sysinfo endpoint.
        :param _args: contains the arguments of the request
        :return: Tuple containing the status_code and response
        """
        self.log.info("Received sysinfo request")
        return 200, self._create_sysinfo_response()

    @staticmethod
    def _create_sysinfo_response():
        info = {
            "sys_time": datetime.datetime.now().strftime("%H:%M:%S"),
            "sys_date": datetime.datetime.now().strftime("%Y-%m-%d")
        }
        return info
