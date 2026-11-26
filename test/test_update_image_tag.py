import tempfile
import unittest
from pathlib import Path
from test.utils import create_kustomization, read_file, write_file

import yaml

from lennybot.actions.update_image_tag import UpdateImageTagAction
from lennybot.config.config import LennyBotActionConfig

FORMATTED_KUSTOMIZATION = """---
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - resources/install.yaml
patches:
  # Large CRDs exceed client-side annotation size limits
  - target:
      kind: CustomResourceDefinition
    patch: |-
      - op: add
        path: /metadata/annotations/argocd.argoproj.io~1sync-options
        value: ServerSideApply=true
images:
  - name: node
    newName: registry.example.com/node
    newTag: v1.0.0
  - name: other
    newName: registry.example.com/other
    newTag: "1.10"
"""


def _config(image, kustomize_path, tag_pattern=None):
    config = LennyBotActionConfig()
    setattr(config, "_image", image)
    setattr(config, "_kustomize_path", str(kustomize_path))
    setattr(config, "_tag_pattern", tag_pattern)
    return config


class TestUpdateImageTagAction(unittest.TestCase):
    def test_constructor_raises_without_kustomize_path(self):
        config = LennyBotActionConfig()
        setattr(config, "_image", "node")
        setattr(config, "_kustomize_path", None)
        with self.assertRaises(Exception):
            UpdateImageTagAction("app", "1.0", "2.0", config)

    def test_run_updates_new_tag(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            kustomize_file = Path(tmpdir) / "kustomization.yaml"
            create_kustomization(kustomize_file, [{"name": "node", "newTag": "old"}, {"name": "other", "newTag": "x"}])

            config = LennyBotActionConfig()
            setattr(config, "_image", "node")
            setattr(config, "_kustomize_path", str(kustomize_file))
            setattr(config, "_tag_pattern", "v{{version}}")

            action = UpdateImageTagAction("app", "1.0", "3.2.1", config)
            action.run()

            content = yaml.safe_load(read_file(kustomize_file))
            found = [img for img in content["images"] if img["name"] == "node"][0]
            self.assertEqual(found["newTag"], "v3.2.1")

    def test_run_only_changes_new_tag_line(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            kustomize_file = write_file(Path(tmpdir) / "kustomization.yaml", FORMATTED_KUSTOMIZATION)

            action = UpdateImageTagAction("app", "1.0.0", "1.1.0", _config("node", kustomize_file, "v{{version}}"))
            action.run()

            expected = FORMATTED_KUSTOMIZATION.replace("newTag: v1.0.0", "newTag: v1.1.0")
            self.assertEqual(read_file(kustomize_file), expected)

    def test_run_adds_missing_new_tag(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            content = "---\nimages:\n  - name: node\n    newName: registry.example.com/node\n"
            kustomize_file = write_file(Path(tmpdir) / "kustomization.yaml", content)

            action = UpdateImageTagAction("app", "1.0.0", "1.1.0", _config("node", kustomize_file))
            action.run()

            self.assertEqual(read_file(kustomize_file), content + "    newTag: 1.1.0\n")

    def test_run_raises_when_images_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            kustomize_file = write_file(Path(tmpdir) / "kustomization.yaml", "---\nresources:\n  - a.yaml\n")

            action = UpdateImageTagAction("app", "1.0.0", "1.1.0", _config("node", kustomize_file))
            with self.assertRaises(Exception):
                action.run()

    def test_run_raises_when_image_not_found(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            kustomize_file = Path(tmpdir) / "kustomization.yaml"
            create_kustomization(kustomize_file, [{"name": "other", "newTag": "x"}])

            config = LennyBotActionConfig()
            setattr(config, "_image", "node")
            setattr(config, "_kustomize_path", str(kustomize_file))

            action = UpdateImageTagAction("app", "1.0", "3.2.1", config)
            with self.assertRaises(Exception):
                action.run()
