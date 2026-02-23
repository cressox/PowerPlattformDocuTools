"""
Power Apps YAML Parser
======================
Resilient parser for Canvas App YAML exports.
Extracts screens, controls, formulas, connectors, variables, collections,
components, and data sources into a canonical JSON model.

Handles multiple Power Apps YAML schema versions gracefully.
"""

from __future__ import annotations
import re, yaml, json, hashlib
from typing import Any
from datetime import datetime, timezone


class PowerAppsYamlParser:
    """
    Parse Power Apps Canvas App YAML into a canonical model.
    
    Supports three input modes:
      - "full"     : Complete app YAML export (default)
      - "fragment" : Partial YAML (single screen, single control, etc.)
      - "auto"     : Auto-detect whether input is full app or fragment
    """

    # Patterns for formula extraction
    FORMULA_PROPERTIES = [
        "OnSelect", "OnChange", "OnVisible", "OnHidden", "OnStart",
        "Items", "Default", "Update", "Text", "Visible", "DisplayMode",
        "Fill", "Color", "X", "Y", "Width", "Height", "Size",
        "OnSuccess", "OnFailure", "OnReset", "OnCheck", "OnUncheck",
        "OnTimerStart", "OnTimerEnd", "Value", "Tooltip", "HintText",
        "InputTextPlaceholder", "Navigate", "Reset", "BorderColor",
        "HoverFill", "PressedFill", "DisabledFill", "FocusedBorderColor",
    ]

    # Known Power Apps control types
    CONTROL_TYPES = {
        "gallery", "form", "button", "label", "textinput", "dropdown",
        "combobox", "datepicker", "checkbox", "toggle", "slider",
        "rating", "timer", "image", "icon", "shape", "htmltext",
        "richtexteditor", "pdfviewer", "barcodescanner", "camera",
        "microphone", "video", "audioplayer", "penInput", "component",
        "screen", "group", "container", "horizontalcontainer",
        "verticalcontainer", "datacard", "datacardvalue",
    }

    # Connector / data source patterns
    CONNECTOR_PATTERNS = [
        (r"'([^']+)'\s*\.\s*(\w+)", "data_source_field"),    # 'ListName'.Column
        (r"(\w+)\.GetItems", "connector_method"),
        (r"Office365Users", "Office365Users"),
        (r"Office365Outlook", "Office365Outlook"),
        (r"SharePoint\w*", "SharePoint"),
        (r"Dataverse|Microsoft Dataverse", "Dataverse"),
        (r"SQL Server|Sql\.", "SQL Server"),
        (r"Power Automate|Flow\.", "Power Automate"),
        (r"HTTP|http[s]?://", "HTTP"),
        (r"AzureAD|Azure AD", "Azure AD"),
        (r"Approvals", "Approvals"),
        (r"Teams|Microsoft Teams", "Microsoft Teams"),
        (r"Excel Online|Excel", "Excel Online"),
        (r"Planner", "Planner"),
        (r"Twitter|X\.", "Twitter/X"),
        (r"Outlook", "Outlook"),
    ]

    # Variable patterns
    SET_PATTERN = re.compile(r'Set\s*\(\s*(\w+)', re.IGNORECASE)
    UPDATE_CTX_PATTERN = re.compile(r'UpdateContext\s*\(\s*\{([^}]+)\}', re.IGNORECASE)
    COLLECT_PATTERN = re.compile(r'(?:Collect|ClearCollect)\s*\(\s*(\w+)', re.IGNORECASE)
    NAVIGATE_PATTERN = re.compile(r'Navigate\s*\(\s*([^,)]+)', re.IGNORECASE)
    NOTIFY_PATTERN = re.compile(r'Notify\s*\(\s*([^,)]+)', re.IGNORECASE)
    IFERROR_PATTERN = re.compile(r'IfError\s*\(', re.IGNORECASE)

    # Delegation risk heuristics
    DELEGATION_RISKY = [
        "CountRows", "CountIf", "Sum", "Average", "Min", "Max",
        "Collect", "ClearCollect", "AddColumns", "DropColumns",
        "ShowColumns", "RenameColumns", "Distinct", "GroupBy",
        "Ungroup", "First", "Last", "FirstN", "LastN",
    ]

    def parse(self, raw_yaml: str, mode: str = "auto") -> dict:
        """
        Main entry: parse raw YAML string into canonical model.
        
        Args:
            raw_yaml: YAML text or pre-parsed dict (from msapp).
            mode: "full", "fragment", or "auto" (default).
                  "auto" detects whether the input is a full app or a fragment.
        """
        # If raw_yaml is already a dict (from MsappParser), skip YAML parsing
        if isinstance(raw_yaml, dict):
            merged = raw_yaml
            unparsed = []
        else:
            # Detect mode if auto
            if mode == "auto":
                mode = self._detect_mode(raw_yaml)

            # Try to parse as YAML (may be multi-document)
            docs = []
            unparsed = []
            try:
                for doc in yaml.safe_load_all(raw_yaml):
                    if doc:
                        docs.append(doc)
            except yaml.YAMLError:
                try:
                    single = yaml.safe_load(raw_yaml)
                    if single:
                        docs = [single]
                except yaml.YAMLError as e:
                    docs = [self._fallback_parse(raw_yaml)]
                    unparsed.append({
                        "section": "root",
                        "reason": f"YAML parse error: {e}",
                        "raw_excerpt": raw_yaml[:500],
                    })

            if not docs:
                docs = [self._fallback_parse(raw_yaml)]

            # Merge all documents
            merged = {}
            for d in docs:
                if isinstance(d, dict):
                    merged.update(d)

            # If fragment mode, wrap the parsed data so it looks like a full app
            if mode == "fragment":
                merged = self._wrap_fragment(merged, raw_yaml if isinstance(raw_yaml, str) else "")

        # Extract everything
        model = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "parser_version": "1.1.0",
            "parse_mode": mode,
            "app_name": self._extract_app_name(merged, raw_yaml if isinstance(raw_yaml, str) else ""),
            "app_properties": self._extract_app_properties(merged),
            "screens": [],
            "controls_flat": [],
            "connectors": [],
            "data_sources": [],
            "variables": {"global_vars": [], "context_vars": [], "collections": []},
            "components": [],
            "forms": [],
            "navigation_graph": [],
            "formulas_all": [],
            "error_handling": [],
            "best_practice_findings": [],
            "stats": {},
            "unparsed": unparsed,
        }

        # Add msapp metadata if present
        if "_msapp_meta" in merged:
            model["msapp_meta"] = merged["_msapp_meta"]

        # Parse screens and controls
        self._extract_screens(merged, model, raw_yaml if isinstance(raw_yaml, str) else "")

        # Scan all formulas for connectors, variables, etc.
        all_formula_text = self._gather_all_formula_text(model)
        model["connectors"] = self._extract_connectors(all_formula_text, merged)
        model["data_sources"] = self._extract_data_sources(all_formula_text, merged)
        model["variables"] = self._extract_variables(model)
        model["navigation_graph"] = self._extract_navigation(model)
        model["error_handling"] = self._extract_error_handling(model)
        model["components"] = self._extract_components(merged, model)
        model["forms"] = self._extract_forms(model)

        # Best practice checks
        model["best_practice_findings"] = self._run_best_practice_checks(model, raw_yaml if isinstance(raw_yaml, str) else "")

        # Stats
        model["stats"] = self._compute_stats(model)

        return model

    # -----------------------------------------------------------------------
    # Fragment detection & wrapping
    # -----------------------------------------------------------------------

    def _detect_mode(self, raw: str) -> str:
        """
        Auto-detect if input is a full app export or a fragment.
        Returns "full" or "fragment".
        """
        if not raw or not raw.strip():
            return "full"

        text = raw.strip()

        # Strong indicators of a full app export
        full_indicators = [
            r'^\s*App\s*:', r'^\s*Screens\s*:', r'^\s*Connections\s*:',
            r'^\s*DataSources\s*:', r'^\s*Components\s*:',
        ]
        full_count = sum(1 for pat in full_indicators if re.search(pat, text, re.MULTILINE))
        if full_count >= 2:
            return "full"

        # If there's an App: key at the top level with nested Screens, it's full
        if re.match(r'^\s*App\s*:', text, re.MULTILINE) and re.search(r'^\s*Screens\s*:', text, re.MULTILINE):
            return "full"

        # Indicators of a fragment: starts with a control-like or screen-like definition
        # without the full App wrapper
        fragment_indicators = [
            # Single control definition: "btnSubmit:" or "galItems As gallery:"
            r'^\s*\w+\s+[Aa]s\s+(screen|gallery|form|button|label|textinput|dropdown|combobox|container|horizontalcontainer|verticalcontainer|component|image|icon|timer|checkbox|toggle|datatable)',
            # Bare control with Control: key
            r'^\s*\w+\s*:\s*\n\s+Control\s*:',
            # Just Properties block
            r'^\s*Properties\s*:\s*\n',
            # Single screen without Screens: wrapper
            r'^\s*\w+Screen\w*\s*:',
            # OnSelect/OnVisible/Items etc as top level (pure formula fragment)
            r'^\s*(OnSelect|OnVisible|OnHidden|OnStart|Items|Default|OnChange|OnSuccess|OnFailure)\s*:\s*[|>]?\s*\n',
            r'^\s*(OnSelect|OnVisible|OnHidden|OnStart|Items|Default|OnChange)\s*:\s*\S',
        ]
        for pat in fragment_indicators:
            if re.search(pat, text, re.MULTILINE):
                return "fragment"

        # If the top-level has only 1-2 keys and none are "App" or "Screens", likely fragment
        try:
            parsed = yaml.safe_load(text)
            if isinstance(parsed, dict):
                keys = set(parsed.keys())
                app_keys = {"App", "Screens", "Connections", "DataSources", "Components"}
                if not keys & app_keys and len(keys) <= 3:
                    return "fragment"
        except:
            pass

        return "full"

    def _wrap_fragment(self, data: dict, raw: str) -> dict:
        """
        Wrap a fragment (partial YAML) into a full-app-like structure.
        Handles: single screen, single control, bare properties, formula-only,
        and mixed sets of controls including those with children (gallery, form).
        """
        # Case 1: Data already has Screens/App keys -> treat as full
        if "Screens" in data or "App" in data:
            return data

        # Case 2: Classify each top-level key
        looks_like_screens = {}
        looks_like_controls = {}
        bare_props = {}

        # Known control types that have children but are NOT screens
        non_screen_parents = {
            "gallery", "form", "container", "horizontalcontainer",
            "verticalcontainer", "group", "component", "datatable",
        }

        for key, val in data.items():
            if not isinstance(val, dict):
                # Could be a formula property: "OnSelect: Navigate(...)"
                bare_props[key] = val
                continue

            has_children = any(k in val for k in ("Children", "Controls", "children", "controls"))
            has_control_key = "Control" in val or "control" in val
            ctrl_type = str(val.get("Control", val.get("control", ""))).lower().strip()

            # Explicitly a screen
            if ctrl_type == "screen":
                looks_like_screens[key] = val
            # Has a Control: key that is NOT "screen" -> always a control
            elif has_control_key and ctrl_type and ctrl_type != "screen":
                looks_like_controls[key] = val
            # Has children but Control key says it's a known parent type -> control
            elif has_children and ctrl_type in non_screen_parents:
                looks_like_controls[key] = val
            # Has children, no Control key, and looks like it could be a screen
            # (name ends with Screen, or has OnVisible/Fill properties)
            elif has_children and not has_control_key:
                props = val.get("Properties", val)
                has_screen_props = isinstance(props, dict) and any(
                    k in props for k in ("OnVisible", "OnHidden", "Fill", "ImagePosition")
                )
                name_looks_like_screen = key.lower().endswith("screen") or key.lower().startswith("screen")
                if has_screen_props or name_looks_like_screen:
                    looks_like_screens[key] = val
                else:
                    # Ambiguous: treat as control (safer for fragments)
                    looks_like_controls[key] = val
            elif has_control_key or "Properties" in val:
                looks_like_controls[key] = val
            elif self._dict_has_formula_keys(val):
                looks_like_controls[key] = {"Control": "Unknown", "Properties": val}
            else:
                looks_like_controls[key] = val

        # Merge: if we have both screens and controls, put controls in a synthetic screen
        if looks_like_screens and looks_like_controls:
            # Add controls as children of a synthetic fragment screen
            looks_like_screens["_FragmentControls"] = {
                "Control": "screen",
                "Properties": {},
                "Children": looks_like_controls,
            }
            return {
                "App": {"Name": "Fragment", "Properties": {}},
                "Screens": looks_like_screens,
            }

        if looks_like_screens:
            return {
                "App": {"Name": "Fragment", "Properties": {}},
                "Screens": looks_like_screens,
            }

        if looks_like_controls:
            return {
                "App": {"Name": "Fragment", "Properties": {}},
                "Screens": {
                    "_Fragment": {
                        "Control": "screen",
                        "Properties": {},
                        "Children": looks_like_controls,
                    }
                },
            }

        # Case 3: Top-level is just formula properties (OnSelect: ..., Items: ...)
        if bare_props:
            formula_keys = set(self.FORMULA_PROPERTIES)
            if any(k in formula_keys for k in bare_props):
                return {
                    "App": {"Name": "Fragment", "Properties": {}},
                    "Screens": {
                        "_Fragment": {
                            "Control": "screen",
                            "Properties": {},
                            "Children": {
                                "_FragmentControl": {
                                    "Control": "Unknown",
                                    "Properties": {k: str(v) for k, v in bare_props.items()},
                                }
                            },
                        }
                    },
                }

        # Fallback
        return {
            "App": {"Name": "Fragment", "Properties": {}},
            "Screens": {"_Fragment": data} if data else {},
        }

    def _dict_has_formula_keys(self, d: dict) -> bool:
        """Check if a dict's keys look like Power Apps formula properties."""
        formula_keys = set(self.FORMULA_PROPERTIES)
        return any(k in formula_keys for k in d.keys())

    # -----------------------------------------------------------------------
    # App-level extraction
    # -----------------------------------------------------------------------

    def _extract_app_name(self, data: dict, raw: str) -> str:
        """Try to find app name from various locations."""
        for key in ["AppName", "App.Name", "Name", "Properties.AppName"]:
            val = self._deep_get(data, key)
            if val and isinstance(val, str) and val != "Fragment":
                return val
        # Check if there is an App key
        app = data.get("App", {})
        if isinstance(app, dict):
            name = app.get("Name") or app.get("Properties", {}).get("Name")
            if name and name != "Fragment":
                return str(name)
        # Fallback: first line comment or filename hint
        if isinstance(raw, str):
            first_lines = raw[:200]
            m = re.search(r"#.*?App[:\s]+(.+)", first_lines)
            if m:
                return m.group(1).strip()
        return "Unbekannte App"

    def _extract_app_properties(self, data: dict) -> dict:
        """Extract app-level properties."""
        props = {}
        app = data.get("App", data)
        if isinstance(app, dict):
            for k in ["BackEnabled", "OnStart", "OnError", "Theme",
                       "StartScreen", "AppVersion", "DocumentVersion",
                       "Author", "LastModified", "Created"]:
                val = self._deep_get(app, k) or self._deep_get(app, f"Properties.{k}")
                if val is not None:
                    props[k] = str(val)
        return props

    # -----------------------------------------------------------------------
    # Screens & Controls
    # -----------------------------------------------------------------------

    def _extract_screens(self, data: dict, model: dict, raw_yaml: str):
        """Extract screens and their control trees."""
        screens_data = self._find_screens(data)

        # Also try to find screens from raw YAML with pattern matching
        if not screens_data:
            screens_data = self._find_screens_from_raw(raw_yaml)

        for idx, (screen_name, screen_data) in enumerate(screens_data):
            screen = {
                "name": screen_name,
                "index": idx,
                "purpose": "",  # user-editable
                "properties": {},
                "controls": [],
                "formulas": [],
            }

            if isinstance(screen_data, dict):
                # Extract screen properties
                props = screen_data.get("Properties", screen_data)
                if isinstance(props, dict):
                    for pk, pv in props.items():
                        if pk != "Children" and pk != "Controls":
                            screen["properties"][pk] = str(pv) if pv is not None else ""
                            # Check if it's a formula
                            sv = str(pv) if pv is not None else ""
                            if self._looks_like_formula(sv):
                                screen["formulas"].append({
                                    "property": pk,
                                    "formula": sv,
                                    "control": screen_name,
                                })
                                model["formulas_all"].append({
                                    "screen": screen_name,
                                    "control": screen_name,
                                    "property": pk,
                                    "formula": sv,
                                })

                # Extract children/controls
                children = (
                    screen_data.get("Children") or
                    screen_data.get("Controls") or
                    screen_data.get("children") or
                    screen_data.get("controls") or
                    []
                )
                if isinstance(children, dict):
                    children = list(children.items())
                elif isinstance(children, list):
                    pass

                self._extract_controls(children, screen, model, screen_name, screen_name)

            model["screens"].append(screen)

    def _find_screens(self, data: dict) -> list[tuple[str, dict]]:
        """Find screen definitions in parsed YAML data."""
        screens = []

        # Pattern 1: Top-level "Screens" key
        scr = data.get("Screens", data.get("screens", {}))
        if isinstance(scr, dict):
            for name, body in scr.items():
                if name not in ("App", "Properties"):
                    screens.append((name, body or {}))
            if screens:
                return screens

        # Pattern 2: List of screen objects
        if isinstance(scr, list):
            for item in scr:
                if isinstance(item, dict):
                    name = item.get("Name", item.get("name", f"Screen_{len(screens)}"))
                    screens.append((name, item))
            if screens:
                return screens

        # Pattern 3: Top-level keys that look like screens
        for key, val in data.items():
            if key in ("App", "Properties", "Connections", "DataSources",
                       "Components", "ComponentDefinitions", "Resources"):
                continue
            if isinstance(val, dict):
                # Heuristic: has Controls/Children or known screen properties
                has_children = any(k in val for k in ["Children", "Controls", "children", "controls"])
                has_props = isinstance(val.get("Properties"), dict)
                ctrl_type = str(val.get("Control", val.get("control", val.get("Type", "")))).lower()
                if has_children or has_props or ctrl_type == "screen":
                    screens.append((key, val))

        # Pattern 4: nested under "App.Screens" or similar
        app = data.get("App", {})
        if isinstance(app, dict):
            app_screens = app.get("Screens", app.get("screens", {}))
            if isinstance(app_screens, dict):
                for name, body in app_screens.items():
                    screens.append((name, body or {}))
            elif isinstance(app_screens, list):
                for item in app_screens:
                    if isinstance(item, dict):
                        name = item.get("Name", f"Screen_{len(screens)}")
                        screens.append((name, item))

        return screens

    def _find_screens_from_raw(self, raw: str) -> list[tuple[str, dict]]:
        """Fallback: extract screen names from raw YAML text."""
        screens = []
        # Look for patterns like "ScreenName As screen:" or "ScreenName:"
        pattern = re.compile(r'^(\w[\w\s]*?)\s+[Aa]s\s+screen\s*[.:]', re.MULTILINE)
        for m in pattern.finditer(raw):
            screens.append((m.group(1).strip(), {}))

        if not screens:
            # Try simpler pattern
            pattern2 = re.compile(r'^(\w+Screen\w*)\s*:', re.MULTILINE)
            for m in pattern2.finditer(raw):
                screens.append((m.group(1).strip(), {}))

        return screens

    def _extract_controls(self, children, screen: dict, model: dict,
                          screen_name: str, parent_name: str):
        """Recursively extract controls."""
        if isinstance(children, dict):
            items = list(children.items())
        elif isinstance(children, list):
            items = []
            for c in children:
                if isinstance(c, dict):
                    name = c.get("Name", c.get("name", f"Control_{len(screen['controls'])}"))
                    items.append((name, c))
                elif isinstance(c, tuple) and len(c) == 2:
                    items.append(c)
        else:
            return

        for ctrl_name, ctrl_data in items:
            if not isinstance(ctrl_data, dict):
                ctrl_data = {}

            ctrl_type = str(
                ctrl_data.get("Control", ctrl_data.get("control",
                ctrl_data.get("Type", ctrl_data.get("type", "Unknown"))))
            ).strip()

            # Clean "As <type>" patterns
            if " As " in ctrl_name or " as " in ctrl_name:
                parts = re.split(r'\s+[Aa]s\s+', ctrl_name, 1)
                if len(parts) == 2:
                    ctrl_name = parts[0].strip()
                    if ctrl_type in ("Unknown", ""):
                        ctrl_type = parts[1].strip().rstrip(":")

            control = {
                "name": ctrl_name,
                "type": ctrl_type,
                "parent": parent_name,
                "screen": screen_name,
                "properties": {},
                "formulas": [],
            }

            # Extract properties
            props = ctrl_data.get("Properties", ctrl_data)
            if isinstance(props, dict):
                for pk, pv in props.items():
                    if pk in ("Children", "Controls", "children", "controls", "Properties"):
                        continue
                    sv = str(pv) if pv is not None else ""
                    control["properties"][pk] = sv
                    if self._looks_like_formula(sv) or pk in self.FORMULA_PROPERTIES:
                        control["formulas"].append({
                            "property": pk,
                            "formula": sv,
                            "control": ctrl_name,
                        })
                        model["formulas_all"].append({
                            "screen": screen_name,
                            "control": ctrl_name,
                            "property": pk,
                            "formula": sv,
                        })

            screen["controls"].append(control)
            model["controls_flat"].append(control)

            # Recurse into children
            sub_children = (
                ctrl_data.get("Children") or
                ctrl_data.get("Controls") or
                ctrl_data.get("children") or
                ctrl_data.get("controls") or
                (props.get("Children") if isinstance(props, dict) else None) or
                []
            )
            if sub_children:
                self._extract_controls(sub_children, screen, model, screen_name, ctrl_name)

    # -----------------------------------------------------------------------
    # Connectors & Data Sources
    # -----------------------------------------------------------------------

    def _extract_connectors(self, formula_text: str, data: dict) -> list[dict]:
        """Extract connectors from formulas and YAML structure."""
        connectors = {}

        # From YAML structure
        for key in ("Connections", "DataSources", "ConnectorReferences",
                     "connections", "datasources"):
            section = data.get(key, {})
            if isinstance(section, dict):
                for name, details in section.items():
                    connectors[name] = {
                        "name": name,
                        "type": self._classify_connector(name),
                        "details": {k: str(v) for k, v in (details or {}).items()}
                        if isinstance(details, dict) else {},
                    }
            elif isinstance(section, list):
                for item in section:
                    if isinstance(item, dict):
                        name = item.get("Name", item.get("name", str(item)))
                        connectors[name] = {
                            "name": name,
                            "type": self._classify_connector(name),
                            "details": item,
                        }

        # From formula text
        for pattern, ctype in self.CONNECTOR_PATTERNS:
            for m in re.finditer(pattern, formula_text):
                name = m.group(0)[:60]
                if name not in connectors:
                    connectors[name] = {
                        "name": name,
                        "type": ctype,
                        "details": {},
                    }

        return list(connectors.values())

    def _extract_data_sources(self, formula_text: str, data: dict) -> list[dict]:
        """Extract referenced data sources (SharePoint lists, Dataverse tables, etc.)."""
        sources = {}

        # 'DataSourceName'.ColumnName pattern
        for m in re.finditer(r"'([^']+)'", formula_text):
            ds_name = m.group(1)
            if len(ds_name) > 2 and not ds_name.startswith("#"):
                if ds_name not in sources:
                    sources[ds_name] = {
                        "name": ds_name,
                        "columns_referenced": set(),
                    }
                # Try to find column references after this
                after = formula_text[m.end():m.end()+200]
                col_match = re.match(r'\s*\.\s*(\w+)', after)
                if col_match:
                    sources[ds_name]["columns_referenced"].add(col_match.group(1))

        # Collect more column references
        for ds_name in list(sources.keys()):
            pattern = re.compile(re.escape(f"'{ds_name}'") + r'\s*\.\s*(\w+)')
            for m in pattern.finditer(formula_text):
                sources[ds_name]["columns_referenced"].add(m.group(1))

        # Convert sets to lists
        for s in sources.values():
            s["columns_referenced"] = sorted(s["columns_referenced"])

        return list(sources.values())

    def _classify_connector(self, name: str) -> str:
        """Classify a connector name."""
        name_lower = name.lower()
        for keyword, ctype in [
            ("sharepoint", "SharePoint"),
            ("dataverse", "Dataverse"),
            ("sql", "SQL Server"),
            ("office365user", "Office365Users"),
            ("office365outlook", "Office365Outlook"),
            ("flow", "Power Automate"),
            ("http", "HTTP"),
            ("azuread", "Azure AD"),
            ("teams", "Microsoft Teams"),
            ("excel", "Excel Online"),
            ("planner", "Planner"),
            ("approval", "Approvals"),
        ]:
            if keyword in name_lower:
                return ctype
        return "Custom/Other"

    # -----------------------------------------------------------------------
    # Variables & Collections
    # -----------------------------------------------------------------------

    def _extract_variables(self, model: dict) -> dict:
        """Extract global vars, context vars, and collections from formulas."""
        global_vars = {}
        context_vars = {}
        collections = {}

        for f in model["formulas_all"]:
            text = f["formula"]
            location = f"{f['screen']}.{f['control']}.{f['property']}"

            # Global variables: Set(varName, ...)
            for m in self.SET_PATTERN.finditer(text):
                vname = m.group(1)
                if vname not in global_vars:
                    global_vars[vname] = {"name": vname, "locations": [], "initialized_in": []}
                global_vars[vname]["locations"].append(location)
                if "OnStart" in f["property"] or "OnVisible" in f["property"]:
                    global_vars[vname]["initialized_in"].append(location)

            # Context variables: UpdateContext({var1: ..., var2: ...})
            for m in self.UPDATE_CTX_PATTERN.finditer(text):
                block = m.group(1)
                for vm in re.finditer(r'(\w+)\s*:', block):
                    vname = vm.group(1)
                    if vname not in context_vars:
                        context_vars[vname] = {"name": vname, "locations": [], "screen": f["screen"]}
                    context_vars[vname]["locations"].append(location)

            # Collections: Collect/ClearCollect(colName, ...)
            for m in self.COLLECT_PATTERN.finditer(text):
                cname = m.group(1)
                if cname not in collections:
                    collections[cname] = {"name": cname, "locations": [], "initialized_in": [], "shape_hint": ""}
                collections[cname]["locations"].append(location)
                if "OnStart" in f["property"] or "OnVisible" in f["property"]:
                    collections[cname]["initialized_in"].append(location)
                # Try to infer shape
                after_match = re.search(
                    re.escape(f"ClearCollect({cname},") + r'\s*\{([^}]+)\}',
                    text, re.IGNORECASE
                )
                if after_match:
                    collections[cname]["shape_hint"] = after_match.group(1).strip()

        return {
            "global_vars": list(global_vars.values()),
            "context_vars": list(context_vars.values()),
            "collections": list(collections.values()),
        }

    # -----------------------------------------------------------------------
    # Navigation
    # -----------------------------------------------------------------------

    def _extract_navigation(self, model: dict) -> list[dict]:
        """Build navigation graph from Navigate() calls."""
        nav = []
        for f in model["formulas_all"]:
            for m in self.NAVIGATE_PATTERN.finditer(f["formula"]):
                target = m.group(1).strip().strip("'\"")
                nav.append({
                    "from_screen": f["screen"],
                    "to_screen": target,
                    "trigger_control": f["control"],
                    "trigger_property": f["property"],
                })
        return nav

    # -----------------------------------------------------------------------
    # Error handling
    # -----------------------------------------------------------------------

    def _extract_error_handling(self, model: dict) -> list[dict]:
        """Find Notify, IfError, and similar patterns."""
        patterns = []
        for f in model["formulas_all"]:
            text = f["formula"]
            if self.IFERROR_PATTERN.search(text):
                patterns.append({
                    "type": "IfError",
                    "location": f"{f['screen']}.{f['control']}.{f['property']}",
                    "excerpt": text[:200],
                })
            for m in self.NOTIFY_PATTERN.finditer(text):
                patterns.append({
                    "type": "Notify",
                    "location": f"{f['screen']}.{f['control']}.{f['property']}",
                    "message_hint": m.group(1).strip()[:100],
                })
        return patterns

    # -----------------------------------------------------------------------
    # Components
    # -----------------------------------------------------------------------

    def _extract_components(self, data: dict, model: dict) -> list[dict]:
        """Extract component definitions."""
        components = []
        comp_section = (
            data.get("Components") or data.get("ComponentDefinitions") or
            data.get("components") or {}
        )

        if isinstance(comp_section, dict):
            for name, body in comp_section.items():
                comp = {
                    "name": name,
                    "properties_in": [],
                    "properties_out": [],
                    "used_in_screens": [],
                    "logic_summary": "",
                }
                if isinstance(body, dict):
                    for k, v in body.items():
                        if "input" in k.lower() or "parameter" in k.lower():
                            comp["properties_in"].append(k)
                        elif "output" in k.lower():
                            comp["properties_out"].append(k)
                components.append(comp)
        elif isinstance(comp_section, list):
            for item in comp_section:
                if isinstance(item, dict):
                    name = item.get("Name", item.get("name", "Component"))
                    components.append({
                        "name": name,
                        "properties_in": [],
                        "properties_out": [],
                        "used_in_screens": [],
                        "logic_summary": "",
                    })

        # Find where components are used
        for comp in components:
            for ctrl in model["controls_flat"]:
                if comp["name"].lower() in ctrl["type"].lower():
                    comp["used_in_screens"].append(ctrl["screen"])

        return components

    # -----------------------------------------------------------------------
    # Forms
    # -----------------------------------------------------------------------

    def _extract_forms(self, model: dict) -> list[dict]:
        """Extract form controls and their data cards."""
        forms = []
        for ctrl in model["controls_flat"]:
            ctrl_type = ctrl["type"].lower()
            if "form" in ctrl_type and "format" not in ctrl_type:
                form = {
                    "name": ctrl["name"],
                    "screen": ctrl["screen"],
                    "mode": ctrl["properties"].get("DefaultMode", "Unknown"),
                    "data_source": ctrl["properties"].get("DataSource", "Unknown"),
                    "data_cards": [],
                }
                # Find child DataCards
                for child in model["controls_flat"]:
                    if child["parent"] == ctrl["name"] and "card" in child["type"].lower():
                        card = {
                            "name": child["name"],
                            "field": child["properties"].get("DataField", ""),
                            "default": child["properties"].get("Default", ""),
                            "update": child["properties"].get("Update", ""),
                        }
                        form["data_cards"].append(card)
                forms.append(form)
        return forms

    # -----------------------------------------------------------------------
    # Best Practice Checks (heuristic/lint-like)
    # -----------------------------------------------------------------------

    def _run_best_practice_checks(self, model: dict, raw: str) -> list[dict]:
        """Run heuristic best-practice checks."""
        findings = []

        # 1. Delegation risks
        for f in model["formulas_all"]:
            text = f["formula"]
            for risky_fn in self.DELEGATION_RISKY:
                if re.search(rf'\b{risky_fn}\b', text):
                    # Check if used with a data source
                    if re.search(r"'[^']+'\s*[,)]", text):
                        findings.append({
                            "type": "delegation_risk",
                            "severity": "warning",
                            "message_de": f"Mögliches Delegierungsproblem: {risky_fn} in {f['screen']}.{f['control']}.{f['property']}",
                            "message_en": f"Potential delegation issue: {risky_fn} in {f['screen']}.{f['control']}.{f['property']}",
                            "location": f"{f['screen']}.{f['control']}.{f['property']}",
                        })
                        break

        # 2. Excessive OnStart load
        onstart_collects = 0
        for f in model["formulas_all"]:
            if "OnStart" in f["property"]:
                onstart_collects += len(self.COLLECT_PATTERN.findall(f["formula"]))
        if onstart_collects > 5:
            findings.append({
                "type": "performance",
                "severity": "warning",
                "message_de": f"Übermäßige OnStart-Last: {onstart_collects} Collect/ClearCollect-Aufrufe in OnStart erkannt.",
                "message_en": f"Excessive OnStart load: {onstart_collects} Collect/ClearCollect calls detected in OnStart.",
                "location": "App.OnStart",
            })

        # 3. Hard-coded URLs
        url_pattern = re.compile(r'https?://[^\s"\'<>,;)]+', re.IGNORECASE)
        for f in model["formulas_all"]:
            for m in url_pattern.finditer(f["formula"]):
                url = m.group(0)
                if not any(x in url for x in ["schema.org", "example.com"]):
                    findings.append({
                        "type": "hardcoded_value",
                        "severity": "info",
                        "message_de": f"Hartcodierte URL gefunden: {url[:80]} in {f['control']}",
                        "message_en": f"Hard-coded URL found: {url[:80]} in {f['control']}",
                        "location": f"{f['screen']}.{f['control']}.{f['property']}",
                    })

        # 4. Naming convention checks
        bad_names = []
        for ctrl in model["controls_flat"]:
            name = ctrl["name"]
            # Check for default names like "Button1", "Label3"
            if re.match(r'^(Button|Label|TextInput|Gallery|Icon|Image|Rectangle|Form|DataCard|Timer)\d+$', name):
                bad_names.append(name)
        if bad_names:
            sample = bad_names[:10]
            findings.append({
                "type": "naming_convention",
                "severity": "info",
                "message_de": f"Standard-Kontrollnamen erkannt ({len(bad_names)} Stück): {', '.join(sample)}{'...' if len(bad_names) > 10 else ''}",
                "message_en": f"Default control names detected ({len(bad_names)} total): {', '.join(sample)}{'...' if len(bad_names) > 10 else ''}",
                "location": "global",
            })

        # 5. Screen naming
        for s in model["screens"]:
            if re.match(r'^Screen\d*$', s["name"]):
                findings.append({
                    "type": "naming_convention",
                    "severity": "info",
                    "message_de": f"Screen mit Standardname: '{s['name']}' – Beschreibender Name empfohlen.",
                    "message_en": f"Screen with default name: '{s['name']}' – Consider descriptive naming.",
                    "location": s["name"],
                })

        # 6. DLP risk flags (risky connectors)
        risky_connectors = {"HTTP", "SQL Server", "Custom/Other"}
        for conn in model["connectors"]:
            if conn["type"] in risky_connectors:
                findings.append({
                    "type": "security",
                    "severity": "warning",
                    "message_de": f"DLP-relevanter Konnektor: {conn['name']} ({conn['type']})",
                    "message_en": f"DLP-relevant connector: {conn['name']} ({conn['type']})",
                    "location": "Konnektoren",
                })

        # 7. Unused variables (heuristic)
        all_text = " ".join(f["formula"] for f in model["formulas_all"])
        for gv in model["variables"]["global_vars"]:
            count = all_text.count(gv["name"])
            if count <= len(gv["locations"]):
                findings.append({
                    "type": "unused",
                    "severity": "info",
                    "message_de": f"Möglicherweise ungenutzte Variable: {gv['name']}",
                    "message_en": f"Potentially unused variable: {gv['name']}",
                    "location": ", ".join(gv["locations"][:3]),
                })

        return findings

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------

    def _gather_all_formula_text(self, model: dict) -> str:
        """Concatenate all formula text for scanning."""
        return " ".join(f["formula"] for f in model["formulas_all"])

    def _looks_like_formula(self, text: str) -> bool:
        """Heuristic: does this string look like a Power Fx formula?"""
        if not text or len(text) < 3:
            return False
        indicators = [
            "(", ".", "If(", "Set(", "Navigate(", "Filter(", "LookUp(",
            "Collect(", "ClearCollect(", "UpdateContext(", "Notify(",
            "Patch(", "Remove(", "SubmitForm(", "ResetForm(", "Refresh(",
            "=", "&&", "||", "!", ";", "//",
        ]
        return any(ind in text for ind in indicators)

    def _deep_get(self, data: dict, dotted_key: str) -> Any:
        """Get nested dict value with dotted key."""
        keys = dotted_key.split(".")
        current = data
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        return current

    def _compute_stats(self, model: dict) -> dict:
        """Compute summary statistics."""
        type_counts = {}
        for ctrl in model["controls_flat"]:
            t = ctrl["type"]
            type_counts[t] = type_counts.get(t, 0) + 1

        return {
            "total_screens": len(model["screens"]),
            "total_controls": len(model["controls_flat"]),
            "total_formulas": len(model["formulas_all"]),
            "total_connectors": len(model["connectors"]),
            "total_data_sources": len(model["data_sources"]),
            "total_global_vars": len(model["variables"]["global_vars"]),
            "total_context_vars": len(model["variables"]["context_vars"]),
            "total_collections": len(model["variables"]["collections"]),
            "total_components": len(model["components"]),
            "total_forms": len(model["forms"]),
            "total_navigation_links": len(model["navigation_graph"]),
            "total_error_patterns": len(model["error_handling"]),
            "total_findings": len(model["best_practice_findings"]),
            "control_type_counts": type_counts,
        }

    def _fallback_parse(self, raw: str) -> dict:
        """Last-resort: try to extract key-value pairs from raw text."""
        result = {}
        lines = raw.split("\n")
        current_key = None
        for line in lines:
            m = re.match(r'^(\w[\w\s]*?):\s*(.*)', line)
            if m:
                current_key = m.group(1).strip()
                val = m.group(2).strip()
                result[current_key] = val if val else {}
        return result
