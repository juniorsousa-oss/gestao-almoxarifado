from pathlib import Path
p=Path('streamlit_app.py')
s=p.read_text(encoding='utf-8')
old='''                        label=nome+"\n"+func+"\n"+equipe.upper()+"\n"+status_txt+" · "+str(c.get('matricula') or 'SEM MATRÍCULA')'''
new='                        label=nome+chr(10)+func+chr(10)+equipe.upper()+chr(10)+status_txt+" · "+str(c.get("matricula") or "SEM MATRÍCULA")'
if old not in s:
    raise SystemExit('label multiline não encontrado')
s=s.replace(old,new)
p.write_text(s,encoding='utf-8')
print('fix_generated_label: OK')
