from .lennybot import LennyBot
import os
import sys

def _find_config():
    if "LB_CONFIG_FILE" in os.environ.keys():
        return os.environ["LB_CONFIG_FILE"]
    if os.path.exists("config.yaml"):
        return "config.yaml"
    if os.path.exists("config.yml"):
        return "config.yml"
    raise Exception("Configuration file not found, create 'config.yaml' or set LB_CONFIG_FILE to point to the config file")

def main() -> int:
    config_file = _find_config()
    app = LennyBot(config_file)
    plan = app.plan()
    result = app.apply(plan)
