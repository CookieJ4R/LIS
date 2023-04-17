import tomllib
from tomllib import TOMLDecodeError

SECTION_HEADER_SERVER = "SERVER"


class StorageManager:

    def __init__(self, path: str):
        self._storage = self._read_toml_file(path)

    @staticmethod
    def _read_toml_file(path: str):
        with open(path, "rb") as f:
            try:
                data = tomllib.load(f)
            except TOMLDecodeError as e:
                print("lis_data.toml is not a valid toml file: " + str(e))
                exit(-1)
            return data

    def get(self, field: str, section: str = None, fallback=None):
        if section is not None:
            if section in self._storage and field in self._storage[section]:
                return self._storage[section][field]
        elif field in self._storage:
            return self._storage[field]
        return fallback

    def add(self, field: str, value, section: str = None, overwrite_if_exists: bool = False):

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
            # self._write_data_file()

    def update(self, field: str, value, section: str = None):
        if section is None and field in self._storage:
            self._storage[field] = value
            # self._write_data_file()
            return
        elif section in self._storage and field in self._storage[section]:
            self._storage[section][field] = value
            # self._write_data_file()
            return
        print("Failed to update because section does not exist!")
