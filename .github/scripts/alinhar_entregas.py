from pathlib import Path

p = Path("indicadores_entregas_v2.py")
s = p.read_text(encoding="utf-8")

# Data CM por projeto; Projeto_Código permanece para Ação/Descrição.
ini = s.index("    # A chave da demanda deve ser única; em caso de problema, interrompe para não duplicar a base.")
fim = s.index("    # TIPOS — primeira aba MRP_Geral")
novo = '''    # A chave Projeto_Código é usada para localizar Ação/Descrição sem duplicar o Relatório Geral.
    duplicadas = dem.loc[dem["Projeto_Código"].duplicated(keep=False) & dem["Projeto_Código"].ne("_")]
    if not duplicadas.empty:
        exemplos = ", ".join(duplicadas["Projeto_Código"].drop_duplicates().head(5).tolist())
        raise ValueError(f"Há chaves Projeto_Código duplicadas no Demanda_Projeto. Exemplos: {exemplos}")

    # DATA CM é informação do PROJETO, conforme a regra validada na planilha de conferência.
    cm_validas = dem.loc[dem["Projeto_norm"].ne("") & dem["Data CM tratada"].notna(), ["Projeto_norm", "Data CM tratada"]].copy()
    conflitos_cm = cm_validas.groupby("Projeto_norm")["Data CM tratada"].nunique()
    conflitos_cm = conflitos_cm[conflitos_cm > 1]
    if not conflitos_cm.empty:
        exemplos = ", ".join(conflitos_cm.index.astype(str).tolist()[:5])
        raise ValueError(f"Há projetos com mais de uma Data CM válida no Demanda_Projeto. Exemplos: {exemplos}")
    cm_map = (
        cm_validas.drop_duplicates("Projeto_norm", keep="first")
        .set_index("Projeto_norm")["Data CM tratada"].to_dict()
    )

    dem_lookup = dem[["Projeto_Código", d_acao, d_desc]].copy()
    dem_lookup.columns = ["Projeto_Código", "Ação", "Descrição MRP"]

'''
s = s[:ini] + novo + s[fim:]

# Fusão: Data CM por projeto, Ação/Descrição por Projeto_Código.
ini = s.index("    # FUSÃO — mantém todas as linhas do Relatório Geral e adiciona a informação do MRP pela chave.")
fim = s.index("    inicio_ts = pd.Timestamp(periodo_inicio)")
novo = '''    # FUSÃO — mantém todas as linhas do Relatório Geral.
    # Data CM vem do PROJETO; Ação e Descrição vêm de Projeto_Código para auditoria dos materiais.
    fundida = rel_base.merge(dem_lookup, on="Projeto_Código", how="left", validate="many_to_one")
    fundida["Data CM"] = fundida["Projeto"].map(cm_map)
    fundida["Tipo"] = fundida["Código normalizado"].map(tipo_map).fillna("")
    fundida["Chave encontrada no MRP"] = fundida["Ação"].notna() | fundida["Descrição MRP"].notna()

'''
s = s[:ini] + novo + s[fim:]

# Compara somente a data, ignorando a hora.
antigo = '''    c1 = base["Data de Separação"].notna() & (base["Data de Separação"] <= base["Data CM"])
    base.loc[c1, "Critério entrega"] = "DATA DE SEPARAÇÃO <= DATA CM"
    base.loc[c1, "Entregue em dia"] = True

    pend = ~base["Entregue em dia"]
    c2 = pend & base["Última Solicitação"].notna() & (base["Última Solicitação"] > base["Data CM"])
    base.loc[c2, "Critério entrega"] = "SOLICITAÇÃO POSTERIOR À DATA CM"
    base.loc[c2, "Entregue em dia"] = True
'''
novo = '''    separacao_dia = base["Data de Separação"].dt.normalize()
    cm_dia = base["Data CM"].dt.normalize()
    solicitacao_dia = base["Última Solicitação"].dt.normalize()

    c1 = base["Data de Separação"].notna() & (separacao_dia <= cm_dia)
    base.loc[c1, "Critério entrega"] = "DATA DE SEPARAÇÃO <= DATA CM (HORA IGNORADA)"
    base.loc[c1, "Entregue em dia"] = True

    pend = ~base["Entregue em dia"]
    c2 = pend & base["Última Solicitação"].notna() & (solicitacao_dia > cm_dia)
    base.loc[c2, "Critério entrega"] = "SOLICITAÇÃO POSTERIOR À DATA CM"
    base.loc[c2, "Entregue em dia"] = True
'''
if antigo not in s:
    raise SystemExit("Bloco de comparação de datas não encontrado")
s = s.replace(antigo, novo, 1)

# Atendidos completamente: replica a aba OPS.
ini = s.index("    # ATENDIDOS COMPLETAMENTE — usa a quantidade efetivamente dependente de fontes futuras indicada em Ação.")
fim = s.index("    projetos_atendidos_pct =")
novo = '''    # ATENDIDOS COMPLETAMENTE — mesma lógica da aba OPS da planilha de conferência.
    # SOLICITADO = COUNTIF(Relatório Geral, Projeto)
    # PENDÊNCIAS = COUNTIF(Demanda_Projeto, Projeto)
    # ATENDIDO = SOLICITADO - PENDÊNCIAS
    projetos_base = sorted(set(base["Projeto"].replace("", pd.NA).dropna().astype(str)))
    solic_por_proj = rel_base.groupby("Projeto").size().to_dict()
    pend_por_proj = dem.groupby("Projeto_norm").size().to_dict()

    resumo_registros = []
    for projeto in projetos_base:
        solicitado = int(solic_por_proj.get(projeto, 0))
        pendencias = int(pend_por_proj.get(projeto, 0))
        atendido = max(solicitado - pendencias, 0)
        pct = (atendido / solicitado * 100.0) if solicitado else 0.0
        resumo_registros.append({
            "Projeto": projeto,
            "Solicitações": solicitado,
            "Pendências no MRP": pendencias,
            "Atendidas": atendido,
            "Atendimento (%)": pct,
            "Atendido completamente": "SIM" if solicitado > 0 and pendencias == 0 else "NÃO",
        })
    resumo_projetos = pd.DataFrame(resumo_registros)
    atendidos_completamente = int(
        resumo_projetos["Atendido completamente"].eq("SIM").sum()
    ) if not resumo_projetos.empty else 0

    # Detalhamento das pendências do Demanda_Projeto para auditoria.
    dem_programados = dem[dem["Projeto_norm"].isin(projetos_base)].copy()
    if dem_programados.empty:
        demanda_auditoria = pd.DataFrame(columns=["Projeto", "Código", "Projeto_Código", "Descrição", "Data CM", "Ação", "Pendência"])
    else:
        demanda_auditoria = pd.DataFrame({
            "Projeto": dem_programados["Projeto_norm"],
            "Código": dem_programados["Código normalizado"],
            "Projeto_Código": dem_programados["Projeto_Código"],
            "Descrição": dem_programados[d_desc],
            "Data CM": dem_programados["Data CM tratada"],
            "Ação": dem_programados[d_acao],
            "Pendência": 1,
        })

'''
s = s[:ini] + novo + s[fim:]

antigo = '        "quantidade_pendente_total": float(demanda_auditoria["Quantidade pendente"].sum()) if not demanda_auditoria.empty else 0.0,\n'
novo = '        "quantidade_pendente_total": int(resumo_projetos["Pendências no MRP"].sum()) if not resumo_projetos.empty else 0,\n'
if antigo not in s:
    raise SystemExit("Campo quantidade_pendente_total não encontrado")
s = s.replace(antigo, novo, 1)

for antigo, novo in {
    '["Chave", "Projeto_Código = Projeto + \'_\' + Código normalizado."],': '["Chave", "Projeto_Código = Projeto + \'_\' + Código normalizado; usada para Ação/Descrição."],',
    '["Fusão", "Relatório Geral recebe Data CM, Ação e Descrição do Demanda_Projeto pela chave Projeto_Código."],': '["Fusão", "Data CM é buscada por Projeto. Ação e Descrição são buscadas por Projeto_Código."],',
    '["Entrega direta", "Data de Separação <= Data CM."],': '["Entrega direta", "Compara somente a data, ignorando a hora: Data de Separação <= Data CM."],',
    '["Quantidade pendente", "Soma das quantidades da Ação vinculadas a Pré Nota + P.C. + Fabricação + S.C.; Estoque não é pendência."],': '["Quantidade pendente", "Quantidade de linhas do projeto ainda existentes no Demanda_Projeto, igual ao COUNTIF da aba OPS."],',
    '["Atendido completamente", "Projeto cuja Quantidade pendente total no Demanda_Projeto do período é zero."],': '["Atendido completamente", "Solicitado = linhas do projeto no Relatório Geral; Atendido = Solicitado - linhas do projeto no Demanda_Projeto; completo quando não resta nenhuma linha pendente."],',
}.items():
    if antigo not in s:
        raise SystemExit(f"Metodologia não encontrada: {antigo}")
    s = s.replace(antigo, novo, 1)

p.write_text(s, encoding="utf-8")
