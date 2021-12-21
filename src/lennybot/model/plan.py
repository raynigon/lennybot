

from typing import Any, List

from lennybot.model.state import LennyBotState


class LennyBotPlan:

    def __init__(self, state: LennyBotState, actions: List[Any]) -> None:
        self._state = state
        self._actions = actions

    @property
    def actions(self)->List[Any]:
        return self._actions

    @property
    def state(self)->LennyBotState:
        return self._state