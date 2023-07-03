import logging
import requests
import subprocess
from ..config.config import LennyBotCheckConfig
from .icheck import ICheck


class DockerImageAvailableCheck(ICheck):

    def __init__(
            self,
            application_name,
            source_version,
            target_version,
            config: LennyBotCheckConfig) -> None:
        self._log = logging.getLogger(self.__class__.__name__)
        self._application_name = application_name
        self._source_version = source_version
        self._target_version = target_version
        self._image_pattern = config.image_pattern

    @property
    def application(self) -> str:
        return self._application_name

    @property
    def source_version(self) -> str:
        return self._source_version

    @property
    def target_version(self) -> str:
        return self._target_version

    def check(self) -> bool:
        image_path = self._image_pattern.replace("{{version}}", self.target_version)
        try:
            subprocess.check_call(["docker", "pull", image_path], shell=False)
        except subprocess.CalledProcessError as error:
            self._log.debug(
                "Subprocess call failed for check {} on application {}\n{}",
                self.__class__.__name__, self.application, error)
            return False
        return True
