"""
models.py – Datenmodell fuer den Power Automate Documentation Generator.
Alle Entitaeten werden als dataclasses abgebildet.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class FlowType(str, Enum):
    CLOUD_AUTOMATED = "Cloud Automated"
    CLOUD_INSTANT = "Cloud Instant"
    CLOUD_SCHEDULED = "Cloud Scheduled"
    DESKTOP = "Desktop"


class FlowStatus(str, Enum):
    ACTIVE = "Aktiv"
    DRAFT = "Entwurf"
    DISABLED = "Deaktiviert"
    ERROR = "Fehlerhaft"


class LicenseType(str, Enum):
    STANDARD = "Standard"
    PREMIUM = "Premium"
    PER_USER = "Per-User"
    PER_FLOW = "Per-Flow"


class EnvironmentType(str, Enum):
    DEV = "Dev"
    TEST = "Test"
    PROD = "Prod"


class ConnectorTier(str, Enum):
    STANDARD = "Standard"
    PREMIUM = "Premium"
    CUSTOM = "Custom"


class VariableType(str, Enum):
    STRING = "String"
    INTEGER = "Integer"
    BOOLEAN = "Boolean"
    ARRAY = "Array"
    OBJECT = "Object"
    FLOAT = "Float"


class Criticality(str, Enum):
    HIGH = "Hoch"
    MEDIUM = "Mittel"
    LOW = "Niedrig"


class ChangeImpact(str, Enum):
    MINOR = "minor"
    MAJOR = "major"
    BREAKING = "breaking"


class RunAfterStatus(str, Enum):
    SUCCEEDED = "is successful"
    FAILED = "has failed"
    SKIPPED = "is skipped"
    TIMED_OUT = "has timed out"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _uid() -> str:
    return uuid.uuid4().hex[:8]


# ---------------------------------------------------------------------------
# A) Projekt-Metadaten
# ---------------------------------------------------------------------------

@dataclass
class EnvironmentInfo:
    env_type: str = EnvironmentType.DEV.value
    url: str = ""


@dataclass
class ProjectMeta:
    flow_name: str = ""
    description: str = ""
    flow_type: str = FlowType.CLOUD_AUTOMATED.value
    owner: str = ""
    author: str = ""
    created_date: str = ""
    last_modified: str = ""
    environments: list[EnvironmentInfo] = field(default_factory=list)
    solution_name: str = ""
    status: str = FlowStatus.DRAFT.value
    license_requirement: str = LicenseType.STANDARD.value
    connected_services: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# B) Trigger
# ---------------------------------------------------------------------------

@dataclass
class FlowTrigger:
    id: str = field(default_factory=_uid)
    name: str = ""
    trigger_type: str = ""          # Manuell, Zeitplan, HTTP Request …
    connector: str = ""             # SharePoint, Outlook, HTTP …
    description: str = ""
    schedule_interval: str = ""
    schedule_frequency: str = ""
    schedule_timezone: str = ""
    filter_expression: str = ""
    input_schema: str = ""          # JSON-Schema als String
    authentication: str = ""        # Service Account, User-Delegated …
    raw_json: str = ""              # Rohes JSON fuer Referenz
    screenshot_id: str = ""


# ---------------------------------------------------------------------------
# C) Aktionen (hierarchisch)
# ---------------------------------------------------------------------------

@dataclass
class FlowAction:
    id: str = field(default_factory=_uid)
    name: str = ""                  # Anzeigename
    action_type: str = ""           # Technischer Typ
    connector: str = ""
    description: str = ""
    configuration: str = ""
    inputs_summary: str = ""
    outputs_summary: str = ""
    expression: str = ""
    run_after: list[str] = field(default_factory=list)  # RunAfterStatus values
    is_parallel: bool = False
    parent_id: str = ""             # fuer Verschachtelung
    order: int = 0
    children: list[FlowAction] = field(default_factory=list)
    raw_json: str = ""
    screenshot_id: str = ""


# ---------------------------------------------------------------------------
# D) Konnektoren
# ---------------------------------------------------------------------------

@dataclass
class FlowConnection:
    id: str = field(default_factory=_uid)
    connector_name: str = ""
    connector_type: str = ConnectorTier.STANDARD.value
    connection_name: str = ""
    auth_type: str = ""
    service_account: str = ""
    required_permissions: str = ""
    gateway: str = ""               # On-Premises Gateway
    description: str = ""


# ---------------------------------------------------------------------------
# E) Variablen
# ---------------------------------------------------------------------------

@dataclass
class FlowVariable:
    id: str = field(default_factory=_uid)
    name: str = ""
    var_type: str = VariableType.STRING.value
    initial_value: str = ""
    description: str = ""
    set_in: str = ""                # Wo gesetzt
    used_in: str = ""               # Wo verwendet


# ---------------------------------------------------------------------------
# F) Fehlerbehandlung
# ---------------------------------------------------------------------------

@dataclass
class ErrorHandling:
    id: str = field(default_factory=_uid)
    scope_name: str = ""
    pattern: str = ""               # Try/Catch Beschreibung
    run_after_config: str = ""
    retry_count: int = 0
    retry_interval: str = ""
    retry_type: str = ""            # fixed, exponential
    notification_method: str = ""   # E-Mail, Teams …
    notification_target: str = ""
    timeout: str = ""
    description: str = ""


# ---------------------------------------------------------------------------
# G) Datenmappings
# ---------------------------------------------------------------------------

@dataclass
class DataMapping:
    id: str = field(default_factory=_uid)
    source_action: str = ""
    target_action: str = ""
    field_mapping: str = ""         # Feld-zu-Feld
    transformation: str = ""        # Expression
    description: str = ""


# ---------------------------------------------------------------------------
# H) SLA und Performance
# ---------------------------------------------------------------------------

@dataclass
class FlowSLA:
    expected_runtime: str = ""
    max_runtime: str = ""
    avg_executions: str = ""
    criticality: str = Criticality.MEDIUM.value
    escalation_path: str = ""
    description: str = ""


# ---------------------------------------------------------------------------
# I) Governance
# ---------------------------------------------------------------------------

@dataclass
class Governance:
    dlp_policy: str = ""
    approval_workflow: str = ""
    monitoring_setup: str = ""
    backup_strategy: str = ""
    test_procedure: str = ""
    test_data: str = ""
    rollback_procedure: str = ""
    assumptions: str = ""
    limitations: str = ""
    description: str = ""


# ---------------------------------------------------------------------------
# J) Abhaengigkeiten
# ---------------------------------------------------------------------------

@dataclass
class FlowDependency:
    id: str = field(default_factory=_uid)
    dep_type: str = ""              # Child Flow, Power App, API …
    name: str = ""
    description: str = ""
    environment_variables: str = ""
    api_spec: str = ""


# ---------------------------------------------------------------------------
# K) Aenderungsprotokoll
# ---------------------------------------------------------------------------

@dataclass
class ChangeLogEntry:
    id: str = field(default_factory=_uid)
    version: str = ""
    date: str = ""
    author: str = ""
    description: str = ""
    impact: str = ChangeImpact.MINOR.value
    ticket: str = ""


# ---------------------------------------------------------------------------
# L) CI / Branding
# ---------------------------------------------------------------------------

@dataclass
class CIBranding:
    company_name: str = ""
    logo_path: str = ""
    primary_color: str = "#5B8DEF"
    accent_color: str = "#E0A526"
    secondary_color: str = "#1A1D28"
    footer_text: str = ""
    header_text: str = ""
    confidentiality_note: str = ""


# ---------------------------------------------------------------------------
# M) Screenshots
# ---------------------------------------------------------------------------

@dataclass
class Screenshot:
    id: str = field(default_factory=_uid)
    filename: str = ""
    description: str = ""
    section: str = ""               # z.B. "trigger", "actions", …


# ---------------------------------------------------------------------------
# Gesamt-Projekt
# ---------------------------------------------------------------------------

@dataclass
class PAProject:
    """Top-Level Container fuer ein Power Automate Dokumentationsprojekt."""
    meta: ProjectMeta = field(default_factory=ProjectMeta)
    branding: CIBranding = field(default_factory=CIBranding)
    trigger: FlowTrigger = field(default_factory=FlowTrigger)
    actions: list[FlowAction] = field(default_factory=list)
    connections: list[FlowConnection] = field(default_factory=list)
    variables: list[FlowVariable] = field(default_factory=list)
    error_handling: list[ErrorHandling] = field(default_factory=list)
    data_mappings: list[DataMapping] = field(default_factory=list)
    sla: FlowSLA = field(default_factory=FlowSLA)
    governance: Governance = field(default_factory=Governance)
    dependencies: list[FlowDependency] = field(default_factory=list)
    changelog: list[ChangeLogEntry] = field(default_factory=list)
    screenshots: list[Screenshot] = field(default_factory=list)
