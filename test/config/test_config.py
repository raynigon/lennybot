import os
import unittest

from lennybot.config import LennyBotConfig


class TestLennyBotConfig(unittest.TestCase):
    def test_XXX(self):
        os.environ["LB_CONTAINER_REGISTRY_ghcr.io_USERNAME"] = "USERNAME"
        config = LennyBotConfig("test/lennybot.yaml")
        self.assertEqual("USERNAME", config._container.registries["ghcr.io"].username)
