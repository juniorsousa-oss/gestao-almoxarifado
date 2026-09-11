from __future__ import annotations

from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)
from reportlab.graphics.shapes import Drawing, Rect, Line, String


GROUPS = ["ACURÁCIA DE ESTOQUE", "ENTREGAS NO PRAZO", "5S"]
ALIASES = {
    "ACURACIDADE DE ESTOQUE": "ACURÁCIA DE ESTOQUE",
    "ACURÁCIDADE DE ESTOQUE": "ACURÁCIA DE ESTOQUE",
    "ACURÁCIA DE ESTOQUE": "ACURÁCIA DE ESTOQUE",
    "ACURACIA DE ESTOQUE": "ACURÁCIA DE ESTOQUE",
    "ENTREGAS NO PRAZO": "ENTREGAS NO PRAZO",
    "5S": "5S",
}


def _pct(v):
    try:
        return f"{float(v):.2f}%".replace(".", ",")
    except Exception:
        return "—"


def _month(value):
    try:
        d = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        meses = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]
        return f"{meses[d.month - 1]}/{d.year}"
    except Exception:
        text = str(value or "—")
        return text[:16]


def _ordered(rows):
    return sorted(rows or [], key=lambda r: str(r.get("competencia") or ""))


def _chart(rows):
    rows = _ordered(rows)
    w, h = 470, 190
    d = Drawing(w, h)
    left, bottom, top = 42, 28, 160
    chart_h = top - bottom
    chart_w = w - left - 12

    d.add(Rect(left, bottom, chart_w, chart_h, fillColor=colors.HexColor("#0b100e"), strokeColor=colors.HexColor("#26342e"), strokeWidth=1))
    for tick in (0, 25, 50, 75, 100):
        y = bottom + chart_h * tick / 100
        d.add(Line(left, y, left + chart_w, y, strokeColor=colors.HexColor("#25302b"), strokeWidth=0.6))
        d.add(String(left - 7, y - 3, f"{tick}%", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor("#7f8a85"), textAnchor="end"))

    if not rows:
        d.add(String(w / 2, 90, "Nenhum lançamento histórico", fontName="Helvetica-Bold", fontSize=10, fillColor=colors.HexColor("#8c9691"), textAnchor="middle"))
        return d

    step = chart_w / max(len(rows), 1)
    bar_w = min(30, step * 0.48)
    for i, row in enumerate(rows):
        try:
            value = max(0.0, min(100.0, float(row.get("valor") or 0)))
        except Exception:
            value = 0.0
        try:
            meta = max(0.0, min(100.0, float(row.get("meta") or 0)))
        except Exception:
            meta = 0.0
        x = left + step * i + (step - bar_w) / 2
        bh = chart_h * value / 100
        d.add(Rect(x, bottom, bar_w, bh, fillColor=colors.HexColor("#ffd43d"), strokeColor=None))
        my = bottom + chart_h * meta / 100
        d.add(Line(x - 4, my, x + bar_w + 4, my, strokeColor=colors.HexColor("#f4f5f4"), strokeWidth=2))
        d.add(String(x + bar_w / 2, max(bottom + 3, bottom + bh + 4), f"{value:.1f}%", fontName="Helvetica-Bold", fontSize=6.5, fillColor=colors.HexColor("#f4f5f4"), textAnchor="middle"))
        d.add(String(x + bar_w / 2, 14, _month(row.get("competencia")), fontName="Helvetica", fontSize=6.5, fillColor=colors.HexColor("#8c9691"), textAnchor="middle"))
    d.add(String(w - 12, h - 10, "Resultado", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor("#ffd43d"), textAnchor="end"))
    d.add(Line(w - 72, h - 7, w - 52, h - 7, strokeColor=colors.HexColor("#f4f5f4"), strokeWidth=2))
    d.add(String(w - 44, h - 10, "Meta", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor("#f4f5f4")))
    return d


def _latest(rows):
    ordered = _ordered(rows)
    if not ordered:
        return None, None, None, "SEM HISTÓRICO"
    row = ordered[-1]
    try:
        value = float(row.get("valor")) if row.get("valor") is not None else None
    except Exception:
        value = None
    try:
        meta = float(row.get("meta")) if row.get("meta") is not None else None
    except Exception:
        meta = None
    diff = value - meta if value is not None and meta is not None else None
    status = "ACIMA DA META" if diff is not None and diff >= 0 else ("ABAIXO DA META" if diff is not None else "SEM META")
    return value, meta, diff, status


def gerar_pdf_indicadores(indicadores) -> bytes:
    groups = {name: [] for name in GROUPS}
    for row in indicadores or []:
        key = ALIASES.get(str(row.get("indicador") or "").strip().upper())
        if key in groups:
            groups[key].append(row)

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title="Indicadores Operacionais",
        author="Gestão Operacional",
    )

    styles = getSampleStyleSheet()
    title = ParagraphStyle("TitleCustom", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=20, leading=23, textColor=colors.HexColor("#18201c"), alignment=TA_LEFT, spaceAfter=4)
    subtitle = ParagraphStyle("SubtitleCustom", parent=styles["Normal"], fontName="Helvetica", fontSize=9, leading=12, textColor=colors.HexColor("#68736d"), spaceAfter=14)
    section = ParagraphStyle("SectionCustom", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=14, leading=17, textColor=colors.HexColor("#18201c"), spaceBefore=3, spaceAfter=8)
    small = ParagraphStyle("Small", parent=styles["Normal"], fontName="Helvetica", fontSize=7.5, leading=10, textColor=colors.HexColor("#68736d"))
    status = ParagraphStyle("Status", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9, leading=11, textColor=colors.HexColor("#18201c"), alignment=TA_CENTER)

    story = [
        Paragraph("INDICADORES OPERACIONAIS", title),
        Paragraph(f"Relatório para divulgação · Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}", subtitle),
    ]

    for index, name in enumerate(GROUPS):
        rows = _ordered(groups[name])
        value, meta, diff, stat = _latest(rows)
        if index:
            story.append(Spacer(1, 7 * mm))

        story.append(Paragraph(f"{index + 1:02d} · {name}", section))
        kpi_data = [[
            Paragraph("RESULTADO", small),
            Paragraph("META", small),
            Paragraph("DIFERENÇA", small),
            Paragraph("STATUS", small),
        ], [
            Paragraph(_pct(value), status),
            Paragraph(_pct(meta), status),
            Paragraph(_pct(diff), status),
            Paragraph(stat, status),
        ]]
        kpi = Table(kpi_data, colWidths=[43 * mm] * 4, rowHeights=[9 * mm, 13 * mm])
        kpi.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f5f7f5")),
            ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#d7ddd9")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dfe4e1")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(kpi)
        story.append(Spacer(1, 4 * mm))
        story.append(_chart(rows))
        story.append(Spacer(1, 3 * mm))

        table_data = [["COMPETÊNCIA", "RESULTADO", "META", "DIFERENÇA", "STATUS"]]
        for row in rows:
            try:
                v = float(row.get("valor")) if row.get("valor") is not None else None
            except Exception:
                v = None
            try:
                m = float(row.get("meta")) if row.get("meta") is not None else None
            except Exception:
                m = None
            df = v - m if v is not None and m is not None else None
            stt = "ACIMA" if df is not None and df >= 0 else ("ABAIXO" if df is not None else "SEM META")
            table_data.append([_month(row.get("competencia")), _pct(v), _pct(m), _pct(df), stt])
        if len(table_data) > 1:
            table = Table(table_data, colWidths=[35 * mm, 35 * mm, 35 * mm, 35 * mm, 30 * mm], repeatRows=1)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#18201c")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7.5),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d7ddd9")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f8f7")]),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(table)
        else:
            story.append(Paragraph("Nenhum lançamento histórico para este indicador.", small))

    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph("Documento gerado automaticamente pelo painel Gestão Operacional. Os valores apresentados são os lançamentos registrados no sistema.", small))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#d7ddd9"))
        canvas.line(16 * mm, 11 * mm, A4[0] - 16 * mm, 11 * mm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#7b8580"))
        canvas.drawString(16 * mm, 7 * mm, "GESTÃO OPERACIONAL")
        canvas.drawRightString(A4[0] - 16 * mm, 7 * mm, f"Página {doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()
