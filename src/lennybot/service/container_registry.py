import logging
from typing import Optional
from urllib.parse import urlencode

import requests

from ..config.config import LennyBotConfigContainerConfig


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


def authenticate_on_registry(
    registry: str,
    authentication_header: WwwAuthenticateHeader,
    container_config: LennyBotConfigContainerConfig,
) -> str:
    params = {
        "scope": authentication_header.scope,
        "grant_type": "password",
        "service": authentication_header.service,
        "client_id": "lennybot",
        "access_type": "offline",
    }

    url = f"{authentication_header.realm}?{urlencode(params)}"

    if registry in container_config.registries.keys():
        registry_data = container_config.registries[registry]
        username = registry_data.username
        password = registry_data.password
        if "<REDACTED>" in [username, password]:
            logging.warning("Either username or password contain '<REDACTED>' and probably have not been overwritten")
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
        logging.error(
            "Authentication failed: %d with %s",
            response.status_code,
            response.headers,
        )
        raise Exception("Error occurred: Unauthenticated: ", response.status_code)

    if response.status_code == 403:
        logging.error(
            "Authorization failed: %d with %s",
            response.status_code,
            response.headers,
        )
        raise Exception("Error occurred: Unauthorization: ", response.status_code)

    if response.status_code == 404:
        logging.error("Nothing Found:  %d with %s", response.status_code, response.headers)
        raise Exception("Error occurred: Nothing Found: ", response.status_code)

    raise Exception("Unexpected Status Code", response.status_code)


def get_registry_token(
    registry: str,
    response,
    container_config: LennyBotConfigContainerConfig,
) -> Optional[str]:
    if response.status_code != 401:
        return None
    authentication_header = WwwAuthenticateHeader.parse(response)
    return authenticate_on_registry(registry, authentication_header, container_config)
