import yaml
import os

class LennyBotConfig:

    def __init__(self, filename) -> None:
        with open(filename) as fp:
            self._data = yaml.safe_load(fp)
        self._github_token = None
        if "applications" not in self._data.keys():
            raise Exception("Missing Application config")
        if "github" in self._data.keys():
            if "token" in self._data["github"].keys():
                self._github_token = self._data["github"]["token"]
        if "LB_GITHUB_TOKEN" in os.environ.keys():
            self._github_token = os.environ["LB_GITHUB_TOKEN"]

    @property
    def applications(self) -> None:
        return self._data["applications"]

    @property
    def github_token(self) -> None:
        return self._github_token