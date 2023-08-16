import argparse
import logging
import os

from .lennybot import LennyBot


def _version() -> str:
    if "__version__" in locals():
        return locals()["__version__"]
    if "__version__" in globals():
        return globals()["__version__"]
    if os.path.exists("version.txt"):
        with open("version.txt", encoding="utf-8") as file_ptr:
            return file_ptr.read()
    return "-"


def _find_config(args):
    if args.config is not None:
        for item in args.config:
            return item
    if "LB_CONFIG_FILE" in os.environ.keys():
        return os.environ["LB_CONFIG_FILE"]
    if os.path.exists("config.yaml"):
        return "config.yaml"
    if os.path.exists("config.yml"):
        return "config.yml"
    raise Exception(
        "Configuration file not found, create 'config.yaml' or set LB_CONFIG_FILE to point to the config file"
    )


def _arg_parser():
    parser = argparse.ArgumentParser(
        prog="lennybot",
        description="""
            The Lennybot checks for updates, creates a plan to update resources and can also apply this plan.
        """,
    )
    parser.add_argument(
        "action",
        metavar="action",
        type=str,
        nargs="?",
        choices=["ci", "plan", "apply"],
        default="ci",
        help='The action which should be executed. Has to be one of "plan", "apply" or "ci". Default is "ci"',
    )
    parser.add_argument(
        "-p",
        "--plan",
        dest="plan",
        type=str,
        required=False,
        help="The filename of plan which should be saved or loaded",
    )
    parser.add_argument(
        "-c",
        "--config",
        dest="config",
        type=str,
        required=False,
        action="append",
        help="A config value in the format key.subkey=value",
    )
    parser.add_argument("-v", "--version", action="version", version=_version())
    return parser.parse_args()


def main() -> int:
    args = _arg_parser()
    config_file = _find_config(args)
    app = LennyBot(config_file)

    # Execute plan only
    if args.action == "plan":
        plan = app.plan()
        app.save_plan("lennybot.plan", plan)
    # Execute plan and apply
    elif args.action == "apply" and args.plan is None:
        plan = app.plan()
        app.apply(plan)
    # Execute apply with given plan
    elif args.action == "apply" and args.plan is not None:
        plan = app.load_plan(args.plan)
        app.apply(plan)
    elif args.action == "ci":
        app.ci_setup()
        plan = app.plan()
        result = app.apply(plan)
        app.ci_finalize(plan, result)
    else:
        logging.error("Unexpected Arguments", args)
        return 1
    return 0
