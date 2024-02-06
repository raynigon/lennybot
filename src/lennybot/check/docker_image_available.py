import logging
import re
from typing import Optional
from urllib.parse import urlencode

import requests

from ..config.config import LennyBotCheckConfig, LennyBotConfigContainerConfig, LennyBotConfigContainerRegistry
from .icheck import ICheck

PATTERN = r"(?:([\-\_\.\w]+)$)|(?:([\-\_\.\w]+)/([\-\_\.\w]+)$)|(?:([\-\.A-z0-9]+)/([\-\_\.\w]+)/([\-\_\.\w]+)$)|(?:([\-\.A-z0-9]+)/([\-\_\.\w]+)/([\-\_\.\w]+)/([\-\_\.\w]+)$)"


class DockerImage:
    def __init__(self, registry: Optional[str], name: str, tag: Optional[str] = None) -> None:
        self._registry = registry
        self._name = name
        self._tag = tag


class WwwAuthenticateHeader:
    def __init__(self, realm: str, scope: str, service: str) -> None:
        self.realm = realm
        self.scope = scope
        self.service = service

    @classmethod
    def parse(cls, response):
        authenticate = response.headers["Www-Authenticate"]
        realm = authenticate.split('realm="')[1].split('"')[0]
        service = authenticate.split('service="')[1].split('"')[0]
        scope = authenticate.split('scope="')[1].split('"')[0]
        return WwwAuthenticateHeader(realm, scope, service)


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
        return DockerImage(match.group(7), match.group(8) + "/" + match.group(9) + "/" + match.group(10), image_tag)

    def _authenticate_on_registry(self, registry: str, authentication_header: WwwAuthenticateHeader) -> str:
        params = {
            "scope": authentication_header.scope,
            "grant_type": "password",
            "service": authentication_header.service,
            "client_id": "lennybot",
            "access_type": "offline",
        }

        url = f"{authentication_header.realm}?{urlencode(params)}"

        if registry in self._container_config.registries.keys():
            registry_data = self._container_config.registries[registry]
            username = registry_data.username
            password = registry_data.password
            if "<REDACTED>" in [username, password]:
                logging.warning(
                    "Either username or password contain '<REDACTED>' and probably have not been overwritten"
                )
            response = requests.get(url, auth=(username, password))
        else:
            logging.debug("Registry not found in config")
            response = requests.get(url)

        if response.status_code == 200:
            token_data = response.json()

            access_token = None
            if "token" in token_data.keys():
                access_token = token_data.get("token")
            elif "access_token" in token_data.keys():
                access_token = token_data.get("access_token")
            else:
                raise Exception("No Access_Token found in response body")

            return str(access_token)

        if response.status_code == 401:
            logging.error("Authentication failed: %d with %s", response.status_code, response.headers)
            raise Exception("Error occurred: Unauthenticated: ", response.status_code)

        if response.status_code == 403:
            logging.error("Authorization failed: %d with %s", response.status_code, response.headers)
            raise Exception("Error occurred: Unauthorization: ", response.status_code)

        if response.status_code == 404:
            logging.error("Nothing Found:  %d with %s", response.status_code, response.headers)
            raise Exception("Error occurred: Nothing Found: ", response.status_code)

        raise Exception("Unexpected Status Code", response.status_code)

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

    def _exists_on_registry(self, image: DockerImage, access_token: Optional[str] = None) -> bool:
        """
        Checks if the given Docker file exists on that perticular registry.
        Also authenticated requests are handled within this function by providing an access token.
        """
        if image._registry is None:
            raise Exception("registry must be set and not be None")

        request_url = f"https://{image._registry}/v2/{image._name}/manifests/{image._tag}"

        headers = {"Accept": "application/vnd.oci.image.index.v1+json"}
        if access_token is not None:
            headers["Authorization"] = f"Bearer {access_token}"
        response = requests.get(request_url, headers=headers)

        if response.status_code == 401 and access_token is None:
            registry = image._registry
            header_value = WwwAuthenticateHeader.parse(response)
            access_token = self._authenticate_on_registry(registry, header_value)

            return self._exists_on_registry(image, access_token)
        if response.status_code == 200:
            return True
        if response.status_code == 404:
            return False
        raise Exception(f"Unexpected status: {response.status_code} for url {request_url}")
