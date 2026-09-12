from pathlib import Path

path = Path("indicadores_pdf.py")
text = path.read_text(encoding="utf-8")

if "import unicodedata" not in text:
    text = text.replace("import base64\n", "import base64\nimport unicodedata\n", 1)

text = text.replace(
    'EXPORT_LAYOUT_VERSION = "print-clean-a4-v5-300dpi"',
    'EXPORT_LAYOUT_VERSION = "print-clean-a4-v6-unicode"',
)
text = text.replace('MUTED = "#64748B"', 'MUTED = "#475569"')

# Garante que toda chamada direta de texto passe pela normalização Unicode.
text = text.replace("d.text(", "_text(d, ")
text = text.replace("draw.text(", "_text(draw, ")

marker = "\n\ndef _pct(v):"
if "def _norm_text(" not in text:
    helper = '''\n\ndef _norm_text(value):\n    """Normaliza strings para NFC antes da renderização pelo Pillow."""\n    if value is None:\n        return ""\n    return unicodedata.normalize("NFC", str(value))\n\n\ndef _text(draw, xy, value, *args, **kwargs):\n    return draw.text(xy, _norm_text(value), *args, **kwargs)\n'''
    if marker not in text:
        raise SystemExit("Ponto de inserção Unicode não encontrado")
    text = text.replace(marker, helper + marker, 1)

# _center usa textbbox; normaliza também antes de medir.
old_center = '''def _center(draw, text, box, font, fill):\n    x1, y1, x2, y2 = box\n    bb = draw.textbbox((0, 0), text, font=font)\n'''
new_center = '''def _center(draw, text, box, font, fill):\n    text = _norm_text(text)\n    x1, y1, x2, y2 = box\n    bb = draw.textbbox((0, 0), text, font=font)\n'''
if old_center in text:
    text = text.replace(old_center, new_center, 1)

# _fit_font mede textos dinâmicos, inclusive nomes de indicadores com acento.
old_fit = '''def _fit_font(draw, text, size, max_width, bold=False):\n    """Ajusta pelo tamanho real dos glifos, inclusive para novos indicadores."""\n    font = _font(size, bold)\n'''
new_fit = '''def _fit_font(draw, text, size, max_width, bold=False):\n    """Ajusta pelo tamanho real dos glifos, inclusive para novos indicadores."""\n    text = _norm_text(text)\n    font = _font(size, bold)\n'''
if old_fit in text:
    text = text.replace(old_fit, new_fit, 1)

# Ajustes visuais finais: maior presença do subtítulo e título do gráfico.
text = text.replace('font=_font(38), fill=MUTED)', 'font=_font(42), fill=MUTED)')
text = text.replace('"Evolução mensal", font=_font(54, True)', '"Evolução mensal do indicador", font=_font(58, True)')
text = text.replace('"Último lançamento de cada mês", font=_font(36)', '"Último lançamento válido de cada mês", font=_font(38)')

# Segurança: evita recursão acidental no helper se o patch for executado novamente.
text = text.replace('def _text(draw, xy, value, *args, **kwargs):\n    return _text(draw, xy, _norm_text(value), *args, **kwargs)',
                    'def _text(draw, xy, value, *args, **kwargs):\n    return draw.text(xy, _norm_text(value), *args, **kwargs)')

path.write_text(text, encoding="utf-8")
print("Unicode e refinamento visual aplicados.")
