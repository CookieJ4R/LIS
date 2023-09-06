import platform
import subprocess

if platform.system() == "Windows":
    import winsound

from typing import Callable

from core_modules.eventing.BaseEvent import BaseEvent
from core_modules.eventing.EventReceiver import EventReceiver
from core_modules.logging.lis_logging import get_logger
from core_modules.storage.StorageManager import StorageManager
from feature_modules.soundplayer.SoundPlayerEvents import SoundPlayerPlayEvent, SoundPlayerPlayFromPoolEvent
from feature_modules.soundplayer.SoundTable import SoundTable

SECTION_HEADER_SOUNDPLAYER = "SOUNDPLAYER"

FIELD_SOUNDPLAYER_SOUNDTABLE = "SOUND_TABLE"


class SoundPlayerInteractor(EventReceiver):
    """
    Interactor to play sounds (either a specific one or from a specific pool)
    """
    log = get_logger(__name__)

    def __init__(self, put_event: Callable, storage: StorageManager):
        super().__init__()
        self.put_event = put_event
        self.sound_table = SoundTable(storage.get(FIELD_SOUNDPLAYER_SOUNDTABLE, SECTION_HEADER_SOUNDPLAYER))

    def fetch_events_to_register(self) -> list[type[BaseEvent]]:
        return [SoundPlayerPlayEvent, SoundPlayerPlayFromPoolEvent]

    async def handle_specific_event(self, event: BaseEvent):
        self.log.info("Handling " + str(event))
        if isinstance(event, SoundPlayerPlayEvent):
            await self.play_sound(event.sound_id)
        elif isinstance(event, SoundPlayerPlayFromPoolEvent):
            await self.play_from_pool(event.sound_id)

    async def play_sound(self, sound_id: str):
        """
        Plays a specific sound by id.
        :param sound_id: The id of the sound to play.
        """
        sound_path = self.sound_table.get_sound_path_for_id(sound_id)
        await self._play(sound_path)

    async def play_from_pool(self, pool_id: str):
        """
        Plays a random sound from a specified pool.
        :param pool_id: The pool to play the sound from.
        """
        sound_path = self.sound_table.get_sound_from_pool(pool_id)
        await self._play(sound_path)

    @staticmethod
    async def _play(sound_path: str):
        """
        Actually plays the provided sound path.
        :param sound_path: The sound path of the file to play.
        """
        if sound_path is None:
            return
        if platform.system() == "Windows":
            winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        else:
            subprocess.Popen(["aplay", sound_path])
