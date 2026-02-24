"""
flow_parser.py – Parser fuer exportierte Power Automate Flow-JSON-Dateien.

Unterstuetzte Formate:
  1. Power Automate Portal-Export (.zip mit definition.json)
  2. Solution-Export (.zip mit Workflows/*.json)
  3. Clipboard-JSON (Peek-Code-Fragment)
  4. Logic App ARM Template
"""
from __future__ import annotations

import io
import json
import re
import zipfile
from pathlib import Path
from typing import Any

from models import (
    FlowAction, FlowConnection, FlowTrigger, FlowVariable,
    PAProject, ProjectMeta, ConnectorTier, VariableType,
)


# ---------------------------------------------------------------------------
# Bekannte Aktionstypen und ihre Kategorien
# ---------------------------------------------------------------------------

CONTROL_ACTIONS = {
    "If", "Switch", "Foreach", "Until", "Scope",
    "Condition", "foreach", "scope",
}

VARIABLE_ACTIONS = {
    "InitializeVariable", "SetVariable", "IncrementVariable",
    "AppendToArrayVariable", "AppendToStringVariable",
    "DecrementVariable",
}

KNOWN_ACTION_TYPES = {
    "OpenApiConnection", "OpenApiConnectionWebhook",
    "Compose", "Http", "HttpWebhook", "Response",
    "Terminate", "Wait", "Delay", "DelayUntil",
    "Query", "Select", "Filter", "Join", "ParseJson",
    "Table", "CreateCsvTable", "CreateHtmlTable",
    *CONTROL_ACTIONS, *VARIABLE_ACTIONS,
}

# Connector-Erkennung aus API-IDs
CONNECTOR_MAP = {
    "shared_sharepointonline": "SharePoint",
    "shared_office365": "Office 365 Outlook",
    "shared_teams": "Microsoft Teams",
    "shared_commondataserviceforapps": "Dataverse",
    "shared_commondataservice": "Dataverse (legacy)",
    "shared_sql": "SQL Server",
    "shared_onedriveforbusiness": "OneDrive for Business",
    "shared_excelonlinebusiness": "Excel Online (Business)",
    "shared_planner": "Planner",
    "shared_approvals": "Approvals",
    "shared_flowpush": "Notifications",
    "shared_sendmail": "Mail",
    "shared_azureblob": "Azure Blob Storage",
    "shared_keyvault": "Azure Key Vault",
    "shared_servicebus": "Service Bus",
    "shared_dynamicscrmonline": "Dynamics 365",
    "shared_twitter": "Twitter",
    "shared_slack": "Slack",
}

VARIABLE_TYPE_MAP = {
    "string": VariableType.STRING.value,
    "integer": VariableType.INTEGER.value,
    "boolean": VariableType.BOOLEAN.value,
    "float": VariableType.FLOAT.value,
    "array": VariableType.ARRAY.value,
    "object": VariableType.OBJECT.value,
}


# ---------------------------------------------------------------------------
# Expression-Formatierung
# ---------------------------------------------------------------------------

def format_expression(expr: str) -> str:
    """Macht PA-Expressions lesbarer."""
    if not expr:
        return ""
    # Entferne aeussere @{...}
    expr = re.sub(r'^@\{(.+)\}$', r'\1', expr.strip())
    return expr


def extract_expressions(text: str) -> list[str]:
    """Extrahiert alle @{...}-Ausdruecke aus einem Text."""
    if not isinstance(text, str):
        return []
    return re.findall(r'@\{[^}]+\}', text)


# ---------------------------------------------------------------------------
# JSON-Format-Erkennung
# ---------------------------------------------------------------------------

class FlowFormat:
    PORTAL_EXPORT = "portal_export"
    SOLUTION_EXPORT = "solution_export"
    CLIPBOARD_ACTION = "clipboard_action"
    CLIPBOARD_TRIGGER = "clipboard_trigger"
    ARM_TEMPLATE = "arm_template"
    RAW_DEFINITION = "raw_definition"
    UNKNOWN = "unknown"


def detect_format(data: dict) -> str:
    """Erkennt das Format der Flow-JSON-Daten."""
    if not isinstance(data, dict):
        return FlowFormat.UNKNOWN

    # ARM Template
    if data.get("$schema") and "deploymentTemplate" in data.get("$schema", ""):
        return FlowFormat.ARM_TEMPLATE

    # Portal-Export (properties.definition)
    props = data.get("properties", {})
    if isinstance(props, dict) and "definition" in props:
        return FlowFormat.PORTAL_EXPORT

    # Raw definition (hat triggers und actions direkt)
    if "triggers" in data and "actions" in data:
        return FlowFormat.RAW_DEFINITION

    # Solution-Export (apiId in properties)
    if isinstance(props, dict) and "apiId" in props:
        return FlowFormat.SOLUTION_EXPORT

    # Clipboard: einzelne Aktion
    if "type" in data and "inputs" in data:
        return FlowFormat.CLIPBOARD_ACTION

    # Clipboard: Trigger
    if "type" in data and ("recurrence" in data or "inputs" in data):
        if data.get("kind") or data.get("type", "").lower().endswith("trigger"):
            return FlowFormat.CLIPBOARD_TRIGGER

    return FlowFormat.UNKNOWN


# ---------------------------------------------------------------------------
# ZIP-Handler
# ---------------------------------------------------------------------------

def load_from_zip(zip_path: Path | str) -> dict:
    """Laedt Flow-JSON aus einer ZIP-Datei (Portal- oder Solution-Export)."""
    zip_path = Path(zip_path)
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()

        # Portal-Export: definition.json
        for name in names:
            if name.endswith("definition.json") or name == "definition.json":
                with zf.open(name) as f:
                    return json.load(f)

        # Solution-Export: Workflows/*.json
        for name in names:
            if "Workflows/" in name and name.endswith(".json"):
                with zf.open(name) as f:
                    return json.load(f)

        # Fallback: erste .json Datei
        for name in names:
            if name.endswith(".json"):
                with zf.open(name) as f:
                    return json.load(f)

    raise ValueError(f"Keine Flow-JSON-Datei in {zip_path} gefunden.")


def load_from_file(file_path: Path | str) -> dict:
    """Laedt Flow-JSON aus einer Datei (ZIP oder JSON)."""
    file_path = Path(file_path)
    if file_path.suffix.lower() == ".zip":
        return load_from_zip(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_from_string(json_str: str) -> dict:
    """Laedt Flow-JSON aus einem String (Clipboard)."""
    return json.loads(json_str)


# ---------------------------------------------------------------------------
# Haupt-Parser
# ---------------------------------------------------------------------------

class FlowParser:
    """Parser fuer Power Automate Flow-Definitionen."""

    def __init__(self):
        self.project = PAProject()
        self._action_order = 0

    def parse(self, data: dict) -> PAProject:
        """Parst Flow-JSON-Daten und gibt ein PAProject zurueck."""
        fmt = detect_format(data)

        if fmt == FlowFormat.PORTAL_EXPORT:
            self._parse_portal_export(data)
        elif fmt == FlowFormat.SOLUTION_EXPORT:
            self._parse_solution_export(data)
        elif fmt == FlowFormat.ARM_TEMPLATE:
            self._parse_arm_template(data)
        elif fmt == FlowFormat.RAW_DEFINITION:
            self._parse_raw_definition(data)
        elif fmt == FlowFormat.CLIPBOARD_ACTION:
            action = self._parse_single_action("Clipboard Action", data)
            self.project.actions.append(action)
        elif fmt == FlowFormat.CLIPBOARD_TRIGGER:
            self.project.trigger = self._parse_trigger("clipboard_trigger", data)
        else:
            raise ValueError("Unbekanntes Flow-JSON-Format.")

        return self.project

    # ---- Portal-Export ----

    def _parse_portal_export(self, data: dict):
        props = data.get("properties", {})
        definition = props.get("definition", {})

        # Metadaten
        self.project.meta.flow_name = props.get("displayName", "")
        self.project.meta.description = props.get("description", "")
        state = props.get("state", "")
        if state.lower() == "started":
            self.project.meta.status = "Aktiv"
        elif state.lower() == "stopped":
            self.project.meta.status = "Deaktiviert"

        created = props.get("createdTime", "")
        if created:
            self.project.meta.created_date = created[:10]
        modified = props.get("lastModifiedTime", "")
        if modified:
            self.project.meta.last_modified = modified[:10]

        # Definition parsen
        self._parse_definition(definition)

        # ConnectionReferences
        conn_refs = props.get("connectionReferences", {})
        self._parse_connection_references(conn_refs)

    # ---- Solution-Export ----

    def _parse_solution_export(self, data: dict):
        props = data.get("properties", {})
        definition = props.get("definition", props.get("workflowDefinition", {}))

        self.project.meta.flow_name = props.get("displayName", data.get("name", ""))
        self.project.meta.description = props.get("description", "")

        self._parse_definition(definition)

        conn_refs = props.get("connectionReferences", {})
        self._parse_connection_references(conn_refs)

    # ---- ARM Template ----

    def _parse_arm_template(self, data: dict):
        resources = data.get("resources", [])
        for res in resources:
            if res.get("type", "").endswith("/workflows"):
                props = res.get("properties", {})
                definition = props.get("definition", {})
                self.project.meta.flow_name = res.get("name", "")
                self._parse_definition(definition)
                break

    # ---- Raw Definition ----

    def _parse_raw_definition(self, data: dict):
        self._parse_definition(data)

    # ---- Definition (Kern) ----

    def _parse_definition(self, definition: dict):
        if not definition:
            return

        # Triggers
        triggers = definition.get("triggers", {})
        for name, trig_data in triggers.items():
            self.project.trigger = self._parse_trigger(name, trig_data)
            break  # Erster Trigger (PA-Flows haben i.d.R. einen)

        # Actions
        actions = definition.get("actions", {})
        self.project.actions = self._parse_actions(actions)

    # ---- Trigger parsen ----

    def _parse_trigger(self, name: str, data: dict) -> FlowTrigger:
        trigger = FlowTrigger()
        trigger.name = name
        trigger.trigger_type = data.get("type", "")

        # Recurrence
        recurrence = data.get("recurrence", {})
        if recurrence:
            trigger.trigger_type = "Recurrence"
            trigger.schedule_frequency = recurrence.get("frequency", "")
            trigger.schedule_interval = str(recurrence.get("interval", ""))
            trigger.schedule_timezone = recurrence.get("timeZone", "")

        # Connector
        metadata = data.get("metadata", {})
        conn_id = metadata.get("operationMetadataId") or ""
        inputs = data.get("inputs", {})
        host = inputs.get("host", {}) if isinstance(inputs, dict) else {}
        api_id = ""
        if isinstance(host, dict):
            api_id = host.get("apiId", "") or ""
            conn_ref = host.get("connectionName", "") or host.get("connection", {})
            if isinstance(conn_ref, dict):
                conn_ref = conn_ref.get("referenceName", "")

        trigger.connector = self._resolve_connector_name(api_id)

        # Input-Schema
        schema = data.get("schema", inputs.get("schema", ""))
        if schema:
            trigger.input_schema = json.dumps(schema, indent=2, ensure_ascii=False)

        # Filter
        conditions = inputs.get("conditions", []) if isinstance(inputs, dict) else []
        if conditions:
            trigger.filter_expression = json.dumps(conditions, indent=2, ensure_ascii=False)

        trigger.raw_json = json.dumps(data, indent=2, ensure_ascii=False)
        return trigger

    # ---- Aktionen rekursiv parsen ----

    def _parse_actions(self, actions_dict: dict, parent_id: str = "") -> list[FlowAction]:
        """Parst ein Dictionary von Aktionen rekursiv."""
        result = []
        if not actions_dict:
            return result

        # Reihenfolge bestimmen (runAfter)
        sorted_names = self._sort_actions(actions_dict)

        for name in sorted_names:
            action_data = actions_dict[name]
            action = self._parse_single_action(name, action_data, parent_id)
            result.append(action)

        return result

    def _parse_single_action(self, name: str, data: dict, parent_id: str = "") -> FlowAction:
        self._action_order += 1
        action = FlowAction()
        action.name = name
        action.action_type = data.get("type", "")
        action.parent_id = parent_id
        action.order = self._action_order

        # Connector aus Host
        inputs = data.get("inputs", {})
        if isinstance(inputs, dict):
            host = inputs.get("host", {})
            if isinstance(host, dict):
                api_id = host.get("apiId", "") or ""
                action.connector = self._resolve_connector_name(api_id)

        # Run After
        run_after = data.get("runAfter", {})
        if run_after:
            for dep_name, statuses in run_after.items():
                for s in statuses:
                    if s not in action.run_after:
                        action.run_after.append(s)

        # Expressions in Inputs extrahieren
        if isinstance(inputs, dict):
            exprs = []
            self._collect_expressions(inputs, exprs)
            if exprs:
                action.expression = "\n".join(exprs)

        # Variable-Aktionen -> FlowVariable erstellen
        if action.action_type in VARIABLE_ACTIONS or name.startswith("Initialize_variable") or name.startswith("InitializeVariable"):
            self._extract_variable(name, data)

        # Kinder parsen (Scope, Condition, Foreach, Until)
        action.children = self._parse_children(name, data, action.id)

        action.raw_json = json.dumps(data, indent=2, ensure_ascii=False)
        return action

    def _parse_children(self, name: str, data: dict, parent_id: str) -> list[FlowAction]:
        """Parst verschachtelte Aktionen in Scopes, Conditions, etc."""
        children = []
        action_type = data.get("type", "").lower()

        # Scope / Foreach / Until: direkte actions
        nested_actions = data.get("actions", {})
        if nested_actions:
            children.extend(self._parse_actions(nested_actions, parent_id))

        # Condition: If/Else
        if action_type in ("if", "condition"):
            # True-Branch
            true_actions = data.get("actions", {})
            if true_actions:
                scope = FlowAction()
                scope.name = f"{name} – Ja"
                scope.action_type = "Branch_True"
                scope.parent_id = parent_id
                scope.children = self._parse_actions(true_actions, scope.id)
                children.append(scope)

            # False-Branch
            else_actions = data.get("else", {}).get("actions", {})
            if else_actions:
                scope = FlowAction()
                scope.name = f"{name} – Nein"
                scope.action_type = "Branch_False"
                scope.parent_id = parent_id
                scope.children = self._parse_actions(else_actions, scope.id)
                children.append(scope)

        # Switch: Cases
        cases = data.get("cases", {})
        for case_name, case_data in cases.items():
            case_actions = case_data.get("actions", {})
            if case_actions:
                scope = FlowAction()
                scope.name = f"{name} – Case: {case_name}"
                scope.action_type = "Switch_Case"
                scope.parent_id = parent_id
                scope.children = self._parse_actions(case_actions, scope.id)
                children.append(scope)

        # Default Case
        default = data.get("default", {})
        default_actions = default.get("actions", {}) if isinstance(default, dict) else {}
        if default_actions:
            scope = FlowAction()
            scope.name = f"{name} – Default"
            scope.action_type = "Switch_Default"
            scope.parent_id = parent_id
            scope.children = self._parse_actions(default_actions, scope.id)
            children.append(scope)

        return children

    def _sort_actions(self, actions_dict: dict) -> list[str]:
        """Sortiert Aktionen basierend auf runAfter-Abhaengigkeiten (topologisch)."""
        sorted_list = []
        remaining = set(actions_dict.keys())

        # Finde Startaktionen (kein runAfter oder leeres runAfter)
        for _ in range(len(actions_dict) + 1):
            if not remaining:
                break
            added = []
            for name in list(remaining):
                run_after = actions_dict[name].get("runAfter", {})
                deps = set(run_after.keys()) if run_after else set()
                if deps.issubset(set(sorted_list)):
                    added.append(name)
            if not added:
                # Zyklus oder fehlende Deps: Rest einfach anfuegen
                sorted_list.extend(sorted(remaining))
                break
            # Stabile Sortierung innerhalb einer Ebene
            added.sort()
            sorted_list.extend(added)
            remaining -= set(added)

        return sorted_list

    # ---- Variablen extrahieren ----

    def _extract_variable(self, name: str, data: dict):
        inputs = data.get("inputs", {})
        if not isinstance(inputs, dict):
            return
        variables = inputs.get("variables", [])
        if not variables and "name" in inputs:
            variables = [inputs]

        for var_data in variables:
            var = FlowVariable()
            var.name = var_data.get("name", name)
            var_type = var_data.get("type", "string").lower()
            var.var_type = VARIABLE_TYPE_MAP.get(var_type, VariableType.STRING.value)
            val = var_data.get("value", "")
            var.initial_value = str(val) if val is not None else ""
            var.set_in = name
            self.project.variables.append(var)

    # ---- Konnektoren ----

    def _parse_connection_references(self, conn_refs: dict):
        for ref_name, ref_data in conn_refs.items():
            conn = FlowConnection()
            conn.connection_name = ref_name

            api_def = ref_data if isinstance(ref_data, dict) else {}
            api_id = api_def.get("api", {}).get("name", "") if isinstance(api_def.get("api"), dict) else ""
            conn.connector_name = self._resolve_connector_name(api_id) or ref_name

            # Tier erkennen
            tier = api_def.get("tier", "").lower()
            if "premium" in tier:
                conn.connector_type = ConnectorTier.PREMIUM.value
            elif "custom" in tier or api_id.startswith("/providers/Microsoft.PowerApps/apis/shared_"):
                conn.connector_type = ConnectorTier.STANDARD.value
            else:
                conn.connector_type = ConnectorTier.STANDARD.value

            conn.auth_type = api_def.get("authenticationType", "")
            conn.service_account = api_def.get("connectionName", "")

            self.project.connections.append(conn)

    def _resolve_connector_name(self, api_id: str) -> str:
        """Loest eine API-ID in einen lesbaren Connector-Namen auf."""
        if not api_id:
            return ""
        for key, name in CONNECTOR_MAP.items():
            if key in api_id.lower():
                return name
        # Fallback: letzter Teil der ID
        parts = api_id.rstrip("/").split("/")
        return parts[-1] if parts else api_id

    # ---- Expressions sammeln ----

    def _collect_expressions(self, obj: Any, result: list[str]):
        if isinstance(obj, str):
            for expr in extract_expressions(obj):
                result.append(format_expression(expr))
        elif isinstance(obj, dict):
            for v in obj.values():
                self._collect_expressions(v, result)
        elif isinstance(obj, list):
            for item in obj:
                self._collect_expressions(item, result)


# ---------------------------------------------------------------------------
# Convenience-Funktionen
# ---------------------------------------------------------------------------

def parse_flow_file(file_path: Path | str) -> PAProject:
    """Parst eine Flow-JSON-Datei und gibt ein PAProject zurueck."""
    file_path = Path(file_path)
    data = load_from_file(file_path)
    parser = FlowParser()
    project = parser.parse(data)
    # Flow-Name aus Dateiname ableiten, falls leer
    if not project.meta.flow_name:
        project.meta.flow_name = file_path.stem
    return project


def parse_flow_string(json_str: str) -> PAProject:
    """Parst einen Flow-JSON-String und gibt ein PAProject zurueck."""
    data = load_from_string(json_str)
    parser = FlowParser()
    return parser.parse(data)


def get_flow_stats(project: PAProject) -> dict:
    """Gibt Statistiken ueber einen Flow zurueck."""

    def _count_recursive(actions: list[FlowAction]) -> int:
        count = len(actions)
        for a in actions:
            count += _count_recursive(a.children)
        return count

    total_actions = _count_recursive(project.actions)
    connectors = {c.connector_name for c in project.connections if c.connector_name}
    variables = len(project.variables)

    return {
        "total_actions": total_actions,
        "top_level_actions": len(project.actions),
        "connectors": len(connectors),
        "connector_names": sorted(connectors),
        "variables": variables,
        "has_trigger": bool(project.trigger.name),
        "trigger_type": project.trigger.trigger_type,
    }
