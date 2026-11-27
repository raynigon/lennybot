import unittest
from unittest.mock import MagicMock, call, patch

from lennybot.config.config import LennyBotConfigContainerConfig, LennyBotConfigContainerRegistry
from lennybot.helper.oci_registry import OciRegistryClient, OciRegistryException, parse_image_reference

REGISTRY = "example.azurecr.io"
DOCKER_HUB_REGISTRY = "registry-1.docker.io"
TAGS_URL = f"https://{REGISTRY}/v2/team/app/tags/list?n=1000"
CHALLENGE = (
    'Bearer realm="https://example.azurecr.io/oauth2/token",'
    'service="example.azurecr.io",scope="repository:team/app:metadata_read"'
)


def response(status_code, json_data=None, headers=None, links=None):
    mock = MagicMock()
    mock.status_code = status_code
    mock.headers = headers or {}
    mock.json.return_value = json_data
    mock.links = links or {}
    return mock


def challenge_response():
    return response(401, headers={"Www-Authenticate": CHALLENGE})


def token_response(token="secret-token"):
    return response(200, {"access_token": token})


class TestParseImageReference(unittest.TestCase):
    def test_registry_with_nested_repository(self):
        self.assertEqual(
            ("wiziopublic.azurecr.io", "wiz-app/wiz-broker"),
            parse_image_reference("wiziopublic.azurecr.io/wiz-app/wiz-broker"),
        )

    def test_registry_with_port(self):
        self.assertEqual(("localhost:5000", "app"), parse_image_reference("localhost:5000/app"))

    def test_docker_hub_user_repository(self):
        self.assertEqual((DOCKER_HUB_REGISTRY, "grafana/grafana"), parse_image_reference("grafana/grafana"))

    def test_docker_hub_official_image(self):
        self.assertEqual((DOCKER_HUB_REGISTRY, "library/nginx"), parse_image_reference("nginx"))

    def test_docker_hub_alias(self):
        self.assertEqual((DOCKER_HUB_REGISTRY, "library/redis"), parse_image_reference("docker.io/redis"))

    def test_reference_with_tag_is_rejected(self):
        with self.assertRaises(OciRegistryException):
            parse_image_reference("quay.io/argoproj/argocd:v2.7.7")

    def test_reference_with_digest_is_rejected(self):
        with self.assertRaises(OciRegistryException):
            parse_image_reference("quay.io/argoproj/argocd@sha256:abc")


class TestListTags(unittest.TestCase):
    def setUp(self) -> None:
        self.container_config = LennyBotConfigContainerConfig()
        self.client = OciRegistryClient(self.container_config)

    @patch("lennybot.helper.oci_registry.requests.get")
    def test_anonymous_token_and_pagination(self, mock_get):
        mock_get.side_effect = [
            challenge_response(),
            token_response(),
            response(
                200,
                {"name": "team/app", "tags": ["1.0.0", "1.1.0"]},
                links={"next": {"url": "/v2/team/app/tags/list?last=1.1.0&n=1000", "rel": "next"}},
            ),
            response(200, {"name": "team/app", "tags": ["2.0.0"]}),
        ]

        tags = self.client.list_tags(REGISTRY, "team/app")

        self.assertEqual(["1.0.0", "1.1.0", "2.0.0"], tags)
        token_url = mock_get.call_args_list[1].args[0]
        self.assertIn("scope=repository%3Ateam%2Fapp%3Ametadata_read", token_url)
        self.assertIn("service=example.azurecr.io", token_url)
        # second page is requested with the token from the first challenge, no new token exchange
        self.assertEqual(
            call(
                f"https://{REGISTRY}/v2/team/app/tags/list?last=1.1.0&n=1000",
                headers={"Authorization": "Bearer secret-token"},
                timeout=30,
            ),
            mock_get.call_args_list[3],
        )
        self.assertEqual(4, mock_get.call_count)

    @patch("lennybot.helper.oci_registry.requests.get")
    def test_without_authentication(self, mock_get):
        mock_get.return_value = response(200, {"name": "team/app", "tags": ["1.0.0"]})

        self.assertEqual(["1.0.0"], self.client.list_tags(REGISTRY, "team/app"))
        mock_get.assert_called_once_with(TAGS_URL, headers={}, timeout=30)

    @patch("lennybot.helper.oci_registry.requests.get")
    def test_configured_credentials_are_used(self, mock_get):
        registry = LennyBotConfigContainerRegistry(REGISTRY)
        registry._username = "user"
        registry._password = "pass"
        self.container_config._registries[REGISTRY] = registry
        mock_get.side_effect = [
            challenge_response(),
            token_response(),
            response(200, {"name": "team/app", "tags": ["1.0.0"]}),
        ]

        self.client.list_tags(REGISTRY, "team/app")

        self.assertEqual(("user", "pass"), mock_get.call_args_list[1].kwargs["auth"])

    @patch("lennybot.helper.oci_registry.requests.get")
    def test_expired_token_during_pagination_is_renewed(self, mock_get):
        mock_get.side_effect = [
            challenge_response(),
            token_response("first"),
            response(
                200,
                {"tags": ["1.0.0"]},
                links={"next": {"url": "/v2/team/app/tags/list?last=1.0.0&n=1000"}},
            ),
            challenge_response(),
            token_response("second"),
            response(200, {"tags": ["2.0.0"]}),
        ]

        self.assertEqual(["1.0.0", "2.0.0"], self.client.list_tags(REGISTRY, "team/app"))
        self.assertEqual({"Authorization": "Bearer second"}, mock_get.call_args_list[5].kwargs["headers"])

    @patch("lennybot.helper.oci_registry.requests.get")
    def test_second_401_is_not_retried_again(self, mock_get):
        mock_get.side_effect = [challenge_response(), token_response(), challenge_response()]

        with self.assertRaises(OciRegistryException):
            self.client.list_tags(REGISTRY, "team/app")
        self.assertEqual(3, mock_get.call_count)

    @patch("lennybot.helper.oci_registry.requests.get")
    def test_unexpected_status_raises(self, mock_get):
        mock_get.return_value = response(404, {"errors": [{"code": "NAME_UNKNOWN"}]})

        with self.assertRaises(OciRegistryException):
            self.client.list_tags(REGISTRY, "team/app")

    @patch("lennybot.helper.oci_registry.requests.get")
    def test_empty_repository(self, mock_get):
        mock_get.return_value = response(200, {"name": "team/app", "tags": None})

        self.assertEqual([], self.client.list_tags(REGISTRY, "team/app"))

    @patch("lennybot.helper.oci_registry.MAX_TAG_PAGES", 3)
    @patch("lennybot.helper.oci_registry.requests.get")
    def test_endless_pagination_is_stopped(self, mock_get):
        mock_get.return_value = response(
            200, {"tags": ["1.0.0"]}, links={"next": {"url": "/v2/team/app/tags/list?last=1.0.0&n=1000"}}
        )

        with self.assertRaises(OciRegistryException):
            self.client.list_tags(REGISTRY, "team/app")
        self.assertEqual(3, mock_get.call_count)
