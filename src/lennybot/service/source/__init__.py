from ...config import LennyBotSourceConfig
from .isource import ISource
from .source_github import GithubSource
from .source_github_query import GithubQuerySource


def create_source(name, config: LennyBotSourceConfig, github) -> ISource:
    source_type = config.type
    if source_type == "github":
        return GithubSource(name, config, github)
    if source_type == "github-query":
        return GithubQuerySource(name, config, github)
    raise Exception(f"Unknown Source Type: {source_type}")
