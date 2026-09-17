from pathlib import Path

p = Path("controle_acesso.py")
text = p.read_text(encoding="utf-8")
start = text.index("def render_login() -> tuple[Client | None, dict[str, Any] | None]:")
end = text.index("\ndef _normalizar_permissoes", start)

new_func = r'''def render_login() -> tuple[Client | None, dict[str, Any] | None]:
    client = cliente_autenticado()
    if client is not None:
        perfil = obter_ou_criar_perfil(client)
        if perfil and perfil.get("ativo"):
            return client, perfil
        st.warning("Seu acesso está aguardando liberação do administrador.")
        if st.button("Sair", key="acesso_logout_pendente"):
            limpar_sessao()
            st.rerun()
        st.stop()

    # Reaproveita a mesma imagem de login configurada no MRP para manter
    # identidade visual consistente entre os aplicativos.
    image = ""
    try:
        publico = criar_cliente_sessao()
        resultado = (
            publico.table("mrp_app_config")
            .select("login_image_data")
            .eq("id", 1)
            .limit(1)
            .execute()
        )
        if resultado.data:
            image = str(resultado.data[0].get("login_image_data") or "")
    except Exception:
        image = ""

    image_html = (
        f'<div class="setta-login-image"><img src="{image}" /></div>'
        if image
        else '<div class="setta-login-image setta-login-image-empty"><div>Setta</div></div>'
    )

    st.markdown(
        f"""
        <style>
          .stApp {{ background:#ffffff !important; color:#202020 !important; }}
          [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stSidebar"] {{ display:none !important; }}
          .block-container {{ max-width:100% !important; min-height:100vh !important; height:100vh !important; padding:0 !important; margin:0 !important; position:relative !important; overflow:hidden !important; }}
          .setta-login-wrap {{
            position:fixed !important; left:50% !important; top:50% !important; transform:translate(-50%,-50%) !important;
            width:286px !important; height:390px !important; margin:0 !important; padding:0 !important;
            box-sizing:border-box !important; background:#fff !important; border:1px solid rgba(0,0,0,.13) !important;
            border-radius:28px !important; box-shadow:0 16px 42px rgba(0,0,0,.16) !important;
            overflow:visible !important; z-index:10 !important;
          }}
          .setta-login-image {{
            width:100% !important; height:135px !important; transform:translateY(-30px) !important; overflow:hidden !important; background:transparent !important;
            display:flex !important; align-items:flex-end !important; justify-content:center !important;
            padding:20px 18px 8px !important; box-sizing:border-box !important;
          }}
          .setta-login-image img {{
            width:auto !important; height:auto !important; max-width:165px !important; max-height:76px !important;
            object-fit:contain !important; object-position:center !important; display:block !important;
          }}
          .setta-login-image-empty {{ display:flex !important; align-items:flex-end !important; justify-content:center !important; }}
          .setta-login-image-empty div {{ font-size:2.55rem !important; font-weight:850 !important; font-style:italic !important; line-height:1 !important; color:#111 !important; }}
          .setta-login-heading {{ text-align:center !important; padding:0 20px !important; height:58px !important; transform:translateY(-30px) !important; box-sizing:border-box !important; }}
          .setta-login-title {{ color:#111 !important; font-size:14px !important; line-height:17px !important; font-weight:800 !important; margin:0 !important; }}
          div[data-testid="InputInstructions"], div[data-testid="stTextInput"] div[data-testid="InputInstructions"] {{ display:none !important; }}
          div[data-testid="stForm"] {{
            position:fixed !important; left:50% !important; top:calc(40% + 15px) !important; transform:translateX(-50%) !important;
            width:286px !important; height:170px !important; margin:0 !important; padding:0 20px 14px !important;
            box-sizing:border-box !important; background:transparent !important; border:0 !important;
            border-radius:0 !important; box-shadow:none !important; z-index:20 !important;
          }}
          div[data-testid="stForm"] label {{ color:#202020 !important; font-size:9px !important; line-height:12px !important; font-weight:600 !important; margin-bottom:2px !important; }}
          div[data-testid="stForm"] [data-testid="stTextInput"] {{ width:100% !important; margin-bottom:9px !important; }}
          div[data-testid="stForm"] input {{
            width:100% !important; height:27px !important; min-height:27px !important; box-sizing:border-box !important;
            padding:0 10px !important; border:0 !important; outline:none !important; box-shadow:none !important;
            border-radius:6px !important; background:transparent !important; color:#202020 !important; font-size:8px !important;
          }}
          div[data-testid="stForm"] [data-baseweb="input"] {{
            width:100% !important; height:31px !important; min-height:31px !important; box-sizing:border-box !important;
            display:flex !important; align-items:center !important; border:2px solid #050505 !important;
            border-radius:8px !important; background:#f0f2f6 !important; box-shadow:none !important; overflow:hidden !important;
          }}
          div[data-testid="stForm"] [data-baseweb="input"] > div {{ height:27px !important; min-height:27px !important; }}
          div[data-testid="stForm"] [data-testid="stTextInput"] [data-baseweb="input"] button {{
            width:34px !important; height:27px !important; min-height:27px !important; margin:0 !important; padding:0 !important;
            flex:0 0 34px !important; position:static !important; top:auto !important; border:0 !important;
            border-radius:0 !important; background:transparent !important; color:#050505 !important;
            box-shadow:none !important; display:flex !important; align-items:center !important; justify-content:center !important;
          }}
          div[data-testid="stForm"] [data-testid="stTextInput"] [data-baseweb="input"] button:hover {{ background:transparent !important; border:0 !important; color:#050505 !important; }}
          div[data-testid="stForm"] [data-testid="stTextInput"] [data-baseweb="input"] button svg {{ width:16px !important; height:16px !important; margin:0 !important; }}
          div[data-testid="stForm"] input::placeholder {{ color:#a6adb8 !important; opacity:1 !important; }}
          div[data-testid="stForm"] input:focus {{ outline:none !important; border:0 !important; box-shadow:none !important; }}
          div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button {{
            position:static !important; width:100% !important; height:29px !important; min-height:29px !important;
            margin:8px 0 0 !important; padding:0 !important; box-sizing:border-box !important; border-radius:7px !important;
            background:#050505 !important; border:1px solid #050505 !important; color:#fff !important;
            font-size:8px !important; font-weight:700 !important; display:flex !important; align-items:center !important; justify-content:center !important;
          }}
          div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button:hover {{ background:#171717 !important; border-color:#171717 !important; }}
          div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button p {{ color:#fff !important; }}
          div[data-testid="stAlert"] {{ position:fixed !important; left:50% !important; top:calc(50% + 205px) !important; transform:translateX(-50%) !important; width:286px !important; box-sizing:border-box !important; z-index:30 !important; }}
          @media (max-width:480px) {{
            .setta-login-wrap, div[data-testid="stForm"] {{ width:286px !important; }}
          }}
        </style>
        <div class="setta-login-wrap">
          {image_html}
          <div class="setta-login-heading">
            <div class="setta-login-title">GESTÃO OPERACIONAL | SETTA</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("form_login_gestao"):
        email = st.text_input("Usuário", placeholder="Digite seu usuário", key="acesso_email_login")
        senha = st.text_input("Senha", type="password", placeholder="Digite sua senha", key="acesso_senha_login")
        entrar = st.form_submit_button("ENTRAR", use_container_width=True)

    if entrar:
        client, erro = autenticar(email, senha)
        if erro:
            st.error("Não foi possível entrar. Verifique usuário e senha.")
        elif client is not None:
            obter_ou_criar_perfil(client)
            st.rerun()

    st.stop()

'''

text = text[:start] + new_func + text[end + 1:]
p.write_text(text, encoding="utf-8")
