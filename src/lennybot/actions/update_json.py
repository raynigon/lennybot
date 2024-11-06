import json
from types import SimpleNamespace

from jsonpath_ng import jsonpath, parse

from ..config.config import LennyBotActionConfig
from .iaction import IAction


class UpdateJsonAction(IAction):
    def __init__(self, name, source_version, target_version, config: LennyBotActionConfig) -> None:
        self._name = name
        self._source_version = source_version
        self._target_version = target_version
        if config.target_file is None:
            raise Exception("Target file is not set for application " + name)
        self._target_file = config.target_file
        if config.json_path is None:
            raise Exception("JSON Path is not set for application " + name)
        self._json_path = parse(config.json_path)
        if config.value_pattern is not None:
            self._value_pattern = config.value_pattern
        else:
            self._value_pattern = "{{version}}"

    @property
    def application(self) -> str:
        return self._name

    @property
    def source_version(self) -> str:
        return self._source_version

    @property
    def target_version(self) -> str:
        return self._target_version

    def run(self):
        # Read the JSON data from the file
        with open(self._target_file, "r", encoding="utf-8") as file_ptr:
            json_data = json.load(file_ptr)
        # Update the value in the JSON data
        self._json_path.update(json_data, self._create_value())
        # Write the updated JSON data back to the file
        with open(self._target_file, "w", encoding="utf-8") as file_ptr:
            json.dump(json_data, fp=file_ptr, indent=4)

    def _create_value(self):
        return self._value_pattern.replace("{{version}}", self._target_version)
