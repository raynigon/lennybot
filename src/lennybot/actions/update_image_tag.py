from .iaction import IAction
import yaml

class UpdateImageTagAction(IAction):

    def __init__(self, name, target_version, config) -> None:
        self._name = name
        self._image = config["image"]
        self._kustomize_path = config["kustomizePath"]
        self._target_version = target_version
        self._tag_pattern = "{{version}}"
        if "tagPattern" in config.keys():
            self._tag_pattern = config["tagPattern"]

    @property
    def application(self) -> str:
        return self._name

    @property
    def target_version(self) -> str:
        return self._target_version

    def run(self):
        with open(self._kustomize_path) as fp:
            kustomize = yaml.safe_load(fp)
        found = False
        for image in kustomize["images"]:
            if image["name"] != self._image:
                continue
            image["newTag"] = self._create_new_tag()
            found = True
            break
        if not found:
            raise Exception(f"Unable to find image {self._image}")
        with open(self._kustomize_path, "w") as fp:
            yaml.safe_dump(kustomize, fp, sort_keys=False, indent=4)

    def _create_new_tag(self):
        return self._tag_pattern.replace("{{version}}", self._target_version)
