"""
pdf_export.py – PDF-Export mit ReportLab inkl. CI-Branding.
"""
from __future__ import annotations

import os
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, NextPageTemplate, PageBreak,
    PageTemplate, Paragraph, SimpleDocTemplate, Spacer, Table,
    TableStyle, Preformatted,
)

from models import PAProject, FlowAction, CIBranding
from diagram import generate_mermaid_diagram
from diagram_renderer import render_flowchart_to_temp_png

PAGE_W, PAGE_H = A4
MARGIN = 2 * cm


def _hex_to_color(hex_str: str) -> colors.Color:
    hex_str = hex_str.lstrip("#")
    if len(hex_str) == 6:
        r, g, b = int(hex_str[:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)
        return colors.Color(r / 255, g / 255, b / 255)
    return colors.HexColor(f"#{hex_str}")


class PDFExporter:
    """Erzeugt ein professionelles PDF-Dokument fuer einen Flow."""

    def __init__(self, project: PAProject):
        self.p = project
        self.b = project.branding
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self):
        primary = _hex_to_color(self.b.primary_color or "#5B8DEF")
        self.primary = primary

        self.styles.add(ParagraphStyle(
            "PA_Title", parent=self.styles["Title"],
            fontSize=28, textColor=primary, spaceAfter=12,
        ))
        self.styles.add(ParagraphStyle(
            "PA_H1", parent=self.styles["Heading1"],
            fontSize=18, textColor=primary, spaceBefore=18, spaceAfter=8,
        ))
        self.styles.add(ParagraphStyle(
            "PA_H2", parent=self.styles["Heading2"],
            fontSize=14, textColor=primary, spaceBefore=12, spaceAfter=6,
        ))
        self.styles.add(ParagraphStyle(
            "PA_H3", parent=self.styles["Heading3"],
            fontSize=11, textColor=colors.HexColor("#333333"),
            spaceBefore=8, spaceAfter=4,
        ))
        self.styles.add(ParagraphStyle(
            "PA_Body", parent=self.styles["Normal"],
            fontSize=9, leading=13, spaceAfter=6,
        ))
        self.styles.add(ParagraphStyle(
            "PA_Code", fontName="Courier", fontSize=7.5, leading=10,
            backColor=colors.HexColor("#F5F5F5"), spaceAfter=6,
            leftIndent=6, rightIndent=6, borderPadding=4,
        ))
        self.styles.add(ParagraphStyle(
            "PA_Footer", fontSize=7, textColor=colors.grey, alignment=TA_CENTER,
        ))
        self.styles.add(ParagraphStyle(
            "PA_Center", parent=self.styles["Normal"],
            alignment=TA_CENTER, fontSize=10,
        ))

    def _header_footer(self, canvas, doc):
        canvas.saveState()
        # Header
        canvas.setStrokeColor(self.primary)
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN, PAGE_H - MARGIN + 8, PAGE_W - MARGIN, PAGE_H - MARGIN + 8)
        if self.b.header_text:
            canvas.setFont("Helvetica", 7)
            canvas.setFillColor(colors.grey)
            canvas.drawString(MARGIN, PAGE_H - MARGIN + 12, self.b.header_text)

        # Footer
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.grey)
        footer = self.b.footer_text or self.b.company_name or ""
        canvas.drawString(MARGIN, MARGIN - 12, footer)
        canvas.drawRightString(PAGE_W - MARGIN, MARGIN - 12, f"Seite {doc.page}")
        canvas.restoreState()

    def _build_title_page(self) -> list:
        """Erzeugt die Titelseite."""
        elements = []
        elements.append(Spacer(1, 4 * cm))

        # Logo
        if self.b.logo_path and os.path.exists(self.b.logo_path):
            try:
                elements.append(Image(self.b.logo_path, width=6 * cm, height=3 * cm))
                elements.append(Spacer(1, 1 * cm))
            except Exception:
                pass

        # Titel
        elements.append(Paragraph(
            self.p.meta.flow_name or "Power Automate Flow",
            self.styles["PA_Title"],
        ))
        elements.append(Spacer(1, 0.5 * cm))
        elements.append(Paragraph("Technische Dokumentation", self.styles["PA_Center"]))
        elements.append(Spacer(1, 2 * cm))

        # Meta-Tabelle
        meta_data = [
            ["Typ", self.p.meta.flow_type],
            ["Status", self.p.meta.status],
            ["Eigentuemer", self.p.meta.owner],
            ["Autor", self.p.meta.author],
            ["Erstellt", self.p.meta.created_date],
            ["Letzte Aenderung", self.p.meta.last_modified],
        ]
        t = Table(meta_data, colWidths=[5 * cm, 10 * cm])
        t.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TEXTCOLOR", (0, 0), (0, -1), self.primary),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(t)

        # Vertraulichkeit
        if self.b.confidentiality_note:
            elements.append(Spacer(1, 2 * cm))
            elements.append(Paragraph(self.b.confidentiality_note, self.styles["PA_Center"]))

        elements.append(PageBreak())
        return elements

    def _build_toc(self) -> list:
        """Erzeugt ein einfaches Inhaltsverzeichnis."""
        elements = [Paragraph("Inhaltsverzeichnis", self.styles["PA_H1"])]
        sections = [
            "1. Uebersicht",
            "2. Trigger",
            "3. Flussdiagramm",
            "4. Flow-Struktur – Aktionen",
            "5. Variablen",
            "6. Datenmappings",
            "7. Konnektoren & Verbindungen",
            "8. Abhaengigkeiten",
            "9. Fehlerbehandlung",
            "10. SLA & Performance",
            "11. Governance & Betrieb",
            "12. Aenderungsprotokoll",
        ]
        for s in sections:
            elements.append(Paragraph(s, self.styles["PA_Body"]))
        elements.append(PageBreak())
        return elements

    def _make_table(self, data: list[list[str]], col_widths=None) -> Table:
        """Erzeugt eine formatierte Tabelle."""
        if not data:
            return Spacer(1, 0)

        # Texte in Paragraphs umwandeln fuer Umbruch
        wrapped = []
        for row in data:
            wrapped.append([
                Paragraph(str(cell), self.styles["PA_Body"]) for cell in row
            ])

        t = Table(wrapped, colWidths=col_widths, repeatRows=1)
        style = [
            ("BACKGROUND", (0, 0), (-1, 0), self.primary),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#CCCCCC")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F8F8")]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]
        t.setStyle(TableStyle(style))
        return t

    def _build_overview(self) -> list:
        elements = [Paragraph("1. Uebersicht", self.styles["PA_H1"])]
        meta = self.p.meta

        data = [
            ["Eigenschaft", "Wert"],
            ["Flow-Name", meta.flow_name],
            ["Typ", meta.flow_type],
            ["Status", meta.status],
            ["Eigentuemer", meta.owner],
            ["Autor", meta.author],
            ["Erstellt", meta.created_date],
            ["Letzte Aenderung", meta.last_modified],
            ["Solution", meta.solution_name],
            ["Lizenz", meta.license_requirement],
        ]
        elements.append(self._make_table(data, [5 * cm, 11 * cm]))
        if meta.description:
            elements.append(Spacer(1, 0.3 * cm))
            elements.append(Paragraph(meta.description, self.styles["PA_Body"]))
        elements.append(PageBreak())
        return elements

    def _build_trigger(self) -> list:
        t = self.p.trigger
        elements = [Paragraph("2. Trigger", self.styles["PA_H1"])]
        data = [
            ["Eigenschaft", "Wert"],
            ["Name", t.name],
            ["Typ", t.trigger_type],
            ["Connector", t.connector],
            ["Frequenz", t.schedule_frequency],
            ["Intervall", t.schedule_interval],
            ["Zeitzone", t.schedule_timezone],
            ["Authentifizierung", t.authentication],
        ]
        elements.append(self._make_table(data, [5 * cm, 11 * cm]))
        if t.description:
            elements.append(Paragraph(t.description, self.styles["PA_Body"]))
        if t.input_schema:
            elements.append(Paragraph("Input-Schema:", self.styles["PA_H3"]))
            elements.append(Preformatted(t.input_schema[:2000], self.styles["PA_Code"]))
        elements.append(PageBreak())
        return elements

    def _build_flowchart(self) -> list:
        """Erzeugt die Flussdiagramm-Seite im PDF als Bild."""
        elements = [Paragraph("3. Flussdiagramm", self.styles["PA_H1"])]
        elements.append(Paragraph(
            "Visuelle Darstellung des Flows als Flussdiagramm.",
            self.styles["PA_Body"],
        ))
        elements.append(Spacer(1, 0.3 * cm))

        # Flussdiagramm als Bild rendern
        try:
            import os
            import io
            from reportlab.lib.utils import ImageReader
            png_path = render_flowchart_to_temp_png(self.p, scale=2.0)
            if os.path.exists(png_path):
                # Bilddaten in Speicher laden, damit die Temp-Datei geloescht werden kann
                with open(png_path, 'rb') as f:
                    img_data = io.BytesIO(f.read())
                # Temp-Datei sofort loeschen
                try:
                    os.unlink(png_path)
                except Exception:
                    pass
                # Bildgroesse an Seite anpassen
                avail_w = PAGE_W - 2 * MARGIN
                avail_h = PAGE_H - 2 * MARGIN - 4 * cm  # Platz fuer Header etc.
                # Seitenverhaeltnis beibehalten
                ir = ImageReader(img_data)
                iw, ih = ir.getSize()
                if iw > 0 and ih > 0:
                    ratio = min(avail_w / iw, avail_h / ih)
                    img_data.seek(0)
                    img = Image(img_data, width=iw * ratio, height=ih * ratio)
                else:
                    img_data.seek(0)
                    img = Image(img_data, width=avail_w, height=avail_h)
                img.hAlign = 'CENTER'
                elements.append(img)
            else:
                elements.append(Paragraph("Flussdiagramm konnte nicht gerendert werden.", self.styles["PA_Body"]))
        except Exception as e:
            elements.append(Paragraph(f"Flussdiagramm-Fehler: {e}", self.styles["PA_Body"]))
            # Fallback: Mermaid-Code als Text
            mermaid_code = generate_mermaid_diagram(self.p)
            if len(mermaid_code) > 3000:
                mermaid_code = mermaid_code[:3000] + "\n... (gekuerzt)"
            elements.append(Preformatted(mermaid_code, self.styles["PA_Code"]))

        elements.append(PageBreak())
        return elements

    def _actions_rows(self, actions: list[FlowAction], depth: int = 0) -> list[list[str]]:
        """Erzeugt Tabellenzeilen fuer die Aktionshierarchie."""
        rows = []
        for a in actions:
            indent = "    " * depth
            rows.append([
                f"{indent}{a.name}",
                a.action_type,
                a.connector,
                a.description[:80] if a.description else "",
            ])
            if a.children:
                rows.extend(self._actions_rows(a.children, depth + 1))
        return rows

    def _build_actions(self) -> list:
        elements = [Paragraph("4. Flow-Struktur – Aktionen", self.styles["PA_H1"])]
        rows = [["Aktion", "Typ", "Connector", "Beschreibung"]]
        rows.extend(self._actions_rows(self.p.actions))
        if len(rows) > 1:
            elements.append(self._make_table(rows, [5.5 * cm, 3.5 * cm, 3 * cm, 4 * cm]))
        else:
            elements.append(Paragraph("Keine Aktionen definiert.", self.styles["PA_Body"]))
        elements.append(PageBreak())
        return elements

    def _build_variables(self) -> list:
        elements = [Paragraph("5. Variablen", self.styles["PA_H1"])]
        if not self.p.variables:
            elements.append(Paragraph("Keine Variablen definiert.", self.styles["PA_Body"]))
        else:
            rows = [["Name", "Typ", "Initialwert", "Beschreibung"]]
            for v in self.p.variables:
                rows.append([v.name, v.var_type, v.initial_value, v.description])
            elements.append(self._make_table(rows))
        elements.append(PageBreak())
        return elements

    def _build_data_mappings(self) -> list:
        elements = [Paragraph("6. Datenmappings", self.styles["PA_H1"])]
        if not self.p.data_mappings:
            elements.append(Paragraph("Keine Datenmappings definiert.", self.styles["PA_Body"]))
        else:
            rows = [["Quelle", "Ziel", "Feldmapping", "Transformation"]]
            for m in self.p.data_mappings:
                rows.append([m.source_action, m.target_action, m.field_mapping, m.transformation])
            elements.append(self._make_table(rows))
        elements.append(PageBreak())
        return elements

    def _build_connectors(self) -> list:
        elements = [Paragraph("7. Konnektoren & Verbindungen", self.styles["PA_H1"])]
        if not self.p.connections:
            elements.append(Paragraph("Keine Konnektoren definiert.", self.styles["PA_Body"]))
        else:
            rows = [["Connector", "Typ", "Auth-Typ", "Service-Account"]]
            for c in self.p.connections:
                rows.append([c.connector_name, c.connector_type, c.auth_type, c.service_account])
            elements.append(self._make_table(rows))
        elements.append(PageBreak())
        return elements

    def _build_dependencies(self) -> list:
        elements = [Paragraph("8. Abhaengigkeiten", self.styles["PA_H1"])]
        if not self.p.dependencies:
            elements.append(Paragraph("Keine Abhaengigkeiten definiert.", self.styles["PA_Body"]))
        else:
            rows = [["Typ", "Name", "Beschreibung"]]
            for d in self.p.dependencies:
                rows.append([d.dep_type, d.name, d.description])
            elements.append(self._make_table(rows))
        elements.append(PageBreak())
        return elements

    def _build_error_handling(self) -> list:
        elements = [Paragraph("9. Fehlerbehandlung", self.styles["PA_H1"])]
        if not self.p.error_handling:
            elements.append(Paragraph("Keine Fehlerbehandlung definiert.", self.styles["PA_Body"]))
        else:
            for eh in self.p.error_handling:
                elements.append(Paragraph(eh.scope_name, self.styles["PA_H2"]))
                data = [["Eigenschaft", "Wert"]]
                if eh.pattern:
                    data.append(["Pattern", eh.pattern])
                if eh.retry_count:
                    data.append(["Retry-Anzahl", str(eh.retry_count)])
                if eh.retry_interval:
                    data.append(["Retry-Intervall", eh.retry_interval])
                if eh.notification_method:
                    data.append(["Benachrichtigung", f"{eh.notification_method} → {eh.notification_target}"])
                if eh.timeout:
                    data.append(["Timeout", eh.timeout])
                if len(data) > 1:
                    elements.append(self._make_table(data, [5 * cm, 11 * cm]))
                if eh.description:
                    elements.append(Paragraph(eh.description, self.styles["PA_Body"]))
        elements.append(PageBreak())
        return elements

    def _build_sla(self) -> list:
        s = self.p.sla
        elements = [Paragraph("10. SLA & Performance", self.styles["PA_H1"])]
        data = [
            ["Eigenschaft", "Wert"],
            ["Erwartete Laufzeit", s.expected_runtime],
            ["Maximale Laufzeit", s.max_runtime],
            ["Durchschnittl. Ausfuehrungen", s.avg_executions],
            ["Kritikalitaet", s.criticality],
            ["Eskalationspfad", s.escalation_path],
        ]
        elements.append(self._make_table(data, [5 * cm, 11 * cm]))
        if s.description:
            elements.append(Paragraph(s.description, self.styles["PA_Body"]))
        elements.append(PageBreak())
        return elements

    def _build_governance(self) -> list:
        g = self.p.governance
        elements = [Paragraph("11. Governance & Betrieb", self.styles["PA_H1"])]
        data = [
            ["Eigenschaft", "Wert"],
            ["DLP-Policy", g.dlp_policy],
            ["Genehmigungs-Workflow", g.approval_workflow],
            ["Monitoring", g.monitoring_setup],
            ["Backup-Strategie", g.backup_strategy],
            ["Rollback", g.rollback_procedure],
            ["Testverfahren", g.test_procedure],
        ]
        elements.append(self._make_table(data, [5 * cm, 11 * cm]))
        if g.assumptions:
            elements.append(Paragraph(f"Annahmen: {g.assumptions}", self.styles["PA_Body"]))
        if g.limitations:
            elements.append(Paragraph(f"Einschraenkungen: {g.limitations}", self.styles["PA_Body"]))
        elements.append(PageBreak())
        return elements

    def _build_changelog(self) -> list:
        elements = [Paragraph("12. Aenderungsprotokoll", self.styles["PA_H1"])]
        if not self.p.changelog:
            elements.append(Paragraph("Keine Eintraege.", self.styles["PA_Body"]))
        else:
            rows = [["Version", "Datum", "Autor", "Beschreibung", "Auswirkung", "Ticket"]]
            for c in self.p.changelog:
                rows.append([c.version, c.date, c.author, c.description, c.impact, c.ticket])
            elements.append(self._make_table(rows))
        return elements

    # ---- Public ----

    def export(self, output_path: Path | str) -> Path:
        """Erzeugt das PDF-Dokument."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            topMargin=MARGIN,
            bottomMargin=MARGIN,
            leftMargin=MARGIN,
            rightMargin=MARGIN,
            title=self.p.meta.flow_name or "Flow-Dokumentation",
            author=self.p.meta.author,
        )

        elements = []
        elements.extend(self._build_title_page())
        elements.extend(self._build_toc())
        elements.extend(self._build_overview())
        elements.extend(self._build_trigger())
        elements.extend(self._build_flowchart())
        elements.extend(self._build_actions())
        elements.extend(self._build_variables())
        elements.extend(self._build_data_mappings())
        elements.extend(self._build_connectors())
        elements.extend(self._build_dependencies())
        elements.extend(self._build_error_handling())
        elements.extend(self._build_sla())
        elements.extend(self._build_governance())
        elements.extend(self._build_changelog())

        doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer)
        return output_path


# ---------------------------------------------------------------------------
# Convenience
# ---------------------------------------------------------------------------

def export_pdf(project: PAProject, output_path: Path | str) -> Path:
    exporter = PDFExporter(project)
    return exporter.export(output_path)
