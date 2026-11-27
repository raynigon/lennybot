from ...config import LennyBotSourceConfig
from ...config.config import LennyBotConfigContainerConfig
from .isource import ISource
from .source_docker_registry_query import DockerRegistryQuerySource
from .source_github import GithubSource
from .source_github_query import GithubQuerySource
from .source_nodejs import NodeJSVersionSource


def create_source(
    name, config: LennyBotSourceConfig, github, container_config: LennyBotConfigContainerConfig
) -> ISource:
    source_type = config.type
    if source_type == "github":
        return GithubSource(name, config, github)
    if source_type == "github-query":
        return GithubQuerySource(name, config, github)
    if source_type == "nodejs-version":
        return NodeJSVersionSource(name, config)
    if source_type == "docker-registry-query":
        return DockerRegistryQuerySource(name, config, container_config)
    raise Exception(f"Unknown Source Type: {source_type}")
