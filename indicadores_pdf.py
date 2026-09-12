from __future__ import annotations

from datetime import datetime
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

from PIL import Image, ImageDraw, ImageFont
import streamlit as st

GROUPS = ["ACURÁCIA DE ESTOQUE", "ENTREGAS NO PRAZO", "5S"]
ALIASES = {
    "ACURACIDADE DE ESTOQUE": "ACURÁCIA DE ESTOQUE",
    "ACURÁCIDADE DE ESTOQUE": "ACURÁCIA DE ESTOQUE",
    "ACURÁCIA DE ESTOQUE": "ACURÁCIA DE ESTOQUE",
    "ACURACIA DE ESTOQUE": "ACURÁCIA DE ESTOQUE",
    "ENTREGAS NO PRAZO": "ENTREGAS NO PRAZO",
    "5S": "5S",
}

LAST_INDICADORES = []
_ORIGINAL_DOWNLOAD_BUTTON = st.download_button

BG = "#080d0b"
PANEL = "#101614"
CARD = "#121916"
BORDER = "#304039"
GRID = "#25302b"
WHITE = "#f4f5f4"
MUTED = "#8c9691"
YELLOW = "#ffd43d"
GREEN = "#4ade80"
RED = "#ff6668"


def _font(size, bold=False):
    path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _pct(v):
    try:
        return f"{float(v):.2f}%".replace(".", ",")
    except Exception:
        return "—"


def _month(value):
    try:
        d = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        meses = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]
        return f"{meses[d.month-1]}/{d.year}"
    except Exception:
        return str(value or "—")[:16].upper()


def _groups(indicadores):
    # Os três indicadores atuais permanecem sempre presentes; novos indicadores
    # encontrados no banco entram automaticamente como novas imagens.
    groups = {name: [] for name in GROUPS}
    for row in indicadores or []:
        raw = str(row.get("indicador") or "").strip()
        key = ALIASES.get(raw.upper(), raw.upper())
        if not key:
            continue
        groups.setdefault(key, []).append(row)
    for name in groups:
        groups[name].sort(key=lambda r: str(r.get("competencia") or ""))
    return groups


def _value_meta_diff(row):
    try:
        value = float(row.get("valor")) if row.get("valor") is not None else None
    except Exception:
        value = None
    try:
        meta = float(row.get("meta")) if row.get("meta") is not None else None
    except Exception:
        meta = None
    diff = value - meta if value is not None and meta is not None else None
    return value, meta, diff


def _rounded(draw, box, fill, outline=BORDER, radius=16, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def _center(draw, text, box, font, fill):
    x1, y1, x2, y2 = box
    bb = draw.textbbox((0, 0), text, font=font)
    draw.text(((x1+x2-(bb[2]-bb[0]))/2, (y1+y2-(bb[3]-bb[1]))/2-2), text, font=font, fill=fill)


def gerar_imagem_indicador(nome, rows, indice):
    W, H = 1600, 980
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    f_title = _font(28, True)
    f_label = _font(13, True)
    f_value = _font(31, True)
    f_sub = _font(13)
    f_chart_title = _font(18, True)
    f_axis = _font(12)
    f_axis_bold = _font(12, True)

    _rounded(d, (24, 20, W-24, H-20), PANEL, BORDER, 20, 1)
    d.text((44, 43), f"{indice:02d} · {nome}", font=f_title, fill=YELLOW)
    d.text((44, 84), "Fechamento mensal · último lançamento válido do período", font=f_sub, fill=MUTED)

    rows = rows or []
    latest = rows[-1] if rows else None
    value, meta, diff = _value_meta_diff(latest) if latest else (None, None, None)
    if diff is None:
        status, status_color = "SEM HISTÓRICO", MUTED
    elif diff >= 0:
        status, status_color = "ACIMA DA META", GREEN
    else:
        status, status_color = "ABAIXO DA META", RED

    kpis = [
        ("RESULTADO SELECIONADO", _pct(value), _month(latest.get("competencia")) if latest else "Nenhum lançamento", WHITE),
        ("META", _pct(meta), "Referência do lançamento", WHITE),
        ("DIFERENÇA", _pct(diff), "Resultado − meta", WHITE),
        ("STATUS", status, _month(latest.get("competencia")) if latest else "Nenhum lançamento", status_color),
    ]
    gap, x0 = 12, 44
    cw = (W-88-gap*3)//4
    for i, (label, val, sub, color) in enumerate(kpis):
        x = x0 + i*(cw+gap)
        _rounded(d, (x, 120, x+cw, 238), CARD, BORDER, 13, 1)
        d.text((x+18, 140), label, font=f_label, fill="#a8b0ac")
        d.text((x+18, 174), val, font=f_value, fill=color)
        d.text((x+18, 215), sub, font=f_sub, fill=MUTED)
        if i == 3:
            d.ellipse((x+cw-78, 145, x+cw-24, 199), fill="#1c2521" if diff is None else ("#1e3528" if diff >= 0 else "#3a2224"))
            _center(d, "↑" if diff is not None and diff >= 0 else ("↓" if diff is not None else "—"), (x+cw-78,145,x+cw-24,199), _font(28, True), color)

    cx1, cy1, cx2, cy2 = 44, 260, W-44, 900
    _rounded(d, (cx1, cy1, cx2, cy2), "#0b100e", BORDER, 14, 1)
    d.text((cx1+18, cy1+18), "Comparativo histórico", font=f_chart_title, fill=WHITE)
    d.rounded_rectangle((cx1+18, cy1+58, cx1+38, cy1+63), radius=3, fill=YELLOW)
    d.text((cx1+46, cy1+53), "Resultado", font=f_axis, fill=MUTED)
    d.rounded_rectangle((cx1+125, cy1+58, cx1+145, cy1+63), radius=3, fill=WHITE)
    d.text((cx1+153, cy1+53), "Meta", font=f_axis, fill=MUTED)

    plot_l, plot_r = cx1+58, cx2-28
    plot_t, plot_b = cy1+105, cy2-62
    plot_h = plot_b-plot_t
    plot_w = plot_r-plot_l
    for tick in (0,20,40,60,80,100):
        y = plot_b - plot_h*tick/100
        d.line((plot_l, y, plot_r, y), fill=GRID, width=1)
        d.text((plot_l-45, y-8), f"{tick}%", font=f_axis, fill="#68736d")

    if not rows:
        _center(d, "Nenhum lançamento histórico.", (plot_l, plot_t, plot_r, plot_b), f_sub, MUTED)
    else:
        n = len(rows)
        step = plot_w / max(n, 1)
        bw = min(48, max(12, step*0.48))
        for i, row in enumerate(rows):
            val, met, _ = _value_meta_diff(row)
            val = max(0, min(100, val or 0))
            met = max(0, min(100, met or 0))
            x = plot_l + i*step + (step-bw)/2
            top = plot_b - plot_h*val/100
            d.rounded_rectangle((x, top, x+bw, plot_b), radius=5, fill=YELLOW)
            my = plot_b - plot_h*met/100
            d.rounded_rectangle((x-7, my-3, x+bw+7, my+3), radius=3, fill=WHITE)
            txt = _pct(val)
            bb = d.textbbox((0,0), txt, font=f_axis_bold)
            d.text((x+bw/2-(bb[2]-bb[0])/2, max(plot_t, top-22)), txt, font=f_axis_bold, fill=WHITE)
            lab = _month(row.get("competencia"))
            bb = d.textbbox((0,0), lab, font=f_axis_bold)
            d.text((x+bw/2-(bb[2]-bb[0])/2, plot_b+18), lab, font=f_axis_bold, fill="#aeb7b2")

    d.text((44, 923), f"GESTÃO OPERACIONAL  ·  {datetime.now().strftime('%d/%m/%Y %H:%M')}", font=f_axis, fill="#65716b")
    return im


def gerar_imagens_zip(indicadores):
    groups = _groups(indicadores)
    buffer = BytesIO()
    with ZipFile(buffer, "w", ZIP_DEFLATED) as zf:
        for idx, (name, rows) in enumerate(groups.items(), 1):
            img = gerar_imagem_indicador(name, rows, idx)
            png = BytesIO()
            img.save(png, format="PNG", optimize=True)
            safe = (name.lower().replace(" ", "_").replace("á", "a").replace("ã", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")).replace("ç", "c")
            zf.writestr(f"{idx:02d}_{safe}.png", png.getvalue())
    return buffer.getvalue()


def gerar_pdf_indicadores(indicadores) -> bytes:
    global LAST_INDICADORES
    LAST_INDICADORES = list(indicadores or [])
    return gerar_imagens_zip(LAST_INDICADORES)


def _patched_download_button(label, data=None, file_name=None, mime=None, **kwargs):
    if str(label).upper().strip() == "EXPORTAR PDF":
        return _ORIGINAL_DOWNLOAD_BUTTON(
            "EXPORTAR IMAGENS",
            data=gerar_imagens_zip(LAST_INDICADORES),
            file_name="indicadores_operacionais_imagens.zip",
            mime="application/zip",
            **kwargs,
        )
    return _ORIGINAL_DOWNLOAD_BUTTON(label, data=data, file_name=file_name, mime=mime, **kwargs)

st.download_button = _patched_download_button
