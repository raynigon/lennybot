from .source_github import GithubSource
from .source_github_query import GithubQuerySource
from .isource import ISource

def create_source(name, config, github) -> ISource:
    source_type = config["type"]
    if source_type == "github":
        return GithubSource(name, config, github)
    elif source_type == "github-query":
        return GithubQuerySource(name, config, github)
    else:
        raise Exception(f"Unknown Source Type: {source_type}")