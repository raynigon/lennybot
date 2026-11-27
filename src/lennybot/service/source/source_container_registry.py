import re

import requests

from ...config.config import LennyBotConfigContainerConfig, LennyBotSourceConfig
from ...helper import semver_2_vc
from ..container_registry import get_registry_token
from .isource import ISource


class ContainerRegistrySource(ISource):
    def __init__(
        self,
        name: str,
        config: LennyBotSourceConfig,
        container_config: LennyBotConfigContainerConfig,
    ) -> None:
        self._name = name
        self._repository = config.repository
        self._version_regex = config.regex
        self._container_config = container_config

    @property
    def application(self) -> str:
        return self._name

    def latest_version(self) -> str:
        registry, separator, repository = self._repository.partition("/")
        if not separator or not registry or not repository:
            raise Exception(
                f"Registry source repository must have the format <registry>/<repository>: {self._repository}"
            )

        url = f"https://{registry}/v2/{repository}/tags/list"
        response = requests.get(url)
        access_token = get_registry_token(registry, response, self._container_config)
        if access_token is not None:
            response = requests.get(url, headers={"Authorization": f"Bearer {access_token}"})

        if response.status_code != 200:
            raise Exception(f"Unable to fetch registry tags, Status: {response.status_code}, Content: {response.text}")

        tags = response.json().get("tags") or []
        results = []
        for tag in tags:
            match = re.fullmatch(self._version_regex, tag)
            if match is None or len(match.groups()) < 1:
                continue
            results.append(match.group(1))

        if not results:
            raise Exception("No valid version was found")
        results.sort(key=semver_2_vc)
        return results[-1]
