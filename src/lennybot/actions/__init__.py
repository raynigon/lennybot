from .download_resources import DownloadResourcesAction
from .update_image_tag import UpdateImageTagAction
from .update_yaml import UpdateYamlAction
from .iaction import IAction

def create_action(name, latest_version, config):
    source_type = config.type
    if source_type == "image-tag-update":
        return UpdateImageTagAction(name, latest_version, config)
    elif source_type == "download-resources":
        return DownloadResourcesAction(name, latest_version, config)
    elif source_type == "update-yaml":
        return UpdateYamlAction(name, latest_version, config)
    else:
        raise Exception(f"Unknown Source Type: {source_type}")