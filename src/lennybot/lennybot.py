from .model.plan import LennyBotPlan
from .config import LennyBotConfig
from .model import LennyBotState
from .actions import *
from .service import PlanService, ApplyService, GitHubService
import pickle
from git import Repo
from datetime import datetime

class LennyBot:

    def __init__(self, config_path):
        self._config = LennyBotConfig(config_path)
        self._github_service = GitHubService(self._config)
        self._plan_service = PlanService(self._github_service, self._config)
        self._apply_service = ApplyService()
        self._repo = None
        self._branch_name = None

    def plan(self) -> LennyBotPlan:
        state = LennyBotState(self._config)
        return self._plan_service.plan(state)

    def apply(self, plan: LennyBotPlan):
        return self._apply_service.apply(plan)

    def load_plan(self, filename: str) -> LennyBotPlan:
        with open(filename, "rb") as file_ptr:
            return pickle.load(file_ptr)

    def save_plan(self, filename: str, plan: LennyBotPlan):
        with open(filename, "wb") as file_ptr:
            pickle.dump(plan, file_ptr)

    def ci_setup(self):
        now = datetime.now().strftime("%Y%m%d%H%M%S")
        self._branch_name = f"{self._config.github_pr.branch_prefix}"
        if not self._branch_name.endswith("-"):
            self._branch_name = f"{self._branch_name}-"
        self._branch_name = f"{self._branch_name}{now}"
        self._repo = Repo("./")
        head = self._repo.create_head(self._branch_name)
        head.checkout()

    def ci_finalize(self, plan: LennyBotPlan, result):
        if not self._repo.index.diff(None) and not self._repo.untracked_files:
            return
        title = f"Lennybot updated {len(plan.applications)} applications"
        if len(plan.applications) == 1:
            title = f"Lennybot updated {plan.applications[0]}"
        body = "Lennybot updated following applications:\n"
        for app in plan.applications:
            body += f"* Bumps {app} from {plan.source_version(app)} to {plan.target_version(app)}\n"
        body += "\n"
        body += "To resolve any conflict try to run the lennybot again\n"
        # Git Commit and Push
        self._repo.config_writer().set_value("user", "name", "lennybot").release()
        self._repo.config_writer().set_value("user", "email", "lennybot@raynigon.com").release()
        self._repo.git.add(A=True)
        self._repo.git.commit(m=title)
        self._repo.git.push('--set-upstream', 'origin', self._branch_name)
        # Create Pull Request
        self._github_service.create_pr(self._branch_name, title, body)
