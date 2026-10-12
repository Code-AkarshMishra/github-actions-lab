from pathlib import Path
import tempfile
import unittest

from scripts.scheduled_check import (
    END_MARKER,
    START_MARKER,
    discover_automation_files,
    replace_inventory,
)


class DiscoverAutomationFilesTests(unittest.TestCase):
    def test_discovers_supported_files_only_from_automation_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / "scripts").mkdir()
            (root / "tests").mkdir()
            (root / "docs").mkdir()
            (root / ".github" / "workflows" / "scheduled.yml").write_text("name: test")
            (root / "scripts" / "check.py").write_text("pass")
            (root / "tests" / "notes.txt").write_text("not inventoried")
            (root / "docs" / "example.py").write_text("outside scope")

            self.assertEqual(
                discover_automation_files(root),
                [".github/workflows/scheduled.yml", "scripts/check.py"],
            )


class ReplaceInventoryTests(unittest.TestCase):
    def test_replaces_only_the_managed_section_in_stable_format(self) -> None:
        readme = f"Before\n{START_MARKER}\nold entry\n{END_MARKER}\nAfter\n"

        updated = replace_inventory(readme, [".github/workflows/check.yml", "scripts/check.py"])

        self.assertTrue(updated.startswith("Before\n"))
        self.assertTrue(updated.endswith("After\n"))
        self.assertIn("- `.github/workflows/check.yml`", updated)
        self.assertIn("- `scripts/check.py`", updated)
        self.assertNotIn("old entry", updated)

    def test_rejects_missing_or_duplicate_markers(self) -> None:
        with self.assertRaisesRegex(ValueError, "exactly one pair"):
            replace_inventory("README without markers", ["scripts/check.py"])

        duplicate = f"{START_MARKER}\n{START_MARKER}\n{END_MARKER}"
        with self.assertRaisesRegex(ValueError, "exactly one pair"):
            replace_inventory(duplicate, ["scripts/check.py"])

    def test_rejects_empty_inventory(self) -> None:
        with self.assertRaisesRegex(ValueError, "refusing an empty inventory"):
            replace_inventory(f"{START_MARKER}\n{END_MARKER}", [])


if __name__ == "__main__":
    unittest.main()
