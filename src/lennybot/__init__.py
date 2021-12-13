from .config import LennyBotConfig, LennyBotState
from .actions import *
from .service import PlanService, ApplyService, GitHubService

def main() -> int:
    config = LennyBotConfig("test/config.yaml")
    github_service = GitHubService(config)
    plan_service = PlanService(github_service, config)
    apply_service = ApplyService()
    state = LennyBotState("test/versions.state.yaml")
    actions = plan_service.plan(state)
    result = apply_service.apply(actions, state)
    return 0
