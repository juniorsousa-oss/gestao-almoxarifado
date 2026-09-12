from pathlib import Path

# Disparo temporário do workflow de aplicação/validação.
path = Path('indicadores_pdf.py')
text = path.read_text(encoding='utf-8')

text = text.replace(
    'EXPORT_LAYOUT_VERSION = "print-approved-v3-logo"',
    'EXPORT_LAYOUT_VERSION = "print-approved-v4-typography"',
)

old_font = '''def _font(size, bold=False):\n    path = (\n        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"\n        if bold\n        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"\n    )\n    try:\n        return ImageFont.truetype(path, size)\n    except Exception:\n        return ImageFont.load_default()\n'''

new_font = '''def _font(size, bold=False):\n    """Fonte TrueType robusta para manter a escala tipográfica em produção.\n\n    O Streamlit Cloud pode não possuir o caminho DejaVu usado localmente.\n    Quando isso acontecia, Pillow caía na fonte bitmap padrão e ignorava\n    completamente os tamanhos definidos no layout.\n    """\n    bold_candidates = [\n        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",\n        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",\n        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",\n        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",\n        "DejaVuSans-Bold.ttf",\n        "LiberationSans-Bold.ttf",\n    ]\n    regular_candidates = [\n        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",\n        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",\n        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",\n        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",\n        "DejaVuSans.ttf",\n        "LiberationSans-Regular.ttf",\n    ]\n    for candidate in (bold_candidates if bold else regular_candidates):\n        try:\n            return ImageFont.truetype(candidate, size=size)\n        except Exception:\n            continue\n\n    # Pillow recente permite escalar a fonte padrão. Isso evita voltar ao\n    # bitmap minúsculo mesmo em ambientes sem fontes de sistema conhecidas.\n    try:\n        return ImageFont.load_default(size=size)\n    except TypeError:\n        return ImageFont.load_default()\n'''

if old_font not in text:
    raise SystemExit('Bloco _font esperado não encontrado; patch interrompido.')
text = text.replace(old_font, new_font)

old_sizes = '''    f_title = _font(43, True)\n    f_subtitle = _font(18)\n    f_label = _font(17, True)\n    f_value = _font(49, True)\n    f_small = _font(16)\n    f_chart_title = _font(27, True)\n    f_axis = _font(16)\n    f_axis_bold = _font(17, True)\n    f_bar_label = _font(17, True)\n    f_status = _font(21, True)\n'''
new_sizes = '''    # Escala visual equivalente ao esboço aprovado para leitura em mural/A4.\n    f_title = _font(50, True)\n    f_subtitle = _font(22)\n    f_label = _font(20, True)\n    f_value = _font(62, True)\n    f_small = _font(18)\n    f_chart_title = _font(31, True)\n    f_axis = _font(18)\n    f_axis_bold = _font(20, True)\n    f_bar_label = _font(20, True)\n    f_status = _font(25, True)\n'''
if old_sizes not in text:
    raise SystemExit('Bloco de tamanhos esperado não encontrado; patch interrompido.')
text = text.replace(old_sizes, new_sizes)

# Ajustes finos de espaçamento para acompanhar o aumento das fontes.
text = text.replace('d.text((80, 105), periodo_txt, font=f_subtitle, fill=MUTED)',
                    'd.text((80, 112), periodo_txt, font=f_subtitle, fill=MUTED)')
text = text.replace('cards_y1, cards_y2 = 168, 405', 'cards_y1, cards_y2 = 176, 405')
text = text.replace('d.text((x1 + 28, cards_y1 + 82), val, font=f_value, fill=color)',
                    'd.text((x1 + 28, cards_y1 + 76), val, font=f_value, fill=color)')
text = text.replace('badge_box = (x1 + 36, cards_y1 + 88, x2 - 36, cards_y1 + 157)',
                    'badge_box = (x1 + 34, cards_y1 + 82, x2 - 34, cards_y1 + 164)')
text = text.replace('cx1, cy1, cx2, cy2 = 38, 448, W - 38, H - 92',
                    'cx1, cy1, cx2, cy2 = 38, 440, W - 38, H - 92')
text = text.replace('legend_y = cy1 + 94', 'legend_y = cy1 + 100')
text = text.replace('plot_t, plot_b = cy1 + 168, cy2 - 85', 'plot_t, plot_b = cy1 + 178, cy2 - 90')
text = text.replace('max(plot_t + 4, top - 31)', 'max(plot_t + 4, top - 36)')
text = text.replace('plot_b + 25', 'plot_b + 27')

path.write_text(text, encoding='utf-8')
print('Patch tipográfico aplicado com sucesso.')
