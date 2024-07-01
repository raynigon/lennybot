import re

from ..config.config import LennyBotActionConfig
from .iaction import IAction


class UpdateDockerfileAction(IAction):
    FROM_PATTERN = r"FROM ([^:]*):[^\s]*(.*)"

    def __init__(self, name, source_version, target_version, config: LennyBotActionConfig) -> None:
        self._name = name
        self._source_version = source_version
        self._target_version = target_version
        if config.target_file is None:
            raise Exception("Target file is not set for application " + name)
        self._target_file = config.target_file
        self._image_name = config.image
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
        with open(self._target_file, "r", encoding="utf-8") as file_ptr:
            lines = file_ptr.readlines()
        result = []
        for line in lines:
            match = re.match(self.FROM_PATTERN, line)
            if match is not None and match.group(1) == self._image_name:
                result.append(f"FROM {self._image_name}:{self._create_value()}{match.group(2)}\n")
                continue
            result.append(line)
        with open(self._target_file, "w", encoding="utf-8") as file_ptr:
            file_ptr.writelines(result)

    def _create_value(self):
        return self._value_pattern.replace("{{version}}", self._target_version)
