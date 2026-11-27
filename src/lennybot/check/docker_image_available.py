import logging
import re
from typing import Optional

import requests

from ..config.config import LennyBotCheckConfig, LennyBotConfigContainerConfig
from ..helper.oci_registry import OciRegistryClient, WwwAuthenticateHeader
from .icheck import ICheck

PATTERN = r"(?:([\-\_\.\w]+)$)|(?:([\-\_\.\w]+)/([\-\_\.\w]+)$)|(?:([\-\.A-z0-9]+)/([\-\_\.\w]+)/([\-\_\.\w]+)$)|(?:([\-\.A-z0-9]+)/([\-\_\.\w]+)/([\-\_\.\w]+)/([\-\_\.\w]+)$)|(?:([\-\.A-z0-9]+)/([\-\.A-z0-9]+)/([\-\_\.\w]+)/([\-\_\.\w]+)/([\-\_\.\w]+)$)"


class DockerImage:
    def __init__(self, registry: Optional[str], name: str, tag: Optional[str] = None) -> None:
        self._registry = registry
        self._name = name
        self._tag = tag


class DockerImageAvailableCheck(ICheck):
    # pylint: disable=too-many-positional-arguments
    def __init__(
        self,
        application_name,
        source_version,
        target_version,
        config: LennyBotCheckConfig,
        container_config: LennyBotConfigContainerConfig,
    ) -> None:
        self._log = logging.getLogger(self.__class__.__name__)
        self._application_name = application_name
        self._source_version = source_version
        self._target_version = target_version
        self._image_pattern = config.image_pattern
        self._container_config = container_config
        self._registry_client = OciRegistryClient(container_config)

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
        image = self._parse_image()

        if image._registry is None:
            return self._exists_on_docker_hub(image)
        return self._exists_on_registry(image)

    def _parse_image(self):
        """
        Parse function to return a docker image is correct by syntax
        """
        if ":" not in self._image_pattern:
            raise Exception("Image pattern does not contain a tag seperator")

        image_name = self._image_pattern.split(":")[0]
        image_tag = self._image_pattern.split(":")[1].replace("{{version}}", self.target_version)

        match = re.match(PATTERN, image_name)
        if match is None:
            raise Exception(f"Given image pattern is not a valid docker image name {image_name}")
        logging.debug("regex matched following pattern: " + match.group(0))
        if match.group(1) is not None:
            logging.debug("regex matched following pattern: " + match.group(1))
            return DockerImage(None, "library/" + match.group(1), image_tag)
        if match.group(2) is not None:
            logging.debug("regex matched following pattern: " + match.group(2) + "/" + match.group(3) + " " + image_tag)
            return DockerImage(None, match.group(2) + "/" + match.group(3), image_tag)
        if match.group(4) is not None:
            logging.debug(
                "regex matched following pattern: "
                + match.group(4)
                + "/"
                + match.group(5)
                + "/"
                + match.group(6)
                + " "
                + image_tag
            )
            return DockerImage(match.group(4), match.group(5) + "/" + match.group(6), image_tag)
        if match.group(7) is not None:
            logging.debug(
                "regex matched following pattern: "
                + match.group(7)
                + "/"
                + match.group(8)
                + "/"
                + match.group(9)
                + "/"
                + match.group(10)
                + " "
                + image_tag
            )
            return DockerImage(
                match.group(7),
                match.group(8) + "/" + match.group(9) + "/" + match.group(10),
                image_tag,
            )
        return DockerImage(
            match.group(11),
            match.group(12) + "/" + match.group(13) + "/" + match.group(14) + "/" + match.group(15),
            image_tag,
        )

    def _authenticate_on_registry(self, registry: str, authentication_header: WwwAuthenticateHeader) -> str:
        return self._registry_client.authenticate(registry, authentication_header)

    def _exists_on_docker_hub(self, image: DockerImage):
        """
        Checks if the given Docker file exists on DockerHub
        """
        url = f"https://hub.docker.com/v2/repositories/{image._name}/tags?page_size=10000"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Unexpected status: {response.status_code} for url: {url}")

        for tag in response.json()["results"]:
            if tag["name"] == image._tag:
                return True
        return False

    def _exists_on_registry(self, image: DockerImage) -> bool:
        """
        Checks if the given Docker file exists on that perticular registry.
        Authentication against the registry is handled by the registry client.
        """
        if image._registry is None:
            raise Exception("registry must be set and not be None")

        request_url = f"https://{image._registry}/v2/{image._name}/manifests/{image._tag}"

        # depending on the registry it my helps adding the write accept header :)
        # https://github.com/goharbor/harbor/issues/16075
        headers = {
            "Accept": "application/vnd.oci.image.index.v1+json, application/vnd.docker.distribution.manifest.list.v2+json",
        }
        response = self._registry_client.get(image._registry, request_url, headers=headers)

        if response.status_code == 200:
            return True
        if response.status_code == 404:
            return False
        raise Exception(f"Unexpected status: {response.status_code} for url {request_url}")
