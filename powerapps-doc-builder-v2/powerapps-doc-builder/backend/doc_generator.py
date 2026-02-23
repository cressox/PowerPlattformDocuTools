"""
Documentation Generator
=======================
Generates Markdown, HTML, JSON, and LaTeX from the canonical app_model.json.
All headings in German. Code comments in English.
"""

from __future__ import annotations
import json, re, html as html_lib
from pathlib import Path
from datetime import datetime, timezone
from typing import Any


class DocGenerator:
    """Generate documentation in multiple formats from the canonical model."""

    def __init__(self, model: dict, project: dict, output_dir: Path, images_dir: Path):
        self.m = model
        self.p = project
        self.out = output_dir
        self.img_dir = images_dir
        self.notes = project.get("manual_notes", {})
        self.settings = project.get("settings", {})
        self.screenshot_map = project.get("screenshot_map", {})
        self.redact = self.settings.get("redact_ids", True)
        self.timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        self.is_fragment = model.get("parse_mode") == "fragment"
        self.input_type = model.get("input_type", "yaml")

    # ===================================================================
    # REDACTION
    # ===================================================================

    def _redact(self, text: str) -> str:
        """Redact sensitive IDs if enabled."""
        if not self.redact:
            return text
        # Environment GUIDs
        text = re.sub(
            r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}',
            '[REDACTED-GUID]', text
        )
        # Connection IDs / long hex strings
        text = re.sub(r'[0-9a-fA-F]{24,}', '[REDACTED-ID]', text)
        return text

    def _truncate(self, text: str, max_len: int = 300) -> tuple[str, bool]:
        """Truncate formula text, return (text, was_truncated)."""
        if len(text) <= max_len:
            return text, False
        return text[:max_len] + "...", True

    # ===================================================================
    # MARKDOWN
    # ===================================================================

    def generate_markdown(self):
        """Generate docs.md."""
        lines = []
        a = lines.append  # shortcut

        a(f"# {self._redact(self.m.get('app_name', 'Power App'))} – Dokumentation")
        a(f"\n> Generiert am: {self.timestamp}  ")
        a(f"> Parser-Version: {self.m.get('parser_version', '?')}")
        if self.input_type == "msapp":
            a(f"> Quelle: .msapp-Datei")
        if self.is_fragment:
            a(f"> Modus: **Fragment** (partieller YAML-Import)")
        a("")

        if self.is_fragment:
            a("> ℹ️ **Hinweis:** Diese Dokumentation wurde aus einem YAML-Fragment generiert (z.B. einzelner Bildschirm oder Kontrollelement). Nicht alle Abschnitte sind verfügbar.\n")

        if self.input_type == "msapp" and self.m.get("msapp_meta"):
            meta = self.m["msapp_meta"]
            if meta.get("parse_errors"):
                for err in meta["parse_errors"]:
                    a(f"> ⚠️ MSAPP-Hinweis: {err}\n")


        # Table of contents
        a("## Inhaltsverzeichnis\n")
        toc = [
            "1. [App-Übersicht](#1-app-übersicht)",
            "2. [Architektur / High-Level-Design](#2-architektur--high-level-design)",
            "3. [Bildschirm-Dokumentation](#3-bildschirm-dokumentation)",
            "4. [Kontroll-Inventar](#4-kontroll-inventar)",
            "5. [Datenquellen & Konnektoren](#5-datenquellen--konnektoren)",
            "6. [Variablen & Sammlungen](#6-variablen--sammlungen)",
            "7. [Komponenten](#7-komponenten)",
            "8. [Formulare & Datenkarten](#8-formulare--datenkarten)",
            "9. [Sicherheit & Governance](#9-sicherheit--governance)",
            "10. [Fehlerbehandlung & Benutzer-Feedback](#10-fehlerbehandlung--benutzer-feedback)",
            "11. [ALM / Deployment-Hinweise](#11-alm--deployment-hinweise)",
            "12. [Best-Practice-Prüfungen](#12-best-practice-prüfungen)",
            "13. [Änderungsprotokoll](#13-änderungsprotokoll)",
            "14. [Nicht interpretierte Abschnitte](#14-nicht-interpretierte-abschnitte)",
        ]
        for t in toc:
            a(t)
        a("")

        # --- 1. App Overview ---
        a("## 1. App-Übersicht\n")
        if not self.is_fragment:
            a(f"| Eigenschaft | Wert |")
            a(f"|---|---|")
            a(f"| **App-Name** | {self._redact(self.m.get('app_name', '-'))} |")
            props = self.m.get("app_properties", {})
            a(f"| **Version** | {props.get('AppVersion', props.get('DocumentVersion', '-'))} |")
            a(f"| **Autor** | {props.get('Author', '-')} |")
            a(f"| **Letzte Änderung** | {props.get('LastModified', '-')} |")
            a(f"| **Bildschirme** | {self.m['stats']['total_screens']} |")
            a(f"| **Kontrollelemente** | {self.m['stats']['total_controls']} |")
            a(f"| **Formeln** | {self.m['stats']['total_formulas']} |")
            a(f"| **Konnektoren** | {self.m['stats']['total_connectors']} |")
            if self.input_type == "msapp":
                a(f"| **Quelle** | .msapp-Datei |")
                if self.m.get("msapp_meta", {}).get("raw_files"):
                    a(f"| **Dateien im Paket** | {len(self.m['msapp_meta']['raw_files'])} |")
        else:
            a(f"| Eigenschaft | Wert |")
            a(f"|---|---|")
            a(f"| **Modus** | Fragment-Dokumentation |")
            a(f"| **Kontrollelemente** | {self.m['stats']['total_controls']} |")
            a(f"| **Formeln** | {self.m['stats']['total_formulas']} |")
        a("")
        if self.notes.get("purpose"):
            a(f"**Zweck / Geschäftskontext:** {self.notes['purpose']}\n")
        if self.notes.get("intended_users"):
            a(f"**Zielbenutzer & Rollen:** {self.notes['intended_users']}\n")
        if self.notes.get("environments"):
            a(f"**Umgebungen (DEV/TEST/PROD):** {self.notes['environments']}\n")

        # Dependencies summary
        a("### Abhängigkeiten\n")
        if self.m["connectors"]:
            for c in self.m["connectors"]:
                a(f"- **{c['name']}** ({c['type']})")
        else:
            a("_Keine Konnektoren erkannt._")
        a("")

        # --- 2. Architecture ---
        a("## 2. Architektur / High-Level-Design\n")
        a("### Bildschirm-Navigationsgraph\n")
        a("```")
        if self.m["navigation_graph"]:
            seen = set()
            for nav in self.m["navigation_graph"]:
                link = f"{nav['from_screen']} --> {nav['to_screen']}  [{nav['trigger_control']}]"
                if link not in seen:
                    a(link)
                    seen.add(link)
        else:
            a("Keine Navigate()-Aufrufe erkannt.")
        a("```\n")

        a("### Datenzugriffsansatz\n")
        if self.m["data_sources"]:
            for ds in self.m["data_sources"]:
                cols = ", ".join(ds["columns_referenced"][:10]) if ds["columns_referenced"] else "-"
                a(f"- **{ds['name']}** – Referenzierte Spalten: {cols}")
        else:
            a("_Keine expliziten Datenquellen erkannt._")
        a("")

        a("### Integrationspunkte\n")
        flows = [c for c in self.m["connectors"] if "automate" in c["type"].lower() or "flow" in c["name"].lower()]
        http = [c for c in self.m["connectors"] if "http" in c["type"].lower()]
        if flows:
            a(f"- **Power Automate Flows:** {', '.join(f['name'] for f in flows)}")
        if http:
            a(f"- **HTTP-Aufrufe:** {', '.join(h['name'][:50] for h in http)}")
        if not flows and not http:
            a("_Keine externen Integrationspunkte erkannt._")
        a("")

        # Delegation warnings summary
        deleg = [f for f in self.m["best_practice_findings"] if f["type"] == "delegation_risk"]
        if deleg:
            a("### Delegierungsrisiken (Performance)\n")
            for d in deleg:
                a(f"- ⚠️ {d['message_de']}")
            a("")

        # --- 3. Screens Documentation ---
        a("## 3. Bildschirm-Dokumentation\n")
        for scr in self.m["screens"]:
            a(f"### 3.{scr['index']+1}. {scr['name']}\n")

            # Screenshot
            img_file = self.screenshot_map.get(scr["name"])
            if img_file:
                a(f"![{scr['name']}](../data/images/{img_file})\n")

            # Purpose
            purpose = scr.get("purpose") or "_Noch nicht beschrieben._"
            a(f"**Zweck:** {purpose}\n")

            # Key controls
            if scr["controls"]:
                a("#### Kontrollelemente\n")
                a("| Name | Typ | Übergeordnet |")
                a("|---|---|---|")
                for ctrl in scr["controls"]:
                    a(f"| {ctrl['name']} | {ctrl['type']} | {ctrl['parent']} |")
                a("")

            # Data bindings & formulas
            bindings = [f for f in scr["formulas"]
                        if f["property"] in ("Items", "Default", "Update", "OnVisible", "OnHidden")]
            bindings += [f for ctrl in scr["controls"] for f in ctrl["formulas"]
                         if f["property"] in ("Items", "Default", "Update", "OnVisible", "OnHidden")]
            if bindings:
                a("#### Datenbindungen\n")
                for b in bindings:
                    trunc, was_trunc = self._truncate(self._redact(b["formula"]))
                    a(f"- **{b['control']}.{b['property']}:** `{trunc}`")
                    if was_trunc:
                        a(f"  <details><summary>Vollständige Formel</summary>\n\n  ```\n  {self._redact(b['formula'])}\n  ```\n  </details>\n")
                a("")

            # Navigation
            screen_nav = [n for n in self.m["navigation_graph"] if n["from_screen"] == scr["name"]]
            if screen_nav:
                a("#### Navigation\n")
                for n in screen_nav:
                    a(f"- → **{n['to_screen']}** (ausgelöst durch: {n['trigger_control']})")
                a("")

            # Business logic
            logic = [f for ctrl in scr["controls"] for f in ctrl["formulas"]
                     if f["property"] in ("OnSelect", "OnChange", "OnCheck", "OnUncheck")]
            if logic:
                a("#### Geschäftslogik\n")
                for l in logic:
                    trunc, was_trunc = self._truncate(self._redact(l["formula"]), 200)
                    a(f"- **{l['control']}.{l['property']}:** `{trunc}`")
                    if was_trunc:
                        a(f"  <details><summary>Vollständige Formel</summary>\n\n  ```\n  {self._redact(l['formula'])}\n  ```\n  </details>\n")
                a("")

        # --- 4. Control Inventory ---
        a("## 4. Kontroll-Inventar\n")
        a("### Typ-Übersicht\n")
        type_counts = self.m["stats"].get("control_type_counts", {})
        if type_counts:
            a("| Typ | Anzahl |")
            a("|---|---|")
            for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
                a(f"| {t} | {c} |")
        a("")

        a("### Wichtige Kontrollelemente (Details)\n")
        major_types = {"gallery", "form", "component", "button", "datatable"}
        major_controls = [c for c in self.m["controls_flat"]
                          if any(mt in c["type"].lower() for mt in major_types)]
        if major_controls:
            for ctrl in major_controls[:50]:  # limit
                a(f"#### {ctrl['name']} ({ctrl['type']})\n")
                a(f"- **Bildschirm:** {ctrl['screen']}")
                a(f"- **Übergeordnet:** {ctrl['parent']}")
                for pk in ("Items", "Default", "Visible", "DisplayMode", "OnSelect", "OnChange", "Update", "Text"):
                    val = ctrl["properties"].get(pk, "")
                    if val:
                        trunc, _ = self._truncate(self._redact(val), 150)
                        a(f"- **{pk}:** `{trunc}`")
                a("")

        # --- 5. Data Sources ---
        a("## 5. Datenquellen & Konnektoren\n")
        a("### Konnektoren\n")
        if self.m["connectors"]:
            a("| Name | Typ | Details |")
            a("|---|---|---|")
            for c in self.m["connectors"]:
                det = json.dumps(c.get("details", {}), ensure_ascii=False)[:100] if c.get("details") else "-"
                a(f"| {self._redact(c['name'])} | {c['type']} | {self._redact(det)} |")
        else:
            a("_Keine Konnektoren erkannt._")
        a("")

        a("### Datenquellen\n")
        if self.m["data_sources"]:
            for ds in self.m["data_sources"]:
                a(f"- **{ds['name']}**")
                if ds["columns_referenced"]:
                    a(f"  - Referenzierte Spalten: {', '.join(ds['columns_referenced'])}")
        else:
            a("_Keine expliziten Datenquellen erkannt._")
        a("")

        a("### Berechtigungshinweise\n")
        a("_Bitte manuell ergänzen: Welche Berechtigungen werden zum Ausführen der App benötigt?_\n")

        # --- 6. Variables ---
        a("## 6. Variablen & Sammlungen\n")
        vars_ = self.m["variables"]

        a("### Globale Variablen (Set)\n")
        if vars_["global_vars"]:
            a("| Name | Initialisiert in | Weitere Verwendung |")
            a("|---|---|---|")
            for v in vars_["global_vars"]:
                init = ", ".join(v["initialized_in"][:3]) or "-"
                locs = ", ".join(v["locations"][:3])
                a(f"| `{v['name']}` | {init} | {locs} |")
        else:
            a("_Keine globalen Variablen erkannt._")
        a("")

        a("### Kontext-Variablen (UpdateContext)\n")
        if vars_["context_vars"]:
            a("| Name | Bildschirm | Verwendung |")
            a("|---|---|---|")
            for v in vars_["context_vars"]:
                locs = ", ".join(v["locations"][:3])
                a(f"| `{v['name']}` | {v.get('screen', '-')} | {locs} |")
        else:
            a("_Keine Kontext-Variablen erkannt._")
        a("")

        a("### Sammlungen (Collections)\n")
        if vars_["collections"]:
            a("| Name | Initialisiert in | Datenform-Hinweis |")
            a("|---|---|---|")
            for v in vars_["collections"]:
                init = ", ".join(v["initialized_in"][:3]) or "-"
                shape = v.get("shape_hint", "-") or "-"
                a(f"| `{v['name']}` | {init} | {self._truncate(shape, 80)[0]} |")
        else:
            a("_Keine Sammlungen erkannt._")
        a("")

        # --- 7. Components ---
        a("## 7. Komponenten\n")
        if self.m["components"]:
            for comp in self.m["components"]:
                a(f"### {comp['name']}\n")
                a(f"- **Eingabe-Eigenschaften:** {', '.join(comp['properties_in']) or '-'}")
                a(f"- **Ausgabe-Eigenschaften:** {', '.join(comp['properties_out']) or '-'}")
                used = list(set(comp.get("used_in_screens", [])))
                a(f"- **Verwendet in:** {', '.join(used) or '-'}")
                a("")
        else:
            a("_Keine Komponenten erkannt._\n")

        # --- 8. Forms ---
        a("## 8. Formulare & Datenkarten\n")
        if self.m["forms"]:
            for form in self.m["forms"]:
                a(f"### {form['name']} ({form['screen']})\n")
                a(f"- **Modus:** {form['mode']}")
                a(f"- **Datenquelle:** {form['data_source']}")
                if form["data_cards"]:
                    a("| DataCard | Feld | Default | Update |")
                    a("|---|---|---|---|")
                    for dc in form["data_cards"]:
                        a(f"| {dc['name']} | {dc['field']} | {self._truncate(dc['default'], 60)[0]} | {self._truncate(dc['update'], 60)[0]} |")
                a("")
        else:
            a("_Keine Formulare erkannt._\n")

        # --- 9. Security ---
        a("## 9. Sicherheit & Governance\n")
        a("### Rollenkonzept\n")
        a(self.notes.get("roles", "_Bitte manuell ergänzen._") + "\n")
        a("### DLP-Überlegungen\n")
        sec_findings = [f for f in self.m["best_practice_findings"] if f["type"] == "security"]
        if sec_findings:
            for sf in sec_findings:
                a(f"- ⚠️ {sf['message_de']}")
        else:
            a("_Keine DLP-relevanten Befunde._")
        a("")
        a("### Konnektor-/Datenklassifizierung\n")
        a(self.notes.get("connector_classification", "_Bitte manuell ergänzen._") + "\n")
        a(self.notes.get("security_notes", "") + "\n")

        # --- 10. Error Handling ---
        a("## 10. Fehlerbehandlung & Benutzer-Feedback\n")
        if self.m["error_handling"]:
            a("| Typ | Ort | Details |")
            a("|---|---|---|")
            for eh in self.m["error_handling"]:
                detail = eh.get("message_hint", eh.get("excerpt", "-"))
                a(f"| {eh['type']} | {eh['location']} | {self._truncate(self._redact(str(detail)), 80)[0]} |")
        else:
            a("_Keine Fehlerbehandlungsmuster erkannt._")
        a("")

        # --- 11. ALM ---
        a("## 11. ALM / Deployment-Hinweise\n")
        a(self.notes.get("alm_notes", "_Bitte manuell ergänzen: Export-/Import-Verfahren, Solution-Packaging, Umgebungskonfigurations-Checkliste._") + "\n")

        # --- 12. Best Practice ---
        a("## 12. Best-Practice-Prüfungen\n")
        a("> ⚠️ Diese Prüfungen sind heuristisch und nicht garantiert vollständig.\n")
        findings = self.m["best_practice_findings"]
        if findings:
            for sev in ["warning", "info"]:
                group = [f for f in findings if f["severity"] == sev]
                if group:
                    icon = "⚠️" if sev == "warning" else "ℹ️"
                    a(f"### {icon} {'Warnungen' if sev == 'warning' else 'Hinweise'}\n")
                    for f in group:
                        a(f"- **[{f['type']}]** {f['message_de']}  \n  _Ort: {f['location']}_")
                    a("")
        else:
            a("_Keine Befunde._\n")

        # --- 13. Change Log ---
        a("## 13. Änderungsprotokoll\n")
        changelog = self.p.get("change_log", [])
        if changelog:
            a("| Datum | Hash | Zusammenfassung | Benutzernotiz |")
            a("|---|---|---|---|")
            for entry in changelog:
                a(f"| {entry['timestamp']} | {entry['yaml_hash'][:12]}... | {entry.get('diff_summary', '-')} | {entry.get('user_note', '-')} |")
        else:
            a("_Noch keine Änderungen protokolliert._")
        a("")

        # --- 14. Unparsed ---
        a("## 14. Nicht interpretierte Abschnitte\n")
        if self.m["unparsed"]:
            for up in self.m["unparsed"]:
                a(f"### {up.get('section', '?')}\n")
                a(f"Grund: {up.get('reason', '-')}\n")
                if up.get("raw_excerpt"):
                    a(f"```\n{up['raw_excerpt']}\n```\n")
        else:
            a("_Alle Abschnitte wurden erfolgreich interpretiert._\n")

        a("---\n")
        a(f"_Dokumentation generiert mit Power Apps Doc Builder am {self.timestamp}._\n")

        # Write
        md = "\n".join(lines)
        (self.out / "docs.md").write_text(md, encoding="utf-8")

    # ===================================================================
    # HTML
    # ===================================================================

    def generate_html(self):
        """Generate docs.html from the markdown (simple conversion)."""
        md_path = self.out / "docs.md"
        if not md_path.exists():
            self.generate_markdown()
        md = md_path.read_text(encoding="utf-8")

        # Simple MD→HTML conversion (no external dependency)
        body = self._md_to_html(md)

        html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html_lib.escape(self.m.get('app_name', 'Power App'))} – Dokumentation</title>
<style>
:root {{
  --bg: #0f1117;
  --surface: #1a1d27;
  --border: #2a2d3a;
  --text: #e2e4ea;
  --text-muted: #8b8fa3;
  --accent: #6c8cff;
  --accent-dim: #3d5299;
  --warn: #f0a040;
  --code-bg: #12141c;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  font-family: 'Segoe UI', system-ui, sans-serif;
  background: var(--bg); color: var(--text);
  line-height: 1.7; padding: 2rem;
  max-width: 1100px; margin: 0 auto;
}}
h1 {{ font-size: 2rem; color: var(--accent); margin: 1.5rem 0 0.5rem; border-bottom: 2px solid var(--accent-dim); padding-bottom: .3rem; }}
h2 {{ font-size: 1.5rem; color: var(--accent); margin: 2rem 0 0.5rem; border-bottom: 1px solid var(--border); padding-bottom: .3rem; }}
h3 {{ font-size: 1.2rem; color: var(--text); margin: 1.5rem 0 0.4rem; }}
h4 {{ font-size: 1rem; margin: 1rem 0 0.3rem; color: var(--text-muted); }}
p {{ margin: 0.4rem 0; }}
table {{ border-collapse: collapse; width: 100%; margin: 0.8rem 0; }}
th, td {{ border: 1px solid var(--border); padding: .5rem .7rem; text-align: left; font-size: .9rem; }}
th {{ background: var(--surface); color: var(--accent); }}
tr:nth-child(even) {{ background: var(--surface); }}
code {{ background: var(--code-bg); padding: .15rem .4rem; border-radius: 3px; font-family: 'Cascadia Code', 'Fira Code', monospace; font-size: .85rem; }}
pre {{ background: var(--code-bg); padding: 1rem; border-radius: 6px; overflow-x: auto; margin: .6rem 0; }}
pre code {{ padding: 0; }}
blockquote {{ border-left: 3px solid var(--warn); padding: .5rem 1rem; margin: .8rem 0; background: rgba(240,160,64,.08); color: var(--warn); }}
img {{ max-width: 100%; border: 1px solid var(--border); border-radius: 6px; margin: .5rem 0; }}
details {{ margin: .3rem 0; }}
summary {{ cursor: pointer; color: var(--accent); }}
ul, ol {{ margin: .4rem 0 .4rem 1.5rem; }}
li {{ margin: .2rem 0; }}
a {{ color: var(--accent); }}
hr {{ border: none; border-top: 1px solid var(--border); margin: 2rem 0; }}
</style>
</head>
<body>
{body}
</body>
</html>"""

        (self.out / "docs.html").write_text(html, encoding="utf-8")

    def _md_to_html(self, md: str) -> str:
        """Minimal Markdown to HTML converter (no external deps)."""
        lines = md.split("\n")
        html_lines = []
        in_code = False
        in_table = False
        in_list = False

        for line in lines:
            # Code blocks
            if line.strip().startswith("```"):
                if in_code:
                    html_lines.append("</code></pre>")
                    in_code = False
                else:
                    html_lines.append("<pre><code>")
                    in_code = True
                continue
            if in_code:
                html_lines.append(html_lib.escape(line))
                continue

            # Close table if needed
            if in_table and not line.strip().startswith("|"):
                html_lines.append("</table>")
                in_table = False

            # Close list if needed
            if in_list and not line.strip().startswith("- ") and not line.strip().startswith("* "):
                html_lines.append("</ul>")
                in_list = False

            # Empty line
            if not line.strip():
                html_lines.append("")
                continue

            # Headers
            hm = re.match(r'^(#{1,6})\s+(.*)', line)
            if hm:
                level = len(hm.group(1))
                text = self._inline_md(hm.group(2))
                tag_id = re.sub(r'[^\w-]', '', hm.group(2).lower().replace(' ', '-'))
                html_lines.append(f'<h{level} id="{tag_id}">{text}</h{level}>')
                continue

            # Blockquote
            if line.strip().startswith(">"):
                text = self._inline_md(line.strip()[1:].strip())
                html_lines.append(f"<blockquote>{text}</blockquote>")
                continue

            # Table
            if line.strip().startswith("|"):
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if all(re.match(r'^[-:]+$', c) for c in cells):
                    continue  # separator row
                if not in_table:
                    html_lines.append("<table>")
                    in_table = True
                    tag = "th"
                else:
                    tag = "td"
                row = "".join(f"<{tag}>{self._inline_md(c)}</{tag}>" for c in cells)
                html_lines.append(f"<tr>{row}</tr>")
                continue

            # Lists
            if line.strip().startswith("- ") or line.strip().startswith("* "):
                if not in_list:
                    html_lines.append("<ul>")
                    in_list = True
                text = self._inline_md(line.strip()[2:])
                html_lines.append(f"<li>{text}</li>")
                continue

            # HR
            if line.strip() == "---":
                html_lines.append("<hr>")
                continue

            # Details/summary
            if "<details>" in line or "<summary>" in line or "</details>" in line or "</summary>" in line:
                html_lines.append(line)
                continue

            # Image
            img_m = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', line.strip())
            if img_m:
                alt = html_lib.escape(img_m.group(1))
                src = img_m.group(2)
                html_lines.append(f'<img src="{src}" alt="{alt}" />')
                continue

            # Paragraph
            html_lines.append(f"<p>{self._inline_md(line)}</p>")

        # Close any open tags
        if in_code:
            html_lines.append("</code></pre>")
        if in_table:
            html_lines.append("</table>")
        if in_list:
            html_lines.append("</ul>")

        return "\n".join(html_lines)

    def _inline_md(self, text: str) -> str:
        """Convert inline markdown (bold, code, links, images)."""
        text = html_lib.escape(text)
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        return text

    # ===================================================================
    # JSON
    # ===================================================================

    def generate_json(self):
        """Generate docs.json – the full structured export."""
        export = {
            "generated_at": self.timestamp,
            "project": {
                "name": self.p.get("name"),
                "notes": self.notes,
                "settings": self.settings,
                "screenshot_map": self.screenshot_map,
                "change_log": self.p.get("change_log", []),
            },
            "app_model": self.m,
        }
        if self.redact:
            export_str = self._redact(json.dumps(export, indent=2, ensure_ascii=False))
            (self.out / "docs.json").write_text(export_str, encoding="utf-8")
        else:
            (self.out / "docs.json").write_text(
                json.dumps(export, indent=2, ensure_ascii=False), encoding="utf-8"
            )

    # ===================================================================
    # LATEX
    # ===================================================================

    def generate_latex(self):
        """Generate docs.tex – compile-ready LaTeX document."""
        e = self._latex_escape  # shortcut

        sections = []
        a = sections.append

        a(r"\documentclass[a4paper,11pt]{article}")
        a(r"\usepackage[utf8]{inputenc}")
        a(r"\usepackage[T1]{fontenc}")
        a(r"\usepackage[ngerman]{babel}")
        a(r"\usepackage{graphicx}")
        a(r"\usepackage{longtable}")
        a(r"\usepackage{booktabs}")
        a(r"\usepackage{hyperref}")
        a(r"\usepackage[left=2.5cm,right=2.5cm,top=2.5cm,bottom=2.5cm]{geometry}")
        a(r"\usepackage{listings}")
        a(r"\usepackage{xcolor}")
        a(r"\usepackage{fancyhdr}")
        a("")
        a(r"\definecolor{codebg}{HTML}{F5F5F5}")
        a(r"\lstset{basicstyle=\ttfamily\small,backgroundcolor=\color{codebg},breaklines=true,frame=single}")
        a("")
        a(r"\pagestyle{fancy}")
        a(r"\fancyhead[L]{\small " + e(self.m.get("app_name", "Power App")) + r"}")
        a(r"\fancyhead[R]{\small Dokumentation}")
        a(r"\fancyfoot[C]{\thepage}")
        a("")
        a(r"\title{" + e(self.m.get("app_name", "Power App")) + r" \\ \large Dokumentation}")
        a(r"\author{Power Apps Doc Builder}")
        a(r"\date{" + e(self.timestamp) + r"}")
        a("")
        a(r"\begin{document}")
        a(r"\maketitle")
        a(r"\tableofcontents")
        a(r"\newpage")
        a("")

        # 1. App Overview
        a(r"\section{App-\"Ubersicht}")
        a(r"\begin{tabular}{ll}")
        a(r"\toprule")
        props = self.m.get("app_properties", {})
        rows = [
            ("App-Name", e(self._redact(self.m.get("app_name", "-")))),
            ("Version", e(props.get("AppVersion", props.get("DocumentVersion", "-")))),
            ("Autor", e(props.get("Author", "-"))),
            ("Bildschirme", str(self.m["stats"]["total_screens"])),
            ("Kontrollelemente", str(self.m["stats"]["total_controls"])),
            ("Formeln", str(self.m["stats"]["total_formulas"])),
        ]
        for label, val in rows:
            a(f"  {e(label)} & {val} \\\\")
        a(r"\bottomrule")
        a(r"\end{tabular}")
        a("")
        if self.notes.get("purpose"):
            a(r"\paragraph{Zweck}" + " " + e(self.notes["purpose"]))
        a("")

        # 2. Architecture
        a(r"\section{Architektur / High-Level-Design}")
        a(r"\subsection{Navigationsgraph}")
        if self.m["navigation_graph"]:
            a(r"\begin{lstlisting}")
            seen = set()
            for nav in self.m["navigation_graph"]:
                link = f"{nav['from_screen']} --> {nav['to_screen']}  [{nav['trigger_control']}]"
                if link not in seen:
                    a(link)
                    seen.add(link)
            a(r"\end{lstlisting}")
        else:
            a("Keine Navigate()-Aufrufe erkannt.")
        a("")

        # 3. Screens
        a(r"\section{Bildschirm-Dokumentation}")
        for scr in self.m["screens"]:
            a(r"\subsection{" + e(scr["name"]) + r"}")

            # Screenshot
            img_file = self.screenshot_map.get(scr["name"])
            if img_file:
                a(r"\begin{figure}[h]")
                a(r"\centering")
                a(r"\includegraphics[width=0.8\textwidth]{../data/images/" + img_file + r"}")
                a(r"\caption{" + e(scr["name"]) + r"}")
                a(r"\end{figure}")
                a("")

            if scr["controls"]:
                a(r"\begin{longtable}{lll}")
                a(r"\toprule Name & Typ & \"Ubergeordnet \\ \midrule")
                a(r"\endhead")
                for ctrl in scr["controls"][:50]:
                    a(f"  {e(ctrl['name'])} & {e(ctrl['type'])} & {e(ctrl['parent'])} \\\\")
                a(r"\bottomrule")
                a(r"\end{longtable}")
            a("")

        # 4-14 abbreviated for LaTeX (following same pattern)
        a(r"\section{Kontroll-Inventar}")
        type_counts = self.m["stats"].get("control_type_counts", {})
        if type_counts:
            a(r"\begin{tabular}{lr}")
            a(r"\toprule Typ & Anzahl \\ \midrule")
            for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
                a(f"  {e(t)} & {c} \\\\")
            a(r"\bottomrule")
            a(r"\end{tabular}")
        a("")

        a(r"\section{Datenquellen \& Konnektoren}")
        if self.m["connectors"]:
            a(r"\begin{longtable}{lll}")
            a(r"\toprule Name & Typ & Details \\ \midrule")
            a(r"\endhead")
            for c in self.m["connectors"]:
                a(f"  {e(self._redact(c['name'])[:40])} & {e(c['type'])} & - \\\\")
            a(r"\bottomrule")
            a(r"\end{longtable}")
        a("")

        a(r"\section{Variablen \& Sammlungen}")
        vars_ = self.m["variables"]
        if vars_["global_vars"]:
            a(r"\subsection{Globale Variablen}")
            a(r"\begin{longtable}{ll}")
            a(r"\toprule Name & Initialisiert in \\ \midrule")
            a(r"\endhead")
            for v in vars_["global_vars"]:
                init = ", ".join(v["initialized_in"][:2]) or "-"
                a(f"  \\texttt{{{e(v['name'])}}} & {e(init)[:60]} \\\\")
            a(r"\bottomrule")
            a(r"\end{longtable}")

        if vars_["collections"]:
            a(r"\subsection{Sammlungen}")
            a(r"\begin{longtable}{ll}")
            a(r"\toprule Name & Initialisiert in \\ \midrule")
            a(r"\endhead")
            for v in vars_["collections"]:
                init = ", ".join(v["initialized_in"][:2]) or "-"
                a(f"  \\texttt{{{e(v['name'])}}} & {e(init)[:60]} \\\\")
            a(r"\bottomrule")
            a(r"\end{longtable}")
        a("")

        a(r"\section{Komponenten}")
        if self.m["components"]:
            for comp in self.m["components"]:
                a(r"\subsection{" + e(comp["name"]) + r"}")
                a(f"Eingabe: {e(', '.join(comp['properties_in']) or '-')}")
                a(f"Ausgabe: {e(', '.join(comp['properties_out']) or '-')}")
        else:
            a("Keine Komponenten erkannt.")
        a("")

        a(r"\section{Formulare \& Datenkarten}")
        if self.m["forms"]:
            for form in self.m["forms"]:
                a(r"\subsection{" + e(form["name"]) + r"}")
                a(f"Modus: {e(form['mode'])}, Datenquelle: {e(form['data_source'])}")
        else:
            a("Keine Formulare erkannt.")
        a("")

        a(r"\section{Sicherheit \& Governance}")
        a(e(self.notes.get("roles", "Bitte manuell erg\"anzen.")))
        a("")

        a(r"\section{Fehlerbehandlung}")
        if self.m["error_handling"]:
            a(r"\begin{longtable}{lll}")
            a(r"\toprule Typ & Ort & Details \\ \midrule")
            a(r"\endhead")
            for eh in self.m["error_handling"]:
                a(f"  {e(eh['type'])} & {e(eh['location'][:40])} & {e(str(eh.get('message_hint', '-'))[:40])} \\\\")
            a(r"\bottomrule")
            a(r"\end{longtable}")
        a("")

        a(r"\section{ALM / Deployment-Hinweise}")
        a(e(self.notes.get("alm_notes", "Bitte manuell erg\"anzen.")))
        a("")

        a(r"\section{Best-Practice-Pr\"ufungen}")
        a(r"\textit{Diese Pr\"ufungen sind heuristisch und nicht garantiert.}")
        a("")
        if self.m["best_practice_findings"]:
            a(r"\begin{longtable}{lll}")
            a(r"\toprule Typ & Schwere & Beschreibung \\ \midrule")
            a(r"\endhead")
            for f in self.m["best_practice_findings"]:
                a(f"  {e(f['type'])} & {e(f['severity'])} & {e(f['message_de'][:60])} \\\\")
            a(r"\bottomrule")
            a(r"\end{longtable}")
        a("")

        a(r"\section{\"Anderungsprotokoll}")
        changelog = self.p.get("change_log", [])
        if changelog:
            a(r"\begin{longtable}{lll}")
            a(r"\toprule Datum & Hash & Notiz \\ \midrule")
            a(r"\endhead")
            for entry in changelog:
                a(f"  {e(entry['timestamp'][:19])} & {e(entry['yaml_hash'][:12])} & {e(entry.get('user_note', '-')[:40])} \\\\")
            a(r"\bottomrule")
            a(r"\end{longtable}")
        a("")

        a(r"\section{Nicht interpretierte Abschnitte}")
        if self.m["unparsed"]:
            for up in self.m["unparsed"]:
                a(r"\subsection{" + e(up.get("section", "?")) + r"}")
                a(e(up.get("reason", "")))
        else:
            a("Alle Abschnitte wurden erfolgreich interpretiert.")
        a("")

        a(r"\end{document}")

        latex = "\n".join(sections)
        (self.out / "docs.tex").write_text(latex, encoding="utf-8")

    def _latex_escape(self, text: str) -> str:
        """Escape special LaTeX characters."""
        if not text:
            return ""
        replacements = [
            ("\\", r"\textbackslash{}"),
            ("&", r"\&"),
            ("%", r"\%"),
            ("$", r"\$"),
            ("#", r"\#"),
            ("_", r"\_"),
            ("{", r"\{"),
            ("}", r"\}"),
            ("~", r"\textasciitilde{}"),
            ("^", r"\textasciicircum{}"),
        ]
        for old, new in replacements:
            text = text.replace(old, new)
        return text
