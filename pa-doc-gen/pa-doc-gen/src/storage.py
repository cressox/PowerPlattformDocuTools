"""
storage.py – YAML / JSON Laden und Speichern fuer PAProject.
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict, fields, is_dataclass
from pathlib import Path
from typing import Any, Type, get_type_hints

import yaml

from models import (
    PAProject, ProjectMeta, CIBranding, FlowTrigger, FlowAction,
    FlowConnection, FlowVariable, ErrorHandling, DataMapping,
    FlowSLA, Governance, FlowDependency, ChangeLogEntry, Screenshot,
    EnvironmentInfo,
)

DEFAULT_PATH = Path("data/project.yml")


# ---------------------------------------------------------------------------
# Serialisierung
# ---------------------------------------------------------------------------

def _to_dict(obj: Any) -> Any:
    """Rekursive Konvertierung von Dataclass-Instanzen in Dicts."""
    if is_dataclass(obj) and not isinstance(obj, type):
        return {k: _to_dict(v) for k, v in asdict(obj).items()}
    if isinstance(obj, list):
        return [_to_dict(item) for item in obj]
    if isinstance(obj, dict):
        return {k: _to_dict(v) for k, v in obj.items()}
    return obj


def _from_dict(cls: Type, data: dict | Any) -> Any:
    """Rekursive Konstruktion einer Dataclass-Instanz aus einem Dict."""
    if data is None:
        return cls()
    if not isinstance(data, dict):
        return data
    if not is_dataclass(cls):
        return data

    kwargs = {}
    for f in fields(cls):
        val = data.get(f.name, None)
        ftype = f.type

        # Resolve string annotations
        if isinstance(ftype, str):
            ftype = _resolve_type(ftype)

        if val is None:
            continue

        # Handle list[SomeDataclass]
        if hasattr(ftype, '__origin__') and ftype.__origin__ is list:
            inner = ftype.__args__[0] if ftype.__args__ else str
            if is_dataclass(inner):
                val = [_from_dict(inner, item) for item in val]
        elif is_dataclass(ftype) if isinstance(ftype, type) else False:
            val = _from_dict(ftype, val)

        kwargs[f.name] = val

    return cls(**kwargs)


# Mapping fuer bekannte Dataclass-Typen
_TYPE_MAPPING = {
    'ProjectMeta': ProjectMeta,
    'CIBranding': CIBranding,
    'FlowTrigger': FlowTrigger,
    'FlowAction': FlowAction,
    'FlowConnection': FlowConnection,
    'FlowVariable': FlowVariable,
    'ErrorHandling': ErrorHandling,
    'DataMapping': DataMapping,
    'FlowSLA': FlowSLA,
    'Governance': Governance,
    'FlowDependency': FlowDependency,
    'ChangeLogEntry': ChangeLogEntry,
    'Screenshot': Screenshot,
    'EnvironmentInfo': EnvironmentInfo,
}


def _resolve_type(type_str: str) -> type:
    """Resolve forward-reference type strings, including parameterized generics like list[X]."""
    import re
    # Handle list[X] patterns from __future__ annotations
    m = re.match(r'^list\[(.+)\]$', type_str.strip())
    if m:
        inner_name = m.group(1).strip()
        inner_type = _TYPE_MAPPING.get(inner_name, str)
        # Return a synthetic generic alias so hasattr(__origin__) works
        return list[inner_type]  # Python 3.9+ generic alias
    return _TYPE_MAPPING.get(type_str, str)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def save_project(project: PAProject, path: Path | str | None = None) -> Path:
    """Speichert ein Projekt als YAML (Fallback: JSON)."""
    path = Path(path) if path else DEFAULT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    data = _to_dict(project)

    try:
        with open(path, "w", encoding="utf-8") as fh:
            yaml.dump(data, fh, default_flow_style=False, allow_unicode=True, sort_keys=False)
    except Exception:
        # Fallback: JSON
        json_path = path.with_suffix(".json")
        with open(json_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
        return json_path

    return path


def load_project(path: Path | str | None = None) -> PAProject:
    """Laedt ein Projekt aus YAML oder JSON."""
    path = Path(path) if path else DEFAULT_PATH

    if not path.exists():
        # Try JSON fallback
        json_path = path.with_suffix(".json")
        if json_path.exists():
            path = json_path
        else:
            return PAProject()

    with open(path, "r", encoding="utf-8") as fh:
        if path.suffix in (".yml", ".yaml"):
            data = yaml.safe_load(fh) or {}
        else:
            data = json.load(fh)

    return _from_dict(PAProject, data)


def export_json(project: PAProject, path: Path | str) -> Path:
    """Exportiert ein Projekt als JSON."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = _to_dict(project)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    return path
