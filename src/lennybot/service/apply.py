from typing import List
from ..config import LennyBotState
from ..actions import IAction

class ApplyService:

    def __init__(self) -> None:
        pass

    def apply(self, actions: List[IAction], state: LennyBotState):
        for action in actions:
            action.run()
            state.update_version(action.application, action.target_version)
        state.save()