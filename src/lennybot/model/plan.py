from typing import Any, List

from ..actions.iaction import IAction
from ..model.state import LennyBotState


class LennyBotPlan:
    def __init__(self, state: LennyBotState, actions: List[IAction]) -> None:
        self._state = state
        self._actions = actions

    @property
    def applications(self) -> List[str]:
        result = []
        for action in self._actions:
            result.append(action.application)
        return list(set(result))

    @property
    def actions(self) -> List[IAction]:
        return self._actions

    @property
    def state(self) -> LennyBotState:
        return self._state

    def source_version(self, application: str) -> str | None:
        for action in self._actions:
            if action.application != application:
                continue
            return action.source_version
        return None

    def target_version(self, application: str) -> str | None:
        for action in self._actions:
            if action.application != application:
                continue
            return action.target_version
        return None
