import unittest
from unittest.mock import MagicMock, call, patch

from lennybot.config.config import LennyBotConfigContainerConfig, LennyBotSourceConfig
from lennybot.service.source.source_container_registry import ContainerRegistrySource


class TestContainerRegistrySource(unittest.TestCase):
    def setUp(self) -> None:
        self.config = LennyBotSourceConfig()
        self.config._repository = "public-registry.wiz.io/wiz-app/wiz-broker"
        self.config._regex = r"([0-9]+\.[0-9]+\.[0-9]+)"
        self.source = ContainerRegistrySource("wiz-broker", self.config, LennyBotConfigContainerConfig())

    @patch("lennybot.service.source.source_container_registry.requests.get")
    def test_latest_version_reads_registry_tags_with_bearer_token(self, mock_get):
        challenge_response = MagicMock()
        challenge_response.status_code = 401
        challenge_response.headers = {
            "Www-Authenticate": (
                'Bearer realm="https://public-registry.wiz.io/oauth2/token",'
                'service="public-registry.wiz.io",'
                'scope="repository:wiz-app/wiz-broker:metadata_read"'
            )
        }

        token_response = MagicMock()
        token_response.status_code = 200
        token_response.json.return_value = {"access_token": "registry-token"}

        tags_response = MagicMock()
        tags_response.status_code = 200
        tags_response.json.return_value = {
            "tags": ["3.0.9", "3.0.10", "3.0.11-rc", "not-a-version"],
        }
        mock_get.side_effect = [challenge_response, token_response, tags_response]

        self.assertEqual(self.source.latest_version(), "3.0.10")
        self.assertEqual(mock_get.call_count, 3)
        self.assertEqual(
            mock_get.call_args,
            call(
                "https://public-registry.wiz.io/v2/wiz-app/wiz-broker/tags/list",
                headers={"Authorization": "Bearer registry-token"},
            ),
        )

    @patch("lennybot.service.source.source_container_registry.requests.get")
    def test_registry_error_is_reported(self, mock_get):
        response = MagicMock()
        response.status_code = 403
        response.text = "forbidden"
        mock_get.return_value = response

        with self.assertRaisesRegex(Exception, "Status: 403"):
            self.source.latest_version()

    def test_repository_must_include_registry_and_path(self):
        self.config._repository = "wiz-broker"
        source = ContainerRegistrySource("wiz-broker", self.config, LennyBotConfigContainerConfig())

        with self.assertRaisesRegex(Exception, "must have the format"):
            source.latest_version()


if __name__ == "__main__":
    unittest.main()
