import unittest

from lennybot.config.config import LennyBotSourceConfig
from lennybot.service.source.source_nodejs import NodeJSVersionSource


class TestParseImage(unittest.TestCase):

    def setUp(self) -> None:
        self.config = LennyBotSourceConfig()

    def test_lts_only_false(self):
        # get latest version from nodejs.org/dist/index.json
        # without ^v
        # min greater than 23.0.0
        self.config.lts_only = False

        release = NodeJSVersionSource("test-node-version", self.config)
        version = release.latest_version()

        assert not version.startswith("v") and version > "23.0.0"

    def test_lts_only_true(self):
        # get latest
        self.config.lts_only = False
        latest_release = NodeJSVersionSource("test-node-version", self.config)

        # get lts version
        self.config.lts_only = True
        lts_release = NodeJSVersionSource("test-node-version", self.config)

        # assert latest > lts for assertion to be true
        assert latest_release.latest_version() > lts_release.latest_version()
