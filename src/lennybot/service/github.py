from typing import Dict, List
from ..config import LennyBotConfig
import requests

class GitHubService:

    def __init__(self, config: LennyBotConfig):
        self._token = config.github_token

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

    def _headers(self)->Dict:
        headers = {}
        if self._token is not None:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers