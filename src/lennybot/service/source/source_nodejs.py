import requests
from typing import Any
from requests.exceptions import HTTPError

from ...config import LennyBotSourceConfig
from .isource import ISource

NODEJS_ORG_VERSIONS_URL = "https://nodejs.org/dist/index.json"


class NodeJSVersionNotFoundException(Exception):
    def __init__(self, data: Any, *args: object) -> None:
        super().__init__(*args)
        self._data = data


class NodeJSFormatException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class NodeJSVersionSource(ISource):
    def __init__(self, name, config: LennyBotSourceConfig) -> None:
        self._name = name
        self._lts_only = config.lts_only
        self._source_url = config.source_url

    @property
    def application(self) -> str:
        return self._name

    def latest_version(self) -> str:
        headers = {"user-agent": "lennybot/0.0.1"}
        response = requests.get(NODEJS_ORG_VERSIONS_URL, headers=headers)
        response.raise_for_status()

        releases = response.json()
        sorted(releases, key=lambda x: x["version"])
        for release in releases:
            if not self._lts_only:
                return self._extract_semver_version(release)
            if release["lts"]:
                return self._extract_semver_version(release)

        raise NodeJSVersionNotFoundException(releases)

    def _extract_semver_version(self, release) -> str:
        if "version" not in release.keys():
            raise NodeJSFormatException("Missing version field in release")
        version = release["version"]

        if not version.startswith("v"):
            raise NodeJSFormatException("Invalid version format")

        version = version.replace("v", "")

        return version
