import aiohttp


class SessionManager:
    """
    The session manager is responsible for providing a shared session. It also handles re-establishing the session
    if it gets closed for some reason (e.g. temporary internet outage)
    """

    def __init__(self):
        """
        Establishes the initial internal shared session
        """
        self._session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False))

    def get_session(self) -> aiohttp.ClientSession:
        """
        Method to provide the current shared session. Will recreate one if the old session was closed.
        :return: The current TCP Session.
        """
        if self._session.closed:
            self._session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False))
        return self._session
