from .model.plan import LennyBotPlan
from .config import LennyBotConfig
from .model import LennyBotState
from .actions import *
from .service import PlanService, ApplyService, GitHubService
import pickle

from lennybot import config


class LennyBot:

    def __init__(self, config_path):
        self._config = LennyBotConfig(config_path)
        self._github_service = GitHubService(self._config)
        self._plan_service = PlanService(self._github_service, self._config)
        self._apply_service = ApplyService()

    def plan(self) -> LennyBotPlan:
        state = LennyBotState(self._config)
        return self._plan_service.plan(state)

    def apply(self, plan: LennyBotPlan):
        return self._apply_service.apply(plan)

    def load_plan(self, filename: str) -> LennyBotPlan:
        with open(filename, "rb") as file_ptr:
            return pickle.load(file_ptr)

    def save_plan(self, filename: str, plan: LennyBotPlan):
        with open(filename, "wb") as file_ptr:
            pickle.dump(plan, file_ptr)

    def ci_finalize(self, plan, result):
        # TODO
        # Create new Pull request and close old pull request
        pr = self._github_service.find_latest_pr()
