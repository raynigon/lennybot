from lennybot.config.config import LennyBotConfig

from .docker_image_available import DockerImageAvailableCheck
from .icheck import ICheck


def create_check(name, source_version, latest_version, config, global_config: LennyBotConfig) -> ICheck:
    check_type = config.type
    if check_type == "docker-image-available":
        return DockerImageAvailableCheck(name, source_version, latest_version, config, global_config._container)
    raise Exception(f"Unknown Check Type: {check_type}")
