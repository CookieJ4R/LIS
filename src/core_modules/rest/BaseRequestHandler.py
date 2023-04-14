from typing import Optional, Awaitable

import tornado.web


class BaseRequestHandler(tornado.web.RequestHandler):
    """
    Extension of the tornado RequestHandler modified for CORS requests
    """

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        """
        Implementation of currently unused (but required) abstract method
        :param chunk: bytes received
        :return: Optional coroutine to influence application flow
        """
        ...

    def set_default_headers(self):
        """
        Sets the default headers for CORS, allowing GET, POST, PUT, DELETE and preflight OPTIONS requests
        """
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')

    def options(self):
        """
        OPTIONS handler to handle preflight response
        """
        self.set_status(204)
        self.finish()
