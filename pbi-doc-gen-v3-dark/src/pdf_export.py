"""
PDF export with CI/Branding support.

Uses ReportLab. Respects CIBranding settings from the Project for
customer-specific documentation.
"""
from __future__ import annotations
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Preformatted, KeepTogether, HRFlowable, Image,
)

from .models import Project, CIBranding


def _hex(c):
    try: return colors.HexColor(c)
    except: return colors.HexColor("#1B3A5C")


def _esc(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _build_styles(ci: CIBranding):
    clr_p = _hex(ci.primary_color)
    clr_s = _hex(ci.secondary_color)
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle("TitleCustom", parent=ss["Title"],
        fontSize=26, leading=32, textColor=clr_p, spaceAfter=6*mm))
    ss.add(ParagraphStyle("Sub", parent=ss["Normal"],
        fontSize=13, leading=18, textColor=colors.HexColor("#64748B"), spaceAfter=4*mm))
    ss.add(ParagraphStyle("H1", parent=ss["Heading1"],
        fontSize=18, leading=24, textColor=clr_p, spaceBefore=10*mm, spaceAfter=4*mm))
    ss.add(ParagraphStyle("H2", parent=ss["Heading2"],
        fontSize=14, leading=19, textColor=clr_s, spaceBefore=6*mm, spaceAfter=3*mm))
    ss.add(ParagraphStyle("H3", parent=ss["Heading3"],
        fontSize=12, leading=16, textColor=clr_p, spaceBefore=4*mm, spaceAfter=2*mm))
    ss.add(ParagraphStyle("Body", parent=ss["Normal"], fontSize=10, leading=14, spaceAfter=2*mm))
    ss.add(ParagraphStyle("CodeBlock", parent=ss["Code"],
        fontSize=8, leading=11, fontName="Courier", backColor=colors.HexColor("#F8FAFC"),
        borderColor=colors.HexColor("#CBD5E1"), borderWidth=0.5, borderPadding=6,
        spaceAfter=3*mm, leftIndent=4*mm, rightIndent=4*mm))
    ss.add(ParagraphStyle("CellN", parent=ss["Normal"], fontSize=9, leading=12))
    ss.add(ParagraphStyle("CellB", parent=ss["Normal"], fontSize=9, leading=12, fontName="Helvetica-Bold"))
    ss.add(ParagraphStyle("MetaL", parent=ss["Normal"], fontSize=10, leading=14, textColor=colors.HexColor("#64748B")))
    ss.add(ParagraphStyle("MetaV", parent=ss["Normal"], fontSize=10, leading=14, fontName="Helvetica-Bold"))
    ss.add(ParagraphStyle("Conf", parent=ss["Normal"], fontSize=9, leading=13,
        textColor=colors.HexColor("#94A3B8"), alignment=TA_CENTER, spaceBefore=4*mm))
    return ss


def _make_table(headers, rows, col_widths, ci):
    ss = _build_styles(ci)
    clr_hdr = _hex(ci.primary_color)
    hdr = [Paragraph("<b>{}</b>".format(h), ss["CellB"]) for h in headers]
    data = [hdr] + [[Paragraph(str(c), ss["CellN"]) for c in row] for row in rows]
    t = Table(data, colWidths=col_widths, repeatRows=1)
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), clr_hdr),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]
    for i in range(2, len(data), 2):
        cmds.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F0F4F8")))
    t.setStyle(TableStyle(cmds))
    return t


def _hr():
    return HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"),
                       spaceBefore=3*mm, spaceAfter=3*mm)


def generate_pdf(project, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ci = project.ci_branding
    clr_accent = _hex(ci.accent_color)
    clr_primary = _hex(ci.primary_color)

    doc = SimpleDocTemplate(str(output_path), pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm, topMargin=18*mm, bottomMargin=20*mm,
        title="{} - Dokumentation".format(project.meta.report_name),
        author=project.meta.author)

    footer_text = ci.footer_text or "Power BI Documentation Generator"
    header_text = ci.header_text

    def _footer(canvas, doc_obj):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#94A3B8"))
        canvas.drawCentredString(A4[0]/2, 12*mm, "{}  |  Seite {}".format(footer_text, doc_obj.page))
        if header_text:
            canvas.drawCentredString(A4[0]/2, A4[1] - 10*mm, header_text)
        canvas.restoreState()

    ss = _build_styles(ci)
    story = []
    pw = A4[0] - 30*mm

    # ── TITLE PAGE ──
    story.append(Spacer(1, 20*mm))

    # Logo
    if ci.logo_path and Path(ci.logo_path).exists():
        try:
            story.append(Image(ci.logo_path, height=30*mm, kind='proportional'))
            story.append(Spacer(1, 8*mm))
        except: pass

    # Accent bar
    at = Table([[""]], colWidths=[pw], rowHeights=[4*mm])
    at.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), clr_accent)]))
    story.append(at)
    story.append(Spacer(1, 8*mm))

    story.append(Paragraph(_esc(project.meta.report_name or "Power BI Report"), ss["TitleCustom"]))
    story.append(Paragraph(_esc(ci.cover_subtitle or "Dokumentation"), ss["Sub"]))

    if ci.company_name:
        story.append(Paragraph(_esc(ci.company_name), ss["Body"]))

    if project.meta.short_description:
        story.append(Spacer(1, 4*mm))
        story.append(Paragraph(_esc(project.meta.short_description), ss["Body"]))

    story.append(Spacer(1, 10*mm))

    meta_rows = [["Eigentuemer", project.meta.owner], ["Autor", project.meta.author],
                  ["Version", project.meta.version], ["Datum", project.meta.date],
                  ["Zielgruppe", project.meta.audience],
                  ["Generiert", datetime.now().strftime("%Y-%m-%d %H:%M")]]
    md = [[Paragraph(r[0], ss["MetaL"]), Paragraph(_esc(r[1]), ss["MetaV"])] for r in meta_rows if r[1]]
    if md:
        mt = Table(md, colWidths=[40*mm, pw - 44*mm])
        mt.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),3),
            ("BOTTOMPADDING",(0,0),(-1,-1),3),("LINEBELOW",(0,0),(-1,-1),0.3,colors.HexColor("#CBD5E1"))]))
        story.append(mt)

    if ci.confidentiality_notice:
        story.append(Spacer(1, 8*mm))
        story.append(Paragraph(_esc(ci.confidentiality_notice), ss["Conf"]))

    story.append(PageBreak())

    # ── TOC ──
    story.append(Paragraph("Inhaltsverzeichnis", ss["H1"]))
    for item in ["1. Uebersicht", "2. KPIs", "3. Datenquellen", "4. Power Query",
                  "5. Datenmodell", "6. Measures", "7. Berichtsseiten", "8. Governance",
                  "9. Annahmen", "10. Aenderungsprotokoll"]:
        story.append(Paragraph(item, ss["Body"]))
    story.append(PageBreak())

    # Helper to add screenshot if exists
    def _add_screenshot(path):
        if not path: return
        p = Path(path)
        if not p.exists():
            p = Path("data") / "screenshots" / path  # try relative to screenshots dir
        if p.exists():
            try:
                story.append(Spacer(1, 3*mm))
                story.append(Image(str(p), width=pw*0.85, kind='proportional'))
                story.append(Spacer(1, 3*mm))
            except: pass

    # ── SECTIONS ──
    # 1. Overview
    story.append(Paragraph("1. Uebersicht", ss["H1"]))
    if project.meta.short_description:
        story.append(Paragraph(_esc(project.meta.short_description), ss["Body"]))
    if project.meta.powerbi_service_url:
        story.append(Paragraph("<b>Power BI:</b> {}".format(_esc(project.meta.powerbi_service_url)), ss["Body"]))
    if project.meta.environments:
        er = [[e.name, e.workspace, e.url] for e in project.meta.environments]
        story.append(_make_table(["Umgebung","Arbeitsbereich","URL"], er, [30*mm,50*mm,pw-84*mm], ci))

    # 2. KPIs
    story.append(Paragraph("2. KPIs", ss["H1"]))
    if project.kpis:
        kr = [[str(i),_esc(k.name),_esc(k.granularity),_esc(k.business_description)] for i,k in enumerate(project.kpis,1)]
        story.append(_make_table(["#","Name","Gran.","Beschreibung"], kr, [10*mm,35*mm,30*mm,pw-79*mm], ci))
        for k in project.kpis:
            story.extend([Paragraph(_esc(k.name), ss["H2"]),
                Paragraph("<b>Beschreibung:</b> {}".format(_esc(k.business_description)), ss["Body"]),
                Paragraph("<b>Technik:</b> {}".format(_esc(k.technical_definition)), ss["Body"]),
                _hr()])
    else:
        story.append(Paragraph("<i>Keine KPIs.</i>", ss["Body"]))

    # 3. Data Sources
    story.append(Paragraph("3. Datenquellen", ss["H1"]))
    if project.data_sources:
        dr = [[_esc(s.name),_esc(s.source_type),_esc(s.connection_info),_esc(s.refresh_cadence),
               _esc(s.gateway_name) if s.gateway_required else "-"] for s in project.data_sources]
        story.append(_make_table(["Name","Typ","Verbindung","Refresh","Gateway"], dr,
                                  [30*mm,22*mm,45*mm,30*mm,pw-131*mm], ci))
    else:
        story.append(Paragraph("<i>Keine Quellen.</i>", ss["Body"]))

    # 4. Power Query
    story.append(Paragraph("4. Power Query (M)", ss["H1"]))
    for q in project.power_queries:
        story.extend([Paragraph(_esc(q.query_name), ss["H2"]),
            Paragraph("<b>Zweck:</b> {}".format(_esc(q.purpose)), ss["Body"])])
        if q.m_code:
            story.append(Paragraph("<b>M-Code:</b>", ss["Body"]))
            story.append(Preformatted(q.m_code, ss["CodeBlock"]))
        story.append(_hr())
    if not project.power_queries:
        story.append(Paragraph("<i>Keine Abfragen.</i>", ss["Body"]))

    # 5. Data Model
    story.append(Paragraph("5. Datenmodell", ss["H1"]))
    dm = project.data_model
    if dm.tables:
        tr = [[_esc(t.name),_esc(t.table_type),_esc(t.keys),_esc(t.description)] for t in dm.tables]
        story.append(_make_table(["Tabelle","Typ","Schluessel","Beschreibung"], tr,
                                  [35*mm,25*mm,40*mm,pw-104*mm], ci))
    if dm.relationships:
        rr = [["{}.{}".format(r.from_table,r.from_column),"{}.{}".format(r.to_table,r.to_column),
               r.cardinality,r.filter_direction] for r in dm.relationships]
        story.append(_make_table(["Von","Nach","Kard.","Filter"], rr, [40*mm,40*mm,30*mm,pw-114*mm], ci))
    if dm.date_logic_notes:
        story.extend([Paragraph("Datumslogik", ss["H2"]), Paragraph(_esc(dm.date_logic_notes), ss["Body"])])
    for sp in dm.screenshot_paths:
        _add_screenshot(sp)
    if not dm.tables and not dm.relationships:
        story.append(Paragraph("<i>Kein Modell.</i>", ss["Body"]))

    # 6. Measures
    story.append(Paragraph("6. Measures (DAX)", ss["H1"]))
    if project.measures:
        mr = [[str(i),_esc(m.name),_esc(m.display_folder),_esc(m.description)] for i,m in enumerate(project.measures,1)]
        story.append(_make_table(["#","Name","Ordner","Beschreibung"], mr, [10*mm,40*mm,30*mm,pw-84*mm], ci))
        story.append(Spacer(1, 4*mm))
        for ms in project.measures:
            story.extend([Paragraph(_esc(ms.name), ss["H2"]),
                Paragraph("<b>Beschreibung:</b> {}".format(_esc(ms.description)), ss["Body"]),
                Paragraph("<b>DAX:</b>", ss["Body"]),
                Preformatted(ms.dax_code, ss["CodeBlock"]), _hr()])
    else:
        story.append(Paragraph("<i>Keine Measures.</i>", ss["Body"]))

    # 7. Report Pages
    story.append(Paragraph("7. Berichtsseiten", ss["H1"]))
    for pg in project.report_pages:
        story.extend([Paragraph(_esc(pg.page_name), ss["H2"]),
            Paragraph("<b>Zweck:</b> {}".format(_esc(pg.purpose)), ss["Body"])])
        if pg.visuals:
            vr = [[_esc(v.name),_esc(v.description)] for v in pg.visuals]
            story.append(_make_table(["Visual","Beschreibung"], vr, [45*mm,pw-49*mm], ci))
        sp = getattr(pg, 'screenshot_path', '')
        _add_screenshot(sp)
        story.append(_hr())
    if not project.report_pages:
        story.append(Paragraph("<i>Keine Seiten.</i>", ss["Body"]))

    # 8. Governance
    story.append(Paragraph("8. Governance", ss["H1"]))
    gov = project.governance
    for title, val in [("Aktualisierung", gov.refresh_schedule), ("Monitoring", gov.monitoring_notes),
                        ("RLS", gov.rls_notes), ("Performance", gov.performance_notes)]:
        story.extend([Paragraph(title, ss["H2"]),
            Paragraph(_esc(val) if val else "<i>Nicht dokumentiert.</i>", ss["Body"])])

    # 9. Assumptions
    story.append(Paragraph("9. Annahmen und Einschraenkungen", ss["H1"]))
    story.extend([Paragraph("Annahmen", ss["H2"]),
        Paragraph(_esc(gov.assumptions) if gov.assumptions else "<i>Keine.</i>", ss["Body"]),
        Paragraph("Einschraenkungen", ss["H2"]),
        Paragraph(_esc(gov.limitations) if gov.limitations else "<i>Keine.</i>", ss["Body"])])

    # 10. Change Log
    story.append(Paragraph("10. Aenderungsprotokoll", ss["H1"]))
    if project.change_log:
        cr = [[_esc(c.version),c.date,_esc(c.description),_esc(c.author),_esc(c.impact),_esc(c.ticket_link)]
              for c in project.change_log]
        story.append(_make_table(["Ver.","Datum","Beschreibung","Autor","Impact","Ticket"], cr,
                                  [16*mm,20*mm,pw-104*mm,20*mm,20*mm,24*mm], ci))
    else:
        story.append(Paragraph("<i>Keine Eintraege.</i>", ss["Body"]))

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return output_path


def default_pdf_filename(project):
    name = project.meta.report_name or "PowerBI_Report"
    safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in name).strip().replace(" ", "_")
    ci = project.ci_branding
    prefix = ci.company_name.replace(" ", "_") + "_" if ci.company_name else ""
    return "{}{}_powerbi_documentation_{}.pdf".format(prefix, safe, datetime.now().strftime("%Y-%m-%d"))
