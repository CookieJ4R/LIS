import json
import random


class SoundTable:
    """
    Class representing the internal table for mapping sound_ids and pool_ids to their respective sound file.
    """

    sound_table: dict
    sound_pool_table: dict

    def __init__(self, sound_table_path: str):
        self._build_internal_table(sound_table_path)

    def _build_internal_table(self, sound_table_path: str):
        """
        Parses the sound table specified in the config and builds the internal sound and soundpool table
        :param sound_table_path: The path of the sound_table file
        """
        self.sound_table = {}
        self.sound_pool_table = {}
        with open(sound_table_path, "r") as sound_table_file:
            content = sound_table_file.read()
            json_table = json.loads(content)
            for sound_obj in json_table["sounds"]:
                self.sound_table[sound_obj["id"]] = sound_obj["path"]
            for sound_pool_obj in json_table["sound_pools"]:
                self.sound_pool_table[sound_pool_obj["id"]] = sound_pool_obj["sound_ids"]

    def get_sound_path_for_id(self, sound_id: str):
        """
        Gets the path to the sound file for a specific sound_id.
        :param sound_id: The sound_id to fetch the path for.
        :return: the path of the sound_file belonging to the sound_id.
        """
        if sound_id in self.sound_table:
            return self.sound_table[sound_id]
        else:
            return None

    def get_sound_from_pool(self, pool_id: str):
        """
        Gets the path to a random sound file in the specified sound pool.
        :param pool_id: The pool_id to get a sound from.
        :return: the path of one sound_file belonging to the sound pool with the specified pool_id.
        """
        if pool_id in self.sound_pool_table:
            pool = self.sound_pool_table[pool_id]
            rnd = random.Random()
            sound_id = pool[rnd.randint(0, len(pool) - 1)]
            return self.get_sound_path_for_id(sound_id)
        else:
            return None
