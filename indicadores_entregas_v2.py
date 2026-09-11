from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime, timedelta, timezone
from io import BytesIO
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st
from supabase_client import get_client

INDICADOR = "ENTREGAS NO PRAZO"
TZ_APP = ZoneInfo("America/Sao_Paulo")


def _agora_local():
    return datetime.now(TZ_APP)


def _norm_code(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    s = str(value).strip()
    if not s or s.lower() == "nan":
        return ""
    if s.endswith(".0"):
        s = s[:-2]
    if s.isdigit():
        return str(int(s))
    return s.upper()


def _norm_project(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    s = str(value).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s


def _column(df, *aliases):
    import unicodedata

    def key(value):
        s = unicodedata.normalize("NFKD", str(value))
        s = "".join(ch for ch in s if not unicodedata.combining(ch))
        return " ".join(s.strip().upper().split())

    lookup = {key(c): c for c in df.columns}
    for alias in aliases:
        if key(alias) in lookup:
            return lookup[key(alias)]
    raise ValueError(f"Coluna não encontrada: {aliases[0]}")


def _excel(uploaded, sheet_name):
    return pd.read_excel(BytesIO(uploaded.getvalue()), sheet_name=sheet_name, dtype=str, engine="openpyxl")


def _to_date(series):
    return pd.to_datetime(series, dayfirst=True, errors="coerce")


def _to_num(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 0.0
    s = str(value).strip().replace(" ", "")
    if not s or s.lower() == "nan":
        return 0.0
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except Exception:
        return 0.0


def _action_quantities(action):
    text = "" if action is None else str(action)
    result = {"Estoque": 0.0, "Pré Nota": 0.0, "P.C.": 0.0, "Fabricação": 0.0, "S.C.": 0.0}
    patterns = [
        ("Estoque", r"Estoque\s+([\d.,]+)"),
        ("Pré Nota", r"Pr[eé]\s*Nota\s+([\d.,]+)"),
        ("P.C.", r"P\.C\.\s+([\d.,]+)"),
        ("Fabricação", r"Fabrica[cç][aã]o\s+([\d.,]+)"),
        ("S.C.", r"S\.C\.\s+([\d.,]+)"),
    ]
    for label, pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            result[label] += _to_num(match.group(1))
    return result


def _action_category(action):
    q = _action_quantities(action)
    active = [k for k, v in q.items() if v > 0]
    return " + ".join(active) if active else "SEM AÇÃO"


def _file_hash(uploaded):
    data = uploaded.getvalue()
    return hashlib.sha256(data).hexdigest(), len(data)


def calcular_entregas_v2(relatorio_file, mrp_file, data_registro: date | None = None):
    data_registro = data_registro or _agora_local().date()
    periodo_inicio = date(data_registro.year, data_registro.month, 1)
    periodo_fim = data_registro - timedelta(days=1)
    if periodo_fim < periodo_inicio:
        raise ValueError("Ainda não há período fechado no mês atual: hoje é o primeiro dia do mês.")

    rel = _excel(relatorio_file, "Geral")
    demanda = _excel(mrp_file, "Demanda_Projeto")
    mrp_geral = _excel(mrp_file, "MRP_Geral")

    # RELATÓRIO GERAL
    r_projeto = _column(rel, "Projeto")
    r_codigo = _column(rel, "Código", "Codigo")
    r_ultima = _column(rel, "Última solicitação", "Ultima solicitacao")
    r_separacao = _column(rel, "Data de separação", "Data de separacao")

    rel_base = rel[[r_projeto, r_codigo, r_ultima, r_separacao]].copy()
    rel_base.columns = ["Projeto", "Código", "Última Solicitação", "Data de Separação"]
    rel_base.insert(0, "Linha Relatório Geral", range(2, len(rel_base) + 2))
    rel_base["Projeto"] = rel_base["Projeto"].map(_norm_project)
    rel_base["Código normalizado"] = rel_base["Código"].map(_norm_code)
    rel_base["Projeto_Código"] = rel_base["Projeto"] + "_" + rel_base["Código normalizado"]
    rel_base["Última Solicitação"] = _to_date(rel_base["Última Solicitação"])
    rel_base["Data de Separação"] = _to_date(rel_base["Data de Separação"])

    # DEMANDA PROJETO
    d_projeto = _column(demanda, "Projeto")
    d_produto = _column(demanda, "Produto")
    d_desc = _column(demanda, "Descrição", "Descricao")
    d_data_cm = _column(demanda, "Data CM")
    d_acao = _column(demanda, "Ação", "Acao")

    dem = demanda.copy()
    dem["Projeto_norm"] = dem[d_projeto].map(_norm_project)
    dem["Código normalizado"] = dem[d_produto].map(_norm_code)
    dem["Projeto_Código"] = dem["Projeto_norm"] + "_" + dem["Código normalizado"]
    dem["Data CM tratada"] = _to_date(dem[d_data_cm])

    # A chave da demanda deve ser única; em caso de problema, interrompe para não duplicar a base.
    duplicadas = dem.loc[dem["Projeto_Código"].duplicated(keep=False) & dem["Projeto_Código"].ne("_")]
    if not duplicadas.empty:
        exemplos = ", ".join(duplicadas["Projeto_Código"].drop_duplicates().head(5).tolist())
        raise ValueError(f"Há chaves Projeto_Código duplicadas no Demanda_Projeto. Exemplos: {exemplos}")

    dem_lookup = dem[["Projeto_Código", "Data CM tratada", d_acao, d_desc]].copy()
    dem_lookup.columns = ["Projeto_Código", "Data CM", "Ação", "Descrição MRP"]

    # TIPOS — primeira aba MRP_Geral
    g_codigo = _column(mrp_geral, "Código", "Codigo")
    g_tipo = _column(mrp_geral, "Tipo")
    tipos = mrp_geral[[g_codigo, g_tipo]].copy()
    tipos["Código normalizado"] = tipos[g_codigo].map(_norm_code)
    tipos["Tipo"] = tipos[g_tipo].fillna("").astype(str).str.strip().str.upper()
    tipos = tipos[tipos["Código normalizado"] != ""].drop_duplicates("Código normalizado", keep="last")
    tipo_map = tipos.set_index("Código normalizado")["Tipo"].to_dict()

    # FUSÃO — mantém todas as linhas do Relatório Geral e adiciona a informação do MRP pela chave.
    fundida = rel_base.merge(dem_lookup, on="Projeto_Código", how="left", validate="many_to_one")
    fundida["Tipo"] = fundida["Código normalizado"].map(tipo_map).fillna("")
    fundida["Chave encontrada no MRP"] = fundida["Data CM"].notna() | fundida["Ação"].notna()

    inicio_ts = pd.Timestamp(periodo_inicio)
    fim_ts = pd.Timestamp(periodo_fim)
    base = fundida[fundida["Data CM"].between(inicio_ts, fim_ts, inclusive="both")].copy()
    if base.empty:
        raise ValueError(
            f"Nenhuma solicitação com Data CM entre {periodo_inicio.strftime('%d/%m/%Y')} e {periodo_fim.strftime('%d/%m/%Y')}."
        )

    # ENTREGA EM DIA — critérios sequenciais.
    base["Critério entrega"] = "ATRASADA"
    base["Entregue em dia"] = False

    c1 = base["Data de Separação"].notna() & (base["Data de Separação"] <= base["Data CM"])
    base.loc[c1, "Critério entrega"] = "DATA DE SEPARAÇÃO <= DATA CM"
    base.loc[c1, "Entregue em dia"] = True

    pend = ~base["Entregue em dia"]
    c2 = pend & base["Última Solicitação"].notna() & (base["Última Solicitação"] > base["Data CM"])
    base.loc[c2, "Critério entrega"] = "SOLICITAÇÃO POSTERIOR À DATA CM"
    base.loc[c2, "Entregue em dia"] = True

    pend = ~base["Entregue em dia"]
    c3 = pend & base["Tipo"].eq("II")
    base.loc[c3, "Critério entrega"] = "MATERIAL TIPO II"
    base.loc[c3, "Entregue em dia"] = True

    base["Categoria Ação"] = base["Ação"].map(_action_category)
    sem_sep = base["Data de Separação"].isna()
    base["Diagnóstico sem separação"] = ""
    base.loc[sem_sep, "Diagnóstico sem separação"] = base.loc[sem_sep, "Categoria Ação"]

    solicitacoes = int(len(base))
    entregues = int(base["Entregue em dia"].sum())
    atrasadas = int((~base["Entregue em dia"]).sum())
    projetos_programados = int(base["Projeto"].replace("", pd.NA).dropna().nunique())

    # ATENDIDOS COMPLETAMENTE — usa a quantidade efetivamente dependente de fontes futuras indicada em Ação.
    # Apenas projetos da base programada e linhas do Demanda_Projeto dentro do mesmo período.
    projetos_base = set(base["Projeto"].dropna().astype(str))
    dem_periodo = dem[
        dem["Projeto_norm"].isin(projetos_base)
        & dem["Data CM tratada"].between(inicio_ts, fim_ts, inclusive="both")
    ].copy()

    registros_demanda = []
    for idx, row in dem_periodo.iterrows():
        q = _action_quantities(row[d_acao])
        pendente = q["Pré Nota"] + q["P.C."] + q["Fabricação"] + q["S.C."]
        registros_demanda.append({
            "Projeto": row["Projeto_norm"],
            "Código": row["Código normalizado"],
            "Projeto_Código": row["Projeto_Código"],
            "Descrição": row[d_desc],
            "Data CM": row["Data CM tratada"],
            "Ação": row[d_acao],
            "Qtd Estoque na Ação": q["Estoque"],
            "Qtd Pré Nota na Ação": q["Pré Nota"],
            "Qtd P.C. na Ação": q["P.C."],
            "Qtd Fabricação na Ação": q["Fabricação"],
            "Qtd S.C. na Ação": q["S.C."],
            "Quantidade pendente": pendente,
        })
    demanda_auditoria = pd.DataFrame(registros_demanda)

    if demanda_auditoria.empty:
        resumo_projetos = pd.DataFrame(columns=["Projeto", "Solicitações", "Linhas MRP", "Quantidade pendente", "Atendido completamente"])
        atendidos_completamente = 0
    else:
        solic_por_proj = base.groupby("Projeto").size().rename("Solicitações")
        resumo_projetos = demanda_auditoria.groupby("Projeto", as_index=False).agg(
            **{
                "Linhas MRP": ("Projeto_Código", "size"),
                "Quantidade pendente": ("Quantidade pendente", "sum"),
                "Linhas com pendência": ("Quantidade pendente", lambda s: int((s > 0).sum())),
            }
        )
        resumo_projetos["Solicitações"] = resumo_projetos["Projeto"].map(solic_por_proj).fillna(0).astype(int)
        resumo_projetos["Atendido completamente"] = resumo_projetos["Quantidade pendente"].le(0).map({True: "SIM", False: "NÃO"})
        resumo_projetos = resumo_projetos[[
            "Projeto", "Solicitações", "Linhas MRP", "Linhas com pendência", "Quantidade pendente", "Atendido completamente"
        ]]
        atendidos_completamente = int(resumo_projetos["Atendido completamente"].eq("SIM").sum())

    projetos_atendidos_pct = (atendidos_completamente / projetos_programados * 100.0) if projetos_programados else 0.0
    entregas_em_dia_pct = (entregues / solicitacoes * 100.0) if solicitacoes else 0.0
    resultado_final = projetos_atendidos_pct * entregas_em_dia_pct / 100.0

    # Auditoria das linhas atrasadas/sem separação por origem da Ação.
    atrasos = base[~base["Entregue em dia"]].copy()
    sem_separacao = base[base["Data de Separação"].isna()].copy()
    acao_resumo = (
        sem_separacao.groupby("Categoria Ação", dropna=False).size().reset_index(name="Quantidade")
        .sort_values("Quantidade", ascending=False)
    )

    rel_hash, rel_size = _file_hash(relatorio_file)
    mrp_hash, mrp_size = _file_hash(mrp_file)

    # Formatação amigável para exportação/tela.
    for df in (base, atrasos, sem_separacao):
        df["Data CM"] = pd.to_datetime(df["Data CM"], errors="coerce")
        df["Última Solicitação"] = pd.to_datetime(df["Última Solicitação"], errors="coerce")
        df["Data de Separação"] = pd.to_datetime(df["Data de Separação"], errors="coerce")
        df["Entregue em dia"] = df["Entregue em dia"].map({True: "SIM", False: "NÃO"})
        df["Chave encontrada no MRP"] = df["Chave encontrada no MRP"].map({True: "SIM", False: "NÃO"})

    return {
        "data_registro": data_registro.isoformat(),
        "periodo_inicio": periodo_inicio.isoformat(),
        "periodo_fim": periodo_fim.isoformat(),
        "gerado_em": _agora_local().isoformat(),
        "solicitacoes": solicitacoes,
        "entregues_em_dia": entregues,
        "entregas_atrasadas": atrasadas,
        "projetos_programados": projetos_programados,
        "atendidos_completamente": atendidos_completamente,
        "entregas_em_dia_pct": entregas_em_dia_pct,
        "projetos_atendidos_pct": projetos_atendidos_pct,
        "resultado_final": resultado_final,
        "diretas": int(c1.sum()),
        "solicitacao_tardia": int(c2.sum()),
        "tipo_ii": int(c3.sum()),
        "sem_separacao": int(sem_sep.sum()),
        "quantidade_pendente_total": float(demanda_auditoria["Quantidade pendente"].sum()) if not demanda_auditoria.empty else 0.0,
        "base_fundida": base.to_dict("records"),
        "atrasos": atrasos.to_dict("records"),
        "sem_separacao_detalhe": sem_separacao.to_dict("records"),
        "acoes_resumo": acao_resumo.to_dict("records"),
        "demanda_projeto": demanda_auditoria.to_dict("records"),
        "projetos": resumo_projetos.to_dict("records"),
        "relatorio_nome": getattr(relatorio_file, "name", "RelatorioGeral.xlsx"),
        "relatorio_sha256": rel_hash,
        "relatorio_tamanho": rel_size,
        "mrp_nome": getattr(mrp_file, "name", "MRP_Consulta.xlsx"),
        "mrp_sha256": mrp_hash,
        "mrp_tamanho": mrp_size,
    }


def _ultima_meta(indicadores):
    rows = [r for r in (indicadores or []) if str(r.get("indicador") or "").strip().upper() == INDICADOR and r.get("meta") is not None]
    if not rows:
        return 0.0
    rows.sort(key=lambda r: pd.to_datetime(r.get("competencia"), errors="coerce"))
    try:
        return float(rows[-1]["meta"])
    except Exception:
        return 0.0


def _excel_auditoria(resultado, meta):
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    output = BytesIO()
    resumo = [
        ["RELATÓRIO DE AUDITORIA — ENTREGAS NO PRAZO", ""],
        ["Data de registro", pd.to_datetime(resultado["data_registro"]).strftime("%d/%m/%Y")],
        ["Período apurado", f"{pd.to_datetime(resultado['periodo_inicio']).strftime('%d/%m/%Y')} a {pd.to_datetime(resultado['periodo_fim']).strftime('%d/%m/%Y')}"],
        ["Gerado em", pd.to_datetime(resultado["gerado_em"]).strftime("%d/%m/%Y %H:%M:%S")],
        ["", ""],
        ["Solicitações", resultado["solicitacoes"]],
        ["Entregues em dia", resultado["entregues_em_dia"]],
        ["Entregas atrasadas", resultado["entregas_atrasadas"]],
        ["Entregas em dia (%)", resultado["entregas_em_dia_pct"]],
        ["Projetos programados", resultado["projetos_programados"]],
        ["Atendidos completamente", resultado["atendidos_completamente"]],
        ["Projetos atendidos (%)", resultado["projetos_atendidos_pct"]],
        ["ENTREGAS NO PRAZO (%)", resultado["resultado_final"]],
        ["Meta (%)", meta],
        ["", ""],
        ["Diretas — Separação <= CM", resultado["diretas"]],
        ["Exceção — Solicitação posterior à CM", resultado["solicitacao_tardia"]],
        ["Exceção — Tipo II", resultado["tipo_ii"]],
        ["Linhas sem Data de Separação", resultado["sem_separacao"]],
        ["Quantidade pendente total no MRP", resultado["quantidade_pendente_total"]],
        ["", ""],
        ["Arquivo Relatório Geral", resultado["relatorio_nome"]],
        ["SHA-256 Relatório Geral", resultado["relatorio_sha256"]],
        ["Tamanho Relatório Geral (bytes)", resultado["relatorio_tamanho"]],
        ["Arquivo MRP", resultado["mrp_nome"]],
        ["SHA-256 MRP", resultado["mrp_sha256"]],
        ["Tamanho MRP (bytes)", resultado["mrp_tamanho"]],
    ]
    metodologia = [
        ["ETAPA", "REGRA"],
        ["Chave", "Projeto_Código = Projeto + '_' + Código normalizado."],
        ["Fusão", "Relatório Geral recebe Data CM, Ação e Descrição do Demanda_Projeto pela chave Projeto_Código."],
        ["Período", "Data CM entre o primeiro dia do mês atual e hoje - 1 dia, inclusive."],
        ["Solicitações", "Quantidade total de linhas do Relatório Geral após o filtro de Data CM."],
        ["Entrega direta", "Data de Separação <= Data CM."],
        ["Solicitação tardia", "Se ainda não entregue em dia e Última Solicitação > Data CM, considerar em dia."],
        ["Tipo II", "Se ainda não entregue em dia e Tipo do material na aba MRP_Geral = II, considerar em dia."],
        ["Atrasada", "Linha que permanece fora dos três critérios anteriores."],
        ["Sem separação", "A coluna Ação é mantida e classificada para evidenciar Estoque, P.C., S.C., Fabricação e/ou Pré Nota."],
        ["Projetos programados", "Quantidade distinta de projetos presentes na base usada para Entregas em Dia."],
        ["Quantidade pendente", "Soma das quantidades da Ação vinculadas a Pré Nota + P.C. + Fabricação + S.C.; Estoque não é pendência."],
        ["Atendido completamente", "Projeto cuja Quantidade pendente total no Demanda_Projeto do período é zero."],
        ["Entregas em dia (%)", "Entregues em dia / Solicitações × 100."],
        ["Projetos atendidos (%)", "Atendidos completamente / Projetos programados × 100."],
        ["Resultado final", "Entregas em dia (%) × Projetos atendidos (%) / 100."],
    ]

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pd.DataFrame(resumo).to_excel(writer, sheet_name="RESUMO", index=False, header=False)
        pd.DataFrame(resultado["base_fundida"]).to_excel(writer, sheet_name="BASE_FUNDIDA", index=False)
        pd.DataFrame(resultado["projetos"]).to_excel(writer, sheet_name="PROJETOS", index=False)
        pd.DataFrame(resultado["demanda_projeto"]).to_excel(writer, sheet_name="DEMANDA_PROJETO", index=False)
        pd.DataFrame(resultado["atrasos"]).to_excel(writer, sheet_name="ATRASOS", index=False)
        pd.DataFrame(resultado["sem_separacao_detalhe"]).to_excel(writer, sheet_name="SEM_SEPARACAO", index=False)
        pd.DataFrame(resultado["acoes_resumo"]).to_excel(writer, sheet_name="RESUMO_ACOES", index=False)
        pd.DataFrame(metodologia).to_excel(writer, sheet_name="METODOLOGIA", index=False, header=False)

        wb = writer.book
        dark = PatternFill("solid", fgColor="1F2937")
        yellow = PatternFill("solid", fgColor="FFD43D")
        soft = PatternFill("solid", fgColor="FFF4BF")
        white = Font(color="FFFFFF", bold=True)
        thin = Side(style="thin", color="D1D5DB")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)

        for ws in wb.worksheets:
            ws.sheet_view.showGridLines = False
            ws.freeze_panes = "A2"
            if ws.title not in ("RESUMO", "METODOLOGIA") and ws.max_row >= 1:
                for cell in ws[1]:
                    cell.fill = dark
                    cell.font = white
                    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                    cell.border = border
                ws.auto_filter.ref = ws.dimensions
            for row in ws.iter_rows():
                for cell in row:
                    cell.alignment = Alignment(vertical="top", wrap_text=True)
                    if ws.title not in ("RESUMO", "METODOLOGIA"):
                        cell.border = border
            for col in range(1, ws.max_column + 1):
                letter = get_column_letter(col)
                vals = [str(ws.cell(r, col).value or "") for r in range(1, min(ws.max_row, 200) + 1)]
                ws.column_dimensions[letter].width = min(max(max((len(x) for x in vals), default=8) + 2, 10), 45)

        ws = wb["RESUMO"]
        ws.merge_cells("A1:B1")
        ws["A1"].fill = yellow
        ws["A1"].font = Font(size=14, bold=True, color="111111")
        ws["A1"].alignment = Alignment(horizontal="center")
        ws.column_dimensions["A"].width = 42
        ws.column_dimensions["B"].width = 82
        for r in range(2, ws.max_row + 1):
            ws.cell(r, 1).font = Font(bold=True)
            ws.cell(r, 1).border = border
            ws.cell(r, 2).border = border
        for r in range(6, 15):
            ws.cell(r, 1).fill = soft
            ws.cell(r, 2).fill = soft

        ws = wb["METODOLOGIA"]
        ws.column_dimensions["A"].width = 30
        ws.column_dimensions["B"].width = 115
        for cell in ws[1]:
            cell.fill = dark
            cell.font = white
            cell.border = border
        for row in ws.iter_rows():
            for cell in row:
                cell.border = border
                cell.alignment = Alignment(vertical="top", wrap_text=True)

    output.seek(0)
    return output.getvalue()


def _salvar(resultado, meta):
    client = get_client()
    competencia = resultado["data_registro"]
    audit = {
        k: resultado[k]
        for k in [
            "data_registro", "periodo_inicio", "periodo_fim", "gerado_em", "solicitacoes", "entregues_em_dia",
            "entregas_atrasadas", "projetos_programados", "atendidos_completamente", "entregas_em_dia_pct",
            "projetos_atendidos_pct", "resultado_final", "diretas", "solicitacao_tardia", "tipo_ii", "sem_separacao",
            "quantidade_pendente_total", "relatorio_nome", "relatorio_sha256", "relatorio_tamanho", "mrp_nome",
            "mrp_sha256", "mrp_tamanho",
        ]
    }
    payload = {
        "competencia": competencia,
        "categoria": "OPERACIONAL",
        "indicador": INDICADOR,
        "valor": round(float(resultado["resultado_final"]), 2),
        "meta": round(float(meta), 2),
        "unidade": "%",
        "observacao": json.dumps({"origem": "entregas_no_prazo_v2", **audit}, ensure_ascii=False, separators=(",", ":")),
        "atualizado_em": datetime.now(timezone.utc).isoformat(),
    }
    existente = (
        client.table("almox_indicadores").select("id").eq("indicador", INDICADOR)
        .eq("competencia", competencia).limit(1).execute().data or []
    )
    if existente:
        client.table("almox_indicadores").update(payload).eq("id", existente[0]["id"]).execute()
        acao = "atualizado"
    else:
        client.table("almox_indicadores").insert(payload).execute()
        acao = "salvo"

    try:
        client.table("almox_historico").insert({
            "tipo": "indicador_entregas_no_prazo_v2",
            "descricao": f"Entregas no prazo {acao}: {pd.to_datetime(competencia).strftime('%d/%m/%Y')}",
            "dados": audit,
        }).execute()
    except Exception:
        pass
    return acao


def render_alimentacao_entregas_v2(indicadores):
    hoje = _agora_local().date()
    periodo_fim = hoje - timedelta(days=1)
    with st.expander("ALIMENTAR · ENTREGAS NO PRAZO", expanded=False):
        st.caption(
            f"Registro: {hoje.strftime('%d/%m/%Y')} · Período automático: 01/{hoje.strftime('%m/%Y')} a {periodo_fim.strftime('%d/%m/%Y')}. "
            "Envie o Relatório Geral e o MRP_Consulta; a fusão e o cálculo são automáticos."
        )
        c1, c2, c3 = st.columns([1.25, 1.25, 0.75])
        with c1:
            relatorio = st.file_uploader(
                "RELATÓRIO GERAL", type=["xlsx", "xlsm", "xltx"], key="entregas_v2_relatorio"
            )
        with c2:
            mrp = st.file_uploader(
                "MRP_CONSULTA", type=["xlsx", "xlsm", "xltx"], key="entregas_v2_mrp"
            )
        with c3:
            st.text_input("Data do registro", value=hoje.strftime("%d/%m/%Y"), disabled=True, key="entregas_v2_data")
            meta = st.number_input(
                "Meta (%)", min_value=0.0, max_value=100.0, value=float(_ultima_meta(indicadores)), step=0.1,
                key="entregas_v2_meta",
            )

        if relatorio is None or mrp is None:
            st.info("Envie as duas bases para gerar automaticamente a apuração.")
            return

        fingerprint = hashlib.sha256(relatorio.getvalue() + mrp.getvalue() + hoje.isoformat().encode()).hexdigest()
        if st.session_state.get("entregas_v2_fingerprint") != fingerprint:
            try:
                with st.spinner("Fundindo as bases e calculando o indicador..."):
                    resultado = calcular_entregas_v2(relatorio, mrp, hoje)
                st.session_state["entregas_v2_resultado"] = resultado
                st.session_state["entregas_v2_fingerprint"] = fingerprint
                st.session_state.pop("entregas_v2_registrado", None)
            except Exception as exc:
                st.session_state.pop("entregas_v2_resultado", None)
                st.error(f"Não foi possível calcular: {exc}")
                return

        resultado = st.session_state.get("entregas_v2_resultado")
        if not resultado:
            return

        st.success(
            f"Base calculada: {resultado['solicitacoes']} solicitações em {resultado['projetos_programados']} projetos."
        )
        a, b, c, d = st.columns(4)
        a.metric("Solicitações", resultado["solicitacoes"])
        b.metric("Entregues em dia", resultado["entregues_em_dia"])
        c.metric("Projetos programados", resultado["projetos_programados"])
        d.metric("Atendidos completamente", resultado["atendidos_completamente"])

        p1, p2, p3 = st.columns(3)
        p1.metric("Entregas em dia", f"{resultado['entregas_em_dia_pct']:.2f}%")
        p2.metric("Projetos atendidos", f"{resultado['projetos_atendidos_pct']:.2f}%")
        p3.metric("ENTREGAS NO PRAZO", f"{resultado['resultado_final']:.2f}%")

        st.caption(
            f"Entregas validadas: {resultado['diretas']} por Separação <= CM · "
            f"{resultado['solicitacao_tardia']} por solicitação posterior à CM · "
            f"{resultado['tipo_ii']} por Tipo II · {resultado['entregas_atrasadas']} permanecem atrasadas."
        )
        st.caption(
            f"Sem Data de Separação: {resultado['sem_separacao']} linhas. "
            f"Quantidade pendente no MRP para os projetos do período: {resultado['quantidade_pendente_total']:.2f}."
        )

        with st.expander("RESUMO DAS AÇÕES — LINHAS SEM DATA DE SEPARAÇÃO"):
            st.dataframe(pd.DataFrame(resultado["acoes_resumo"]), use_container_width=True, hide_index=True)
        with st.expander("CONFERÊNCIA POR PROJETO"):
            st.dataframe(pd.DataFrame(resultado["projetos"]), use_container_width=True, hide_index=True)
        with st.expander("BASE FUNDIDA — LINHA A LINHA"):
            st.dataframe(pd.DataFrame(resultado["base_fundida"]), use_container_width=True, hide_index=True)

        excel_bytes = _excel_auditoria(resultado, meta)
        x1, x2 = st.columns(2)
        with x1:
            st.download_button(
                "EXPORTAR AUDITORIA · EXCEL",
                data=excel_bytes,
                file_name=f"auditoria_entregas_no_prazo_{hoje.isoformat()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="entregas_v2_excel",
            )
        with x2:
            if st.button(
                f"REGISTRAR RESULTADO · {hoje.strftime('%d/%m/%Y')}", type="primary", use_container_width=True,
                key="entregas_v2_salvar"
            ):
                try:
                    acao = _salvar(resultado, meta)
                    st.session_state["entregas_v2_registrado"] = True
                    st.success(f"Resultado {acao} com a data de hoje: {resultado['resultado_final']:.2f}%.")
                except Exception as exc:
                    st.error(f"Não foi possível registrar no Supabase: {exc}")

        if st.session_state.get("entregas_v2_registrado"):
            st.info("A mesma data atualiza o registro existente, sem duplicar o indicador.")
