"""
tests/test_all.py – Unit-Tests fuer den PA Documentation Generator.
Mindestens 16 Tests wie gefordert.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from models import (
    PAProject, FlowAction, FlowConnection, FlowVariable,
    FlowTrigger, ErrorHandling, DataMapping, FlowDependency,
    ChangeLogEntry, CIBranding, ProjectMeta, FlowSLA, Governance,
    Screenshot, EnvironmentInfo,
    FlowType, FlowStatus, LicenseType, ConnectorTier, VariableType,
    Criticality, ChangeImpact,
)
from storage import save_project, load_project, _to_dict, _from_dict
from flow_parser import (
    FlowParser, detect_format, FlowFormat, format_expression,
    extract_expressions, get_flow_stats, parse_flow_string,
)
from generator import generate_docs, _actions_tree_md, _actions_detail_md


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture
def sample_project() -> PAProject:
    p = PAProject()
    p.meta.flow_name = "Test-Flow"
    p.meta.description = "Ein Test-Flow fuer Unit-Tests"
    p.meta.flow_type = FlowType.CLOUD_AUTOMATED.value
    p.meta.status = FlowStatus.ACTIVE.value
    p.meta.owner = "Max Mustermann"
    p.meta.author = "Test Autor"
    p.meta.created_date = "2025-01-15"
    p.meta.last_modified = "2025-02-20"
    p.meta.environments = [
        EnvironmentInfo("Dev", "https://dev.example.com"),
        EnvironmentInfo("Prod", "https://prod.example.com"),
    ]

    p.trigger = FlowTrigger(
        name="When_an_item_is_created",
        trigger_type="OpenApiConnection",
        connector="SharePoint",
        description="Wird ausgeloest wenn ein neues Element erstellt wird",
        schedule_frequency="",
        schedule_interval="",
    )

    p.actions = [
        FlowAction(
            id="a1", name="Get_item", action_type="OpenApiConnection",
            connector="SharePoint", description="Element abrufen",
        ),
        FlowAction(
            id="a2", name="Condition_Check", action_type="If",
            description="Status pruefen",
            children=[
                FlowAction(id="a3", name="Send_email", action_type="OpenApiConnection",
                           connector="Office 365 Outlook", description="E-Mail senden"),
            ]
        ),
    ]

    p.variables = [
        FlowVariable(name="varStatus", var_type="String", initial_value="Pending"),
    ]

    p.connections = [
        FlowConnection(connector_name="SharePoint", connector_type="Standard"),
        FlowConnection(connector_name="Office 365 Outlook", connector_type="Standard"),
    ]

    return p


@pytest.fixture
def sample_flow_json() -> dict:
    """Simuliert ein Portal-Export-JSON."""
    return {
        "properties": {
            "displayName": "My Test Flow",
            "description": "A test flow",
            "state": "Started",
            "createdTime": "2025-01-01T10:00:00Z",
            "lastModifiedTime": "2025-02-15T14:30:00Z",
            "definition": {
                "triggers": {
                    "When_a_new_item_is_created": {
                        "type": "OpenApiConnection",
                        "inputs": {
                            "host": {
                                "apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
                                "connectionName": "shared_sharepointonline"
                            }
                        },
                        "recurrence": {},
                        "metadata": {}
                    }
                },
                "actions": {
                    "Initialize_variable": {
                        "type": "InitializeVariable",
                        "inputs": {
                            "variables": [
                                {"name": "myVar", "type": "string", "value": "Hello"}
                            ]
                        },
                        "runAfter": {}
                    },
                    "Get_item": {
                        "type": "OpenApiConnection",
                        "inputs": {
                            "host": {
                                "apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline"
                            },
                            "parameters": {
                                "dataset": "https://mysite.sharepoint.com/sites/test",
                                "table": "MyList",
                                "id": "@{triggerOutputs()?['body/ID']}"
                            }
                        },
                        "runAfter": {
                            "Initialize_variable": ["Succeeded"]
                        }
                    },
                    "Check_Status": {
                        "type": "If",
                        "expression": {
                            "equals": ["@{outputs('Get_item')?['body/Status']}", "Active"]
                        },
                        "actions": {
                            "Send_approval": {
                                "type": "OpenApiConnection",
                                "inputs": {
                                    "host": {
                                        "apiId": "/providers/Microsoft.PowerApps/apis/shared_approvals"
                                    }
                                },
                                "runAfter": {}
                            }
                        },
                        "else": {
                            "actions": {
                                "Send_notification": {
                                    "type": "OpenApiConnection",
                                    "inputs": {
                                        "host": {
                                            "apiId": "/providers/Microsoft.PowerApps/apis/shared_teams"
                                        }
                                    },
                                    "runAfter": {}
                                }
                            }
                        },
                        "runAfter": {
                            "Get_item": ["Succeeded"]
                        }
                    }
                }
            },
            "connectionReferences": {
                "shared_sharepointonline": {
                    "api": {"name": "shared_sharepointonline"},
                    "connectionName": "sp-connection",
                    "tier": "standard"
                },
                "shared_teams": {
                    "api": {"name": "shared_teams"},
                    "connectionName": "teams-connection",
                    "tier": "standard"
                }
            }
        }
    }


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)


# ===========================================================================
# 1. Model Tests
# ===========================================================================

class TestModels:

    def test_01_project_creation(self):
        """PAProject kann erstellt werden."""
        p = PAProject()
        assert p.meta.flow_name == ""
        assert p.actions == []
        assert p.variables == []

    def test_02_enum_values(self):
        """Enums haben die erwarteten Werte."""
        assert FlowType.CLOUD_AUTOMATED.value == "Cloud Automated"
        assert FlowStatus.ACTIVE.value == "Aktiv"
        assert LicenseType.PREMIUM.value == "Premium"
        assert Criticality.HIGH.value == "Hoch"
        assert ChangeImpact.BREAKING.value == "breaking"

    def test_03_action_hierarchy(self):
        """Aktionen koennen hierarchisch verschachtelt werden."""
        parent = FlowAction(name="Scope1", action_type="Scope")
        child1 = FlowAction(name="Action1", parent_id=parent.id)
        child2 = FlowAction(name="Action2", parent_id=parent.id)
        parent.children = [child1, child2]

        assert len(parent.children) == 2
        assert parent.children[0].name == "Action1"
        assert parent.children[1].parent_id == parent.id

    def test_04_unique_ids(self):
        """Jede Entitaet bekommt eine eindeutige ID."""
        a1 = FlowAction()
        a2 = FlowAction()
        assert a1.id != a2.id


# ===========================================================================
# 2. Storage Tests
# ===========================================================================

class TestStorage:

    def test_05_save_and_load_yaml(self, sample_project, temp_dir):
        """Projekt kann als YAML gespeichert und geladen werden."""
        path = temp_dir / "test.yml"
        save_project(sample_project, path)
        assert path.exists()

        loaded = load_project(path)
        assert loaded.meta.flow_name == "Test-Flow"
        assert loaded.meta.owner == "Max Mustermann"
        assert len(loaded.actions) == 2
        assert len(loaded.variables) == 1

    def test_06_roundtrip_preserves_data(self, sample_project, temp_dir):
        """Roundtrip-Test: Save -> Load erhaelt alle Daten."""
        path = temp_dir / "roundtrip.yml"
        save_project(sample_project, path)
        loaded = load_project(path)

        assert loaded.meta.flow_type == FlowType.CLOUD_AUTOMATED.value
        assert loaded.trigger.name == "When_an_item_is_created"
        assert loaded.trigger.connector == "SharePoint"
        assert loaded.connections[0].connector_name == "SharePoint"

    def test_07_load_nonexistent(self, temp_dir):
        """Laden einer nicht existierenden Datei gibt leeres Projekt zurueck."""
        loaded = load_project(temp_dir / "nonexistent.yml")
        assert loaded.meta.flow_name == ""

    def test_08_to_dict(self, sample_project):
        """_to_dict konvertiert korrekt."""
        d = _to_dict(sample_project)
        assert isinstance(d, dict)
        assert d["meta"]["flow_name"] == "Test-Flow"
        assert isinstance(d["actions"], list)


# ===========================================================================
# 3. Parser Tests
# ===========================================================================

class TestParser:

    def test_09_detect_portal_format(self, sample_flow_json):
        """Portal-Export-Format wird korrekt erkannt."""
        fmt = detect_format(sample_flow_json)
        assert fmt == FlowFormat.PORTAL_EXPORT

    def test_10_detect_raw_definition(self):
        """Raw-Definition-Format wird korrekt erkannt."""
        data = {"triggers": {}, "actions": {}}
        assert detect_format(data) == FlowFormat.RAW_DEFINITION

    def test_11_detect_clipboard_action(self):
        """Clipboard-Action-Format wird korrekt erkannt."""
        data = {"type": "Compose", "inputs": "test"}
        assert detect_format(data) == FlowFormat.CLIPBOARD_ACTION

    def test_12_parse_portal_export(self, sample_flow_json):
        """Portal-Export wird korrekt geparst."""
        parser = FlowParser()
        project = parser.parse(sample_flow_json)

        assert project.meta.flow_name == "My Test Flow"
        assert project.meta.description == "A test flow"
        assert project.meta.status == "Aktiv"

    def test_13_parse_trigger(self, sample_flow_json):
        """Trigger wird korrekt erkannt."""
        parser = FlowParser()
        project = parser.parse(sample_flow_json)

        assert project.trigger.name == "When_a_new_item_is_created"
        assert project.trigger.connector == "SharePoint"

    def test_14_parse_actions_hierarchy(self, sample_flow_json):
        """Aktionen inkl. Verschachtelung werden geparst."""
        parser = FlowParser()
        project = parser.parse(sample_flow_json)

        action_names = [a.name for a in project.actions]
        assert "Initialize_variable" in action_names
        assert "Get_item" in action_names
        assert "Check_Status" in action_names

        # Condition sollte Kinder haben
        condition = next(a for a in project.actions if a.name == "Check_Status")
        assert len(condition.children) >= 1  # Mindestens True/False Branch

    def test_15_parse_variables(self, sample_flow_json):
        """Variablen werden aus InitializeVariable extrahiert."""
        parser = FlowParser()
        project = parser.parse(sample_flow_json)

        var_names = [v.name for v in project.variables]
        assert "myVar" in var_names
        myvar = next(v for v in project.variables if v.name == "myVar")
        assert myvar.var_type == "String"
        assert myvar.initial_value == "Hello"

    def test_16_parse_connections(self, sample_flow_json):
        """ConnectionReferences werden geparst."""
        parser = FlowParser()
        project = parser.parse(sample_flow_json)

        conn_names = [c.connector_name for c in project.connections]
        assert "SharePoint" in conn_names
        assert "Microsoft Teams" in conn_names

    def test_17_format_expression(self):
        """PA-Expressions werden korrekt formatiert."""
        expr = "@{formatDateTime(triggerOutputs()?['body/Modified'],'yyyy-MM-dd')}"
        result = format_expression(expr)
        assert "formatDateTime" in result
        assert result.startswith("formatDateTime")

    def test_18_extract_expressions(self):
        """Expressions werden aus Text extrahiert."""
        text = "Value is @{variables('myVar')} and date is @{utcNow()}"
        exprs = extract_expressions(text)
        assert len(exprs) == 2
        assert "@{variables('myVar')}" in exprs

    def test_19_get_flow_stats(self, sample_flow_json):
        """Flow-Statistiken werden korrekt berechnet."""
        parser = FlowParser()
        project = parser.parse(sample_flow_json)
        stats = get_flow_stats(project)

        assert stats["has_trigger"] is True
        assert stats["top_level_actions"] == 3
        assert stats["variables"] >= 1
        assert stats["connectors"] >= 2

    def test_20_parse_flow_string(self, sample_flow_json):
        """parse_flow_string funktioniert mit JSON-String."""
        json_str = json.dumps(sample_flow_json)
        project = parse_flow_string(json_str)
        assert project.meta.flow_name == "My Test Flow"


# ===========================================================================
# 4. Generator Tests
# ===========================================================================

class TestGenerator:

    def test_21_generate_docs(self, sample_project, temp_dir):
        """Markdown-Docs werden generiert."""
        out = generate_docs(sample_project, temp_dir / "docs")

        assert (out / "index.md").exists()
        assert (out / "01_overview" / "overview.md").exists()
        assert (out / "02_flow_structure" / "actions.md").exists()

    def test_22_actions_tree_md(self, sample_project):
        """Aktions-Baum wird als Markdown dargestellt."""
        md = _actions_tree_md(sample_project.actions)
        assert "Get_item" in md
        assert "Condition_Check" in md
        assert "Send_email" in md  # Kind-Aktion

    def test_23_index_contains_links(self, sample_project, temp_dir):
        """Index.md enthaelt Links zu allen Sektionen."""
        out = generate_docs(sample_project, temp_dir / "docs")
        content = (out / "index.md").read_text()
        assert "overview.md" in content
        assert "trigger.md" in content
        assert "actions.md" in content

    def test_24_overview_contains_metadata(self, sample_project, temp_dir):
        """Overview.md enthaelt Metadaten."""
        out = generate_docs(sample_project, temp_dir / "docs")
        content = (out / "01_overview" / "overview.md").read_text()
        assert "Test-Flow" in content
        assert "Max Mustermann" in content


# ===========================================================================
# 5. PDF Tests (basic – nur dass es nicht crasht)
# ===========================================================================

class TestPDF:

    def test_25_pdf_export(self, sample_project, temp_dir):
        """PDF kann exportiert werden ohne Fehler."""
        from pdf_export import export_pdf
        path = temp_dir / "test.pdf"
        result = export_pdf(sample_project, path)
        assert result.exists()
        assert result.stat().st_size > 0


# ===========================================================================
# Run
# ===========================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
