import hashlib
import os

import yaml

from ..config.config import LennyBotConfig


class LennyBotState:
    def __init__(self, config: LennyBotConfig) -> None:
        self._filename = config.state_file
        self._init_file()
        self._hash = self._calculate_hash()
        with open(self._filename, encoding="utf-8") as file_ptr:
            self._data = yaml.safe_load(file_ptr)
        if self._data is None:
            self._data = {}

    def _init_file(self):
        if not os.path.exists(self._filename):
            with open(self._filename, "w", encoding="utf-8") as file_ptr:
                yaml.safe_dump({}, file_ptr)

    def _calculate_hash(self):
        with open(self._filename, "rb") as file_ptr:
            return hashlib.sha256(file_ptr.read()).hexdigest()

    def current_version(self, name):
        if name in self._data.keys():
            return self._data[name]["version"]
        return None

    def update_version(self, name, version):
        if name in self._data.keys():
            self._data[name]["version"] = version
        else:
            self._data[name] = {"version": version}

    def is_valid(self):
        return self._hash == self._calculate_hash()

    def save(self):
        if not self.is_valid():
            raise Exception("Invalid State")
        with open(self._filename, "w", encoding="utf-8") as file_ptr:
            yaml.safe_dump(self._data, file_ptr, sort_keys=False, indent=4)
