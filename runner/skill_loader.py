from __future__ import annotations

import zipfile
from pathlib import Path

MARKER = ".skill-package-mtime"


def _package_mtime(package: Path) -> float:
    return package.stat().st_mtime


def _needs_extract(package: Path, cache_dir: Path) -> bool:
    skill_md = _skill_root(cache_dir) / "SKILL.md"
    build_script = _skill_root(cache_dir) / "scripts" / "build_cip_report.py"
    marker = cache_dir / MARKER

    if not skill_md.exists() or not build_script.exists():
        return True
    if not marker.exists():
        return True
    try:
        return _package_mtime(package) > float(marker.read_text(encoding="utf-8").strip())
    except ValueError:
        return True


def _skill_root(cache_dir: Path) -> Path:
    """Return the directory containing SKILL.md inside the cache."""
    if (cache_dir / "SKILL.md").exists():
        return cache_dir
    children = [p for p in cache_dir.iterdir() if p.is_dir()]
    if len(children) == 1 and (children[0] / "SKILL.md").exists():
        return children[0]
    for child in children:
        if (child / "SKILL.md").exists():
            return child
    return cache_dir


def ensure_skill_extracted(package: Path, cache_dir: Path) -> Path:
    """
    Extract a packaged .skill file (ZIP) into cache_dir when missing or stale.
    Returns the path to the extracted skill root (directory with SKILL.md).
    """
    if not package.exists():
        raise FileNotFoundError(f"Skill package not found: {package}")

    cache_dir.mkdir(parents=True, exist_ok=True)

    if _needs_extract(package, cache_dir):
        for item in cache_dir.iterdir():
            if item.is_dir():
                _remove_tree(item)
            elif item.name != MARKER:
                item.unlink(missing_ok=True)

        with zipfile.ZipFile(package, "r") as archive:
            archive.extractall(cache_dir)

        (cache_dir / MARKER).write_text(str(_package_mtime(package)), encoding="utf-8")

    skill_root = _skill_root(cache_dir)
    if not (skill_root / "SKILL.md").exists():
        raise FileNotFoundError(
            f"Extracted skill is missing SKILL.md under {cache_dir}. "
            f"Check the layout inside {package.name}."
        )
    return skill_root


def _remove_tree(path: Path) -> None:
    for child in sorted(path.rglob("*"), reverse=True):
        if child.is_file() or child.is_symlink():
            child.unlink(missing_ok=True)
        elif child.is_dir():
            child.rmdir()
    path.rmdir()
