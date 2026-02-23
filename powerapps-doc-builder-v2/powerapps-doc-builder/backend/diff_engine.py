"""
Diff Engine
============
Computes structural diffs between two app_model versions.
Used for incremental documentation updates.
"""

from __future__ import annotations
from typing import Any


class DiffEngine:
    """Compute diffs between old and new app models."""

    def compute(self, old: dict, new: dict) -> dict:
        """Compare two canonical models and produce a diff report."""
        diff = {
            "screens_added": [],
            "screens_removed": [],
            "screens_modified": [],
            "connectors_added": [],
            "connectors_removed": [],
            "variables_added": [],
            "variables_removed": [],
            "formula_changes": [],
            "summary": "",
        }

        # Screen diffs
        old_screens = {s["name"] for s in old.get("screens", [])}
        new_screens = {s["name"] for s in new.get("screens", [])}

        diff["screens_added"] = sorted(new_screens - old_screens)
        diff["screens_removed"] = sorted(old_screens - new_screens)

        # Modified screens (compare control counts and formulas)
        common = old_screens & new_screens
        old_screen_map = {s["name"]: s for s in old.get("screens", [])}
        new_screen_map = {s["name"]: s for s in new.get("screens", [])}

        for sname in common:
            old_s = old_screen_map[sname]
            new_s = new_screen_map[sname]
            old_ctrl_count = len(old_s.get("controls", []))
            new_ctrl_count = len(new_s.get("controls", []))
            old_formula_count = len(old_s.get("formulas", []))
            new_formula_count = len(new_s.get("formulas", []))

            if old_ctrl_count != new_ctrl_count or old_formula_count != new_formula_count:
                diff["screens_modified"].append({
                    "name": sname,
                    "controls_before": old_ctrl_count,
                    "controls_after": new_ctrl_count,
                    "formulas_before": old_formula_count,
                    "formulas_after": new_formula_count,
                })

        # Connector diffs
        old_connectors = {c["name"] for c in old.get("connectors", [])}
        new_connectors = {c["name"] for c in new.get("connectors", [])}
        diff["connectors_added"] = sorted(new_connectors - old_connectors)
        diff["connectors_removed"] = sorted(old_connectors - new_connectors)

        # Variable diffs
        old_vars = set()
        new_vars = set()
        for category in ("global_vars", "context_vars", "collections"):
            for v in old.get("variables", {}).get(category, []):
                old_vars.add(v["name"])
            for v in new.get("variables", {}).get(category, []):
                new_vars.add(v["name"])
        diff["variables_added"] = sorted(new_vars - old_vars)
        diff["variables_removed"] = sorted(old_vars - new_vars)

        # Formula changes (compare by control.property)
        old_formulas = {}
        for f in old.get("formulas_all", []):
            key = f"{f['screen']}.{f['control']}.{f['property']}"
            old_formulas[key] = f["formula"]

        new_formulas = {}
        for f in new.get("formulas_all", []):
            key = f"{f['screen']}.{f['control']}.{f['property']}"
            new_formulas[key] = f["formula"]

        for key in set(old_formulas.keys()) | set(new_formulas.keys()):
            old_val = old_formulas.get(key)
            new_val = new_formulas.get(key)
            if old_val != new_val:
                diff["formula_changes"].append({
                    "location": key,
                    "old": (old_val or "")[:200],
                    "new": (new_val or "")[:200],
                    "change_type": "added" if not old_val else ("removed" if not new_val else "modified"),
                })

        # Summary
        parts = []
        if diff["screens_added"]:
            parts.append(f"+{len(diff['screens_added'])} Bildschirme")
        if diff["screens_removed"]:
            parts.append(f"-{len(diff['screens_removed'])} Bildschirme")
        if diff["screens_modified"]:
            parts.append(f"~{len(diff['screens_modified'])} geänderte Bildschirme")
        if diff["connectors_added"] or diff["connectors_removed"]:
            parts.append(f"Konnektoren: +{len(diff['connectors_added'])}/-{len(diff['connectors_removed'])}")
        if diff["formula_changes"]:
            parts.append(f"{len(diff['formula_changes'])} Formeländerungen")
        diff["summary"] = "; ".join(parts) if parts else "Keine wesentlichen Änderungen."

        return diff
