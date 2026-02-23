"""
Storage helpers – load / save a Project to YAML.

We use PyYAML (pyyaml) which is available on virtually every Python
installation. If not installed the tool falls back to JSON.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from .models import Project

# Try YAML first, fall back to JSON
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

DEFAULT_DATA_DIR = Path("data")
DEFAULT_PROJECT_FILE = DEFAULT_DATA_DIR / "project.yml"


def _ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def save_project(project: Project, path: Optional[Path] = None) -> Path:
    """Persist project to YAML (preferred) or JSON."""
    path = path or DEFAULT_PROJECT_FILE
    _ensure_dir(path)
    data = project.to_dict()

    if HAS_YAML and path.suffix in (".yml", ".yaml"):
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    else:
        if not HAS_YAML:
            path = path.with_suffix(".json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    return path


def load_project(path: Optional[Path] = None) -> Project:
    """Load project from YAML or JSON."""
    path = path or DEFAULT_PROJECT_FILE
    if not path.exists():
        # Try alternate extension
        alt = path.with_suffix(".json") if path.suffix in (".yml", ".yaml") else path.with_suffix(".yml")
        if alt.exists():
            path = alt
        else:
            raise FileNotFoundError(f"Project file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        if path.suffix in (".yml", ".yaml"):
            if not HAS_YAML:
                raise ImportError("PyYAML is required to read .yml files. Install with: pip install pyyaml")
            data = yaml.safe_load(f) or {}
        else:
            data = json.load(f)

    return Project.from_dict(data)


def project_exists(path: Optional[Path] = None) -> bool:
    path = path or DEFAULT_PROJECT_FILE
    if path.exists():
        return True
    alt = path.with_suffix(".json") if path.suffix in (".yml", ".yaml") else path.with_suffix(".yml")
    return alt.exists()
