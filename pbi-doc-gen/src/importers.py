"""
Import helpers – read measures or queries from simple text files.

Supported formats:
- Measures file: sections separated by a line starting with "MEASURE:"
- Queries file:  sections separated by a line starting with "QUERY:"

These are intentionally simple; no PBIX parsing.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List

from .models import Measure, PowerQuery, _new_id


def import_measures_from_file(filepath: Path) -> List[Measure]:
    """
    Import DAX measures from a text file.

    Expected format (repeating blocks):
    ---
    MEASURE: <name>
    FOLDER: <optional display folder>
    DESCRIPTION: <optional one-line description>
    DAX:
    <dax code, possibly multi-line>
    ---

    Blocks are separated by a line starting with 'MEASURE:'.
    """
    text = filepath.read_text(encoding="utf-8")
    blocks = re.split(r"(?m)^MEASURE:\s*", text)
    measures: List[Measure] = []

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        m = Measure(id=_new_id())
        lines = block.split("\n")
        m.name = lines[0].strip()

        rest = "\n".join(lines[1:])

        # Extract optional fields
        folder_match = re.search(r"(?m)^FOLDER:\s*(.+)", rest)
        if folder_match:
            m.display_folder = folder_match.group(1).strip()

        desc_match = re.search(r"(?m)^DESCRIPTION:\s*(.+)", rest)
        if desc_match:
            m.description = desc_match.group(1).strip()

        dax_match = re.search(r"(?ms)^DAX:\s*\n(.+)", rest)
        if dax_match:
            m.dax_code = dax_match.group(1).strip()
        else:
            # If no DAX: header, take everything after the metadata lines
            remaining = rest
            for pattern in (r"(?m)^FOLDER:.*\n?", r"(?m)^DESCRIPTION:.*\n?"):
                remaining = re.sub(pattern, "", remaining)
            m.dax_code = remaining.strip()

        if m.dax_code:
            measures.append(m)

    return measures


def import_queries_from_file(filepath: Path) -> List[PowerQuery]:
    """
    Import Power Query (M) queries from a text file.

    Expected format (repeating blocks):
    ---
    QUERY: <name>
    PURPOSE: <optional>
    OUTPUT: <optional output table name>
    M:
    <M code, possibly multi-line>
    ---
    """
    text = filepath.read_text(encoding="utf-8")
    blocks = re.split(r"(?m)^QUERY:\s*", text)
    queries: List[PowerQuery] = []

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        q = PowerQuery(id=_new_id())
        lines = block.split("\n")
        q.query_name = lines[0].strip()

        rest = "\n".join(lines[1:])

        purpose_match = re.search(r"(?m)^PURPOSE:\s*(.+)", rest)
        if purpose_match:
            q.purpose = purpose_match.group(1).strip()

        output_match = re.search(r"(?m)^OUTPUT:\s*(.+)", rest)
        if output_match:
            q.output_table = output_match.group(1).strip()

        m_match = re.search(r"(?ms)^M:\s*\n(.+)", rest)
        if m_match:
            q.m_code = m_match.group(1).strip()

        queries.append(q)

    return queries


def export_measures_to_file(measures: List[Measure], filepath: Path) -> None:
    """Export measures to the simple text format."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for m in measures:
            f.write(f"MEASURE: {m.name}\n")
            if m.display_folder:
                f.write(f"FOLDER: {m.display_folder}\n")
            if m.description:
                f.write(f"DESCRIPTION: {m.description}\n")
            f.write("DAX:\n")
            f.write(m.dax_code + "\n\n")
