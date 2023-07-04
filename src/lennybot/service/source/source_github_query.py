import re

from ...config import LennyBotSourceConfig
from ...helper import semver_2_vc
from ..github import GitHubService
from .isource import ISource


class GithubQuerySource(ISource):
    def __init__(self, name, config: LennyBotSourceConfig, github: GitHubService) -> None:
        self._name = name
        self._github = github
        self._repository = config.repository
        self._version_regex = config.regex

    @property
    def application(self) -> str:
        return self._name

    def latest_version(self):
        tags = self._github.fetch_tags(self._repository)
        results = []
        for tag in tags:
            tag_name = tag["ref"].replace("refs/tags/", "")
            match = re.fullmatch(self._version_regex, tag_name)
            if match is None:
                continue
            if len(match.groups()) < 1:
                continue
            results.append(match.group(1))
        if len(results) == 0:
            raise Exception("No valid version was found")
        results.sort(key=semver_2_vc)
        return results[-1]
