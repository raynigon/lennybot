from .update_dockerfile import UpdateDockerfileAction
from .download_resources import DownloadResourcesAction
from .update_image_tag import UpdateImageTagAction
from .update_yaml import UpdateYamlAction
from .remove_checksums import RemoveChecksumsAction
from .check_image_exists import CheckImagesExistsAction
from .iaction import IAction


def create_action(name, source_version, latest_version, config) -> IAction:
    source_type = config.type
    if source_type == "image-tag-update":
        return UpdateImageTagAction(name, source_version, latest_version, config)
    if source_type == "download-resources":
        return DownloadResourcesAction(name, source_version, latest_version, config)
    if source_type == "update-yaml":
        return UpdateYamlAction(name, source_version, latest_version, config)
    if source_type == "update-dockerfile":
        return UpdateDockerfileAction(name, source_version, latest_version, config)
    if source_type == "remove-checksums":
        return RemoveChecksumsAction(name, source_version, latest_version, config)
    if source_type == "check-image-exists":
        return CheckImagesExistsAction(name, source_version, latest_version, config)
    raise Exception(f"Unknown Source Type: {source_type}")