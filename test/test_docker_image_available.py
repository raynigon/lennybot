# 5 test für :
# 1. nur ein Docker Image Name
# 2. Docker image Name mit Repo
# 3. Remote Registry
# 4. Image pfad mit ungültigem Pfad
# 5.

import unittest
from lennybot.check.docker_image_available import (
    DockerImage,
    DockerImageAvailableCheck
)
from lennybot.config import LennyBotCheckConfig

class TestParseImage(unittest.TestCase):
    def setUp(self) -> None:
        # erstelle lennybotcheckconfig
        self.config = LennyBotCheckConfig()
        

    def test_parse_image_without_tag_separator(self):
        self.config._image_pattern = "missing-colon"
        check = DockerImageAvailableCheck("test-app","0.2.3","stable",self.config)

        self.assertRaises(Exception, check.check)

    def test_given_single_image(self):
        self.config._image_pattern = "nginx:stable"
        check = DockerImageAvailableCheck("test-app","0.2.3","stable",self.config)
        check.check()

    def test_given_image_with_repo(self):
        self.config._image_pattern = "grafana/grafana:{{version}}"
        check = DockerImageAvailableCheck("test-app","9.5.5","9.5.6",self.config)
        check.check()
        
    def test_given_image_with_registry(self):
        self.config._image_pattern = "quay.io/argoproj/argocd:v{{version}}"
        check = DockerImageAvailableCheck("test-app","2.7.6","2.7.7",self.config)
        check.check()

    def test_given_faulty_image_path(self):
        self.config._image_pattern = "qua_y.io/argoproj/argocd:v{{version}}"
        check = DockerImageAvailableCheck("test-app","2.7.6","2.7.7",self.config)
        self.assertRaises(Exception, check.check)
        
    def test_given_toolong_image_path(self):
        self.config._image_pattern = "quay.io/argo/proj/argocd:v{{version}}"
        check = DockerImageAvailableCheck("test-app","2.7.6","2.7.7",self.config)
        self.assertRaises(Exception, check.check)

    def test_given_image_with_authentication(self):
        self.config._image_pattern = "ghcr.io/raynigon/raylevation:v{{version}}"
        check = DockerImageAvailableCheck("test-app","0.0.1","0.0.2",self.config)
        # check.check() # // TODO not implemented yet