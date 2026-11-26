from yamlpath.common import Parsers

from ..config.config import LennyBotActionConfig
from .iaction import IAction


class UpdateImageTagAction(IAction):
    def __init__(self, name, source_version, target_version, config: LennyBotActionConfig) -> None:
        self._name = name
        self._image = config.image
        if config.kustomize_path is None:
            raise Exception("Kustomize Path file is not set for application " + name)
        self._kustomize_path = config.kustomize_path
        self._source_version = source_version
        self._target_version = target_version
        if config.tag_pattern is not None:
            self._tag_pattern = config.tag_pattern
        else:
            self._tag_pattern = "{{version}}"

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
        # Round-trip editor (same as update-yaml) so comments, quotes, block
        # scalars and the document start marker survive the rewrite.
        yaml = Parsers.get_yaml_editor()
        with open(self._kustomize_path, encoding="utf-8") as file_ptr:
            kustomize = yaml.load(file_ptr)
        found = False
        for image in kustomize.get("images") or []:
            if image["name"] != self._image:
                continue
            image["newTag"] = self._create_new_tag()
            found = True
            break
        if not found:
            raise Exception(f"Unable to find image {self._image}")
        with open(self._kustomize_path, "w", encoding="utf-8") as file_ptr:
            yaml.dump(kustomize, file_ptr)

    def _create_new_tag(self):
        return self._tag_pattern.replace("{{version}}", self._target_version)
