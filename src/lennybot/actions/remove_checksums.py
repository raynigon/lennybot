import yaml

from ..config.config import LennyBotActionConfig
from .iaction import IAction


class RemoveChecksumsAction(IAction):
    def __init__(self, name, source_version, target_version, config: LennyBotActionConfig) -> None:
        self._name = name
        self._source_version = source_version
        self._target_version = target_version
        if config.target is None:
            raise Exception("Target Path is not set for application " + name)
        self._target_file = config.target

    @property
    def application(self) -> str:
        return self._name

    @property
    def source_version(self) -> str:
        return self._source_version

    @property
    def target_version(self) -> str:
        return self._target_version

    def run(self):
        with open(self._target_file, encoding="utf-8") as file_ptr:
            docs = list(yaml.safe_load_all(file_ptr))

        for doc in docs:
            if doc["kind"] == "Deployment":
                self._update_deployment(doc)
            elif doc["kind"] == "Job":
                self._update_job(doc)

        with open(self._target_file, "w", encoding="utf-8") as file_ptr:
            docs = yaml.safe_dump_all(docs, file_ptr)

    def _update_deployment(self, doc):
        containers = doc["spec"]["template"]["spec"]["containers"]
        for container in containers:
            image = container["image"]
            if "@" not in image:
                continue
            container["image"] = image.split("@")[0]

    def _update_job(self, doc):
        containers = doc["spec"]["template"]["spec"]["containers"]
        for container in containers:
            image = container["image"]
            if "@" not in image:
                continue
            container["image"] = image.split("@")[0]
