from pathlib import Path
# trigger final
p=Path('indicadores_pdf.py')
t=p.read_text(encoding='utf-8')
old='''    _text(d, (left, 2334), f"GESTÃO OPERACIONAL  •  {now:%d/%m/%Y às %H:%M}", font=_font(30), fill=MUTED)'''
new='''    _text(d, (left, 2334), f"GESTÃO OPERACIONAL  •  {now:%d/%m/%Y às %H:%M}", font=_font(32), fill="#334155")'''
if old not in t:
    raise SystemExit('Rodape esperado nao encontrado')
t=t.replace(old,new,1)
p.write_text(t,encoding='utf-8')
print('Rodape final ajustado')
