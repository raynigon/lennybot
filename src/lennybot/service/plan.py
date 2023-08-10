import logging
from typing import List

from lennybot.check import create_check

from ..actions import IAction, create_action
from ..config import LennyBotAppConfig, LennyBotConfig
from ..helper import semver_2_vc
from ..model import LennyBotPlan, LennyBotState
from .github import GitHubService
from .source import create_source


class LennyBotApplication:
    def __init__(self, config: LennyBotAppConfig, global_config: LennyBotConfig, github) -> None:
        self._log = logging.getLogger(self.__class__.__name__)
        self._name = config.name
        self._config = config
        self._global_config = global_config
        self._source = create_source(self._name, config.source, github)
        self._checks = []
        self._action_configs = config.actions
        self._current_version = None
        self._latest_version = None

    @property
    def name(self) -> str:
        return self._name

    def init(self, state: LennyBotState):
        self._current_version = state.current_version(self._name)
        self._latest_version = self._source.latest_version()
        for config in self._config._checks:
            check = create_check(self.name, self._current_version, self._latest_version, config, self._global_config)
            self._checks.append(check)

    def should_update(self) -> bool:
        if self._latest_version is None:
            raise Exception("Application is initialized")
        if self._current_version == self._latest_version:
            return False
        current_vc = semver_2_vc(self._current_version)
        latest_vc = semver_2_vc(self._latest_version)

        if current_vc >= latest_vc:
            return False

        for check in self._checks:
            if not check.check():
                self._log.info("Check '%s' failed for application '%s'", check.__class__.__name__, self.name)
                return False
        return True

    def create_actions(self) -> List[IAction]:
        if self._latest_version is None:
            raise Exception("Application is initialized")
        result = []
        for config in self._action_configs:
            action = create_action(self.name, self._current_version, self._latest_version, config)
            result.append(action)
        return result


class PlanService:
    def __init__(self, github: GitHubService, config: LennyBotConfig) -> None:
        self._log = logging.getLogger(self.__class__.__name__)
        self._github = github
        self._applications: List[LennyBotApplication] = []
        for app_config in config.applications:
            self._applications.append(LennyBotApplication(app_config, config, self._github))

    def plan(self, state: LennyBotState) -> LennyBotPlan:
        actions = []
        for app in self._applications:
            try:
                app.init(state)
                if app.should_update():
                    actions.extend(app.create_actions())
            except Exception as exception:
                self._log.error(f"Exception during action planning for {app.name}")
                raise exception
        return LennyBotPlan(state, actions)
