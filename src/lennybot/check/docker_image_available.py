from ..config.config import LennyBotCheckConfig
from .icheck import ICheck
import requests

class DockerImageAvailableCheck(ICheck):

    def __init__(self, application_name, source_version, target_version, config: LennyBotCheckConfig) -> None:
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
        return False