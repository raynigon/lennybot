from typing import List
from .source import create_source
from ..actions import IAction, create_action
from ..config import LennyBotConfig, LennyBotState, LennyBotAppConfig
from ..helper import semver_2_vc
from .github import GitHubService

class PlanService:

    def __init__(self, github: GitHubService, config: LennyBotConfig) -> None:
        self._github = github
        self._applications = []
        for app_config in config.applications:
            self._applications.append(LennyBotApplication(app_config, self._github))

    def plan(self, state: LennyBotState):
        actions = []
        for app in self._applications:
            state_version = state.current_version(app.name)
            latest_version = app.latest_version()
            if state_version is not None and not self._should_update(state_version, latest_version):
                continue
            actions.extend(app.create_actions())
        return actions
    
    def _should_update(self, state_version, latest_version):
        if state_version == latest_version:
            return False
        state_vc = semver_2_vc(state_version)
        latest_vc = semver_2_vc(latest_version)
        if latest_vc <= state_vc:
            return False
        return True

class LennyBotApplication:

    def __init__(self, config: LennyBotAppConfig, github) -> None:
        self._name = config.name
        self._source = create_source(self._name, config.source, github)
        self._action_configs = config.actions
        self._latest_version = None

    @property
    def name(self) -> str:
        return self._name

    def latest_version(self) -> str:
        if self._latest_version is None:
            self._latest_version = self._source.latest_version()
        return self._latest_version

    def create_actions(self) -> List[IAction]:
        result = []
        for config in self._action_configs:
            result.append(create_action(self.name, self.latest_version(), config))
        return result

