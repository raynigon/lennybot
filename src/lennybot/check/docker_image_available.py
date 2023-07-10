import logging

import requests

from ..config.config import LennyBotCheckConfig
from .icheck import ICheck

# import subprocess


class DockerImageAvailableCheck(ICheck):
    def __init__(self, application_name, source_version, target_version, config: LennyBotCheckConfig) -> None:
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
        """
        Checks if an image exists in the remote registry from _image_pattern.
        """
        image_path = self._image_pattern.replace("{{version}}", self.target_version)
        image_url = f"https://{image_path}"

        res = requests.get(image_url)
        if res.status_code == 200:
            return True
        elif res.status_code == 404:
            return False
        raise Exception("Unexpected status")
