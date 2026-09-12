from pathlib import Path

path = Path("indicadores_pdf.py")
text = path.read_text(encoding="utf-8")

text = text.replace(
    'EXPORT_LAYOUT_VERSION = "print-clean-a4-v6-unicode"',
    'EXPORT_LAYOUT_VERSION = "print-official-a4-v7"',
)

if 'PRINT_STANDARD = "A4_EXECUTIVO_V1"' not in text:
    text = text.replace(
        'EXPORT_LAYOUT_VERSION = "print-official-a4-v7"\n',
        'EXPORT_LAYOUT_VERSION = "print-official-a4-v7"\nPRINT_STANDARD = "A4_EXECUTIVO_V1"\n',
        1,
    )

text = text.replace(
    'status, status_color, _ = _status(diff)',
    'status, status_color, status_bg = _status(diff)',
    1,
)

old_status = '''        if i == 3:\n            words = main.split(" ", 1)\n            f = _font(54, True)\n            for j, line in enumerate(words):\n                _text(d, (x + 38, top + 115 + j * 64), line, font=f, fill=color)\n        else:\n'''
new_status = '''        if i == 3:\n            # Badge executivo: destaca o status sem competir com os KPIs numéricos.\n            badge = (x + 34, top + 112, end - 34, top + 238)\n            _rounded(d, badge, status_bg, outline=None, radius=36, width=0)\n            status_font = _fit_font(d, main, 48, card_width - 116, True)\n            _center(d, main, badge, status_font, color)\n        else:\n'''
if old_status not in text:
    raise SystemExit("Bloco de status esperado não encontrado")
text = text.replace(old_status, new_status, 1)

text = text.replace(
    '"Último lançamento válido de cada mês", font=_font(38)',
    '"Último fechamento válido de cada mês", font=_font(38)',
    1,
)

# Legenda e linha de meta mais elegantes, sem perder contraste.
text = text.replace(
    'd.line((right - 300, 910, right - 220, 910), fill=META, width=6)',
    'd.line((right - 300, 910, right - 220, 910), fill=META, width=4)',
    1,
)
text = text.replace(
    'd.ellipse((right - 268, 902, right - 252, 918), fill=BG, outline=META, width=4)',
    'd.ellipse((right - 266, 904, right - 254, 916), fill=BG, outline=META, width=3)',
    1,
)
text = text.replace(
    'd.line((a, b), fill=META, width=6)',
    'd.line((a, b), fill=META, width=4)',
)
text = text.replace(
    'd.ellipse((x - 9, y - 9, x + 9, y + 9), fill=BG, outline=META, width=5)',
    'd.ellipse((x - 7, y - 7, x + 7, y + 7), fill=BG, outline=META, width=4)',
)

# Rodapé com contraste e hierarquia um pouco maiores para impressão.
text = text.replace(
    'font=_font(30), fill=MUTED)',
    'font=_font(32), fill="#334155")',
    1,
)
text = text.replace(
    'font=_font(30, True), fill=MUTED)',
    'font=_font(32, True), fill="#334155")',
    1,
)

path.write_text(text, encoding="utf-8")
print("Padrão oficial A4 executivo v1 aplicado.")
