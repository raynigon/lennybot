import unittest
from unittest.mock import MagicMock, call, patch

from lennybot.config.config import LennyBotConfigContainerConfig, LennyBotSourceConfig
from lennybot.service.source import create_source
from lennybot.service.source.source_docker_registry_query import DockerRegistryQuerySource

# Excerpt of the real tag scheme of wiziopublic.azurecr.io/wiz-app/wiz-broker
WIZ_BROKER_TAGS = [
    "2",
    "2-demo",
    "2.2",
    "2.2-rc",
    "2.2.192458",
    "2.4.311331",
    "2.8.2",
    "3",
    "3.0",
    "3.0-demo",
    "3.0.7",
    "3.0.26",
    "3.0.9",
    "3.0.26-gov",
]


class TestDockerRegistryQuerySource(unittest.TestCase):
    def setUp(self) -> None:
        self.config = LennyBotSourceConfig()
        self.config._type = "docker-registry-query"
        self.config._repository = "wiziopublic.azurecr.io/wiz-app/wiz-broker"
        self.config._regex = "^([0-9]+\\.[0-9]+\\.[0-9]+)$"
        self.container_config = LennyBotConfigContainerConfig()

    def create(self) -> DockerRegistryQuerySource:
        source = create_source("wiz-broker", self.config, None, self.container_config)
        self.assertIsInstance(source, DockerRegistryQuerySource)
        return source  # type: ignore[return-value]

    @patch("lennybot.helper.oci_registry.OciRegistryClient.list_tags")
    def test_latest_fine_grained_version(self, mock_list_tags):
        mock_list_tags.return_value = WIZ_BROKER_TAGS

        self.assertEqual("3.0.26", self.create().latest_version())
        mock_list_tags.assert_called_once_with("wiziopublic.azurecr.io", "wiz-app/wiz-broker")

    @patch("lennybot.helper.oci_registry.OciRegistryClient.list_tags")
    def test_large_build_numbers_are_compared_numerically(self, mock_list_tags):
        mock_list_tags.return_value = ["2.2.192458", "2.4.311331", "2.8.2", "2.10.0"]

        self.assertEqual("2.10.0", self.create().latest_version())

    @patch("lennybot.helper.oci_registry.OciRegistryClient.list_tags")
    def test_capture_group_extracts_version(self, mock_list_tags):
        self.config._regex = "v([0-9]+\\.[0-9]+\\.[0-9]+)"
        mock_list_tags.return_value = ["v1.2.3", "v1.10.0", "latest", "1.99.0"]

        self.assertEqual("1.10.0", self.create().latest_version())

    @patch("lennybot.helper.oci_registry.OciRegistryClient.list_tags")
    def test_no_matching_tag_raises(self, mock_list_tags):
        mock_list_tags.return_value = ["latest", "3.0", "3.0-demo"]

        with self.assertRaises(Exception) as context:
            self.create().latest_version()
        self.assertIn("wiziopublic.azurecr.io/wiz-app/wiz-broker", str(context.exception))

    @patch("lennybot.helper.oci_registry.OciRegistryClient.list_tags")
    def test_regex_without_group_is_ignored(self, mock_list_tags):
        self.config._regex = "[0-9]+\\.[0-9]+\\.[0-9]+"
        mock_list_tags.return_value = ["3.0.26"]

        with self.assertRaises(Exception):
            self.create().latest_version()

    @patch("lennybot.helper.oci_registry.OciRegistryClient.list_tags")
    def test_docker_hub_image(self, mock_list_tags):
        self.config._repository = "nginx"
        self.config._regex = "([0-9]+\\.[0-9]+\\.[0-9]+)"
        mock_list_tags.return_value = ["1.27.0", "1.27.3", "stable"]

        self.assertEqual("1.27.3", self.create().latest_version())
        mock_list_tags.assert_called_once_with("registry-1.docker.io", "library/nginx")


class TestDockerRegistryQuerySourceWithRegistry(unittest.TestCase):
    """End-to-end through the registry client, only the HTTP layer is mocked."""

    def setUp(self) -> None:
        self.config = LennyBotSourceConfig()
        self.config._type = "docker-registry-query"
        self.config._repository = "public-registry.wiz.io/wiz-app/wiz-broker"
        self.config._regex = r"([0-9]+\.[0-9]+\.[0-9]+)"
        self.source = create_source("wiz-broker", self.config, None, LennyBotConfigContainerConfig())

    @patch("lennybot.helper.oci_registry.requests.get")
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
        tags_response.links = {}
        tags_response.json.return_value = {
            "tags": ["3.0.9", "3.0.10", "3.0.11-rc", "not-a-version"],
        }
        mock_get.side_effect = [challenge_response, token_response, tags_response]

        self.assertEqual(self.source.latest_version(), "3.0.10")
        self.assertEqual(mock_get.call_count, 3)
        self.assertEqual(
            mock_get.call_args,
            call(
                "https://public-registry.wiz.io/v2/wiz-app/wiz-broker/tags/list?n=1000",
                headers={"Authorization": "Bearer registry-token"},
                timeout=30,
            ),
        )

    @patch("lennybot.helper.oci_registry.requests.get")
    def test_registry_error_is_reported(self, mock_get):
        response = MagicMock()
        response.status_code = 403
        mock_get.return_value = response

        with self.assertRaisesRegex(Exception, "Unexpected status: 403"):
            self.source.latest_version()
