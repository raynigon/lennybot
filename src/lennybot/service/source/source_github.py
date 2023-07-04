import re

import requests

from ...config import LennyBotSourceConfig
from ..github import GitHubService
from .isource import ISource


class GithubSource(ISource):
    def __init__(self, name, config: LennyBotSourceConfig, github: GitHubService) -> None:
        self._name = name
        self._github = github
        self._repository = config.repository
        self._version_regex = config.regex

    @property
    def application(self) -> str:
        return self._name

    def latest_version(self):
        release = self._github.fetch_latest_release(self._repository)
        # TODO check if tag_name property exists
        tag_name = release["tag_name"]
        match = re.fullmatch(self._version_regex, tag_name)
        # TODO check if matched
        if match is None:
            raise Exception(f"Version pattern does not match, Pattern: {self._version_regex}, Tag: {tag_name}")
        if len(match.groups()) < 1:
            raise Exception(f"Missing Group in regex pattern, Pattern: {self._version_regex}, Tag: {tag_name}")
        return match.group(1)
