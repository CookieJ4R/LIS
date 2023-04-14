from typing import Coroutine

from tornado import web

from core_modules.rest.AbstractBaseApi import AbstractBaseApi
from core_modules.rest.RestOmniRequestHandler import RestOmniRequestHandler

REST_METHOD_GET = "GET"
REST_METHOD_POST = "POST"
REST_METHOD_PUT = "PUT"
REST_METHOD_DELETE = "DELETE"


class RestServer:
    """
    Class responsible for handling the http requests and starting the tornado web server
    """

    def __init__(self):
        self.server = web.Application([(r'/.*', RestOmniRequestHandler, {"rest_server": self})])
        self.endpoint_map = {
            REST_METHOD_GET: {},
            REST_METHOD_POST: {},
            REST_METHOD_PUT: {},
            REST_METHOD_DELETE: {}
        }

    def register_apis(self, apis_to_register: list[AbstractBaseApi]):
        """
        Registers the passed api objects with the rest server.
        :param list[AbstractBaseApi] apis_to_register: The api objects to register.
        """
        for api in apis_to_register:
            api.register_endpoints(self.register_endpoint)

    def register_endpoint(self, endpoint: str, method: str, handler: Coroutine):
        """
        Method to register a specific endpoint. Injected into the api objects register method during registering.
        :param endpoint: The endpoint to register the handler for (e.g. /ping)
        :param method: The method to register the endpoint for (e.g. GET). Use constants here!
        Attention: Registering a handler for a method + endpoint combination that already has a registered handler
        will override it!
        :param Coroutine handler: The async coroutine responsible for handling the http request.
        :raises ValueError: When an api tries to register a handler for a non-supported method.
        """
        if method not in self.endpoint_map:
            raise ValueError("API tried to register an endpoint for a non defined endpoint")
        self.endpoint_map[method][endpoint] = handler

    def start_server(self, host: str, port: int):
        """
        Starts the RestServer.
        :param host: The host ip of the server.
        :param port: The port the webserver should run on.
        """
        self.server.listen(port, host)

    async def handle_request(self, path, args, method):
        """
        Method for handling all http requests. Will call the registered handler for the
        corresponding method and endpoint.
        :param path: The endpoint that was called.
        :param args: The arguments that were passed to the endpoint.
        :param method: The method that was used to call the endpoint.
        :return: Will either return the status and result of the called handler,
        405 (Method not allowed) if an endpoint was called that has a registered handler under
        a different method or 404 if no registered handler was found for this endpoint.
        """
        if method in self.endpoint_map:
            registered_api_endpoints = self.endpoint_map[method]
            if self._is_endpoint_path_registered_for_method(path, method):
                return await registered_api_endpoints[path](args)
            elif self._is_endpoint_registered_for_different_method(path, method):
                return 405, ""
        return 404, ""

    def _is_endpoint_path_registered_for_method(self, endpoint_path: str, method: str):
        """
        Helper method to lookup if an endpoint is available under a specified method.
        :param endpoint_path: The endpoint to lookup.
        :param method: The method to check.
        :return: True if the endpoint is available under the specified method, False otherwise.
        """
        return endpoint_path in self.endpoint_map[method]

    def _is_endpoint_registered_for_different_method(self, endpoint_path: str, method_to_exclude: str):
        """
        Helper method to lookup if an endpoint is available under a different method.
        :param endpoint_path: The endpoint to lookup.
        :param method_to_exclude: The method to exclude - this is the method that was used for the request.
        :return: True if the endpoint is available under a different method, False otherwise.
        """
        for method in self.endpoint_map:
            if method == method_to_exclude:
                continue
            else:
                if self._is_endpoint_path_registered_for_method(endpoint_path, method):
                    return True
        return False
