from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from runner.skill_loader import MARKER, ensure_skill_extracted


def make_skill_package(path: Path, *, nested: bool = False, body: str = "v1") -> None:
    prefix = "skill/" if nested else ""
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(f"{prefix}SKILL.md", body)
        archive.writestr(f"{prefix}scripts/build_cip_report.py", "print('ok')")


class SkillLoaderTests(unittest.TestCase):
    def test_extracts_flat_package_and_reuses_cache(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            package = root / "test.skill"
            cache = root / "cache"
            make_skill_package(package)

            skill_root = ensure_skill_extracted(package, cache)
            extra = cache / "preserved.txt"
            extra.write_text("cache was reused", encoding="utf-8")
            second_root = ensure_skill_extracted(package, cache)

            self.assertEqual(skill_root, cache)
            self.assertEqual(second_root, cache)
            self.assertTrue((cache / MARKER).exists())
            self.assertTrue(extra.exists())

    def test_finds_skill_root_inside_single_top_level_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            package = root / "nested.skill"
            cache = root / "cache"
            make_skill_package(package, nested=True)

            skill_root = ensure_skill_extracted(package, cache)

            self.assertEqual(skill_root, cache / "skill")
            self.assertTrue((skill_root / "scripts" / "build_cip_report.py").exists())

    def test_missing_package_raises_clear_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            with self.assertRaisesRegex(FileNotFoundError, "Skill package not found"):
                ensure_skill_extracted(root / "missing.skill", root / "cache")


if __name__ == "__main__":
    unittest.main()
