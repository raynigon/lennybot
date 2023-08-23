import logging
import os
import pickle
import subprocess
from datetime import datetime

from git import GitDB, Repo  # pyright: ignore [reportPrivateImportUsage]

from .actions import *
from .config import LennyBotConfig
from .model import LennyBotState
from .model.plan import LennyBotPlan
from .service import ApplyService, GitHubService, PlanService


class LennyBot:
    def __init__(self, config_path):
        self._config = LennyBotConfig(config_path)
        self._log = logging.getLogger(self.__class__.__name__)
        self._github_service = GitHubService(self._config)
        self._plan_service = PlanService(self._github_service, self._config)
        self._apply_service = ApplyService()
        self._repo = None
        self._branch_name = None

    def plan(self) -> LennyBotPlan:
        self._log.info("Start planning...")
        state = LennyBotState(self._config)
        plan = self._plan_service.plan(state)
        self._log.info(f"Created plan with {len(plan.actions)} actions")
        return plan

    def apply(self, plan: LennyBotPlan):
        self._log.info("Start apply...")
        result = self._apply_service.apply(plan)
        self._log.info(f"Applied {len(plan.actions)} actions")
        return result

    def load_plan(self, filename: str) -> LennyBotPlan:
        self._log.debug(f"Load plan from '{filename}'")
        with open(filename, "rb") as file_ptr:
            return pickle.load(file_ptr)

    def save_plan(self, filename: str, plan: LennyBotPlan):
        self._log.debug(f"Store plan to '{filename}'")
        with open(filename, "wb") as file_ptr:
            pickle.dump(plan, file_ptr)

    def ci_setup(self):
        self._log.debug(f"Setup CI")
        now = datetime.now().strftime("%Y%m%d%H%M%S")
        self._branch_name = f"{self._config.github_pr.branch_prefix}"
        if not self._branch_name.endswith("-"):
            self._branch_name = f"{self._branch_name}-"
        self._branch_name = f"{self._branch_name}{now}"
        self._log.debug(f"Determined branch name {self._branch_name}")
        result = subprocess.call(["git", "config", "--global", "--add", "safe.directory", os.getcwd()])
        if result != 0:
            self._log.error("Unexpected return code from git config")
        self._repo = Repo("./", odbt=GitDB)  # type: ignore
        self._log.debug(f"Initialized repository")
        head = self._repo.create_head(self._branch_name)
        self._log.debug(f"Created Head")
        head.checkout()
        self._log.info(f"Working branch is {self._branch_name}")

    def ci_finalize(self, plan: LennyBotPlan, result):
        self._log.debug(f"Finalize CI")
        if self._repo is None:
            raise Exception("Repository is non, ci_setup was not called")
        if not self._repo.index.diff(None) and not self._repo.untracked_files:
            return
        title = f"Lennybot updated {len(plan.applications)} applications"
        if len(plan.applications) == 1:
            title = f"Lennybot updated {plan.applications[0]}"
        body = "Lennybot updated following applications:\n"
        for app in plan.applications:
            body += f"* Bumps {app} from {plan.source_version(app)} to {plan.target_version(app)}\n"
        body += "\n"
        body += "To resolve any conflict try to run the lennybot again\n"
        # Git Commit and Push
        self._repo.config_writer().set_value("user", "name", "lennybot").release()
        self._repo.config_writer().set_value("user", "email", "lennybot@raynigon.com").release()
        self._repo.git.add(A=True)
        self._repo.git.commit(m=title)
        self._repo.git.push("--set-upstream", "origin", self._branch_name)
        # Create Pull Request
        self._github_service.create_pr(self._branch_name, title, body)
