import yaml
import os
from .config import LennyBotConfig

class LennyBotState:

    def __init__(self, config: LennyBotConfig) -> None:
        self._filename = config.state_file
        self._init_file()
        with open(self._filename) as fp:
            self._data = yaml.safe_load(fp)

    def _init_file(self):
        if not os.path.exists(self._filename):
            with open(self._filename, "w") as fp:
                yaml.safe_dump({}, fp)

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
        with open(self._filename, "w") as fp:
            yaml.safe_dump(self._data, fp, sort_keys=False, indent=4)
