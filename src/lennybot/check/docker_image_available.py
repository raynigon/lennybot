import logging
import re
from typing import Optional

import requests

from ..config.config import LennyBotCheckConfig, LennyBotConfigContainerConfig, LennyBotConfigContainerRegistry
from .icheck import ICheck

PATTERN = r"(?:([\-\_\.\w]+)$)|(?:([\-\_\.\w]+)/([\-\_\.\w]+)$)|(?:([\-\.A-z0-9]+)/([\-\_\.\w]+)/([\-\_\.\w]+)$)"
BLOCKED_REGISTRIES = []  # "docker.elastic.co"]  # Requires authentication, but is a public registry


class DockerImage:
    def __init__(self, registry: Optional[str], name: str, tag: Optional[str] = None) -> None:
        self._registry = registry
        self._name = name
        self._tag = tag


class DockerImageAvailableCheck(ICheck):
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
        if image._registry in BLOCKED_REGISTRIES:
            raise Exception(f"Registry in Blocked Registries {image._registry}")
        return self._exists_on_registry(image)

    def _parse_image(self):
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
        return DockerImage(match.group(4), match.group(5) + "/" + match.group(6), image_tag)

    def _authenticate_on_registry(self, registry: str, realm: str, service: str, scope: str) -> str:
        if registry not in self._container_config.registries.keys():
            raise Exception(f"No credentials found for registry: {registry}")

        registry_data = self._container_config.registries[registry]

        if registry_data.password is None or "":
            url = f"{realm}?scope={scope}&grant_type=password&service={service}&username={registry_data.username}&password={registry_data.password}&client_id=lennybot&access_type=offline"
            response = requests.get(url)
        else:
            params = {"scope": scope, "grant_type": "password", "service": service, "client_id": "lennybot", "access_type": "offline"}
            url = f"{realm}?{url_encode_params(params)}"
            response = requests.get(url)

        if response.status_code == 401:
            raise Exception("Error occured: Unauthenticated: ", response.status_code)

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("token")
            return access_token

        ## TODO: test for unauthenticated

    def _exists_on_docker_hub(self, image: DockerImage):
        url = f"https://hub.docker.com/v2/repositories/{image._name}/tags?page_size=10000"
        res = requests.get(url)
        if res.status_code != 200:
            raise Exception(f"Unexpected status: {res.status_code} for url: {url}")

        for tag in res.json()["results"]:
            if tag["name"] == image._tag:
                return True
        return False

    def _exists_on_registry(self, image: DockerImage, access_token: Optional[str] = None) -> bool:
        request_url = f"https://{image._registry}/v2/{image._name}/manifests/{image._tag}"

        if access_token is not None:
            headers = {"Authorization": f"Bearer {access_token}"}
            res = requests.get(request_url, headers=headers)
        else:
            res = requests.get(request_url)

        if res.status_code == 401 and access_token is None:
            registry = image._registry
            authenticate = res.headers["Www-Authenticate"]
            realm = authenticate.split('realm="')[1].split('"')[0]
            service = authenticate.split('service="')[1].split('"')[0]
            scope = authenticate.split('scope="')[1].split('"')[0]

            access_token = self._authenticate_on_registry(registry, realm, service, scope)

            return self._exists_on_registry(image, access_token)
        if res.status_code == 200:
            return True
        if res.status_code == 404:
            return False
        raise Exception(f"Unexpected status: {res.status_code} for url {request_url}")
