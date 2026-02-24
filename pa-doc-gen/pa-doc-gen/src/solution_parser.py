"""
solution_parser.py – Parser fuer Power Platform Solution-Exporte (.zip).

Erkennt und dokumentiert alle Entitaeten einer Solution:
  - Cloud Flows (Power Automate)
  - Canvas Apps
  - Model-Driven Apps
  - Custom Connectors
  - Connection References
  - Environment Variables
  - Dataverse Tables (Entities)
  - Security Roles
  - Sitemaps
  - Web Resources
  - Plugins / Assemblies
  - Business Process Flows
  - AI Models
  - Chatbots / Copilot Agents
  - Dashboards
  - Charts
"""
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional
from enum import Enum

from models import PAProject, _uid
from flow_parser import FlowParser


# ---------------------------------------------------------------------------
# Solution-Entitaetstypen
# ---------------------------------------------------------------------------

class SolutionComponentType(str, Enum):
    FLOW = "Cloud Flow"
    CANVAS_APP = "Canvas App"
    MODEL_APP = "Model-Driven App"
    CUSTOM_CONNECTOR = "Custom Connector"
    CONNECTION_REFERENCE = "Connection Reference"
    ENV_VARIABLE_DEF = "Environment Variable (Definition)"
    ENV_VARIABLE_VAL = "Environment Variable (Wert)"
    TABLE = "Dataverse Table"
    SECURITY_ROLE = "Security Role"
    SITEMAP = "Sitemap"
    WEB_RESOURCE = "Web Resource"
    PLUGIN = "Plugin Assembly"
    BPF = "Business Process Flow"
    AI_MODEL = "AI Model"
    CHATBOT = "Chatbot"
    DASHBOARD = "Dashboard"
    CHART = "Chart"
    OPTION_SET = "Option Set"
    PROCESS = "Workflow (klassisch)"
    OTHER = "Sonstige"


# Solution XML Component-Type Codes (aus solution.xml)
# https://learn.microsoft.com/en-us/power-apps/developer/data-platform/reference/entities/solutioncomponent
COMPONENT_TYPE_MAP = {
    1: SolutionComponentType.TABLE,          # Entity
    2: SolutionComponentType.TABLE,          # Attribute
    9: SolutionComponentType.OPTION_SET,     # OptionSet
    10: SolutionComponentType.TABLE,         # Entity Relationship
    20: SolutionComponentType.SECURITY_ROLE, # Security Role
    24: SolutionComponentType.PROCESS,       # Workflow (classic)
    26: SolutionComponentType.DASHBOARD,     # Form (SystemForm)
    29: SolutionComponentType.PROCESS,       # Process
    60: SolutionComponentType.WEB_RESOURCE,  # WebResource
    61: SolutionComponentType.SITEMAP,       # Sitemap
    62: SolutionComponentType.PLUGIN,        # PluginAssembly
    65: SolutionComponentType.PLUGIN,        # PluginType
    66: SolutionComponentType.PLUGIN,        # SDKMessageProcessingStep
    70: SolutionComponentType.TABLE,         # FieldSecurityProfile
    91: SolutionComponentType.PLUGIN,        # PluginType
    300: SolutionComponentType.CANVAS_APP,   # CanvasApp
    371: SolutionComponentType.CUSTOM_CONNECTOR,  # Connector
    372: SolutionComponentType.CONNECTION_REFERENCE,
    380: SolutionComponentType.ENV_VARIABLE_DEF,
    381: SolutionComponentType.ENV_VARIABLE_VAL,
    10062: SolutionComponentType.AI_MODEL,
    10143: SolutionComponentType.CHATBOT,
}


# ---------------------------------------------------------------------------
# Solution-Entitaet
# ---------------------------------------------------------------------------

@dataclass
class SolutionEntity:
    """Eine Entitaet innerhalb einer Power Platform Solution."""
    id: str = field(default_factory=_uid)
    name: str = ""
    display_name: str = ""
    entity_type: str = SolutionComponentType.OTHER.value
    description: str = ""
    schema_name: str = ""
    publisher: str = ""
    version: str = ""
    # Extra-Details je nach Typ
    details: dict = field(default_factory=dict)
    # Fuer Flows: referenz zum geparsten PAProject
    flow_project: PAProject | None = None
    # Raw-Daten
    raw_data: str = ""


@dataclass
class SolutionInfo:
    """Metadaten einer Power Platform Solution."""
    unique_name: str = ""
    display_name: str = ""
    description: str = ""
    version: str = ""
    publisher_name: str = ""
    publisher_prefix: str = ""
    managed: bool = False
    created_date: str = ""

    # Alle Entitaeten
    entities: list[SolutionEntity] = field(default_factory=list)

    # Kategorisierte Entitaeten
    flows: list[SolutionEntity] = field(default_factory=list)
    canvas_apps: list[SolutionEntity] = field(default_factory=list)
    model_apps: list[SolutionEntity] = field(default_factory=list)
    custom_connectors: list[SolutionEntity] = field(default_factory=list)
    connection_references: list[SolutionEntity] = field(default_factory=list)
    env_variables: list[SolutionEntity] = field(default_factory=list)
    tables: list[SolutionEntity] = field(default_factory=list)
    security_roles: list[SolutionEntity] = field(default_factory=list)
    web_resources: list[SolutionEntity] = field(default_factory=list)
    plugins: list[SolutionEntity] = field(default_factory=list)
    processes: list[SolutionEntity] = field(default_factory=list)
    other_components: list[SolutionEntity] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Solution-Parser
# ---------------------------------------------------------------------------

class SolutionParser:
    """Parser fuer Power Platform Solution-ZIP-Dateien."""

    def __init__(self):
        self.solution = SolutionInfo()

    def parse(self, zip_path: Path | str) -> SolutionInfo:
        """
        Parst eine Solution-ZIP-Datei und gibt SolutionInfo zurueck.
        """
        zip_path = Path(zip_path)
        if not zip_path.exists():
            raise FileNotFoundError(f"Solution-Datei nicht gefunden: {zip_path}")

        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()

            # 1. solution.xml parsen
            if "solution.xml" in names:
                with zf.open("solution.xml") as f:
                    self._parse_solution_xml(f.read().decode("utf-8"))
            elif "[Content_Types].xml" in names:
                # Manche Exporte haben solution.xml in einem Unterordner
                for name in names:
                    if name.endswith("solution.xml"):
                        with zf.open(name) as f:
                            self._parse_solution_xml(f.read().decode("utf-8"))
                        break

            # 2. Flows parsen (Workflows/*.json)
            self._parse_flows(zf, names)

            # 3. Canvas Apps erkennen
            self._parse_canvas_apps(zf, names)

            # 4. Custom Connectors
            self._parse_custom_connectors(zf, names)

            # 5. Connection References
            self._parse_connection_references(zf, names)

            # 6. Environment Variables
            self._parse_env_variables(zf, names)

            # 7. Entities / Tables
            self._parse_entities(zf, names)

            # 8. Web Resources
            self._parse_web_resources(zf, names)

            # 9. Sitemaps
            self._parse_sitemaps(zf, names)

            # 10. Security Roles
            self._parse_security_roles(zf, names)

            # 11. Plugins
            self._parse_plugins(zf, names)

            # 12. AI Models & Chatbots
            self._parse_ai_components(zf, names)

        # Kategorisieren
        self._categorize()
        return self.solution

    # ---- solution.xml ----

    def _parse_solution_xml(self, xml_content: str):
        """Extrahiert Metadaten aus solution.xml."""
        try:
            root = ET.fromstring(xml_content)
            # Namespace entfernen wenn vorhanden
            ns = ""
            if root.tag.startswith("{"):
                ns = root.tag.split("}")[0] + "}"

            sol = root.find(f"{ns}SolutionManifest") or root

            self.solution.unique_name = self._xml_text(sol, f"{ns}UniqueName") or ""
            self.solution.version = self._xml_text(sol, f"{ns}Version") or ""
            self.solution.managed = self._xml_text(sol, f"{ns}Managed") == "1"

            # LocalizedNames
            ln = sol.find(f".//{ns}LocalizedName")
            if ln is not None:
                self.solution.display_name = ln.get("description", "")

            # Descriptions
            desc = sol.find(f".//{ns}Description")
            if desc is not None:
                self.solution.description = desc.get("description", "")

            # Publisher
            pub = sol.find(f".//{ns}Publisher")
            if pub is not None:
                pub_ln = pub.find(f".//{ns}LocalizedName")
                if pub_ln is not None:
                    self.solution.publisher_name = pub_ln.get("description", "")
                self.solution.publisher_prefix = self._xml_text(pub, f"{ns}CustomizationPrefix") or ""

            # RootComponents (Komponentenliste)
            root_comps = sol.find(f".//{ns}RootComponents")
            if root_comps is not None:
                for comp in root_comps:
                    comp_type = int(comp.get("type", "0"))
                    comp_id = comp.get("id", "") or comp.get("schemaName", "")
                    entity_type = COMPONENT_TYPE_MAP.get(comp_type, SolutionComponentType.OTHER)
                    entity = SolutionEntity(
                        name=comp_id,
                        schema_name=comp.get("schemaName", ""),
                        entity_type=entity_type.value,
                    )
                    self.solution.entities.append(entity)

        except ET.ParseError:
            pass

    def _xml_text(self, parent, tag: str) -> str | None:
        el = parent.find(tag)
        if el is not None and el.text:
            return el.text.strip()
        return None

    # ---- Flows ----

    def _parse_flows(self, zf: zipfile.ZipFile, names: list[str]):
        """Parst alle Flow-JSON-Dateien im Workflows-Ordner."""
        flow_files = [n for n in names
                      if ("Workflows/" in n or "workflows/" in n)
                      and n.endswith(".json")]

        for fname in flow_files:
            try:
                with zf.open(fname) as f:
                    data = json.loads(f.read().decode("utf-8"))
                parser = FlowParser()
                project = parser.parse(data)
                # Name aus Dateiname falls leer
                if not project.meta.flow_name:
                    project.meta.flow_name = Path(fname).stem

                entity = SolutionEntity(
                    name=project.meta.flow_name,
                    display_name=project.meta.flow_name,
                    entity_type=SolutionComponentType.FLOW.value,
                    description=project.meta.description,
                    flow_project=project,
                )
                self.solution.entities.append(entity)
            except Exception:
                entity = SolutionEntity(
                    name=Path(fname).stem,
                    entity_type=SolutionComponentType.FLOW.value,
                    description=f"Fehler beim Parsen von {fname}",
                )
                self.solution.entities.append(entity)

    # ---- Canvas Apps ----

    def _parse_canvas_apps(self, zf: zipfile.ZipFile, names: list[str]):
        """Erkennt Canvas Apps in der Solution."""
        app_files = [n for n in names
                     if ("CanvasApps/" in n or "canvasapps/" in n)]

        # Gruppiere nach App-Ordner
        app_dirs = set()
        for f in app_files:
            parts = f.split("/")
            if len(parts) >= 2:
                app_dirs.add(parts[0] + "/" + parts[1])

        for app_dir in app_dirs:
            # Suche nach Properties.json oder AppInfo
            app_name = app_dir.split("/")[-1]
            details = {}

            for fname in names:
                if fname.startswith(app_dir) and fname.endswith(".json"):
                    try:
                        with zf.open(fname) as f:
                            data = json.loads(f.read().decode("utf-8"))
                        if "Properties" in fname or "properties" in fname:
                            details["author"] = data.get("Author", "")
                            details["app_version"] = data.get("AppVersion", "")
                            details["name"] = data.get("Name", app_name)
                            app_name = details.get("name") or app_name
                    except Exception:
                        pass

            entity = SolutionEntity(
                name=app_name,
                display_name=app_name,
                entity_type=SolutionComponentType.CANVAS_APP.value,
                details=details,
            )
            self.solution.entities.append(entity)

    # ---- Custom Connectors ----

    def _parse_custom_connectors(self, zf: zipfile.ZipFile, names: list[str]):
        """Erkennt Custom Connectors."""
        conn_files = [n for n in names
                      if ("Connectors/" in n or "connectors/" in n)
                      and n.endswith(".json")]

        for fname in conn_files:
            try:
                with zf.open(fname) as f:
                    data = json.loads(f.read().decode("utf-8"))
                name = data.get("properties", {}).get("displayName", Path(fname).stem)
                desc = data.get("properties", {}).get("description", "")
                details = {
                    "host": data.get("properties", {}).get("connectionParameters", {}).get("baseUrl", ""),
                    "auth_type": data.get("properties", {}).get("connectionParametersSet", {}).get("authenticationType", ""),
                    "icon_uri": data.get("properties", {}).get("iconUri", ""),
                }
                entity = SolutionEntity(
                    name=name,
                    display_name=name,
                    entity_type=SolutionComponentType.CUSTOM_CONNECTOR.value,
                    description=desc,
                    details=details,
                )
                self.solution.entities.append(entity)
            except Exception:
                pass

    # ---- Connection References ----

    def _parse_connection_references(self, zf: zipfile.ZipFile, names: list[str]):
        """Parst Connection References."""
        cr_files = [n for n in names
                    if ("connectionreferences/" in n.lower())
                    and n.endswith(".json")]

        for fname in cr_files:
            try:
                with zf.open(fname) as f:
                    data = json.loads(f.read().decode("utf-8"))
                name = data.get("connectionreferencelogicalname", Path(fname).stem)
                details = {
                    "connector_id": data.get("connectorid", ""),
                    "connection_name": data.get("connectionreferencedisplayname", ""),
                }
                entity = SolutionEntity(
                    name=name,
                    display_name=details.get("connection_name") or name,
                    entity_type=SolutionComponentType.CONNECTION_REFERENCE.value,
                    details=details,
                )
                self.solution.entities.append(entity)
            except Exception:
                pass

    # ---- Environment Variables ----

    def _parse_env_variables(self, zf: zipfile.ZipFile, names: list[str]):
        """Parst Environment Variables."""
        ev_def_files = [n for n in names
                        if ("environmentvariabledefinitions/" in n.lower()
                            or "environmentvariabledef" in n.lower())
                        and n.endswith(".json")]

        for fname in ev_def_files:
            try:
                with zf.open(fname) as f:
                    data = json.loads(f.read().decode("utf-8"))
                name = data.get("schemaname", data.get("displayname", Path(fname).stem))
                details = {
                    "type": data.get("type", ""),
                    "default_value": data.get("defaultvalue", ""),
                    "display_name": data.get("displayname", ""),
                    "is_required": data.get("isrequired", False),
                }
                entity = SolutionEntity(
                    name=name,
                    display_name=details.get("display_name") or name,
                    entity_type=SolutionComponentType.ENV_VARIABLE_DEF.value,
                    details=details,
                )
                self.solution.entities.append(entity)
            except Exception:
                pass

        # Environment Variable Values
        ev_val_files = [n for n in names
                        if ("environmentvariablevalues/" in n.lower()
                            or "environmentvariableval" in n.lower())
                        and n.endswith(".json")]

        for fname in ev_val_files:
            try:
                with zf.open(fname) as f:
                    data = json.loads(f.read().decode("utf-8"))
                name = data.get("schemaname", Path(fname).stem)
                details = {
                    "value": data.get("value", ""),
                }
                entity = SolutionEntity(
                    name=name,
                    entity_type=SolutionComponentType.ENV_VARIABLE_VAL.value,
                    details=details,
                )
                self.solution.entities.append(entity)
            except Exception:
                pass

    # ---- Entities / Tables ----

    def _parse_entities(self, zf: zipfile.ZipFile, names: list[str]):
        """Erkennt Dataverse Tables / Entities."""
        entity_files = [n for n in names
                        if ("Entities/" in n or "entities/" in n)
                        and n.endswith(".xml")]

        for fname in entity_files:
            try:
                with zf.open(fname) as f:
                    xml_content = f.read().decode("utf-8")
                root = ET.fromstring(xml_content)
                entity_name = root.get("Name", Path(fname).stem)

                # Display-Name suchen
                display_name = entity_name
                ln = root.find(".//DisplayName")
                if ln is not None:
                    desc_elem = ln.find(".//Description")
                    if desc_elem is not None:
                        display_name = desc_elem.get("description", entity_name)
                    else:
                        display_name = ln.get("description", entity_name)

                # Attribute zaehlen
                attrs = root.findall(".//attribute") or root.findall(".//Attribute")
                details = {
                    "attribute_count": len(attrs),
                    "entity_name": entity_name,
                }

                entity = SolutionEntity(
                    name=entity_name,
                    display_name=display_name,
                    entity_type=SolutionComponentType.TABLE.value,
                    details=details,
                )
                self.solution.entities.append(entity)
            except Exception:
                pass

    # ---- Web Resources ----

    def _parse_web_resources(self, zf: zipfile.ZipFile, names: list[str]):
        """Erkennt Web Resources."""
        wr_files = [n for n in names
                    if ("WebResources/" in n or "webresources/" in n)]

        wr_names = set()
        for f in wr_files:
            parts = f.split("/")
            if len(parts) >= 2:
                wr_name = "/".join(parts[1:])
                if wr_name and wr_name not in wr_names:
                    wr_names.add(wr_name)
                    ext = Path(wr_name).suffix.lower()
                    wr_type = {
                        ".js": "JavaScript",
                        ".html": "HTML",
                        ".htm": "HTML",
                        ".css": "CSS",
                        ".png": "Bild (PNG)",
                        ".jpg": "Bild (JPG)",
                        ".gif": "Bild (GIF)",
                        ".svg": "Bild (SVG)",
                        ".ico": "Icon",
                        ".xml": "XML",
                        ".xsl": "XSL Stylesheet",
                        ".resx": "Resource",
                    }.get(ext, "Sonstige")

                    entity = SolutionEntity(
                        name=wr_name,
                        entity_type=SolutionComponentType.WEB_RESOURCE.value,
                        details={"resource_type": wr_type},
                    )
                    self.solution.entities.append(entity)

    # ---- Sitemaps ----

    def _parse_sitemaps(self, zf: zipfile.ZipFile, names: list[str]):
        """Erkennt Sitemaps."""
        sm_files = [n for n in names
                    if ("SiteMap" in n or "sitemap" in n.lower())
                    and n.endswith(".xml")]

        for fname in sm_files:
            entity = SolutionEntity(
                name=Path(fname).stem,
                entity_type=SolutionComponentType.SITEMAP.value,
            )
            self.solution.entities.append(entity)

    # ---- Security Roles ----

    def _parse_security_roles(self, zf: zipfile.ZipFile, names: list[str]):
        """Erkennt Security Roles."""
        role_files = [n for n in names
                      if ("Roles/" in n or "roles/" in n)
                      and n.endswith(".xml")]

        for fname in role_files:
            try:
                with zf.open(fname) as f:
                    xml_content = f.read().decode("utf-8")
                root = ET.fromstring(xml_content)
                role_name = root.get("name", Path(fname).stem)
                entity = SolutionEntity(
                    name=role_name,
                    entity_type=SolutionComponentType.SECURITY_ROLE.value,
                )
                self.solution.entities.append(entity)
            except Exception:
                entity = SolutionEntity(
                    name=Path(fname).stem,
                    entity_type=SolutionComponentType.SECURITY_ROLE.value,
                )
                self.solution.entities.append(entity)

    # ---- Plugins ----

    def _parse_plugins(self, zf: zipfile.ZipFile, names: list[str]):
        """Erkennt Plugin Assemblies."""
        plugin_files = [n for n in names
                        if ("PluginAssemblies/" in n or "pluginassemblies/" in n)]

        plugin_dirs = set()
        for f in plugin_files:
            parts = f.split("/")
            if len(parts) >= 2:
                plugin_dirs.add(parts[1])

        for pd in plugin_dirs:
            entity = SolutionEntity(
                name=pd,
                entity_type=SolutionComponentType.PLUGIN.value,
            )
            self.solution.entities.append(entity)

    # ---- AI Models & Chatbots ----

    def _parse_ai_components(self, zf: zipfile.ZipFile, names: list[str]):
        """Erkennt AI-Modelle und Chatbots."""
        ai_files = [n for n in names
                    if ("AIModels/" in n or "aimodels/" in n or
                        "aipluginoperations/" in n)
                    and n.endswith(".json")]

        for fname in ai_files:
            try:
                with zf.open(fname) as f:
                    data = json.loads(f.read().decode("utf-8"))
                name = data.get("name", Path(fname).stem)
                entity = SolutionEntity(
                    name=name,
                    entity_type=SolutionComponentType.AI_MODEL.value,
                )
                self.solution.entities.append(entity)
            except Exception:
                pass

        bot_files = [n for n in names
                     if ("Bots/" in n or "bots/" in n or
                         "botcomponents/" in n)
                     and n.endswith(".json")]

        for fname in bot_files:
            try:
                with zf.open(fname) as f:
                    data = json.loads(f.read().decode("utf-8"))
                name = data.get("name", data.get("displayName", Path(fname).stem))
                entity = SolutionEntity(
                    name=name,
                    entity_type=SolutionComponentType.CHATBOT.value,
                )
                self.solution.entities.append(entity)
            except Exception:
                pass

    # ---- Kategorisierung ----

    def _categorize(self):
        """Verteilt Entitaeten in die kategorisierten Listen."""
        cat_map = {
            SolutionComponentType.FLOW.value: self.solution.flows,
            SolutionComponentType.CANVAS_APP.value: self.solution.canvas_apps,
            SolutionComponentType.MODEL_APP.value: self.solution.model_apps,
            SolutionComponentType.CUSTOM_CONNECTOR.value: self.solution.custom_connectors,
            SolutionComponentType.CONNECTION_REFERENCE.value: self.solution.connection_references,
            SolutionComponentType.ENV_VARIABLE_DEF.value: self.solution.env_variables,
            SolutionComponentType.ENV_VARIABLE_VAL.value: self.solution.env_variables,
            SolutionComponentType.TABLE.value: self.solution.tables,
            SolutionComponentType.SECURITY_ROLE.value: self.solution.security_roles,
            SolutionComponentType.WEB_RESOURCE.value: self.solution.web_resources,
            SolutionComponentType.PLUGIN.value: self.solution.plugins,
            SolutionComponentType.BPF.value: self.solution.processes,
            SolutionComponentType.PROCESS.value: self.solution.processes,
        }

        seen_names = set()
        for entity in self.solution.entities:
            key = (entity.entity_type, entity.name)
            if key in seen_names:
                continue
            seen_names.add(key)

            target = cat_map.get(entity.entity_type)
            if target is not None:
                target.append(entity)
            else:
                self.solution.other_components.append(entity)


# ---------------------------------------------------------------------------
# Convenience-Funktionen
# ---------------------------------------------------------------------------

def parse_solution(zip_path: Path | str) -> SolutionInfo:
    """Parst eine Solution-ZIP-Datei und gibt SolutionInfo zurueck."""
    parser = SolutionParser()
    return parser.parse(zip_path)


def get_solution_stats(solution: SolutionInfo) -> dict:
    """Gibt Statistiken ueber eine Solution zurueck."""
    return {
        "total_components": len(solution.entities),
        "flows": len(solution.flows),
        "canvas_apps": len(solution.canvas_apps),
        "model_apps": len(solution.model_apps),
        "custom_connectors": len(solution.custom_connectors),
        "connection_references": len(solution.connection_references),
        "env_variables": len(solution.env_variables),
        "tables": len(solution.tables),
        "security_roles": len(solution.security_roles),
        "web_resources": len(solution.web_resources),
        "plugins": len(solution.plugins),
        "processes": len(solution.processes),
        "other": len(solution.other_components),
    }
