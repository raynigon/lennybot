import unittest

from lennybot.helper import semver_2_vc


class TestSemverToVersionCode(unittest.TestCase):
    def test_components_are_compared_numerically(self):
        self.assertLess(semver_2_vc("2.4.311331"), semver_2_vc("2.8.2"))
        self.assertLess(semver_2_vc("1.9.0"), semver_2_vc("1.10.0"))
        self.assertLess(semver_2_vc("3.0.7"), semver_2_vc("3.0.26"))

    def test_equal_versions(self):
        self.assertEqual(semver_2_vc("1.2.3"), semver_2_vc("1.2.3"))

    def test_none_is_lower_than_any_version(self):
        self.assertLess(semver_2_vc(None), semver_2_vc("0.0.1"))

    def test_sorting(self):
        versions = ["2.2.192458", "3.0.26", "2.8.2", "3.0.7"]
        self.assertEqual(["2.2.192458", "2.8.2", "3.0.7", "3.0.26"], sorted(versions, key=semver_2_vc))
