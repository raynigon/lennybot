import logging
import re
from typing import Optional

import requests

from ..config.config import LennyBotCheckConfig
from .icheck import ICheck


class DockerImage:
    def __init__(self, registry: str, name: str, tag: Optional[str] = None) -> None:
        self._registry = registry
        self._name = name
        self._tag = tag


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
        image = self._parse_image()

        if image._registry is None:
            return self._exists_on_docker_hub(image)

        return self._exists_on_registry(image)

    def _parse_image(self):
        if ":" not in self._image_pattern:
            raise Exception("Image pattern does not contain a tag seperator")

        image_name = self._image_pattern.split(":")[0]
        image_tag = self._image_pattern.split(":")[1].replace("{{version}}", self.target_version)

        pattern = (
            r"(?:([\-\_\.\w]+)$)|(?:([\-\_\.\w]+)/([\-\_\.\w]+)$)|(?:([\-\.A-z0-9]+)/([\-\_\.\w]+)/([\-\_\.\w]+)$)"
        )

        match = re.match(pattern, image_name)
        if match is None:
               raise Exception(f"Given image pattern is not a valid docker image name {image_name}")
        logging.debug("regex matched following pattern: " + match.group(0))
        if match.group(1) is not None:
            logging.debug("regex matched following pattern: " + match.group(1))
            return DockerImage("", match.group(1), image_tag)
        elif match.group(2) is not None:
            logging.debug("regex matched following pattern: " + match.group(2) + "/" + match.group(3) + " " + image_tag)
            return DockerImage("", match.group(2) + "/" + match.group(3), image_tag)
        else:
            return DockerImage(match.group(4), match.group(5) + "/" + match.group(6), image_tag)

    def _exists_on_docker_hub(self, image: DockerImage):
        res = requests.get(f"https://hub.docker.com/v2/repositories/{image._name}/tags")
        if res.status_code != 200:
            raise Exception("Unexpected status")

        for tag in res.json()["results"]:
            if tag["name"] == image._tag:
                return True
        return False

    def _exists_on_registry(self, image: DockerImage):
        res = requests.get(f"https://{image._registry}/v2/{image._name}/manifests/{image._tag}")
        if res.status_code == 200:
            return True
        elif res.status_code == 404:
            return False
        raise Exception("Unexpected status")
