from typing import Dict, List

from github.PullRequest import PullRequest

from ..config import LennyBotConfig
import requests
from github import Github

class GitHubService:

    def __init__(self, config: LennyBotConfig):
        self._config = config
        self._token = self._config.github_token
        self._github = None
        if self._token is not None:
            self._github = Github(self._token)

    def fetch_latest_release(self, repository: str) -> Dict:
        url = f"https://api.github.com/repos/{repository}/releases/latest"
        response = requests.get(url, headers=self._headers())
        if response.status_code != 200:
            raise Exception(f"Unable to fetch latest version, Status: {response.status_code}, Content: {response.text}")
        return response.json()

    def fetch_tags(self, repository: str) -> List:
        url = f"https://api.github.com/repos/{repository}/git/refs/tags"
        response = requests.get(url, headers=self._headers())
        if response.status_code != 200:
            raise Exception(f"Unable to fetch latest version, Status: {response.status_code}, Content: {response.text}")
        return response.json()

    def create_pr(self, branch_name, title, body):
        if self._github is None:
            raise Exception("GitHub is not configured")
        repo = self._github.get_repo(self._config.github_pr.repository)
        new_pull = repo.create_pull(title, body, repo.master_branch, branch_name)
        pulls = self._find_own_pulls()
        for pull in pulls:
            if new_pull.id == pull.id:
                continue
            pull.create_comment(f"Superseded by #{new_pull.number}")
            pull.state = "closed"
        

    def _find_own_pulls(self)->List[PullRequest]:
        repo = self._github.get_repo(self._config.github_pr.repository)
        pulls = repo.get_pulls("open")
        result = []
        for pull in pulls:
            if pull.head.ref.startswith(self._config.github_pr.branch_prefix):
                result.append(pull)
        return result

    def _headers(self)->Dict:
        headers = {}
        if self._token is not None:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers