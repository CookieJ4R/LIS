from abc import abstractmethod, ABC
from typing import Callable


class AbstractBaseApi(ABC):
    """
    Base class for apis that can be registered with the RestServer
    """

    @abstractmethod
    def register_endpoints(self, register_handler: Callable):
        """
        Called by the RestServer during registration for each api.
        Used to define the endpoints and handler methods by the apis.
        Example:
            register_handler("/ping", REST_METHOD_GET, self._ping_response)
        :param register_handler: method responsible for registering endpoints injected by the RestServer.
        """
        raise NotImplementedError()
