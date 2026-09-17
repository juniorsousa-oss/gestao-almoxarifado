from pathlib import Path
import py_compile

# 1) Usa no runtime a mesma configuração de página do MRP (sem sidebar forçada)
p = Path('streamlit_app.py')
text = p.read_text(encoding='utf-8')
text = text.replace('# DEPLOY_VERSION: access-control-v1', '# DEPLOY_VERSION: login-mrp-1to1-v2', 1)
old = '''_source = _source.replace(
    _page_config_anchor,
    _page_config_anchor + "\\n_acesso_client,_acesso_perfil=render_login()\\n",
    1,
)'''
new = '''_page_config_login = 'st.set_page_config(page_title="GESTÃO | SETTA", page_icon="assets/mrp_setta_icon.png", layout="wide")\\n'
_source = _source.replace(
    _page_config_anchor,
    _page_config_login + "\\n_acesso_client,_acesso_perfil=render_login()\\n",
    1,
)'''
if old not in text:
    raise RuntimeError('Bloco de page_config não encontrado')
text = text.replace(old, new, 1)
p.write_text(text, encoding='utf-8')

# 2) Neutraliza o tema dark dentro dos inputs do login para reproduzir o MRP
p = Path('controle_acesso.py')
text = p.read_text(encoding='utf-8')
text = text.replace(
    'border-radius:6px !important; background:transparent !important; color:#202020 !important; font-size:8px !important;',
    'border-radius:6px !important; background:#f0f2f6 !important; color:#202020 !important; -webkit-text-fill-color:#202020 !important; font-size:8px !important;',
    1,
)
anchor = '''          div[data-testid="stForm"] [data-baseweb="input"] {{
            width:100% !important; height:31px !important; min-height:31px !important; box-sizing:border-box !important;
            display:flex !important; align-items:center !important; border:2px solid #050505 !important;
            border-radius:8px !important; background:#f0f2f6 !important; box-shadow:none !important; overflow:hidden !important;
          }}
          div[data-testid="stForm"] [data-baseweb="input"] > div {{ height:27px !important; min-height:27px !important; }}'''
replacement = '''          div[data-testid="stForm"] [data-baseweb="input"],
          div[data-testid="stForm"] [data-baseweb="base-input"] {{
            width:100% !important; height:31px !important; min-height:31px !important; box-sizing:border-box !important;
            display:flex !important; align-items:center !important; border:2px solid #050505 !important;
            border-radius:8px !important; background:#f0f2f6 !important; box-shadow:none !important; overflow:hidden !important;
            color:#202020 !important;
          }}
          div[data-testid="stForm"] [data-baseweb="input"] > div,
          div[data-testid="stForm"] [data-baseweb="base-input"] > div {{
            height:27px !important; min-height:27px !important; background:#f0f2f6 !important; color:#202020 !important;
          }}'''
if anchor not in text:
    raise RuntimeError('Bloco BaseWeb do login não encontrado')
text = text.replace(anchor, replacement, 1)
# garante que autofill/tema do navegador não escureça os campos
focus_anchor = '          div[data-testid="stForm"] input:focus {{ outline:none !important; border:0 !important; box-shadow:none !important; }}'
focus_repl = '''          div[data-testid="stForm"] input:focus {{ outline:none !important; border:0 !important; box-shadow:none !important; background:#f0f2f6 !important; color:#202020 !important; -webkit-text-fill-color:#202020 !important; }}
          div[data-testid="stForm"] input:-webkit-autofill,
          div[data-testid="stForm"] input:-webkit-autofill:hover,
          div[data-testid="stForm"] input:-webkit-autofill:focus {{
            -webkit-box-shadow:0 0 0 1000px #f0f2f6 inset !important;
            -webkit-text-fill-color:#202020 !important;
          }}'''
if focus_anchor not in text:
    raise RuntimeError('Bloco de foco do login não encontrado')
text = text.replace(focus_anchor, focus_repl, 1)
p.write_text(text, encoding='utf-8')

py_compile.compile('streamlit_app.py', doraise=True)
py_compile.compile('controle_acesso.py', doraise=True)
print('OK - login 1:1 aplicado e arquivos compilados')
