from pathlib import Path

p = Path('streamlit_app.py')
s = p.read_text(encoding='utf-8')
old_start = 'elif pagina == "equipes":\n'
old_end = '\nelif pagina == "carreira":\n'
i = s.find(old_start)
j = s.find(old_end, i)
if i < 0 or j < 0:
    print('Bloco de equipes já atualizado ou não encontrado; nada a fazer.')
    raise SystemExit(0)

new = '''elif pagina == "equipes":
    client = get_client()

    def carregar_equipes():
        return client.table("almox_equipes").select("*").order("nome").execute().data or []

    def carregar_colaboradores():
        return client.table("almox_colaboradores").select("*").order("nome").execute().data or []

    def registrar_historico(tipo, descricao, dados):
        try:
            client.table("almox_historico").insert({"tipo": tipo, "descricao": descricao, "dados": dados}).execute()
        except Exception:
            pass

    equipes_raw = carregar_equipes()
    colaboradores_raw = carregar_colaboradores()
    ativos_equipes = [x for x in equipes_raw if x.get("ativo", True)]
    ativos_colaboradores = [x for x in colaboradores_raw if x.get("ativo", True)]

    m1, m2, m3 = st.columns(3)
    m1.metric("Equipes ativas", len(ativos_equipes))
    m2.metric("Colaboradores ativos", len(ativos_colaboradores))
    m3.metric("Colaboradores sem equipe", sum(1 for x in ativos_colaboradores if not x.get("equipe_id")))

    tab_equipes, tab_colaboradores = st.tabs(["EQUIPES", "COLABORADORES"])

    with tab_equipes:
        st.markdown("### Cadastro de equipe")
        with st.form("form_nova_equipe", clear_on_submit=True):
            ec1, ec2 = st.columns(2)
            with ec1:
                nome_equipe = st.text_input("Nome da equipe *", placeholder="Ex.: Almoxarifado")
                objetivo_equipe = st.text_area("Objetivo", placeholder="Descreva a finalidade da equipe.", height=100)
            with ec2:
                responsaveis = {"Nenhum": None}
                for c in ativos_colaboradores:
                    responsaveis[f"{c.get('nome', '')} — {c.get('funcao') or 'Sem função'}"] = c.get("id")
                resp_label = st.selectbox("Responsável", list(responsaveis.keys()))
                tarefas_texto = st.text_area("Tarefas principais", placeholder="Uma tarefa por linha", height=100)
            criar_equipe = st.form_submit_button("CRIAR EQUIPE", type="primary", use_container_width=True)

        if criar_equipe:
            nome_limpo = nome_equipe.strip()
            if not nome_limpo:
                st.error("Informe o nome da equipe.")
            elif any((x.get("nome") or "").strip().casefold() == nome_limpo.casefold() and x.get("ativo", True) for x in equipes_raw):
                st.error("Já existe uma equipe ativa com esse nome.")
            else:
                try:
                    novo = client.table("almox_equipes").insert({"nome": nome_limpo, "objetivo": objetivo_equipe.strip() or None, "tarefas": [x.strip() for x in tarefas_texto.splitlines() if x.strip()], "responsavel_id": responsaveis[resp_label], "ativo": True}).execute().data
                    if novo:
                        registrar_historico("equipe_criada", f"Equipe criada: {nome_limpo}", {"equipe_id": novo[0].get("id"), "nome": nome_limpo})
                        st.success(f"Equipe '{nome_limpo}' criada com sucesso.")
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro ao criar equipe: {e}")

        st.markdown("### Equipes cadastradas")
        filtro_eq = st.text_input("Buscar equipe", placeholder="Digite parte do nome...", key="busca_equipe")
        equipes_exibicao = [x for x in equipes_raw if filtro_eq.strip().casefold() in (x.get("nome") or "").casefold()]
        nomes_colab = {str(x.get("id")): x.get("nome", "") for x in colaboradores_raw}
        if not equipes_exibicao:
            st.info("Nenhuma equipe cadastrada para o filtro informado.")
        for equipe in equipes_exibicao:
            eid = str(equipe.get("id"))
            with st.expander(f"{'ATIVA' if equipe.get('ativo', True) else 'INATIVA'} • {equipe.get('nome', '')}"):
                st.write(f"**Objetivo:** {equipe.get('objetivo') or 'Não informado'}")
                st.write(f"**Responsável:** {nomes_colab.get(str(equipe.get('responsavel_id')), 'Não definido')}")
                st.write(f"**Tarefas:** {', '.join(equipe.get('tarefas') or []) or 'Não informadas'}")
                ca, cb = st.columns(2)
                with ca:
                    if st.button("EDITAR EQUIPE", key=f"editar_eq_{eid}", use_container_width=True):
                        st.session_state["editar_equipe_id"] = eid
                        st.rerun()
                with cb:
                    if st.button("INATIVAR EQUIPE" if equipe.get("ativo", True) else "REATIVAR EQUIPE", key=f"status_eq_{eid}", use_container_width=True):
                        try:
                            client.table("almox_equipes").update({"ativo": not equipe.get("ativo", True)}).eq("id", eid).execute()
                            registrar_historico("equipe_status", f"Status alterado: {equipe.get('nome', '')}", {"equipe_id": eid, "ativo": not equipe.get("ativo", True)})
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao alterar status: {e}")
                if st.session_state.get("editar_equipe_id") == eid:
                    with st.form(f"form_editar_eq_{eid}"):
                        nome_edit = st.text_input("Nome", value=equipe.get("nome") or "")
                        obj_edit = st.text_area("Objetivo", value=equipe.get("objetivo") or "", height=90)
                        tarefas_edit = st.text_area("Tarefas — uma por linha", value="\\n".join(equipe.get("tarefas") or []), height=90)
                        resp_opts = {"Nenhum": None}
                        for c in ativos_colaboradores:
                            resp_opts[f"{c.get('nome', '')} — {c.get('funcao') or 'Sem função'}"] = c.get("id")
                        ids_resp = list(resp_opts.values())
                        atual_resp = equipe.get("responsavel_id")
                        idx_resp = ids_resp.index(atual_resp) if atual_resp in ids_resp else 0
                        resp_edit = st.selectbox("Responsável", list(resp_opts.keys()), index=idx_resp)
                        salvar_eq = st.form_submit_button("SALVAR ALTERAÇÕES", type="primary")
                    if salvar_eq:
                        try:
                            client.table("almox_equipes").update({"nome": nome_edit.strip(), "objetivo": obj_edit.strip() or None, "tarefas": [x.strip() for x in tarefas_edit.splitlines() if x.strip()], "responsavel_id": resp_opts[resp_edit]}).eq("id", eid).execute()
                            registrar_historico("equipe_editada", f"Equipe editada: {nome_edit.strip()}", {"equipe_id": eid, "nome": nome_edit.strip()})
                            st.session_state.pop("editar_equipe_id", None)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao editar equipe: {e}")

    with tab_colaboradores:
        st.markdown("### Cadastro de colaborador")
        equipes_opts = {x.get("nome", ""): x.get("id") for x in ativos_equipes}
        with st.form("form_novo_colaborador", clear_on_submit=True):
            cc1, cc2 = st.columns(2)
            with cc1:
                nome_colab = st.text_input("Nome completo *", placeholder="Nome do colaborador")
                matricula = st.text_input("Matrícula", placeholder="Matrícula / registro interno")
                funcao = st.text_input("Função / cargo", placeholder="Ex.: Almoxarife")
            with cc2:
                data_adm = st.date_input("Data de admissão", value=None, key="data_adm_novo")
                equipe_label = st.selectbox("Equipe", ["Sem equipe"] + list(equipes_opts.keys()))
                foto_url = st.text_input("URL da foto", placeholder="Opcional")
            criar_colab = st.form_submit_button("CADASTRAR COLABORADOR", type="primary", use_container_width=True)
        if criar_colab:
            nome_limpo = nome_colab.strip()
            mat = matricula.strip() or None
            if not nome_limpo:
                st.error("Informe o nome do colaborador.")
            elif mat and any((x.get("matricula") or "").strip().casefold() == mat.casefold() for x in colaboradores_raw):
                st.error("Essa matrícula já está cadastrada.")
            else:
                try:
                    novo = client.table("almox_colaboradores").insert({"nome": nome_limpo, "matricula": mat, "funcao": funcao.strip() or None, "data_admissao": data_adm.isoformat() if data_adm else None, "equipe_id": equipes_opts.get(equipe_label), "equipe_atual": equipe_label if equipe_label != "Sem equipe" else None, "foto_url": foto_url.strip() or None, "ativo": True}).execute().data
                    if novo:
                        registrar_historico("colaborador_criado", f"Colaborador criado: {nome_limpo}", {"colaborador_id": novo[0].get("id"), "nome": nome_limpo})
                        st.success(f"Colaborador '{nome_limpo}' cadastrado com sucesso.")
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro ao cadastrar colaborador: {e}")

        st.markdown("### Colaboradores cadastrados")
        cf1, cf2 = st.columns([2, 1])
        with cf1:
            busca = st.text_input("Buscar colaborador", placeholder="Nome, matrícula ou função...", key="busca_colab")
        with cf2:
            status = st.selectbox("Status", ["Todos", "Ativos", "Inativos"], key="filtro_status_colab")
        filtrados = []
        for c in colaboradores_raw:
            texto = " ".join([str(c.get("nome") or ""), str(c.get("matricula") or ""), str(c.get("funcao") or "")]).casefold()
            ok = status == "Todos" or (status == "Ativos" and c.get("ativo", True)) or (status == "Inativos" and not c.get("ativo", True))
            if busca.strip().casefold() in texto and ok:
                filtrados.append(c)
        nomes_eq = {str(x.get("id")): x.get("nome", "") for x in equipes_raw}
        linhas = [{"Nome": c.get("nome"), "Matrícula": c.get("matricula") or "", "Função": c.get("funcao") or "", "Equipe": nomes_eq.get(str(c.get("equipe_id")), c.get("equipe_atual") or "Sem equipe"), "Admissão": c.get("data_admissao") or "", "Status": "Ativo" if c.get("ativo", True) else "Inativo"} for c in filtrados]
        if linhas:
            st.dataframe(pd.DataFrame(linhas), use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum colaborador encontrado.")

        if filtrados:
            opcoes = {f"{c.get('nome', '')} — {c.get('matricula') or 'sem matrícula'}": c for c in filtrados}
            escolhido = opcoes[st.selectbox("Selecione um colaborador para ações", list(opcoes.keys()), key="colab_acao")]
            cid = str(escolhido.get("id"))
            ca, cb = st.columns(2)
            with ca:
                if st.button("EDITAR COLABORADOR", key=f"editar_colab_{cid}", use_container_width=True):
                    st.session_state["editar_colaborador_id"] = cid
                    st.rerun()
            with cb:
                if st.button("INATIVAR COLABORADOR" if escolhido.get("ativo", True) else "REATIVAR COLABORADOR", key=f"status_colab_{cid}", use_container_width=True):
                    try:
                        client.table("almox_colaboradores").update({"ativo": not escolhido.get("ativo", True)}).eq("id", cid).execute()
                        registrar_historico("colaborador_status", f"Status alterado: {escolhido.get('nome', '')}", {"colaborador_id": cid, "ativo": not escolhido.get("ativo", True)})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao alterar status: {e}")
            if st.session_state.get("editar_colaborador_id") == cid:
                with st.form(f"form_editar_colab_{cid}"):
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        nome_e = st.text_input("Nome completo", value=escolhido.get("nome") or "")
                        mat_e = st.text_input("Matrícula", value=escolhido.get("matricula") or "")
                        func_e = st.text_input("Função / cargo", value=escolhido.get("funcao") or "")
                    with ec2:
                        try:
                            data_val = pd.to_datetime(escolhido.get("data_admissao")).date() if escolhido.get("data_admissao") else None
                        except Exception:
                            data_val = None
                        data_e = st.date_input("Data de admissão", value=data_val, key=f"data_edit_{cid}")
                        eqids = [None] + list(equipes_opts.values())
                        atual = escolhido.get("equipe_id")
                        idx = eqids.index(atual) if atual in eqids else 0
                        eq_e_label = st.selectbox("Equipe", ["Sem equipe"] + list(equipes_opts.keys()), index=idx, key=f"eq_edit_{cid}")
                        foto_e = st.text_input("URL da foto", value=escolhido.get("foto_url") or "", key=f"foto_edit_{cid}")
                    salvar_c = st.form_submit_button("SALVAR COLABORADOR", type="primary")
                if salvar_c:
                    mat_e = mat_e.strip() or None
                    if not nome_e.strip():
                        st.error("O nome é obrigatório.")
                    elif mat_e and any(str(x.get("id")) != cid and (x.get("matricula") or "").strip().casefold() == mat_e.casefold() for x in colaboradores_raw):
                        st.error("Essa matrícula já está cadastrada para outro colaborador.")
                    else:
                        try:
                            eqid = equipes_opts.get(eq_e_label)
                            client.table("almox_colaboradores").update({"nome": nome_e.strip(), "matricula": mat_e, "funcao": func_e.strip() or None, "data_admissao": data_e.isoformat() if data_e else None, "equipe_id": eqid, "equipe_atual": eq_e_label if eqid else None, "foto_url": foto_e.strip() or None}).eq("id", cid).execute()
                            registrar_historico("colaborador_editado", f"Colaborador editado: {nome_e.strip()}", {"colaborador_id": cid, "nome": nome_e.strip()})
                            st.session_state.pop("editar_colaborador_id", None)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao editar colaborador: {e}")
'''

s = s[:i] + new + s[j:]
p.write_text(s, encoding='utf-8')
print('Módulo Gestão de Equipes aplicado.')
