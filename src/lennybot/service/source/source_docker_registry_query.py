import re

from ...config import LennyBotSourceConfig
from ...config.config import LennyBotConfigContainerConfig
from ...helper import semver_2_vc
from ...helper.oci_registry import OciRegistryClient, parse_image_reference
from .isource import ISource


class DockerRegistryQuerySource(ISource):
    """
    Determines the latest version from the tags of an image in an OCI registry (GET /v2/<name>/tags/list).
    The repository is the image reference without tag, e.g. "wiziopublic.azurecr.io/wiz-app/wiz-broker".
    """

    def __init__(self, name, config: LennyBotSourceConfig, container_config: LennyBotConfigContainerConfig) -> None:
        self._name = name
        self._repository = config.repository
        self._version_regex = config.regex
        self._client = OciRegistryClient(container_config)

    @property
    def application(self) -> str:
        return self._name

    def latest_version(self) -> str:
        registry, image_name = parse_image_reference(self._repository)
        tags = self._client.list_tags(registry, image_name)
        results = []
        for tag in tags:
            match = re.fullmatch(self._version_regex, tag)
            if match is None:
                continue
            if len(match.groups()) < 1:
                continue
            results.append(match.group(1))
        if len(results) == 0:
            raise Exception(
                f"No tag of {registry}/{image_name} matches the version pattern {self._version_regex} "
                f"({len(tags)} tags checked)"
            )
        results.sort(key=semver_2_vc)
        return results[-1]
