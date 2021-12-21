from typing import List

from ..model.plan import LennyBotPlan

class ApplyService:

    def __init__(self) -> None:
        pass

    def apply(self, plan: LennyBotPlan):
        state=plan.state
        if not state.is_valid():
            raise Exception("Invalid State")
        for action in plan.actions:
            action.run()
            state.update_version(action.application, action.target_version)
        state.save()