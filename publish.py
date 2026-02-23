from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

DEFAULT_PATTERNS = [
    "**/docs/**/*.md",
    "**/data/sample*",
    "**/data/**/*.sample.*",
]

DEFAULT_EXCLUDES = [
    ".git/**",
    "**/.venv/**",
    "**/__pycache__/**",
    "**/node_modules/**",
]

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)
HOST_PORT_RE = re.compile(r"\b[a-z0-9][a-z0-9.-]*:\d{2,5}\b", re.IGNORECASE)
UUID_RE = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b", re.IGNORECASE)
TENANT_RE = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.IGNORECASE)

REPLACERS = [
    (EMAIL_RE, "redacted@example.com"),
    (URL_RE, "https://redacted.example"),
    (HOST_PORT_RE, "redacted-host:0000"),
    (UUID_RE, "00000000-0000-0000-0000-000000000000"),
    (TENANT_RE, "00000000-0000-0000-0000-000000000000"),
]

SENSITIVE_TO_SAMPLE = {
    "project.json": "project.sample.json",
    "project.yml": "project.sample.yml",
    "project.yaml": "project.sample.yaml",
    "app_model.json": "app_model.sample.json",
}

SAMPLE_JSON = {
    "project.sample.json": {
        "id": "00000000-0000-0000-0000-000000000000",
        "name": "Sample Project",
        "created": "1970-01-01T00:00:00+00:00",
        "updated": "1970-01-01T00:00:00+00:00",
        "yaml_hash": "sample",
        "screenshot_map": {},
        "manual_notes": {},
        "change_log": [],
        "settings": {
            "redact_ids": True,
            "include_best_practice_checks": True,
            "language": "de",
        },
    },
    "app_model.sample.json": {
        "meta": "sample",
        "screens": [],
        "connectors": [],
    },
}

SAMPLE_YAML = {
    "project.sample.yml": "meta:\n  report_name: Sample Report\n  owner: redacted\n  version: \"0.0.0\"\n",
    "project.sample.yaml": "meta:\n  report_name: Sample Report\n  owner: redacted\n  version: \"0.0.0\"\n",
}


@dataclass
class FileResult:
    path: Path
    changed: bool
    replacements: int


@dataclass
class WipeResult:
    removed_files: int
    removed_dirs: int
    created_samples: int
    placeholders: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Redact sensitive data and optionally commit for publishing.")
    parser.add_argument("--root", default=".", help="Repository root path")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without writing files")
    parser.add_argument("--commit", action="store_true", help="Create git commit after redaction")
    parser.add_argument("--message", default="chore: sanitize repository for publishing", help="Commit message")
    parser.add_argument(
        "--pattern",
        action="append",
        dest="patterns",
        help="Additional include glob pattern (can be repeated)",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        dest="excludes",
        help="Additional exclude glob pattern (can be repeated)",
    )
    parser.add_argument("--report", default="publish-report.json", help="Path for JSON report")
    return parser.parse_args()


def is_allowed_data_path(path: Path, data_dir: Path) -> bool:
    rel = path.relative_to(data_dir)
    rel_posix = rel.as_posix()
    name = path.name
    if rel_posix == "templates" or rel_posix.startswith("templates/"):
        return True
    if name == ".gitkeep" or name == "README.md":
        return True
    if name.startswith("sample"):
        return True
    if ".sample." in name:
        return True
    return False


def write_sample_file(path: Path, dry_run: bool) -> bool:
    name = path.name
    if name in SAMPLE_JSON:
        content = json.dumps(SAMPLE_JSON[name], indent=2, ensure_ascii=False) + "\n"
    elif name in SAMPLE_YAML:
        content = SAMPLE_YAML[name]
    else:
        content = "sample: true\n"
    if dry_run:
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def touch_gitkeep(path: Path, dry_run: bool) -> bool:
    if dry_run:
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("", encoding="utf-8")
    return True


def wipe_data_dirs(root: Path, dry_run: bool) -> WipeResult:
    removed_files = 0
    removed_dirs = 0
    created_samples = 0
    placeholders = 0

    data_dirs = [directory for directory in root.rglob("data") if directory.is_dir()]
    for data_dir in data_dirs:
        for source_name, sample_name in SENSITIVE_TO_SAMPLE.items():
            source = data_dir / source_name
            sample = data_dir / sample_name
            if source.exists() and not sample.exists():
                if write_sample_file(sample, dry_run):
                    created_samples += 1

        files = sorted([path for path in data_dir.rglob("*") if path.is_file()], key=lambda p: len(p.parts), reverse=True)
        for file_path in files:
            if is_allowed_data_path(file_path, data_dir):
                continue
            if not dry_run:
                file_path.unlink(missing_ok=True)
            removed_files += 1

        dirs = sorted([path for path in data_dir.rglob("*") if path.is_dir()], key=lambda p: len(p.parts), reverse=True)
        for dir_path in dirs:
            if is_allowed_data_path(dir_path, data_dir):
                continue
            if not dry_run:
                try:
                    dir_path.rmdir()
                    removed_dirs += 1
                except OSError:
                    pass
            else:
                removed_dirs += 1

        for placeholder_dir in ("images", "screenshots", "output"):
            gitkeep = data_dir / placeholder_dir / ".gitkeep"
            if touch_gitkeep(gitkeep, dry_run):
                placeholders += 1

    return WipeResult(
        removed_files=removed_files,
        removed_dirs=removed_dirs,
        created_samples=created_samples,
        placeholders=placeholders,
    )


def is_match(path: Path, patterns: Iterable[str]) -> bool:
    p = path.as_posix()
    return any(fnmatch.fnmatch(p, pattern) for pattern in patterns)


def collect_targets(root: Path, patterns: list[str], excludes: list[str]) -> list[Path]:
    targets: list[Path] = []
    for file in root.rglob("*"):
        if not file.is_file():
            continue
        rel = file.relative_to(root)
        if is_match(rel, excludes):
            continue
        if is_match(rel, patterns):
            targets.append(file)
    return targets


def redact_text(text: str) -> tuple[str, int]:
    total = 0
    current = text
    for pattern, replacement in REPLACERS:
        current, count = pattern.subn(replacement, current)
        total += count
    return current, total


def process_file(path: Path, dry_run: bool) -> FileResult:
    try:
        original = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return FileResult(path=path, changed=False, replacements=0)

    redacted, replacements = redact_text(original)
    changed = redacted != original

    if changed and not dry_run:
        path.write_text(redacted, encoding="utf-8")

    return FileResult(path=path, changed=changed, replacements=replacements)


def run_git(args: list[str], cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True)


def create_commit(root: Path, message: str) -> None:
    run_git(["add", "-A"], cwd=root)
    run_git(["commit", "-m", message], cwd=root)


def write_report(results: list[FileResult], report_path: Path) -> None:
    payload = {
        "changed_files": [r.path.as_posix() for r in results if r.changed],
        "total_files": len(results),
        "changed_count": sum(1 for r in results if r.changed),
        "replacement_count": sum(r.replacements for r in results),
    }
    report_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    patterns = DEFAULT_PATTERNS + (args.patterns or [])
    excludes = DEFAULT_EXCLUDES + (args.excludes or [])

    wipe_result = wipe_data_dirs(root=root, dry_run=args.dry_run)

    targets = collect_targets(root, patterns, excludes)
    results = [process_file(path, dry_run=args.dry_run) for path in targets]

    changed = [r for r in results if r.changed]
    replacement_count = sum(r.replacements for r in results)

    for entry in changed:
        print(f"sanitized: {entry.path.relative_to(root)} ({entry.replacements} replacements)")

    print(f"data files removed: {wipe_result.removed_files}")
    print(f"data folders removed: {wipe_result.removed_dirs}")
    print(f"sample files created: {wipe_result.created_samples}")
    print(f"placeholder folders touched: {wipe_result.placeholders}")

    print(f"checked files: {len(results)}")
    print(f"changed files: {len(changed)}")
    print(f"total replacements: {replacement_count}")

    report_path = (root / args.report).resolve()
    if not args.dry_run:
        write_report(results, report_path)
        print(f"report: {report_path.relative_to(root)}")

    if args.commit:
        if args.dry_run:
            print("commit skipped: --dry-run is active")
        else:
            create_commit(root, args.message)
            print("git commit created")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
