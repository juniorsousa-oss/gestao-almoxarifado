from pathlib import Path

p=Path('controle_acesso.py')
text=p.read_text(encoding='utf-8')

old='''          div[data-testid="stForm"] [data-baseweb="input"],\n          div[data-testid="stForm"] [data-baseweb="base-input"] {{\n            width:100% !important; height:31px !important; min-height:31px !important; box-sizing:border-box !important;\n            display:flex !important; align-items:center !important; border:2px solid #050505 !important;\n            border-radius:8px !important; background:#f0f2f6 !important; box-shadow:none !important; overflow:hidden !important;\n            color:#202020 !important;\n          }}\n          div[data-testid="stForm"] [data-baseweb="input"] > div,\n          div[data-testid="stForm"] [data-baseweb="base-input"] > div {{\n            height:27px !important; min-height:27px !important; background:#f0f2f6 !important; color:#202020 !important;\n          }}'''
new='''          div[data-testid="stForm"] [data-baseweb="input"] {{\n            width:100% !important; height:31px !important; min-height:31px !important; box-sizing:border-box !important;\n            display:flex !important; align-items:center !important; border:2px solid #050505 !important;\n            border-radius:8px !important; background:#f0f2f6 !important; box-shadow:none !important; overflow:hidden !important;\n            color:#202020 !important;\n          }}\n          div[data-testid="stForm"] [data-baseweb="base-input"] {{\n            width:100% !important; height:27px !important; min-height:27px !important;\n            border:0 !important; outline:0 !important; box-shadow:none !important;\n            background:#f0f2f6 !important; color:#202020 !important;\n          }}\n          div[data-testid="stForm"] [data-baseweb="input"] > div {{\n            height:27px !important; min-height:27px !important; background:#f0f2f6 !important; color:#202020 !important;\n          }}'''
if old not in text:
    raise SystemExit('bloco de input não encontrado')
text=text.replace(old,new,1)

old_media='''          @media (max-width:480px) {{\n            .setta-login-wrap, div[data-testid="stForm"] {{ width:286px !important; }}\n          }}'''
new_media='''          @media (max-width:480px) {{\n            .setta-login-wrap {{\n              width:286px !important;\n              transform:translate(-50%,-50%) scale(1.18) !important;\n              transform-origin:center center !important;\n            }}\n            div[data-testid="stForm"] {{\n              width:286px !important;\n              transform:translateX(-50%) scale(1.18) !important;\n              transform-origin:top center !important;\n            }}\n          }}'''
if old_media not in text:
    raise SystemExit('media query não encontrada')
text=text.replace(old_media,new_media,1)
p.write_text(text,encoding='utf-8')
