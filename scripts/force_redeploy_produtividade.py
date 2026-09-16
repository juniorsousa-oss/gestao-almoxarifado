from pathlib import Path

p = Path('streamlit_app.py')
t = p.read_text(encoding='utf-8')
marker = '# DEPLOY_VERSION: produtividade-v1\n'
if marker not in t:
    insert_after = 'from pathlib import Path\n'
    if insert_after in t:
        t = t.replace(insert_after, insert_after + marker, 1)
    else:
        t = marker + t
p.write_text(t, encoding='utf-8')
print('Marcador de deploy da Produtividade aplicado em streamlit_app.py')
