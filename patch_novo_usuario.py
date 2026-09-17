from pathlib import Path

p = Path('controle_acesso.py')
text = p.read_text(encoding='utf-8')

helper_anchor = '\ndef render_admin_usuarios(client: Client, perfil_logado: dict[str, Any]) -> None:\n'
if helper_anchor not in text:
    raise RuntimeError('Ponto de integração do painel de usuários não encontrado.')

helper = r'''
def convidar_usuario(
    client: Client,
    nome: str,
    email: str,
    perfil: str,
    ativo: bool,
    permissoes: dict[str, Any],
) -> tuple[bool, str]:
    try:
        access_token = str(st.session_state.get("acesso_access_token") or "")
        if not access_token:
            return False, "Sua sessão expirou. Entre novamente antes de criar um usuário."

        response = client.functions.invoke(
            "almox-convidar-usuario",
            invoke_options={
                "headers": {"Authorization": f"Bearer {access_token}"},
                "body": {
                    "nome": nome.strip(),
                    "email": email.strip().lower(),
                    "perfil": perfil,
                    "ativo": bool(ativo),
                    "permissoes": permissoes,
                },
            },
        )

        data = getattr(response, "data", response)
        if isinstance(data, bytes):
            import json
            data = json.loads(data.decode("utf-8"))
        elif isinstance(data, str):
            import json
            data = json.loads(data)

        if isinstance(data, dict):
            if data.get("ok"):
                return True, str(data.get("message") or "Convite enviado com sucesso.")
            if data.get("error"):
                return False, str(data.get("error"))
        return True, "Convite enviado com sucesso."
    except Exception as exc:
        mensagem = str(exc)
        if "already" in mensagem.lower() and "registered" in mensagem.lower():
            mensagem = "Este e-mail já possui uma conta no Supabase Auth. Ajuste as permissões dele na lista de usuários."
        return False, mensagem

'''
text = text.replace(helper_anchor, '\n' + helper + helper_anchor.lstrip('\n'), 1)

panel_anchor = '''    st.markdown("### Usuários e Acessos")
    st.caption("Defina o perfil e, quando necessário, personalize a visualização e edição de cada aba.")

'''
if panel_anchor not in text:
    raise RuntimeError('Cabeçalho do painel administrativo não encontrado.')

panel = r'''    st.markdown("### Usuários e Acessos")
    st.caption("Crie novos acessos e defina o perfil e as permissões de cada usuário neste aplicativo.")

    with st.expander("+ NOVO USUÁRIO", expanded=False):
        st.caption("O usuário receberá um convite por e-mail para ativar a conta no Supabase Auth.")
        with st.form("form_novo_usuario_gestao", clear_on_submit=True):
            c_nome, c_email = st.columns(2)
            with c_nome:
                novo_nome = st.text_input("Nome", key="novo_usuario_nome")
            with c_email:
                novo_email = st.text_input("E-mail", key="novo_usuario_email")

            novo_perfil = st.selectbox(
                "Perfil",
                ["ADMINISTRADOR", "GESTOR", "OPERACIONAL", "CONSULTA", "PERSONALIZADO"],
                index=2,
                key="novo_usuario_perfil",
            )
            novo_ativo = st.toggle(
                "Liberar acesso assim que o convite for aceito",
                value=True,
                key="novo_usuario_ativo",
            )

            if novo_perfil == "PERSONALIZADO":
                st.markdown("**Permissões por aba**")
                novas_permissoes = {}
                for modulo, rotulo in MODULOS.items():
                    c1, c2, c3 = st.columns([2.2, 1, 1])
                    with c1:
                        st.write(rotulo)
                    with c2:
                        ver = st.checkbox("Visualizar", key=f"novo_{modulo}_ver")
                    with c3:
                        editar = st.checkbox("Editar", key=f"novo_{modulo}_editar")
                    if editar:
                        ver = True
                    novas_permissoes[modulo] = {"ver": bool(ver), "editar": bool(editar)}
            else:
                novas_permissoes = _normalizar_permissoes(novo_perfil)
                st.caption("As permissões padrão desse perfil serão aplicadas automaticamente.")

            enviar_convite = st.form_submit_button(
                "ENVIAR CONVITE",
                use_container_width=True,
                type="primary",
            )

        if enviar_convite:
            if not novo_nome.strip():
                st.error("Informe o nome do usuário.")
            elif "@" not in novo_email or "." not in novo_email.split("@")[-1]:
                st.error("Informe um e-mail válido.")
            else:
                ok, mensagem = convidar_usuario(
                    client,
                    novo_nome,
                    novo_email,
                    novo_perfil,
                    novo_ativo,
                    novas_permissoes,
                )
                if ok:
                    st.success(mensagem)
                    st.rerun()
                else:
                    st.error(f"Não foi possível criar o usuário: {mensagem}")

    st.markdown("#### Usuários cadastrados")

'''
text = text.replace(panel_anchor, panel, 1)
p.write_text(text, encoding='utf-8')
