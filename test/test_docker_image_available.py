import unittest

from lennybot.check.docker_image_available import DockerImageAvailableCheck, WwwAuthenticateHeader
from lennybot.config.config import LennyBotCheckConfig, LennyBotConfigContainerConfig, LennyBotConfigContainerRegistry


class TestParseImage(unittest.TestCase):
    def setUp(self) -> None:
        self.config = LennyBotCheckConfig()
        self.container_config = LennyBotConfigContainerConfig()

    def test_parse_image_without_tag_separator(self):
        self.config._image_pattern = "missing-colon"
        check = DockerImageAvailableCheck("test-app", "0.2.3", "stable", self.config, self.container_config)
        self.assertRaises(Exception, check.check)

    def test_given_single_image(self):
        self.config._image_pattern = "nginx:stable"
        check = DockerImageAvailableCheck("test-app", "0.2.3", "stable", self.config, self.container_config)
        check.check()

    def test_given_image_with_repo(self):
        self.config._image_pattern = "grafana/grafana:{{version}}"
        check = DockerImageAvailableCheck("test-app", "9.5.5", "9.5.6", self.config, self.container_config)
        check.check()

    def test_given_image_with_registry(self):
        self.config._image_pattern = "quay.io/argoproj/argocd:v{{version}}"
        check = DockerImageAvailableCheck("test-app", "2.7.6", "2.7.7", self.config, self.container_config)
        check.check()

    def test_given_faulty_image_path(self):
        self.config._image_pattern = "qua_y.io/argoproj/argocd:v{{version}}"
        check = DockerImageAvailableCheck("test-app", "2.7.6", "2.7.7", self.config, self.container_config)
        self.assertRaises(Exception, check.check)

    def test_given_image_path_with_4_segments(self):
        self.config._image_pattern = "quay.io/argo/proj/argocd:v{{version}}"
        check = DockerImageAvailableCheck("test-app", "2.7.6", "2.7.7", self.config, self.container_config)
        self.assertRaises(Exception, check.check)

    def test_given_toolong_image_path(self):
        self.config._image_pattern = "quay.io/argo/proj/argo/argocd:v{{version}}"
        check = DockerImageAvailableCheck("test-app", "2.7.6", "2.7.7", self.config, self.container_config)
        self.assertRaises(Exception, check.check)


class TestAuthenticateImage(unittest.TestCase):
    def setUp(self) -> None:
        self.config = LennyBotCheckConfig()
        self.container_config = LennyBotConfigContainerConfig()
        self.docker_image_check = DockerImageAvailableCheck("", "", "", self.config, self.container_config)

    def test_authenticate_on_registry_returns_access_token(self):
        registry = LennyBotConfigContainerRegistry("hub.docker.io")
        header_value = WwwAuthenticateHeader(
            "https://docker-auth.elastic.co/auth", "repository:beats/filebeat:pull", "token-service"
        )
        access_token = self.docker_image_check._authenticate_on_registry(registry.name, header_value)
        self.assertIsNotNone(access_token)

    def test_authenticate_without_credentials_in_config(self):
        self.config._image_pattern = "quay.io/argoproj/argocd:v{{version}}"
        header_value = WwwAuthenticateHeader(
            "https://quay.io/v2/auth", "repository:argoproj/argocd:pull", "token-service"
        )
        access_token = self.docker_image_check._authenticate_on_registry("", header_value)
        self.assertIsNotNone(access_token)

    def test_authenticate_on_registry_wrong_credentials(self):
        self.config._image_pattern = "ghcr.io/brose-ebike/postgres-operator:v{{version}}"
        registry = LennyBotConfigContainerRegistry("ghcr.io")
        registry._username = "ABCD"
        registry._password = "1234"
        self.container_config._registries["ghcr.io"] = registry
        header_value = WwwAuthenticateHeader(
            "https://ghcr.io/v2/auth", "repository:brose-ebike/postgres-operator:pull", "token-service"
        )

        with self.assertRaises(Exception) as context:
            access_token = self.docker_image_check._authenticate_on_registry(registry.name, header_value)
            self.assertIsNone(access_token)
        self.assertFalse("Fails due wrong credentials" in str(context.exception))
