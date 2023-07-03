from .docker_image_available import DockerImageAvailableCheck
from .icheck import ICheck


def create_check(name, source_version, latest_version, config) -> ICheck:
    check_type = config.type
    if check_type == "docker-image-available":
        return DockerImageAvailableCheck(
            name,
            source_version,
            latest_version,
            config
            )
    raise Exception(f"Unknown Check Type: {check_type}")
