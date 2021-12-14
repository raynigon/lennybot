from .config import LennyBotConfig, LennyBotState
from .actions import *
from .service import PlanService, ApplyService, GitHubService

class LennyBot:

    def __init__(self, config_path):
        self._config = LennyBotConfig(config_path)
        self._github_service = GitHubService(self._config)
        self._plan_service = PlanService(self._github_service, self._config)
        self._apply_service = ApplyService()

    def plan(self):
        state = LennyBotState(self._config)
        return self._plan_service.plan(state)

    def apply(self, plan):
        state = LennyBotState(self._config)
        return self._apply_service.apply(plan, state)