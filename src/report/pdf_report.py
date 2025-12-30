from __future__ import annotations
import os
from typing import List, Dict

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie

from ..engine.models import Finding, RunMeta, STATUS_PASS, STATUS_FAIL, STATUS_MANUAL, STATUS_UNKNOWN

def _count_status(findings: List[Finding]) -> Dict[str, int]:
    c = {STATUS_PASS: 0, STATUS_FAIL: 0, STATUS_MANUAL: 0, STATUS_UNKNOWN: 0}
    for f in findings:
        c[f.status] = c.get(f.status, 0) + 1
    return c

def _pie(counts: Dict[str, int]) -> Drawing:
    d = Drawing(400, 200)
    pie = Pie()
    pie.x = 10
    pie.y = 10
    pie.width = 170
    pie.height = 170

    labels = []
    data = []
    for k in (STATUS_PASS, STATUS_FAIL, STATUS_MANUAL, STATUS_UNKNOWN):
        v = counts.get(k, 0)
        if v > 0:
            labels.append(f"{k} ({v})")
            data.append(v)
    if not data:
        labels, data = ["No findings"], [1]

    pie.data = data
    pie.labels = labels
    pie.slices.strokeWidth = 0.5
    d.add(pie)
    return d

def build_pdf(out_path: str, findings: List[Finding], meta: RunMeta):
    styles = getSampleStyleSheet()
    body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=9, leading=11)
    small = ParagraphStyle("small", parent=styles["BodyText"], fontSize=8, leading=10)
    h1 = styles["Heading1"]
    h2 = styles["Heading2"]

    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    doc = SimpleDocTemplate(out_path, pagesize=A4, leftMargin=1.6*cm, rightMargin=1.6*cm, topMargin=1.6*cm, bottomMargin=1.6*cm)

    counts = _count_status(findings)

    story = []
    story.append(Paragraph("Switch Configuration Review Report (CIS-aligned / CIS-style)", h1))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"<b>Generated:</b> {meta.generated_at}", body))
    story.append(Paragraph(f"<b>Profile:</b> {meta.vendor_profile}", body))
    story.append(Paragraph("<b>Sources:</b> " + ", ".join(meta.source_files), body))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Executive Summary", h2))
    story.append(Paragraph(
        "This report summarizes an offline configuration review of network switch configuration files. "
        "Checks are CIS-aligned (CIS-style) controls focusing on management plane hardening, AAA, logging, time synchronization, "
        "and L2 protections. If a setting cannot be deterministically validated from the exported configuration, the status is MANUAL.",
        body
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Summary", h2))
    story.append(Paragraph(
        f"Total checks: {len(findings)} | PASS: {counts.get('PASS',0)} | FAIL: {counts.get('FAIL',0)} | "
        f"MANUAL: {counts.get('MANUAL',0)} | UNKNOWN: {counts.get('UNKNOWN',0)}",
        body
    ))
    story.append(Spacer(1, 8))
    story.append(_pie(counts))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Findings", h2))

    col_widths = [2.5*cm, 6.0*cm, 2.2*cm, 2.2*cm, 4.9*cm]  # sum ~17.8cm
    header = ["Issue ID", "Issue Name", "Status", "Fix Type", "Remediation"]
    rows = [header]
    for f in findings:
        rows.append([
            Paragraph(f.issue_id, small),
            Paragraph(f.issue_name, small),
            Paragraph(f.status, small),
            Paragraph(f.fix_type, small),
            Paragraph(f.remediation, small),
        ])

    tbl = Table(rows, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#2f5597")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 9),
        ("ALIGN", (2,1), (3,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.lightgrey]),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    story.append(tbl)

    story.append(PageBreak())
    story.append(Paragraph("Details and Evidence", h2))
    for f in findings:
        story.append(Paragraph(f"<b>{f.issue_id}</b> — {f.issue_name}", body))
        story.append(Paragraph(f"<b>Status:</b> {f.status} &nbsp;&nbsp; <b>Fix Type:</b> {f.fix_type}", body))
        story.append(Paragraph(f"<b>Device:</b> {f.device} &nbsp;&nbsp; <b>Vendor:</b> {f.vendor}", body))
        if f.remediation:
            story.append(Paragraph(f"<b>Remediation:</b> {f.remediation}", body))
        if f.evidence:
            ev = f.evidence.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(f"<b>Evidence:</b><br/><font name='Courier'>{ev.replace('\n','<br/>')}</font>", small))
        if f.notes:
            story.append(Paragraph(f"<b>Notes:</b> {f.notes}", body))
        story.append(Spacer(1, 10))

    doc.build(story)
