from __future__ import annotations

import base64
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

# Sempre que o desenho da imagem mudar, altere esta versão para invalidar o cache.
EXPORT_LAYOUT_VERSION = "print-approved-v3-logo"

LAST_INDICADORES = []
_ORIGINAL_DOWNLOAD_BUTTON = st.download_button

# Paleta aprovada: clara, alto contraste e adequada para impressão.
BG = "#FFFFFF"
PANEL = "#FFFFFF"
CARD = "#FFFFFF"
BORDER = "#CBD5E1"
GRID = "#E2E8F0"
TEXT = "#0F172A"
MUTED = "#64748B"
YELLOW = "#FFC21C"
YELLOW_DARK = "#D89E00"
META = "#1E293B"
GREEN = "#149447"
RED = "#C62828"
STATUS_NEUTRAL_BG = "#F1F5F9"
STATUS_OK_BG = "#D1FAE5"
STATUS_BAD_BG = "#FEE2E2"


def _font(size, bold=False):
    path = (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    )
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _pct(v):
    try:
        return f"{float(v):.2f}%".replace(".", ",")
    except Exception:
        return "—"


def _pct_signed(v):
    try:
        return f"{float(v):+.2f}%".replace(".", ",")
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
        value = float(row.get("valor")) if row and row.get("valor") is not None else None
    except Exception:
        value = None
    try:
        meta = float(row.get("meta")) if row and row.get("meta") is not None else None
    except Exception:
        meta = None
    diff = value - meta if value is not None and meta is not None else None
    return value, meta, diff


def _rounded(draw, box, fill, outline=BORDER, radius=18, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def _center(draw, text, box, font, fill):
    x1, y1, x2, y2 = box
    bb = draw.textbbox((0, 0), text, font=font)
    tw = bb[2] - bb[0]
    th = bb[3] - bb[1]
    draw.text(
        ((x1 + x2 - tw) / 2, (y1 + y2 - th) / 2 - 2),
        text,
        font=font,
        fill=fill,
    )


def _status(diff):
    if diff is None:
        return "SEM HISTÓRICO", MUTED, STATUS_NEUTRAL_BG
    if diff >= 0:
        return "ACIMA DA META", GREEN, STATUS_OK_BG
    return "ABAIXO DA META", RED, STATUS_BAD_BG


def _logo_from_config():
    """Retorna a mesma logo configurada no aplicativo/menu lateral."""
    try:
        cfg = st.session_state.get("config") or {}
        return cfg.get("logo_base64"), cfg.get("logo_mime")
    except Exception:
        return None, None


def _load_logo(logo_base64=None, logo_mime=None):
    if not logo_base64:
        logo_base64, logo_mime = _logo_from_config()
    if not logo_base64:
        return None
    # O upload atual do app trabalha com imagem raster; SVG fica sem renderização
    # na exportação até existir um conversor SVG no ambiente.
    if str(logo_mime or "").lower() == "image/svg+xml":
        return None
    try:
        raw = base64.b64decode(logo_base64)
        logo = Image.open(BytesIO(raw)).convert("RGBA")
        return logo
    except Exception:
        return None


def _draw_logo(canvas, logo_base64=None, logo_mime=None):
    """Desenha a logo real no canto superior direito preservando proporção."""
    logo = _load_logo(logo_base64, logo_mime)
    if logo is None:
        return False

    # Caixa reservada conforme esboço aprovado.
    box = (1325, 38, 1692, 132)
    x1, y1, x2, y2 = box
    max_w, max_h = x2 - x1, y2 - y1
    lw, lh = logo.size
    if not lw or not lh:
        return False

    scale = min(max_w / lw, max_h / lh)
    nw, nh = max(1, int(lw * scale)), max(1, int(lh * scale))
    logo = logo.resize((nw, nh), Image.Resampling.LANCZOS)
    px = x2 - nw
    py = y1 + (max_h - nh) // 2
    canvas.paste(logo, (px, py), logo)
    return True


def gerar_imagem_indicador(nome, rows, indice, logo_base64=None, logo_mime=None):
    # A4 paisagem aproximado a 150 dpi.
    W, H = 1754, 1240
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)

    # Hierarquia tipográfica do esboço aprovado.
    f_title = _font(43, True)
    f_subtitle = _font(18)
    f_label = _font(17, True)
    f_value = _font(49, True)
    f_small = _font(16)
    f_chart_title = _font(27, True)
    f_axis = _font(16)
    f_axis_bold = _font(17, True)
    f_bar_label = _font(17, True)
    f_status = _font(21, True)

    rows = rows or []
    latest = rows[-1] if rows else None
    first = rows[0] if rows else None
    value, meta, diff = _value_meta_diff(latest)
    status, status_color, status_bg = _status(diff)

    # Cabeçalho limpo, sem moldura geral pesada.
    d.rounded_rectangle((38, 45, 52, 132), radius=7, fill=YELLOW)
    d.text((78, 47), f"{indice:02d} · {nome}", font=f_title, fill=TEXT)

    if first and latest:
        periodo_txt = (
            f"Fechamento mensal | {_month(first.get('competencia'))} até "
            f"{_month(latest.get('competencia'))} | último lançamento válido de cada mês"
        )
    else:
        periodo_txt = "Fechamento mensal | último lançamento válido de cada mês"
    d.text((80, 105), periodo_txt, font=f_subtitle, fill=MUTED)

    # Usa exatamente a logo cadastrada no app.
    _draw_logo(im, logo_base64, logo_mime)

    # Quatro KPIs grandes e legíveis.
    cards = [
        ("RESULTADO FINAL", _pct(value), _month(latest.get("competencia")) if latest else "Sem lançamento", TEXT),
        ("META DO PERÍODO", _pct(meta), "Referência do fechamento", TEXT),
        ("DIFERENÇA", _pct_signed(diff), "Resultado em relação à meta", status_color if diff is not None else TEXT),
        ("STATUS", status, _month(latest.get("competencia")) if latest else "Sem lançamento", status_color),
    ]

    cards_y1, cards_y2 = 168, 405
    margin_x, gap = 38, 18
    card_w = (W - (margin_x * 2) - (gap * 3)) // 4

    for i, (label, val, sub, color) in enumerate(cards):
        x1 = margin_x + i * (card_w + gap)
        x2 = x1 + card_w
        _rounded(d, (x1, cards_y1, x2, cards_y2), CARD, outline=BORDER, radius=18, width=2)
        d.text((x1 + 28, cards_y1 + 28), label, font=f_label, fill="#475569")

        if i < 3:
            d.text((x1 + 28, cards_y1 + 82), val, font=f_value, fill=color)
        else:
            # Status vira badge central, como no esboço aprovado.
            badge_box = (x1 + 36, cards_y1 + 88, x2 - 36, cards_y1 + 157)
            _rounded(d, badge_box, status_bg, outline=None, radius=27, width=0)
            _center(d, val, badge_box, f_status, status_color)

        d.text((x1 + 28, cards_y2 - 50), sub, font=f_small, fill=MUTED)

    # Painel principal do gráfico.
    cx1, cy1, cx2, cy2 = 38, 448, W - 38, H - 92
    _rounded(d, (cx1, cy1, cx2, cy2), PANEL, outline=BORDER, radius=18, width=2)
    d.text((cx1 + 34, cy1 + 28), "Evolução mensal do indicador", font=f_chart_title, fill=TEXT)

    # Legenda ampla e clara.
    legend_y = cy1 + 94
    d.rounded_rectangle((cx1 + 34, legend_y, cx1 + 96, legend_y + 22), radius=5, fill=YELLOW)
    d.text((cx1 + 114, legend_y - 2), "Resultado", font=f_axis, fill=MUTED)
    d.line((cx1 + 260, legend_y + 11, cx1 + 326, legend_y + 11), fill=META, width=5)
    d.ellipse((cx1 + 288, legend_y + 2, cx1 + 306, legend_y + 20), fill="#FFFFFF", outline=META, width=4)
    d.text((cx1 + 342, legend_y - 2), "Meta", font=f_axis, fill=MUTED)

    plot_l, plot_r = cx1 + 105, cx2 - 38
    plot_t, plot_b = cy1 + 168, cy2 - 85
    plot_h = plot_b - plot_t
    plot_w = plot_r - plot_l

    # 112% deixa respiro para rótulos de barras próximas de 100%.
    scale_max = 112.0
    for tick in (0, 20, 40, 60, 80, 100):
        y = plot_b - plot_h * (tick / scale_max)
        d.line((plot_l, y, plot_r, y), fill=GRID, width=1)
        tick_txt = f"{tick}%"
        bb = d.textbbox((0, 0), tick_txt, font=f_axis)
        d.text((plot_l - 22 - (bb[2] - bb[0]), y - 10), tick_txt, font=f_axis, fill=MUTED)

    d.line((plot_l, plot_b, plot_r, plot_b), fill="#CBD5E1", width=2)

    if not rows:
        _center(
            d,
            "Nenhum lançamento histórico para o período selecionado.",
            (plot_l, plot_t, plot_r, plot_b),
            f_subtitle,
            MUTED,
        )
    else:
        n = len(rows)
        step = plot_w / max(n, 1)
        bar_w = min(92, max(46, step * 0.48))
        meta_points = []

        for i, row in enumerate(rows):
            val, met, _ = _value_meta_diff(row)
            val = max(0.0, min(100.0, val or 0.0))
            met = max(0.0, min(100.0, met or 0.0))

            center_x = plot_l + (i + 0.5) * step
            x1 = center_x - bar_w / 2
            x2 = center_x + bar_w / 2
            top = plot_b - plot_h * (val / scale_max)

            d.rounded_rectangle(
                (x1, top, x2, plot_b),
                radius=7,
                fill=YELLOW,
                outline=YELLOW_DARK,
                width=1,
            )

            result_txt = _pct(val)
            bb = d.textbbox((0, 0), result_txt, font=f_bar_label)
            d.text(
                (center_x - (bb[2] - bb[0]) / 2, max(plot_t + 4, top - 31)),
                result_txt,
                font=f_bar_label,
                fill=TEXT,
            )

            month_txt = _month(row.get("competencia"))
            bbm = d.textbbox((0, 0), month_txt, font=f_axis_bold)
            d.text(
                (center_x - (bbm[2] - bbm[0]) / 2, plot_b + 25),
                month_txt,
                font=f_axis_bold,
                fill="#475569",
            )

            my = plot_b - plot_h * (met / scale_max)
            meta_points.append((center_x, my))

        if len(meta_points) >= 2:
            d.line(meta_points, fill=META, width=5, joint="curve")
        for mx, my in meta_points:
            d.ellipse((mx - 8, my - 8, mx + 8, my + 8), fill="#FFFFFF", outline=META, width=4)

    # Rodapé do modelo aprovado.
    divider_y = H - 64
    d.line((38, divider_y, W - 38, divider_y), fill="#E2E8F0", width=2)
    d.text(
        (40, H - 47),
        f"GESTÃO OPERACIONAL · Exportado em {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        font=f_small,
        fill="#94A3B8",
    )
    footer = "Formato otimizado para impressão"
    bb = d.textbbox((0, 0), footer, font=f_small)
    d.text((W - 40 - (bb[2] - bb[0]), H - 47), footer, font=f_small, fill="#94A3B8")

    return im


def gerar_imagens_zip(indicadores, logo_base64=None, logo_mime=None):
    if not logo_base64:
        logo_base64, logo_mime = _logo_from_config()

    groups = _groups(indicadores)
    buffer = BytesIO()
    with ZipFile(buffer, "w", ZIP_DEFLATED) as zf:
        for idx, (name, rows) in enumerate(groups.items(), 1):
            img = gerar_imagem_indicador(
                name,
                rows,
                idx,
                logo_base64=logo_base64,
                logo_mime=logo_mime,
            )
            png = BytesIO()
            img.save(png, format="PNG", optimize=True)
            safe = (
                name.lower()
                .replace(" ", "_")
                .replace("á", "a")
                .replace("ã", "a")
                .replace("é", "e")
                .replace("í", "i")
                .replace("ó", "o")
                .replace("ú", "u")
                .replace("ç", "c")
            )
            zf.writestr(f"{idx:02d}_{safe}.png", png.getvalue())
    return buffer.getvalue()


def gerar_pdf_indicadores(indicadores, logo_base64=None, logo_mime=None) -> bytes:
    global LAST_INDICADORES
    LAST_INDICADORES = list(indicadores or [])
    return gerar_imagens_zip(
        LAST_INDICADORES,
        logo_base64=logo_base64,
        logo_mime=logo_mime,
    )


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
