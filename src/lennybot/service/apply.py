import logging
from typing import List

from ..model.plan import LennyBotPlan


class ApplyService:
    def __init__(self) -> None:
        self._log = logging.getLogger(self.__class__.__name__)

    def apply(self, plan: LennyBotPlan):
        state = plan.state
        if not state.is_valid():
            raise Exception("Invalid State")
        for action in plan.actions:
            try:
                action.run()
                state.update_version(action.application, action.target_version)
            except Exception as exception:
                self._log.error(f"Exception during action execution for {action.application}")
                raise exception
        state.save()
