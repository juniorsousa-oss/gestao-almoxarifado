from pathlib import Path
p=Path("streamlit_app.py")
s=p.read_text(encoding="utf-8")
old='''label=f"{nome}
{func}
{equipe.upper()}
{status_txt} · {c.get('matricula') or 'SEM MATRÍCULA'}"'''
new='label=f"{nome}\\n{func}\\n{equipe.upper()}\\n{status_txt} · {c.get(\'matricula\') or \'SEM MATRÍCULA\'}"'
if old in s:
    s=s.replace(old,new)
else:
    raise SystemExit("label quebrado não encontrado")
p.write_text(s,encoding="utf-8")
print("patch_equipes_layout: label corrigido")
