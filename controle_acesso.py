from __future__ import annotations

import os
from typing import Any

import streamlit as st
from supabase import Client, create_client

PROJECT_URL = "https://cuixazpxkvniqldmmnth.supabase.co"

MODULOS = {
    "dashboard": "Dashboard",
    "indicadores": "Alimentar Indicadores",
    "historico": "Histórico",
    "equipes": "Gestão de Equipes",
    "carreira": "Plano de Carreira",
    "configuracoes": "Configurações",
}

PERFIS_PADRAO = {
    "ADMINISTRADOR": {
        modulo: {"ver": True, "editar": True} for modulo in MODULOS
    },
    "GESTOR": {
        "dashboard": {"ver": True, "editar": False},
        "indicadores": {"ver": True, "editar": True},
        "historico": {"ver": True, "editar": False},
        "equipes": {"ver": True, "editar": True},
        "carreira": {"ver": True, "editar": True},
        "configuracoes": {"ver": False, "editar": False},
    },
    "OPERACIONAL": {
        "dashboard": {"ver": True, "editar": False},
        "indicadores": {"ver": True, "editar": True},
        "historico": {"ver": True, "editar": False},
        "equipes": {"ver": False, "editar": False},
        "carreira": {"ver": False, "editar": False},
        "configuracoes": {"ver": False, "editar": False},
    },
    "CONSULTA": {
        "dashboard": {"ver": True, "editar": False},
        "indicadores": {"ver": True, "editar": False},
        "historico": {"ver": True, "editar": False},
        "equipes": {"ver": False, "editar": False},
        "carreira": {"ver": False, "editar": False},
        "configuracoes": {"ver": False, "editar": False},
    },
    "PERSONALIZADO": {modulo: {"ver": False, "editar": False} for modulo in MODULOS},
}

SESSION_KEYS = (
    "acesso_access_token",
    "acesso_refresh_token",
    "acesso_user_id",
    "acesso_email",
    "acesso_perfil",
)


def _secret(name: str, default: str = "") -> str:
    try:
        value = st.secrets.get(name, default)
        if value is not None and str(value).strip():
            return str(value).strip().strip('"').strip("'")
    except Exception:
        pass
    value = os.getenv(name, default)
    return str(value or "").strip().strip('"').strip("'")


def criar_cliente_sessao() -> Client:
    url = _secret("SUPABASE_URL", PROJECT_URL)
    key = _secret("SUPABASE_KEY") or _secret("SUPABASE_ANON_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL/SUPABASE_KEY não configurados para autenticação.")
    return create_client(url, key)


def _salvar_tokens(response: Any) -> None:
    session = getattr(response, "session", None)
    user = getattr(response, "user", None)
    if session is not None:
        st.session_state.acesso_access_token = getattr(session, "access_token", "") or ""
        st.session_state.acesso_refresh_token = getattr(session, "refresh_token", "") or ""
    if user is not None:
        st.session_state.acesso_user_id = str(getattr(user, "id", "") or "")
        st.session_state.acesso_email = str(getattr(user, "email", "") or "")


def cliente_autenticado() -> Client | None:
    access_token = st.session_state.get("acesso_access_token")
    refresh_token = st.session_state.get("acesso_refresh_token")
    if not access_token or not refresh_token:
        return None
    try:
        client = criar_cliente_sessao()
        response = client.auth.set_session(access_token, refresh_token)
        _salvar_tokens(response)
        verified = client.auth.get_user()
        user = getattr(verified, "user", None)
        if user is None:
            return None
        st.session_state.acesso_user_id = str(getattr(user, "id", "") or "")
        st.session_state.acesso_email = str(getattr(user, "email", "") or "")
        return client
    except Exception:
        limpar_sessao()
        return None


def autenticar(email: str, senha: str) -> tuple[Client | None, str | None]:
    try:
        client = criar_cliente_sessao()
        response = client.auth.sign_in_with_password({"email": email.strip(), "password": senha})
        _salvar_tokens(response)
        verified = client.auth.get_user()
        user = getattr(verified, "user", None)
        if user is None:
            raise RuntimeError("Usuário não validado pelo Supabase Auth.")
        st.session_state.acesso_user_id = str(getattr(user, "id", "") or "")
        st.session_state.acesso_email = str(getattr(user, "email", "") or "")
        return client, None
    except Exception as exc:
        limpar_sessao()
        return None, str(exc)


def solicitar_acesso(nome: str, email: str, senha: str) -> tuple[bool, str]:
    try:
        client = criar_cliente_sessao()
        response = client.auth.sign_up(
            {
                "email": email.strip(),
                "password": senha,
                "options": {"data": {"nome": nome.strip()}},
            }
        )
        session = getattr(response, "session", None)
        if session is None:
            return True, "Cadastro criado. Confirme o e-mail e depois faça login para solicitar a liberação."
        _salvar_tokens(response)
        perfil = obter_ou_criar_perfil(client, nome_padrao=nome)
        if perfil:
            return True, "Cadastro criado. A solicitação de acesso foi enviada ao administrador."
        return True, "Cadastro criado. Faça login novamente para concluir a solicitação de acesso."
    except Exception as exc:
        return False, str(exc)


def obter_ou_criar_perfil(client: Client, nome_padrao: str = "") -> dict[str, Any] | None:
    user_id = str(st.session_state.get("acesso_user_id") or "")
    email = str(st.session_state.get("acesso_email") or "")
    if not user_id or not email:
        return None

    result = (
        client.table("almox_usuarios_acesso")
        .select("user_id,email,nome,perfil,ativo,permissoes")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    rows = result.data or []
    if rows:
        perfil = rows[0]
        st.session_state.acesso_perfil = perfil
        return perfil

    nome = (nome_padrao or email.split("@", 1)[0]).strip()
    payload = {
        "user_id": user_id,
        "email": email,
        "nome": nome,
        "perfil": "PENDENTE",
        "ativo": False,
        "permissoes": {},
    }
    try:
        created = client.table("almox_usuarios_acesso").insert(payload).execute()
        rows = created.data or []
        perfil = rows[0] if rows else payload
        st.session_state.acesso_perfil = perfil
        return perfil
    except Exception:
        return None


def permissao(perfil: dict[str, Any] | None, modulo: str, acao: str = "ver") -> bool:
    if not perfil or not perfil.get("ativo"):
        return False
    if str(perfil.get("perfil") or "").upper() == "ADMINISTRADOR":
        return True
    permissoes = perfil.get("permissoes") or {}
    item = permissoes.get(modulo) or {}
    return bool(item.get(acao, False))


def modulos_visiveis(perfil: dict[str, Any] | None) -> list[str]:
    return [modulo for modulo in MODULOS if permissao(perfil, modulo, "ver")]


def limpar_sessao() -> None:
    for key in SESSION_KEYS:
        st.session_state.pop(key, None)


def render_login() -> tuple[Client | None, dict[str, Any] | None]:
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

    st.markdown("## Acesso ao Gestão Operacional")
    st.caption("Entre com sua conta corporativa autorizada.")
    tab_login, tab_solicitar = st.tabs(["ENTRAR", "SOLICITAR ACESSO"])

    with tab_login:
        with st.form("form_login_gestao"):
            email = st.text_input("E-mail", key="acesso_email_login")
            senha = st.text_input("Senha", type="password", key="acesso_senha_login")
            entrar = st.form_submit_button("Entrar", use_container_width=True, type="primary")
        if entrar:
            client, erro = autenticar(email, senha)
            if erro:
                st.error("Não foi possível entrar. Verifique e-mail e senha.")
            elif client is not None:
                obter_ou_criar_perfil(client)
                st.rerun()

    with tab_solicitar:
        with st.form("form_solicitar_acesso"):
            nome = st.text_input("Nome", key="acesso_nome_novo")
            email_novo = st.text_input("E-mail corporativo", key="acesso_email_novo")
            senha_nova = st.text_input("Crie uma senha", type="password", key="acesso_senha_nova")
            solicitar = st.form_submit_button("Solicitar acesso", use_container_width=True)
        if solicitar:
            if len(senha_nova) < 8:
                st.error("Use uma senha com pelo menos 8 caracteres.")
            elif not nome.strip() or not email_novo.strip():
                st.error("Preencha nome e e-mail.")
            else:
                ok, mensagem = solicitar_acesso(nome, email_novo, senha_nova)
                (st.success if ok else st.error)(mensagem)

    st.stop()


def _normalizar_permissoes(perfil_nome: str, atual: dict[str, Any] | None = None) -> dict[str, Any]:
    perfil_nome = str(perfil_nome or "PERSONALIZADO").upper()
    if perfil_nome in PERFIS_PADRAO and perfil_nome != "PERSONALIZADO":
        return {k: dict(v) for k, v in PERFIS_PADRAO[perfil_nome].items()}
    atual = atual or {}
    return {
        modulo: {
            "ver": bool((atual.get(modulo) or {}).get("ver", False)),
            "editar": bool((atual.get(modulo) or {}).get("editar", False)),
        }
        for modulo in MODULOS
    }


def render_admin_usuarios(client: Client, perfil_logado: dict[str, Any]) -> None:
    if str(perfil_logado.get("perfil") or "").upper() != "ADMINISTRADOR":
        st.error("Apenas administradores podem gerenciar usuários e acessos.")
        return

    st.markdown("### Usuários e Acessos")
    st.caption("Defina o perfil e, quando necessário, personalize a visualização e edição de cada aba.")

    response = (
        client.table("almox_usuarios_acesso")
        .select("user_id,email,nome,perfil,ativo,permissoes,criado_em,atualizado_em")
        .order("criado_em", desc=False)
        .execute()
    )
    usuarios = response.data or []
    if not usuarios:
        st.info("Nenhum usuário cadastrado.")
        return

    for idx, usuario in enumerate(usuarios):
        titulo = usuario.get("nome") or usuario.get("email") or "Usuário"
        situacao = "ATIVO" if usuario.get("ativo") else "PENDENTE / BLOQUEADO"
        with st.expander(f"{titulo} · {situacao}", expanded=not bool(usuario.get("ativo"))):
            st.caption(usuario.get("email") or "")
            key_base = f"usr_{usuario.get('user_id')}_{idx}"

            perfil_atual = str(usuario.get("perfil") or "PENDENTE").upper()
            opcoes = ["ADMINISTRADOR", "GESTOR", "OPERACIONAL", "CONSULTA", "PERSONALIZADO"]
            if perfil_atual not in opcoes:
                perfil_atual = "CONSULTA"
            perfil_escolhido = st.selectbox(
                "Perfil",
                opcoes,
                index=opcoes.index(perfil_atual),
                key=f"{key_base}_perfil",
            )
            ativo = st.toggle("Acesso ativo", value=bool(usuario.get("ativo")), key=f"{key_base}_ativo")

            base = _normalizar_permissoes(
                perfil_escolhido,
                usuario.get("permissoes") if perfil_escolhido == "PERSONALIZADO" else None,
            )
            permissoes = {}
            st.markdown("**Permissões por aba**")
            for modulo, rotulo in MODULOS.items():
                c1, c2, c3 = st.columns([2.2, 1, 1])
                with c1:
                    st.write(rotulo)
                with c2:
                    ver = st.checkbox(
                        "Visualizar",
                        value=bool((base.get(modulo) or {}).get("ver")),
                        key=f"{key_base}_{modulo}_ver",
                        disabled=perfil_escolhido != "PERSONALIZADO",
                    )
                with c3:
                    editar = st.checkbox(
                        "Editar",
                        value=bool((base.get(modulo) or {}).get("editar")),
                        key=f"{key_base}_{modulo}_editar",
                        disabled=perfil_escolhido != "PERSONALIZADO",
                    )
                if editar:
                    ver = True
                permissoes[modulo] = {"ver": bool(ver), "editar": bool(editar)}

            if perfil_escolhido != "PERSONALIZADO":
                permissoes = _normalizar_permissoes(perfil_escolhido)

            if st.button("Salvar acesso", key=f"{key_base}_salvar", type="primary"):
                client.table("almox_usuarios_acesso").update(
                    {
                        "perfil": perfil_escolhido,
                        "ativo": ativo,
                        "permissoes": permissoes,
                    }
                ).eq("user_id", usuario.get("user_id")).execute()
                st.success("Permissões atualizadas.")
                st.rerun()


def render_usuario_sidebar(perfil: dict[str, Any]) -> None:
    nome = perfil.get("nome") or perfil.get("email") or "Usuário"
    perfil_nome = str(perfil.get("perfil") or "").replace("_", " ")
    st.markdown(
        f"<div style='margin:8px 4px 12px;padding:10px;border:1px solid #2c3933;border-radius:10px;'>"
        f"<div style='font-size:12px;font-weight:800'>{nome}</div>"
        f"<div style='font-size:10px;color:#9aa39f;margin-top:3px'>{perfil_nome}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
    if st.button("Sair", key="acesso_logout_sidebar", use_container_width=True):
        limpar_sessao()
        st.rerun()
