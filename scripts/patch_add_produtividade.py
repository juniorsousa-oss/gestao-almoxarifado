from pathlib import Path
# trigger

# 1) Dashboard: inclui PRODUTIVIDADE como 4º indicador no mesmo fluxo visual.
p = Path('indicadores_dashboard.py')
t = p.read_text(encoding='utf-8')
old = 'groups = {"ACURÁCIA DE ESTOQUE": [], "ENTREGAS NO PRAZO": [], "5S": []}'
new = 'groups = {"ACURÁCIA DE ESTOQUE": [], "ENTREGAS NO PRAZO": [], "5S": [], "PRODUTIVIDADE": []}'
if old not in t:
    raise SystemExit('Estrutura groups do dashboard não encontrada')
t = t.replace(old, new, 1)
needle = '        "5S": "5S",\n'
if needle not in t:
    raise SystemExit('Aliases do dashboard não encontrados')
t = t.replace(needle, needle + '        "PRODUTIVIDADE": "PRODUTIVIDADE",\n', 1)
p.write_text(t, encoding='utf-8')

# 2) Exportação: inclui PRODUTIVIDADE no padrão A4 oficial.
p = Path('indicadores_pdf.py')
t = p.read_text(encoding='utf-8')
old = 'GROUPS = ["ACURÁCIA DE ESTOQUE", "ENTREGAS NO PRAZO", "5S"]'
new = 'GROUPS = ["ACURÁCIA DE ESTOQUE", "ENTREGAS NO PRAZO", "5S", "PRODUTIVIDADE"]'
if old not in t:
    raise SystemExit('GROUPS do exportador não encontrado')
t = t.replace(old, new, 1)
needle = '    "5S": "5S",\n'
if needle not in t:
    raise SystemExit('ALIASES do exportador não encontrado')
t = t.replace(needle, needle + '    "PRODUTIVIDADE": "PRODUTIVIDADE",\n', 1)
t = t.replace('EXPORT_LAYOUT_VERSION = "print-official-a4-v7"', 'EXPORT_LAYOUT_VERSION = "print-official-a4-v8-productividade"', 1)
p.write_text(t, encoding='utf-8')

print('Indicador PRODUTIVIDADE adicionado ao dashboard e exportação.')
