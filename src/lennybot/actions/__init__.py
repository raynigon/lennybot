from .download_resources import DownloadResourceAction
from .iaction import IAction
from .remove_checksums import RemoveChecksumsAction
from .update_dockerfile import UpdateDockerfileAction
from .update_image_tag import UpdateImageTagAction
from .update_json import UpdateJsonAction
from .update_yaml import UpdateYamlAction


def create_action(name, source_version, latest_version, config) -> IAction:
    action_type = config.type
    if action_type == "image-tag-update":
        return UpdateImageTagAction(name, source_version, latest_version, config)
    if action_type in ["download-resource", "download-resources"]:
        return DownloadResourceAction(name, source_version, latest_version, config)
    if action_type == "update-json":
        return UpdateJsonAction(name, source_version, latest_version, config)
    if action_type == "update-yaml":
        return UpdateYamlAction(name, source_version, latest_version, config)
    if action_type == "update-dockerfile":
        return UpdateDockerfileAction(name, source_version, latest_version, config)
    if action_type == "remove-checksums":
        return RemoveChecksumsAction(name, source_version, latest_version, config)
    raise Exception(f"Unknown Action Type: {action_type}")
