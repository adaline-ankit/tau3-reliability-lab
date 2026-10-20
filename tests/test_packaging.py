"""Sharing boundaries: reject traversal, credentials, and symlinked sources."""

import tempfile
import unittest
from pathlib import Path

from package_sample import validate_inventory


class PackagingTests(unittest.TestCase):
    def test_rejects_paths_outside_sample(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "path"):
                validate_inventory(Path(tmp), ["../outside.txt"])

    def test_rejects_environment_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".env").write_text("example")
            with self.assertRaisesRegex(ValueError, "excluded"):
                validate_inventory(Path(tmp), [".env"])

    def test_rejects_symlinked_parent_even_when_file_is_regular(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "actual").mkdir()
            (root / "actual/file.md").write_text("public")
            (root / "linked").symlink_to(root / "actual", target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink"):
                validate_inventory(root, ["linked/file.md"])


if __name__ == "__main__":
    unittest.main()
