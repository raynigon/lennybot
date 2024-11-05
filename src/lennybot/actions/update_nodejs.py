from typing import Optional
import requests
from http import HTTPStatus

from requests.exceptions import HTTPError
from ..config.config import LennyBotActionConfig
from .iaction import IAction

lts_url = "https://www.nodejs.org/dist/index.json"
docker_image = "node"


class UpdateNodeJSAction(IAction):
    def __init__(self, name, source_version, target_version, config: LennyBotActionConfig) -> None:
        self._name = name
        self._source_version = source_version
        self._target_version = target_version
        if config.target_file is None:
            raise Exception("Target file is not set for application " + name)
        self._target_file = config.target_file
        if config.yaml_path is None:
            raise Exception("YAML Path is not set for application " + name)
        self._yaml_path = config.yaml_path
        if config.value_pattern is not None:
            self._value_pattern = config.value_pattern
        else:
            self._value_pattern = "{{version}}"
        self._lts_url = config.lts_url

    def run(self):
        pass


def get_lts_from_url(lts_url) -> Optional[str]:
    headers = {"user-agent": "lennybot/0.0.1"}

    try:
        response = requests.get(lts_url, headers=headers)
        response.raise_for_status()

        if response.status_code == 200:
            data = response.json()
            sorted(data, key=lambda x: x["version"])
            for response in data:
                if response["lts"] != False:
                    return str(response["version"])
    except HTTPError as exception:
        code = exception.response.status_code
        raise
