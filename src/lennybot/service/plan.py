from typing import List
from .source import create_source
from ..actions import IAction, create_action
from ..config import LennyBotConfig, LennyBotAppConfig
from ..model import LennyBotState, LennyBotPlan
from ..helper import semver_2_vc
from .github import GitHubService

class LennyBotApplication:

    def __init__(self, config: LennyBotAppConfig, github) -> None:
        self._name = config.name
        self._source = create_source(self._name, config.source, github)
        self._action_configs = config.actions
        self._current_version = None
        self._latest_version = None

    @property
    def name(self) -> str:
        return self._name

    def init(self, state: LennyBotState):
        self._current_version = state.current_version(self._name)
        self._latest_version = self._source.latest_version()

    def should_update(self) -> bool:
        if self._latest_version is None:
            raise Exception("Application is initialized")
        if self._current_version == self._latest_version:
            return False
        current_vc = semver_2_vc(self._current_version)
        latest_vc = semver_2_vc(self._latest_version)
        return latest_vc > current_vc

    def create_actions(self) -> List[IAction]:
        if self._latest_version is None:
            raise Exception("Application is initialized")
        result = []
        for config in self._action_configs:
            action = create_action(
                self.name, self._current_version, self._latest_version, config)
            result.append(action)
        return result

class PlanService:

    def __init__(self, github: GitHubService, config: LennyBotConfig) -> None:
        self._github = github
        self._applications:List[LennyBotApplication] = []
        for app_config in config.applications:
            self._applications.append(
                LennyBotApplication(app_config, self._github))

    def plan(self, state: LennyBotState) -> LennyBotPlan:
        actions = []
        for app in self._applications:
            app.init(state)
            if app.should_update():
                actions.extend(app.create_actions())
        return LennyBotPlan(state, actions)


