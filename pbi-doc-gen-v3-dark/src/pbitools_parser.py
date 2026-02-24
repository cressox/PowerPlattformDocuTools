"""
pbi-tools-Integration – Optionale Erweiterung.

Falls pbi-tools auf dem System installiert ist (pbi-tools.exe im PATH),
kann eine .pbix-Datei vollstaendig extrahiert werden, inklusive:
  - Model/database.json  (= .bim-Format)
  - Report/report.json   (Layout)
  - Mashup/Package/Formulas/Section1.m

pbi-tools ist NICHT erforderlich. Wenn nicht verfuegbar, wird der
reine PBIX-Parser verwendet (eingeschraenkt: keine Measures/Relationships).

Download: https://pbi.tools
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from .bim_parser import BimImportResult, parse_bim
from .pbix_parser import PbixImportResult, parse_pbix, _parse_layout
from .models import ReportPage

# ── Bekannte Installationspfade ──────────────────────────────────
_KNOWN_PATHS = [
    Path(os.environ.get("LOCALAPPDATA", "")) / "pbi-tools" / "pbi-tools.exe",
    Path(os.environ.get("PROGRAMFILES", "")) / "pbi-tools" / "pbi-tools.exe",
    Path(os.environ.get("USERPROFILE", "")) / "pbi-tools" / "pbi-tools.exe",
]


def _find_pbitools_exe() -> Optional[str]:
    """Findet pbi-tools.exe – erst im PATH, dann an bekannten Orten."""
    exe = shutil.which("pbi-tools") or shutil.which("pbi-tools.exe")
    if exe:
        return exe
    for p in _KNOWN_PATHS:
        if p.exists():
            return str(p)
    return None


def pbitools_available() -> bool:
    """Prueft ob pbi-tools verfuegbar ist (PATH + bekannte Installationspfade)."""
    exe = _find_pbitools_exe()
    if exe:
        try:
            result = subprocess.run(
                [exe, "info"],
                capture_output=True,
                timeout=10,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, OSError):
            pass
    return False


def pbitools_version() -> str:
    """Gibt die pbi-tools-Version zurueck, oder leeren String."""
    exe = _find_pbitools_exe()
    if not exe:
        return ""
    try:
        result = subprocess.run(
            [exe, "info"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            # Erste Zeile enthaelt oft die Version
            first_line = result.stdout.strip().split("\n")[0]
            return first_line
    except Exception:
        pass
    return ""


def extract_with_pbitools(pbix_path: Path, output_dir: Optional[Path] = None) -> Path:
    """
    Ruft 'pbi-tools extract' auf und gibt den Ausgabeordner zurueck.

    Raises:
        FileNotFoundError: pbi-tools nicht gefunden
        RuntimeError: Extraktion fehlgeschlagen
    """
    exe = _find_pbitools_exe()
    if not exe:
        raise FileNotFoundError(
            "pbi-tools nicht gefunden. "
            "Bitte installieren: https://pbi.tools"
        )

    if output_dir is None:
        # Eigenes Verzeichnis unter TEMP anlegen – tempfile.mkdtemp() kann
        # auf Windows eingeschraenkte ACLs setzen, die pbi-tools blockieren.
        import uuid
        output_dir = Path(tempfile.gettempdir()) / f"pbitools_{uuid.uuid4().hex[:12]}"
        if output_dir.exists():
            shutil.rmtree(output_dir, ignore_errors=True)
        output_dir.mkdir(parents=True, exist_ok=True)

    try:
        result = subprocess.run(
            [
                exe, "extract", str(pbix_path),
                "-extractFolder", str(output_dir),
                "-modelSerialization", "Raw",
            ],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            stdout = (result.stdout or "").strip()
            detail = stderr or stdout or "(keine Details)"
            raise RuntimeError(
                f"pbi-tools extract fehlgeschlagen (Code {result.returncode}):\n"
                f"{detail}"
            )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            "pbi-tools extract: Timeout nach 120 Sekunden."
        ) from exc

    return output_dir


def parse_pbitools_output(extracted_dir: Path) -> BimImportResult:
    """
    Parst die von pbi-tools extrahierten Dateien.

    Fokus: Model-Daten (Tabellen, Measures, Relationships, Queries, RLS).
    Report-Seiten/Visuals kommen separat vom PBIX-Parser.

    Erwartete Struktur (mit -modelSerialization Raw):
      extracted_dir/
        Model/
          database.json      (BIM-Format, vollstaendig)
    """
    result = BimImportResult()

    # ── Model (database.json) ─── Hauptquelle ────────
    model_file = extracted_dir / "Model" / "database.json"
    if model_file.exists():
        bim_result = parse_bim(model_file)
        # Alles vom BIM-Result uebernehmen
        result.tables = bim_result.tables
        result.relationships = bim_result.relationships
        result.measures = bim_result.measures
        result.power_queries = bim_result.power_queries
        result.data_sources = bim_result.data_sources
        result.rls_notes = bim_result.rls_notes
        result.report_name = bim_result.report_name
        result.date_logic_notes = bim_result.date_logic_notes
        result.warnings.extend(bim_result.warnings)
    else:
        result.warnings.append(
            f"Model/database.json nicht gefunden in: {extracted_dir}. "
            f"Pruefen Sie, ob pbi-tools korrekt extrahiert hat."
        )

    return result


def parse_pbix_with_pbitools(pbix_path: Path) -> BimImportResult:
    """
    Kombinierte Funktion: Extrahiert .pbix mit pbi-tools und parst alles.

    Raises:
        FileNotFoundError: pbi-tools nicht gefunden
        RuntimeError: Extraktion fehlgeschlagen
    """
    output_dir = extract_with_pbitools(pbix_path)
    try:
        return parse_pbitools_output(output_dir)
    finally:
        # Temp-Verzeichnis aufraeumen
        try:
            shutil.rmtree(output_dir, ignore_errors=True)
        except Exception:
            pass
