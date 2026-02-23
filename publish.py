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
    "**/data/project.yml",
    "**/data/project.yaml",
    "**/data/project.json",
    "**/data/app_model.json",
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


@dataclass
class FileResult:
    path: Path
    changed: bool
    replacements: int


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

    targets = collect_targets(root, patterns, excludes)
    results = [process_file(path, dry_run=args.dry_run) for path in targets]

    changed = [r for r in results if r.changed]
    replacement_count = sum(r.replacements for r in results)

    for entry in changed:
        print(f"sanitized: {entry.path.relative_to(root)} ({entry.replacements} replacements)")

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
