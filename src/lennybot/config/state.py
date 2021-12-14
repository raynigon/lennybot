import yaml
import os
from .config import LennyBotConfig

class LennyBotState:

    def __init__(self, config: LennyBotConfig) -> None:
        self._filename = config.state_file
        self._init_file()
        with open(self._filename) as file_ptr:
            self._data = yaml.safe_load(file_ptr)

    def _init_file(self):
        if not os.path.exists(self._filename):
            with open(self._filename, "w") as file_ptr:
                yaml.safe_dump({}, file_ptr)

    def current_version(self, name):
        if name in self._data.keys():
            return self._data[name]["version"]
        return None

    def update_version(self, name, version):
        if name in self._data.keys():
            self._data[name]["version"] = version
        else:
            self._data[name] = {
                "version": version
            }
    
    def save(self):
        with open(self._filename, "w") as file_ptr:
            yaml.safe_dump(self._data, file_ptr, sort_keys=False, indent=4)
