import logging
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlencode, urljoin

import requests

from ..config.config import LennyBotConfigContainerConfig

DOCKER_HUB_REGISTRY = "registry-1.docker.io"
DOCKER_HUB_ALIASES = ["docker.io", "index.docker.io", DOCKER_HUB_REGISTRY]

# Page size requested from /v2/<name>/tags/list, registries may return fewer per page
TAGS_PAGE_SIZE = 1000
# Upper bound for pagination, protects against registries which never stop returning a next link
MAX_TAG_PAGES = 100
REQUEST_TIMEOUT_SECONDS = 30


class OciRegistryException(Exception):
    pass


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


def parse_image_reference(reference: str) -> Tuple[str, str]:
    """
    Splits an image reference without tag (e.g. "quay.io/argoproj/argocd") into registry and repository name.
    References without a registry host (e.g. "grafana/grafana" or "nginx") resolve to Docker Hub.
    """
    last_segment = reference.split("/")[-1]
    if ":" in last_segment or "@" in reference:
        raise OciRegistryException(f"Image reference must not contain a tag or digest: {reference}")

    parts = reference.split("/", 1)
    has_registry = len(parts) == 2 and ("." in parts[0] or ":" in parts[0] or parts[0] == "localhost")
    if has_registry and parts[0] not in DOCKER_HUB_ALIASES:
        return parts[0], parts[1]

    name = parts[1] if has_registry else reference
    if "/" not in name:
        name = f"library/{name}"
    return DOCKER_HUB_REGISTRY, name


class OciRegistryClient:
    """
    Minimal client for the OCI distribution API (/v2/...).
    Handles the Bearer token challenge (WWW-Authenticate) and uses the credentials
    from the container registries configuration if the registry is configured there.
    """

    def __init__(self, container_config: LennyBotConfigContainerConfig) -> None:
        self._log = logging.getLogger(self.__class__.__name__)
        self._container_config = container_config

    def authenticate(self, registry: str, authentication_header: WwwAuthenticateHeader) -> str:
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
                self._log.warning(
                    "Either username or password contain '<REDACTED>' and probably have not been overwritten"
                )
            response = requests.get(url, auth=(username, password), timeout=REQUEST_TIMEOUT_SECONDS)
        else:
            self._log.debug("Registry not found in config")
            response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)

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
            self._log.error(
                "Authentication failed: %d with %s",
                response.status_code,
                response.headers,
            )
            raise Exception("Error occurred: Unauthenticated: ", response.status_code)

        if response.status_code == 403:
            self._log.error(
                "Authorization failed: %d with %s",
                response.status_code,
                response.headers,
            )
            raise Exception("Error occurred: Unauthorization: ", response.status_code)

        if response.status_code == 404:
            self._log.error("Nothing Found:  %d with %s", response.status_code, response.headers)
            raise Exception("Error occurred: Nothing Found: ", response.status_code)

        raise Exception("Unexpected Status Code", response.status_code)

    def get(self, registry: str, url: str, headers: Optional[Dict[str, str]] = None) -> requests.Response:
        """
        Sends a GET request to the registry, authenticates once if the registry answers with a 401 challenge.
        """
        response, _ = self._get(registry, url, headers, None)
        return response

    def list_tags(self, registry: str, name: str) -> List[str]:
        """
        Returns all tags of the repository, following the pagination "Link" header of the registry.
        """
        url = f"https://{registry}/v2/{name}/tags/list?n={TAGS_PAGE_SIZE}"
        tags: List[str] = []
        access_token = None
        for _ in range(MAX_TAG_PAGES):
            response, access_token = self._get(registry, url, None, access_token)
            if response.status_code != 200:
                raise OciRegistryException(f"Unexpected status: {response.status_code} for url {url}")
            tags.extend(response.json().get("tags") or [])
            next_link = response.links.get("next", {}).get("url")
            if not next_link:
                self._log.debug("Found %d tags for %s/%s", len(tags), registry, name)
                return tags
            url = urljoin(url, next_link)
        raise OciRegistryException(f"Tag list of {registry}/{name} has more than {MAX_TAG_PAGES} pages")

    def _get(
        self,
        registry: str,
        url: str,
        headers: Optional[Dict[str, str]],
        access_token: Optional[str],
        allow_authentication: bool = True,
    ) -> Tuple[requests.Response, Optional[str]]:
        request_headers = dict(headers or {})
        if access_token is not None:
            request_headers["Authorization"] = f"Bearer {access_token}"
        response = requests.get(url, headers=request_headers, timeout=REQUEST_TIMEOUT_SECONDS)

        # A 401 means either no token was sent yet or the token expired (e.g. during pagination)
        if response.status_code == 401 and allow_authentication:
            challenge = WwwAuthenticateHeader.parse(response)
            access_token = self.authenticate(registry, challenge)
            return self._get(registry, url, headers, access_token, allow_authentication=False)
        return response, access_token
