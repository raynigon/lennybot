from ..config.config import LennyBotActionConfig
from .iaction import IAction
import yaml

class UpdateImageTagAction(IAction):

    def __init__(self, name, target_version, config: LennyBotActionConfig) -> None:
        self._name = name
        self._image = config.image
        self._kustomize_path = config.kustomize_path
        self._target_version = target_version
        if config.tag_pattern is not None:
            self._tag_pattern = config.tag_pattern
        else:
            self._tag_pattern = "{{version}}"
            
    @property
    def application(self) -> str:
        return self._name

    @property
    def target_version(self) -> str:
        return self._target_version

    def run(self):
        with open(self._kustomize_path) as file_ptr:
            kustomize = yaml.safe_load(file_ptr)
        found = False
        for image in kustomize["images"]:
            if image["name"] != self._image:
                continue
            image["newTag"] = self._create_new_tag()
            found = True
            break
        if not found:
            raise Exception(f"Unable to find image {self._image}")
        with open(self._kustomize_path, "w") as file_ptr:
            yaml.safe_dump(kustomize, file_ptr, sort_keys=False, indent=4)

    def _create_new_tag(self):
        return self._tag_pattern.replace("{{version}}", self._target_version)
