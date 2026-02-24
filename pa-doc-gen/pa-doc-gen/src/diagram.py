"""
diagram.py – Mermaid-Flussdiagramm-Generierung aus Flow-Aktionen.

Erzeugt Mermaid-Syntax fuer visuelle Darstellung des Flows,
aehnlich der Ansicht in Power Automate.
"""
from __future__ import annotations

import re
from typing import Optional

from models import PAProject, FlowAction, FlowTrigger


# ---------------------------------------------------------------------------
# Mermaid-Node-Formatierung
# ---------------------------------------------------------------------------

def _sanitize_id(name: str) -> str:
    """Erzeugt eine gueltige Mermaid-Node-ID aus einem Aktionsnamen."""
    clean = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    clean = re.sub(r'_+', '_', clean).strip('_')
    if not clean or clean[0].isdigit():
        clean = "n_" + clean
    return clean[:50]


def _sanitize_label(name: str) -> str:
    """Escaped Zeichen fuer Mermaid-Labels."""
    return name.replace('"', "'").replace('<', '&lt;').replace('>', '&gt;')


# Aktionstyp -> Mermaid-Shape
SHAPE_MAP = {
    "If": ("{{", "}}"),           # Raute / Decision
    "Condition": ("{{", "}}"),
    "Switch": ("{{", "}}"),
    "Foreach": ("[[", "]]"),      # Subroutine / Loop
    "Until": ("[[", "]]"),
    "Scope": ("([", "])"),        # Stadium / Scope
    "Branch_True": ("([", "])"),
    "Branch_False": ("([", "])"),
    "Switch_Case": ("([", "])"),
    "Switch_Default": ("([", "])"),
    "Terminate": ("((", "))"),    # Kreis / Ende
    "Response": ("((", "))"),
}

DEFAULT_SHAPE = ("[", "]")  # Rechteck


def _node_shape(action_type: str) -> tuple[str, str]:
    """Gibt das Mermaid-Shape-Paar fuer einen Aktionstyp zurueck."""
    return SHAPE_MAP.get(action_type, DEFAULT_SHAPE)


# Aktionstyp -> CSS-Klasse fuer Styling
STYLE_MAP = {
    "If": "condition",
    "Condition": "condition",
    "Switch": "condition",
    "Foreach": "loop",
    "Until": "loop",
    "Scope": "scope",
    "Branch_True": "branch_true",
    "Branch_False": "branch_false",
    "Switch_Case": "branch_true",
    "Switch_Default": "branch_false",
    "InitializeVariable": "variable",
    "SetVariable": "variable",
    "IncrementVariable": "variable",
    "DecrementVariable": "variable",
    "AppendToArrayVariable": "variable",
    "AppendToStringVariable": "variable",
    "Compose": "data",
    "ParseJson": "data",
    "Http": "http",
    "HttpWebhook": "http",
    "Terminate": "terminate",
    "Response": "terminate",
    "OpenApiConnection": "connector",
    "OpenApiConnectionWebhook": "connector",
}


def _node_class(action_type: str) -> str:
    """Gibt die CSS-Klasse fuer einen Aktionstyp zurueck."""
    return STYLE_MAP.get(action_type, "action")


# ---------------------------------------------------------------------------
# Mermaid-Diagramm erstellen
# ---------------------------------------------------------------------------

def _build_action_nodes(
    actions: list[FlowAction],
    lines: list[str],
    prev_ids: list[str],
    class_assignments: list[str],
    depth: int = 0,
) -> list[str]:
    """
    Rekursive Erzeugung von Mermaid-Nodes und -Edges.
    Gibt die IDs der letzten Knoten zurueck (fuer Verknuepfung).
    """
    last_ids = prev_ids

    for action in actions:
        node_id = _sanitize_id(action.name) + f"_{id(action) % 10000}"
        label = _sanitize_label(action.name)
        atype = action.action_type

        # Connector-Info in Label
        if action.connector:
            label = f"{label}\\n[{_sanitize_label(action.connector)}]"

        # Shape
        shape_open, shape_close = _node_shape(atype)
        lines.append(f"    {node_id}{shape_open}\"{label}\"{shape_close}")

        # Klasse zuweisen
        cls = _node_class(atype)
        class_assignments.append(f"    class {node_id} {cls}")

        # Edges von vorherigen Knoten
        for pid in last_ids:
            lines.append(f"    {pid} --> {node_id}")

        # Children verarbeiten (Scope, Condition, Loop, etc.)
        if action.children:
            if atype in ("If", "Condition"):
                # Ja/Nein-Zweige
                true_branch = [c for c in action.children if c.action_type == "Branch_True"]
                false_branch = [c for c in action.children if c.action_type == "Branch_False"]
                other = [c for c in action.children
                         if c.action_type not in ("Branch_True", "Branch_False")]

                branch_ends = []

                if true_branch:
                    tb = true_branch[0]
                    tb_id = _sanitize_id(tb.name) + f"_{id(tb) % 10000}"
                    lines.append(f"    {tb_id}([\"{_sanitize_label(tb.name)}\"])")
                    lines.append(f"    {node_id} -->|Ja| {tb_id}")
                    class_assignments.append(f"    class {tb_id} branch_true")
                    if tb.children:
                        ends = _build_action_nodes(
                            tb.children, lines, [tb_id], class_assignments, depth + 1
                        )
                        branch_ends.extend(ends)
                    else:
                        branch_ends.append(tb_id)

                if false_branch:
                    fb = false_branch[0]
                    fb_id = _sanitize_id(fb.name) + f"_{id(fb) % 10000}"
                    lines.append(f"    {fb_id}([\"{_sanitize_label(fb.name)}\"])")
                    lines.append(f"    {node_id} -->|Nein| {fb_id}")
                    class_assignments.append(f"    class {fb_id} branch_false")
                    if fb.children:
                        ends = _build_action_nodes(
                            fb.children, lines, [fb_id], class_assignments, depth + 1
                        )
                        branch_ends.extend(ends)
                    else:
                        branch_ends.append(fb_id)

                # Andere Kinder (nicht Branch)
                if other:
                    ends = _build_action_nodes(
                        other, lines, [node_id], class_assignments, depth + 1
                    )
                    branch_ends.extend(ends)

                last_ids = branch_ends if branch_ends else [node_id]

            elif atype == "Switch":
                # Switch-Cases
                case_ends = []
                for child in action.children:
                    c_id = _sanitize_id(child.name) + f"_{id(child) % 10000}"
                    c_label = _sanitize_label(child.name)
                    lines.append(f"    {c_id}([\"{c_label}\"])")
                    case_label = child.name.split("Case: ")[-1] if "Case: " in child.name else child.name
                    lines.append(f"    {node_id} -->|{_sanitize_label(case_label)}| {c_id}")
                    cls_c = "branch_true" if child.action_type != "Switch_Default" else "branch_false"
                    class_assignments.append(f"    class {c_id} {cls_c}")
                    if child.children:
                        ends = _build_action_nodes(
                            child.children, lines, [c_id], class_assignments, depth + 1
                        )
                        case_ends.extend(ends)
                    else:
                        case_ends.append(c_id)
                last_ids = case_ends if case_ends else [node_id]

            else:
                # Scope, Foreach, Until – Kinder sequentiell
                ends = _build_action_nodes(
                    action.children, lines, [node_id], class_assignments, depth + 1
                )
                last_ids = ends
        else:
            last_ids = [node_id]

    return last_ids


def generate_mermaid_diagram(project: PAProject) -> str:
    """
    Erzeugt ein Mermaid-Flussdiagramm aus dem Flow-Projekt.
    Gibt den kompletten Mermaid-Code als String zurueck.
    """
    lines: list[str] = []
    class_assignments: list[str] = []

    lines.append("flowchart TD")

    # Trigger-Node
    trigger = project.trigger
    if trigger.name:
        trig_id = "TRIGGER"
        trig_label = _sanitize_label(trigger.name)
        if trigger.connector:
            trig_label = f"{trig_label}\\n[{_sanitize_label(trigger.connector)}]"
        if trigger.trigger_type:
            trig_label = f"{trig_label}\\n({_sanitize_label(trigger.trigger_type)})"
        lines.append(f"    {trig_id}([\"⚡ {trig_label}\"])")
        class_assignments.append(f"    class {trig_id} trigger")
        prev_ids = [trig_id]
    else:
        lines.append("    START([\"Start\"])")
        class_assignments.append("    class START trigger")
        prev_ids = ["START"]

    # Aktions-Knoten
    if project.actions:
        end_ids = _build_action_nodes(
            project.actions, lines, prev_ids, class_assignments
        )
        # End-Node
        lines.append("    FLOW_END([\"Ende\"])")
        class_assignments.append("    class FLOW_END terminate")
        for eid in end_ids:
            lines.append(f"    {eid} --> FLOW_END")

    # Styling
    lines.append("")
    lines.extend(class_assignments)
    lines.append("")
    lines.append("    %% Styles")
    lines.append("    classDef trigger fill:#5B8DEF,stroke:#3A6FD8,color:#fff,stroke-width:2px")
    lines.append("    classDef action fill:#1E2233,stroke:#5B8DEF,color:#E0E0E0,stroke-width:1px")
    lines.append("    classDef connector fill:#1A3A5C,stroke:#5B8DEF,color:#E0E0E0,stroke-width:1px")
    lines.append("    classDef condition fill:#E0A526,stroke:#C48F20,color:#fff,stroke-width:2px")
    lines.append("    classDef loop fill:#9C27B0,stroke:#7B1FA2,color:#fff,stroke-width:2px")
    lines.append("    classDef scope fill:#2E3B4E,stroke:#5B8DEF,color:#E0E0E0,stroke-width:1px,stroke-dasharray: 5 5")
    lines.append("    classDef branch_true fill:#4CAF50,stroke:#388E3C,color:#fff,stroke-width:1px")
    lines.append("    classDef branch_false fill:#EF5B5B,stroke:#D32F2F,color:#fff,stroke-width:1px")
    lines.append("    classDef variable fill:#00897B,stroke:#00695C,color:#fff,stroke-width:1px")
    lines.append("    classDef data fill:#546E7A,stroke:#37474F,color:#fff,stroke-width:1px")
    lines.append("    classDef http fill:#FF7043,stroke:#E64A19,color:#fff,stroke-width:1px")
    lines.append("    classDef terminate fill:#EF5B5B,stroke:#D32F2F,color:#fff,stroke-width:2px")

    return "\n".join(lines)


def generate_mermaid_markdown(project: PAProject) -> str:
    """
    Erzeugt einen Markdown-Abschnitt mit dem Mermaid-Flussdiagramm.
    """
    diagram = generate_mermaid_diagram(project)

    legend = """
### Legende

| Farbe | Bedeutung |
|---|---|
| 🔵 Blau | Trigger / Standard-Aktion |
| 🟡 Gelb | Bedingung (If/Switch) |
| 🟣 Lila | Schleife (Foreach/Until) |
| 🟢 Gruen | Ja-Zweig / Case |
| 🔴 Rot | Nein-Zweig / Default / Ende |
| 🟤 Orange | HTTP-Aktionen |
| 🔷 Tuerkis | Variablen-Aktionen |
| ⬜ Grau | Daten-Operationen (Compose, ParseJson) |
"""

    return f"""# Flussdiagramm

## Flow-Visualisierung

```mermaid
{diagram}
```

{legend}
"""
