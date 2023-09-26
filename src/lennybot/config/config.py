import logging
import os
from typing import Any, Dict, List, Optional

import yaml

CONFIGURATION_OPTIONS = {
    "github": {
        "type": "object",
        "properties": {
            "token": {"type": "string", "required": True, "attribute": "_github_token"},
            "pr": {
                "type": "object",
                "attribute": "_github_pr",
                "properties": {
                    "enabled": {"type": "bool", "attribute": "_enabled"},
                    "repository": {"type": "bool", "attribute": "_repository"},
                    "branchPrefix": {"type": "bool", "attribute": "_branch_prefix"},
                },
            },
        },
    },
    "state": {
        "type": "object",
        "properties": {"file": {"type": "string", "required": True, "attribute": "_state_file"}},
    },
    "logging": {
        "type": "object",
        "properties": {"level": {"type": "string", "required": False, "attribute": "_logging_level"}},
    },
    "container": {
        "type": "object",
        "attribute": "_container",
        "properties": {
            "registries": {
                "type": "map",
                "required": False,
                "attribute": "_registries",
                "value_class": "LennyBotConfigContainerRegistry",
                "properties": {
                    "username": {"type": "string", "attribute": "_username"},
                    "password": {"type": "string", "attribute": "_password"},
                },
            }
        },
    },
    "applications": {
        "type": "list",
        "required": True,
        "class": "LennyBotAppConfig",
        "attribute": "_applications",
        "properties": {
            "name": {"type": "string", "required": True, "attribute": "_name"},
            "source": {
                "type": "object",
                "attribute": "_source",
                "properties": {
                    "type": {"type": "string", "required": True, "attribute": "_type"},
                    "repository": {"type": "string", "required": True, "attribute": "_repository"},
                    "regex": {"type": "string", "attribute": "_regex"},
                },
            },
            "checks": {
                "type": "list",
                "class": "LennyBotCheckConfig",
                "attribute": "_checks",
                "properties": {
                    "type": {"type": "string", "attribute": "_type"},
                    "imagePattern": {"type": "string", "attribute": "_image_pattern"},
                },
            },
            "actions": {
                "type": "list",
                "class": "LennyBotActionConfig",
                "attribute": "_actions",
                "properties": {
                    "type": {"type": "string", "attribute": "_type"},
                    "image": {"type": "string", "attribute": "_image"},
                    "kustomizePath": {"type": "string", "attribute": "_kustomize_path"},
                    "tagPattern": {"type": "string", "attribute": "_tag_pattern"},
                    "url": {"type": "string", "attribute": "_url"},
                    "target": {"type": "string", "attribute": "_target"},
                    "targetFile": {"type": "string", "attribute": "_target_file"},
                    "yamlPath": {"type": "string", "attribute": "_yaml_path"},
                    "valuePattern": {"type": "string", "attribute": "_value_pattern"},
                },
            },
        },
    },
}


class LennyBotSourceConfig:
    def __init__(self) -> None:
        self._type = None
        self._repository = None
        self._regex = None

    @property
    def type(self) -> str:
        return str(self._type)

    @property
    def repository(self) -> str:
        return str(self._repository)

    @property
    def regex(self) -> str:
        return str(self._regex)


class LennyBotCheckConfig:
    def __init__(self) -> None:
        self._type = None
        self._image_pattern: Optional[str] = None

    @property
    def type(self) -> str:
        return str(self._type)

    @property
    def image_pattern(self) -> str:
        return str(self._image_pattern)


class LennyBotActionConfig:
    def __init__(self) -> None:
        self._type = None
        self._image = None
        self._kustomize_path = None
        self._tag_pattern = None
        self._target = None
        self._url = None
        self._target_file = None
        self._yaml_path = None
        self._value_pattern = None

    @property
    def type(self) -> str:
        return str(self._type)

    @property
    def image(self) -> str | None:
        return self._image

    @property
    def kustomize_path(self) -> str | None:
        return self._kustomize_path

    @property
    def tag_pattern(self) -> str | None:
        return self._tag_pattern

    @property
    def target(self) -> str | None:
        return self._target

    @property
    def url(self) -> str | None:
        return self._url

    @property
    def target_file(self) -> str | None:
        return self._target_file

    @property
    def yaml_path(self) -> str | None:
        return self._yaml_path

    @property
    def value_pattern(self) -> str | None:
        return self._value_pattern


class LennyBotAppConfig:
    def __init__(self) -> None:
        self._name = None
        self._source = LennyBotSourceConfig()
        self._checks = []
        self._actions = []

    @property
    def name(self) -> str:
        return str(self._name)

    @property
    def source(self) -> LennyBotSourceConfig:
        return self._source

    @property
    def actions(self) -> List[LennyBotActionConfig]:
        return self._actions


class LennyBotGithubPr:
    def __init__(self) -> None:
        self._enabled = False
        self._repository = None
        self._branch_prefix = "lennybot-"

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def repository(self) -> str:
        return str(self._repository)

    @property
    def branch_prefix(self) -> str:
        return str(self._branch_prefix)


class LennyBotConfigContainerRegistry:
    def __init__(self, name) -> None:
        self._name = name
        self._username: Optional[str] = None
        self._password: Optional[str] = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def username(self) -> str:
        return str(self._username)

    @property
    def password(self) -> str:
        return str(self._password)


class LennyBotConfigContainerConfig:
    def __init__(self) -> None:
        self._registries = {}

    @property
    def registries(self) -> Dict[str, LennyBotConfigContainerRegistry]:
        return self._registries


class LennyBotConfig:
    def __init__(self, filename) -> None:
        self._log = None
        with open(filename, encoding="utf-8") as file_ptr:
            self._data = yaml.safe_load(file_ptr)
        self._state_file = None
        self._github_token = None
        self._github_pr = LennyBotGithubPr()
        self._logging_level = "INFO"
        self._container = LennyBotConfigContainerConfig()
        self._applications = []
        self._parse()
        self._configure_logging()

    def _parse(self):
        self._parse_data(CONFIGURATION_OPTIONS, self._data, self)
        self._parse_env()

    def _configure_logging(self):
        logging_level = logging._nameToLevel.get(self._logging_level, logging.DEBUG)
        logging.basicConfig(level=logging_level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        self._log = logging.getLogger(self.__class__.__name__)
        self._log.debug("Logging was configured")

    def _parse_data(self, schema, data, target):
        for name, property in schema.items():
            if name not in data.keys():
                continue
            config_type = property["type"]
            if config_type in ["object", "list", "map"]:
                self._parse_nested_data(name, property, data, target)
                continue
            attribute_name = property["attribute"]
            property_value = data[name]
            if config_type == "string":
                property_value = str(property_value)
            setattr(target, attribute_name, property_value)

    def _parse_nested_data(self, name, property, data, target):
        attribute_name = None
        config_type = property["type"]
        if "attribute" in property:
            attribute_name = property["attribute"]
            for item in attribute_name.split("."):
                if attribute_name.endswith(item):
                    continue
                target = getattr(target, item)
        if config_type == "object":
            if "attribute" in property:
                target = getattr(target, property["attribute"].split(".")[-1])
            self._parse_data(property["properties"], data[name], target)
            return
        if config_type == "list":
            if attribute_name is None:
                raise Exception("Attribute name was not set, but is needed for config_type list")
            attribute_name = attribute_name.split(".")[-1]
            for item in data[name]:
                array_target = globals()[property["class"]]()
                self._parse_data(property["properties"], item, array_target)
                getattr(target, attribute_name).append(array_target)
            return
        if config_type == "map":
            if "attribute" in property:
                target = getattr(target, property["attribute"].split(".")[-1])
            for key in data[name].keys():
                map_target = globals()[property["value_class"]](key)
                self._parse_data(property["properties"], data[name][key], map_target)
                target[key] = map_target
            return

    def _parse_env(self):
        if "LB_GITHUB_TOKEN" in os.environ.keys():
            self._github_token = os.environ["LB_GITHUB_TOKEN"]
        if "LB_STATE_FILE" in os.environ.keys():
            self._state_file = os.environ["LB_STATE_FILE"]
        for key in os.environ.keys():
            if not key.startswith("LB_CONTAINER_REGISTRY_"):
                continue
            parts = key.removeprefix("LB_CONTAINER_REGISTRY_").split("_")
            registry = parts[0]
            suffix = parts[1]
            registry_data = None
            for name, data in self._container._registries.items():
                if name.lower() == registry.lower():
                    registry_data = data
                    break
            if registry_data is None:
                raise Exception(f"Registry {registry} was not found in configuration")
            if suffix == "USERNAME":
                registry_data._username = os.environ[key]
            elif suffix == "PASSWORD":
                registry_data._password = os.environ[key]
            else:
                raise Exception(f"Unknown suffix: {suffix}")
        # TODO make this generic

    @property
    def state_file(self) -> str:
        return str(self._state_file)

    @property
    def applications(self) -> List[LennyBotAppConfig]:
        return self._applications

    @property
    def github_token(self) -> str | None:
        return self._github_token

    @property
    def github_pr(self) -> LennyBotGithubPr:
        return self._github_pr
