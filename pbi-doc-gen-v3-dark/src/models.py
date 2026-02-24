"""
Data models for the Power BI Documentation Generator.

All structured data is represented as dataclasses that can be
serialized to / deserialized from YAML (via dict round-trip).
Includes CI/Branding config and Screenshot references.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from typing import List, Optional


def _new_id() -> str:
    return uuid.uuid4().hex[:8]

def _today() -> str:
    return date.today().isoformat()


# ── CI / Branding ────────────────────────────────────────────────

@dataclass
class CIBranding:
    """Corporate Identity settings for customer-specific documentation."""
    company_name: str = ""
    logo_path: str = ""                # Path to company logo image
    primary_color: str = "#1B3A5C"     # Main brand colour (hex)
    accent_color: str = "#F2C811"      # Accent colour (hex)
    secondary_color: str = "#2563EB"   # Secondary colour (hex)
    font_name: str = ""                # Custom font name (optional)
    footer_text: str = "Dokumentiert von Felix Tischler"
    header_text: str = ""              # Optional header on every page
    cover_subtitle: str = "Dokumentation"
    confidentiality_notice: str = ""   # e.g. "Vertraulich – Nur für internen Gebrauch"

    @classmethod
    def from_dict(cls, d: dict) -> "CIBranding":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ── Screenshot reference ─────────────────────────────────────────

@dataclass
class Screenshot:
    """A screenshot attached to any documentation section."""
    id: str = field(default_factory=_new_id)
    filename: str = ""       # Relative path under data/screenshots/
    caption: str = ""
    section: str = ""        # Which section it belongs to (e.g. "data_model", "page:Overview")

    @classmethod
    def from_dict(cls, d: dict) -> "Screenshot":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ── A) Project / Report metadata ────────────────────────────────

@dataclass
class Environment:
    name: str = ""
    workspace: str = ""
    url: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "Environment":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class ProjectMeta:
    report_name: str = ""
    short_description: str = ""
    audience: str = ""
    owner: str = ""
    author: str = ""
    version: str = "0.1.0"
    date: str = field(default_factory=_today)
    environments: List[Environment] = field(default_factory=list)
    powerbi_service_url: str = ""
    sharepoint_folder_url: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "ProjectMeta":
        envs = [Environment.from_dict(e) for e in d.pop("environments", [])]
        obj = cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})
        obj.environments = envs
        return obj


# ── B) KPI definitions ──────────────────────────────────────────

@dataclass
class KPI:
    id: str = field(default_factory=_new_id)
    name: str = ""
    business_description: str = ""
    technical_definition: str = ""
    granularity: str = ""
    filters_context: str = ""
    caveats: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "KPI":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ── C) Data sources ─────────────────────────────────────────────

@dataclass
class DataSource:
    id: str = field(default_factory=_new_id)
    name: str = ""
    source_type: str = ""
    connection_info: str = ""
    refresh_cadence: str = ""
    gateway_required: bool = False
    gateway_name: str = ""
    owner_contact: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "DataSource":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ── D) Power Query (M) ─────────────────────────────────────────

@dataclass
class PowerQuery:
    id: str = field(default_factory=_new_id)
    query_name: str = ""
    purpose: str = ""
    inputs: str = ""
    major_transformations: str = ""
    m_code: str = ""
    output_table: str = ""
    notes: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "PowerQuery":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ── E) Data model ───────────────────────────────────────────────

@dataclass
class ModelTable:
    name: str = ""
    table_type: str = ""
    description: str = ""
    keys: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "ModelTable":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class ModelRelationship:
    from_table: str = ""
    from_column: str = ""
    to_table: str = ""
    to_column: str = ""
    cardinality: str = ""
    filter_direction: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "ModelRelationship":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class DataModel:
    tables: List[ModelTable] = field(default_factory=list)
    relationships: List[ModelRelationship] = field(default_factory=list)
    date_logic_notes: str = ""
    screenshot_paths: List[str] = field(default_factory=list)
    notes: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "DataModel":
        tables = [ModelTable.from_dict(t) for t in d.pop("tables", [])]
        rels = [ModelRelationship.from_dict(r) for r in d.pop("relationships", [])]
        obj = cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})
        obj.tables = tables
        obj.relationships = rels
        return obj


# ── F) Measures (DAX) ───────────────────────────────────────────

@dataclass
class Measure:
    id: str = field(default_factory=_new_id)
    name: str = ""
    display_folder: str = ""
    description: str = ""
    dax_code: str = ""
    dependencies: str = ""
    filter_context_notes: str = ""
    validation_notes: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "Measure":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ── G) Report pages & visuals ───────────────────────────────────

@dataclass
class Visual:
    name: str = ""
    description: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "Visual":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class ReportPage:
    id: str = field(default_factory=_new_id)
    page_name: str = ""
    purpose: str = ""
    visuals: List[Visual] = field(default_factory=list)
    slicers_filters: str = ""
    notes: str = ""
    screenshot_path: str = ""   # Screenshot of this page

    @classmethod
    def from_dict(cls, d: dict) -> "ReportPage":
        visuals = [Visual.from_dict(v) for v in d.pop("visuals", [])]
        obj = cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})
        obj.visuals = visuals
        return obj


# ── H) Governance ───────────────────────────────────────────────

@dataclass
class Governance:
    refresh_schedule: str = ""
    monitoring_notes: str = ""
    rls_notes: str = ""
    performance_notes: str = ""
    assumptions: str = ""
    limitations: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "Governance":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ── I) Change log ───────────────────────────────────────────────

@dataclass
class ChangeLogEntry:
    id: str = field(default_factory=_new_id)
    version: str = ""
    date: str = field(default_factory=_today)
    description: str = ""
    author: str = ""
    impact: str = ""
    ticket_link: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "ChangeLogEntry":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ── J) Permissions / Berechtigungen ─────────────────────────────

@dataclass
class Permissions:
    """Access rights, roles, and data sensitivity for the report."""
    workspace_roles: str = ""            # Workspace-Rollen (Admin, Member, Contributor, Viewer)
    rls_details: str = ""                # Row-Level Security Konfiguration
    sharing_permissions: str = ""        # Freigabe-/Sharing-Regelungen
    data_sensitivity: str = ""           # Datensensitivitaet / Klassifizierung
    required_roles_for_changes: str = "" # Rollen fuer Aenderungen am Bericht
    service_principal: str = ""          # Service Principal / App-Registrierung
    notes: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "Permissions":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ── K) Storage Structure / Ablagestruktur ────────────────────────

@dataclass
class StorageStructure:
    """Where files are stored and how the workspace is organized."""
    pbix_location: str = ""              # Speicherort der PBIX-Datei
    workspace_name: str = ""             # Power BI Workspace
    sharepoint_path: str = ""            # SharePoint-/OneDrive-Pfad
    data_gateway: str = ""               # Data Gateway Name/Standort
    backup_strategy: str = ""            # Backup-/Versionierung-Strategie
    deployment_pipeline: str = ""        # Deployment Pipeline (Dev/Test/Prod)
    repo_url: str = ""                   # Git-Repository-URL
    notes: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "StorageStructure":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ── L) Naming Conventions / Namenskonzept ────────────────────────

@dataclass
class NamingConventions:
    """Naming rules and conventions for report artefacts."""
    measures: str = ""                   # Namensregeln fuer Measures
    tables: str = ""                     # Namensregeln fuer Tabellen
    columns: str = ""                    # Namensregeln fuer Spalten
    pages: str = ""                      # Namensregeln fuer Berichtsseiten
    reports: str = ""                    # Namensregeln fuer Berichte/Dateien
    queries: str = ""                    # Namensregeln fuer Power Queries
    general_rules: str = ""              # Allgemeine Regeln (Sprache, CamelCase, …)
    notes: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "NamingConventions":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ── M) Change Guidance / Aenderungshinweise ──────────────────────

@dataclass
class ChangeGuidance:
    """Best practices and checklists for modifying the report."""
    before_changes: str = ""             # Was vor Aenderungen zu beachten ist
    testing_checklist: str = ""          # Test-Checkliste
    deployment_steps: str = ""           # Schritte fuer Deployment
    rollback_plan: str = ""              # Rollback-Plan
    contact_persons: str = ""            # Ansprechpartner
    notes: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "ChangeGuidance":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ── Root project ────────────────────────────────────────────────

@dataclass
class Project:
    meta: ProjectMeta = field(default_factory=ProjectMeta)
    ci_branding: CIBranding = field(default_factory=CIBranding)
    kpis: List[KPI] = field(default_factory=list)
    data_sources: List[DataSource] = field(default_factory=list)
    power_queries: List[PowerQuery] = field(default_factory=list)
    data_model: DataModel = field(default_factory=DataModel)
    measures: List[Measure] = field(default_factory=list)
    report_pages: List[ReportPage] = field(default_factory=list)
    governance: Governance = field(default_factory=Governance)
    change_log: List[ChangeLogEntry] = field(default_factory=list)
    screenshots: List[Screenshot] = field(default_factory=list)
    permissions: Permissions = field(default_factory=Permissions)
    storage_structure: StorageStructure = field(default_factory=StorageStructure)
    naming_conventions: NamingConventions = field(default_factory=NamingConventions)
    change_guidance: ChangeGuidance = field(default_factory=ChangeGuidance)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Project":
        meta = ProjectMeta.from_dict(d.pop("meta", {}))
        ci = CIBranding.from_dict(d.pop("ci_branding", {}))
        kpis = [KPI.from_dict(k) for k in d.pop("kpis", [])]
        sources = [DataSource.from_dict(s) for s in d.pop("data_sources", [])]
        queries = [PowerQuery.from_dict(q) for q in d.pop("power_queries", [])]
        dm = DataModel.from_dict(d.pop("data_model", {}))
        measures = [Measure.from_dict(m) for m in d.pop("measures", [])]
        pages = [ReportPage.from_dict(p) for p in d.pop("report_pages", [])]
        gov = Governance.from_dict(d.pop("governance", {}))
        changelog = [ChangeLogEntry.from_dict(c) for c in d.pop("change_log", [])]
        screenshots = [Screenshot.from_dict(s) for s in d.pop("screenshots", [])]
        perms = Permissions.from_dict(d.pop("permissions", {}))
        storage = StorageStructure.from_dict(d.pop("storage_structure", {}))
        naming = NamingConventions.from_dict(d.pop("naming_conventions", {}))
        chg_guide = ChangeGuidance.from_dict(d.pop("change_guidance", {}))
        return cls(
            meta=meta, ci_branding=ci, kpis=kpis, data_sources=sources,
            power_queries=queries, data_model=dm, measures=measures,
            report_pages=pages, governance=gov, change_log=changelog,
            screenshots=screenshots, permissions=perms,
            storage_structure=storage, naming_conventions=naming,
            change_guidance=chg_guide,
        )
