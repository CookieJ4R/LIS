from typing import Callable

from core_modules.logging.lis_logging import get_logger
from core_modules.rest.AbstractBaseApi import AbstractBaseApi
from core_modules.rest.RestServer import REST_METHOD_PUT
from core_modules.rest.request_util import get_string_from_args_obj
from feature_modules.soundplayer.SoundPlayerEvents import SoundPlayerPlayEvent, SoundPlayerPlayFromPoolEvent


class SoundPlayerApi(AbstractBaseApi):
    """
    API for all commands related to the sound player
    """

    log = get_logger(__name__)

    def __init__(self, put_event):
        self.put_event = put_event

    def register_endpoints(self, register_endpoint: Callable):
        self.log.debug("Registering api endpoints...")
        register_endpoint("/soundplayer/play", REST_METHOD_PUT, self._play_sound)
        register_endpoint("/soundplayer/play_pool", REST_METHOD_PUT, self._play_sound_pool)

    async def _play_sound(self, args):
        """
        Endpoint handler to play a specific sound.
        :param args: The args passed to the request.
        :return: 200 after the event was sent. Note that this also returns 200 when the sound is not played.
        The 200 only signifies, that the request has reached the REST server.
        """
        sound_id = get_string_from_args_obj("id", args)
        self.log.info(f"Received request - playing sound: {sound_id}")
        await self.put_event(SoundPlayerPlayEvent(sound_id))
        return 200, ""

    async def _play_sound_pool(self, args):
        """
        Endpoint handler to play a sound from a specific pool.
        :param args: The args passed to the request.
        :return: 200 after the event was sent. Note that this also returns 200 when the sound is not played.
        The 200 only signifies, that the request has reached the REST server.
        """
        pool_id = get_string_from_args_obj("id", args)
        self.log.info(f"Received request - playing from sound pool: {pool_id}")
        await self.put_event(SoundPlayerPlayFromPoolEvent(pool_id))
        return 200, ""
