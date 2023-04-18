import os.path
import tomllib
from tomllib import TOMLDecodeError

import tomli_w

from core_modules.logging.lis_logging import get_logger

SECTION_HEADER_SERVER = "SERVER"
SECTION_HEADER_HUE = "PHILIPPS_HUE"

FIELD_SERVER_IP = "SERVER_IP"
FIELD_SERVER_PORT = "SERVER_PORT"

FIELD_HUE_BRIDGE_IP = "HUE_BRIDGE_IP"
FIELD_HUE_CLIENT_KEY = "HUE_CLIENT_KEY"
FIELD_DESK_LAMP_ID = "HUE_DESK_LAMP_ID"


class StorageManager:
    """
    The StorageManager is responsible for loading data from the data.toml file as well as providing an interface
    to use and manipulate the loaded data (get, add, update, remove)
    """

    log = get_logger(__name__)

    def __init__(self, path: str):
        """
        Initializes the StorageManager
        :param path: The path to the .toml file to use
        """
        self.log.info("Starting...")
        self.data_file_path = path
        self._read_toml_file()

    def _read_toml_file(self) -> None:
        """
        Reads the content of the .toml file this StorageManager instance is associated with.
        Will create an empty file if no .toml exists with the given path.
        """
        if not os.path.exists(self.data_file_path):
            # create empty file if it does not exist
            open(self.data_file_path, 'a').close()

        with open(self.data_file_path, "rb") as f:
            try:
                self._storage = tomllib.load(f)
            except TOMLDecodeError as e:
                self.log.error(self.data_file_path + " is not a valid toml file: " + str(e))
                exit(-1)

    def _write_toml_file(self) -> None:
        """
        Dumps and writes the current _storage object into a .toml file at the path this
        StorageManager instance is associated with.
        """
        with open(self.data_file_path, "wb") as f:
            tomli_w.dump(self._storage, f)

    def get(self, field: str, section: str = None, fallback=None):
        """
        Gets a value from a specified field and section, returning the fallback value if it does not exist.
        :param field: The field to get.
        :param section: The section to get the field from.
        :param fallback: The value that is returned if either the field or section does not exist.
        :return: The value at the specified section and field if they exist, otherwise the provided fallback value.
        """
        if section is not None:
            if section in self._storage and field in self._storage[section]:
                return self._storage[section][field]
        elif field in self._storage:
            return self._storage[field]
        return fallback

    def add(self, value, field: str, section: str = None, overwrite_if_exists: bool = False) -> None:
        """
        Adds the value at the provided field and section.
        :param value: The value to insert.
        :param field: The field to insert the value at.
        :param section: The section in which the field will be inserted into.
        :param overwrite_if_exists: Whether to overwrite and existing field if it already exists.
        """
        self.log.debug("Adding " + str(value) + " to field " + field + " in section " + str(section))
        if section is None:
            storage_area = self._storage
        else:
            if section in self._storage:
                storage_area = self._storage[section]
            else:
                self._storage[section] = None
                storage_area = self._storage[section]

        if field in storage_area:
            if overwrite_if_exists:
                self.update(field, value, section)
        else:
            storage_area[field] = value
            self._write_toml_file()

    def update(self, value, field: str, section: str = None) -> None:
        """
        Updates the value at the given field and section if they exist.
        :param value: The new value to insert at the given field and section.
        :param field: The field to update.
        :param section: The section to update
        """
        self.log.debug("Updating " + str(value) + " to field " + field + " in section " + str(section))
        if section is None and field in self._storage:
            self._storage[field] = value
            self._write_toml_file()
            return
        elif section in self._storage and field in self._storage[section]:
            self._storage[section][field] = value
            self._write_toml_file()
            return
        self.log.warning("Failed to update because section or field does not exist!")

    def remove(self, field: str, section: str = None) -> None:
        """
        Removes the value at the specified field and section if they exist.
        :param field: The field to remove
        :param section: The section the field should be removed in.
        """
        self.log.debug("Removing field " + field + " in section " + str(section))
        if section is None and field in self._storage:
            self._storage[field].pop()
            self._write_toml_file()
            return
        elif section in self._storage and field in self._storage[section]:
            self._storage[section][field].pop()
            self._write_toml_file()
            return
        self.log.warning("Failed to remove because section or field does not exist!")
