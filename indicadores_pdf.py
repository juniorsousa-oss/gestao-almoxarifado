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

EXPORT_LAYOUT_VERSION = "print-clean-a4-v2"

LAST_INDICADORES = []
_ORIGINAL_DOWNLOAD_BUTTON = st.download_button

# Tema claro, de alto contraste e pensado para impressão em A4 paisagem.
BG = "#FFFFFF"
PANEL = "#FFFFFF"
CARD = "#FFFFFF"
BORDER = "#D1D5DB"
GRID = "#E5E7EB"
TEXT = "#111827"
MUTED = "#6B7280"
YELLOW = "#F4C430"
YELLOW_DARK = "#B88900"
META = "#1F2937"
GREEN = "#15803D"
RED = "#B91C1C"
STATUS_NEUTRAL_BG = "#F3F4F6"
STATUS_OK_BG = "#DCFCE7"
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
        return "SEM HISTÓRICO", MUTED, STATUS_NEUTRAL_BG, "—"
    if diff >= 0:
        return "ACIMA DA META", GREEN, STATUS_OK_BG, "OK"
    return "ABAIXO DA META", RED, STATUS_BAD_BG, "ATENÇÃO"


def gerar_imagem_indicador(nome, rows, indice):
    # A4 paisagem aproximado a 150 dpi: excelente leitura em tela e impressão.
    W, H = 1754, 1240
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)

    f_title = _font(36, True)
    f_subtitle = _font(18)
    f_label = _font(16, True)
    f_value = _font(40, True)
    f_small = _font(15)
    f_chart_title = _font(23, True)
    f_axis = _font(15)
    f_axis_bold = _font(16, True)
    f_bar_label = _font(16, True)
    f_status = _font(16, True)

    rows = rows or []
    latest = rows[-1] if rows else None
    first = rows[0] if rows else None
    value, meta, diff = _value_meta_diff(latest)
    status, status_color, status_bg, status_badge = _status(diff)

    # Moldura geral discreta.
    _rounded(d, (28, 24, W - 28, H - 24), PANEL, outline="#C7CDD4", radius=24, width=2)

    # Cabeçalho.
    d.rounded_rectangle((54, 50, 66, 94), radius=4, fill=YELLOW)
    d.text((82, 47), f"{indice:02d} · {nome}", font=f_title, fill=TEXT)

    if first and latest:
        periodo_txt = (
            f"Fechamento mensal | {_month(first.get('competencia'))} até "
            f"{_month(latest.get('competencia'))} | último lançamento válido de cada mês"
        )
    else:
        periodo_txt = "Fechamento mensal | último lançamento válido de cada mês"
    d.text((82, 102), periodo_txt, font=f_subtitle, fill=MUTED)

    # KPIs com mais espaço e leitura.
    cards = [
        ("RESULTADO FINAL", _pct(value), _month(latest.get("competencia")) if latest else "Sem lançamento", TEXT),
        ("META DO PERÍODO", _pct(meta), "Referência do fechamento", TEXT),
        ("DIFERENÇA", _pct_signed(diff), "Resultado − meta", status_color if diff is not None else TEXT),
        ("STATUS", status, _month(latest.get("competencia")) if latest else "Sem lançamento", status_color),
    ]

    cards_y1, cards_y2 = 155, 335
    margin_x, gap = 54, 18
    card_w = (W - (margin_x * 2) - (gap * 3)) // 4

    for i, (label, val, sub, color) in enumerate(cards):
        x1 = margin_x + i * (card_w + gap)
        x2 = x1 + card_w
        _rounded(d, (x1, cards_y1, x2, cards_y2), CARD, outline=BORDER, radius=18, width=2)
        d.text((x1 + 22, cards_y1 + 22), label, font=f_label, fill="#374151")

        # Evita texto de status muito largo.
        val_font = f_value if i < 3 else _font(25, True)
        d.text((x1 + 22, cards_y1 + 72), val, font=val_font, fill=color)
        d.text((x1 + 22, cards_y1 + 140), sub, font=f_small, fill=MUTED)

        if i == 3:
            badge_box = (x2 - 132, cards_y1 + 30, x2 - 22, cards_y1 + 72)
            _rounded(d, badge_box, status_bg, outline="#CBD5E1", radius=18, width=1)
            _center(d, status_badge, badge_box, f_status, status_color)

    # Painel do gráfico.
    cx1, cy1, cx2, cy2 = 54, 375, W - 54, H - 86
    _rounded(d, (cx1, cy1, cx2, cy2), "#FFFFFF", outline=BORDER, radius=20, width=2)

    d.text((cx1 + 24, cy1 + 22), "Evolução mensal do indicador", font=f_chart_title, fill=TEXT)

    # Legenda compacta e legível.
    legend_y = cy1 + 74
    d.rounded_rectangle((cx1 + 24, legend_y, cx1 + 54, legend_y + 12), radius=4, fill=YELLOW)
    d.text((cx1 + 66, legend_y - 5), "Resultado", font=f_axis, fill=MUTED)

    d.line((cx1 + 190, legend_y + 6, cx1 + 226, legend_y + 6), fill=META, width=4)
    d.ellipse((cx1 + 205, legend_y + 1, cx1 + 215, legend_y + 11), fill="#FFFFFF", outline=META, width=2)
    d.text((cx1 + 238, legend_y - 5), "Meta", font=f_axis, fill=MUTED)

    plot_l, plot_r = cx1 + 82, cx2 - 36
    plot_t, plot_b = cy1 + 130, cy2 - 90
    plot_h = plot_b - plot_t
    plot_w = plot_r - plot_l

    # Usamos 110% internamente para deixar espaço acima das barras e evitar
    # percentuais encavalando o limite superior.
    scale_max = 110.0
    for tick in (0, 20, 40, 60, 80, 100):
        y = plot_b - plot_h * (tick / scale_max)
        d.line((plot_l, y, plot_r, y), fill=GRID, width=1)
        tick_txt = f"{tick}%"
        bb = d.textbbox((0, 0), tick_txt, font=f_axis)
        d.text((plot_l - 18 - (bb[2] - bb[0]), y - 9), tick_txt, font=f_axis, fill=MUTED)

    # Eixo base.
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
        bar_w = min(70, max(34, step * 0.42))
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

            # Resultado acima da barra, sem colisão com a meta.
            result_txt = _pct(val)
            bb = d.textbbox((0, 0), result_txt, font=f_bar_label)
            tw = bb[2] - bb[0]
            label_y = max(plot_t + 4, top - 28)
            d.text((center_x - tw / 2, label_y), result_txt, font=f_bar_label, fill=TEXT)

            # Mês abaixo do eixo.
            month_txt = _month(row.get("competencia"))
            bbm = d.textbbox((0, 0), month_txt, font=f_axis_bold)
            mw = bbm[2] - bbm[0]
            d.text((center_x - mw / 2, plot_b + 22), month_txt, font=f_axis_bold, fill="#374151")

            my = plot_b - plot_h * (met / scale_max)
            meta_points.append((center_x, my))

        # Meta como linha contínua, muito mais limpa que um traço em cada barra.
        if len(meta_points) >= 2:
            d.line(meta_points, fill=META, width=4, joint="curve")
        for mx, my in meta_points:
            d.ellipse((mx - 6, my - 6, mx + 6, my + 6), fill="#FFFFFF", outline=META, width=3)

    # Rodapé discreto.
    d.text(
        (56, H - 53),
        f"GESTÃO OPERACIONAL · Exportado em {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        font=f_small,
        fill="#9CA3AF",
    )
    d.text(
        (W - 310, H - 53),
        "Formato otimizado para impressão",
        font=f_small,
        fill="#9CA3AF",
    )
    return im


def gerar_imagens_zip(indicadores):
    groups = _groups(indicadores)
    buffer = BytesIO()
    with ZipFile(buffer, "w", ZIP_DEFLATED) as zf:
        for idx, (name, rows) in enumerate(groups.items(), 1):
            img = gerar_imagem_indicador(name, rows, idx)
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
