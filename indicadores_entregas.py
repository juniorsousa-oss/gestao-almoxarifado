from __future__ import annotations

from datetime import date, datetime, timezone
from io import BytesIO
import json
import re
import unicodedata

import pandas as pd
import streamlit as st

from supabase_client import get_client


INDICADOR = "ENTREGAS NO PRAZO"


def _norm_header(value):
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", text).strip().upper()


def _norm_code(value):
    if pd.isna(value):
        return ""
    return re.sub(r"[^0-9A-Za-z]", "", str(value)).upper()


def _find_column(df, *names):
    lookup = {_norm_header(col): col for col in df.columns}
    for name in names:
        key = _norm_header(name)
        if key in lookup:
            return lookup[key]
    raise ValueError(f"Coluna não encontrada: {names[0]}")


def _read_excel_bytes(uploaded, **kwargs):
    return pd.read_excel(BytesIO(uploaded.getvalue()), engine="openpyxl", **kwargs)


def calcular_entregas_no_prazo(relatorio_file, cadastros_file, data_analise: date):
    rel = _read_excel_bytes(relatorio_file, sheet_name="RelatorioTratado", dtype=str)
    cad = _read_excel_bytes(cadastros_file, sheet_name=0, header=1, dtype=str)

    c_projeto = _find_column(rel, "Projeto")
    c_codigo = _find_column(rel, "Código", "Codigo")
    c_ultima = _find_column(rel, "Última solicitação", "Ultima solicitacao")
    c_pend = _find_column(rel, "Pendência", "Pendencia")
    c_sep = _find_column(rel, "Data de separação", "Data de separacao")
    c_cm = _find_column(rel, "DATA CM")
    c_semana = _find_column(rel, "SEMANA DE NECESSIDADE")

    cad_codigo = _find_column(cad, "Código", "Codigo")
    cad_tipo = _find_column(cad, "Tipo")

    cad_base = cad[[cad_codigo, cad_tipo]].copy()
    cad_base["_codigo"] = cad_base[cad_codigo].map(_norm_code)
    cad_base["_tipo"] = cad_base[cad_tipo].fillna("").astype(str).str.strip().str.upper()
    cad_base = cad_base[cad_base["_codigo"] != ""].drop_duplicates("_codigo", keep="last")
    tipos = cad_base.set_index("_codigo")["_tipo"].to_dict()

    base = rel[[c_projeto, c_codigo, c_ultima, c_pend, c_sep, c_cm, c_semana]].copy()
    base.columns = ["projeto", "codigo", "ultima_solicitacao", "pendencia", "data_separacao", "data_cm", "semana_necessidade"]
    base["projeto"] = base["projeto"].fillna("").astype(str).str.strip()
    base["codigo_norm"] = base["codigo"].map(_norm_code)
    base["tipo"] = base["codigo_norm"].map(tipos).fillna("")
    base["ultima_solicitacao"] = pd.to_datetime(base["ultima_solicitacao"], dayfirst=True, errors="coerce")
    base["data_separacao"] = pd.to_datetime(base["data_separacao"], dayfirst=True, errors="coerce")
    base["data_cm"] = pd.to_datetime(base["data_cm"], dayfirst=True, errors="coerce")
    base["pendencia"] = pd.to_numeric(
        base["pendencia"].fillna("0").astype(str).str.replace(",", ".", regex=False), errors="coerce"
    ).fillna(0.0)
    base["semana_num"] = pd.to_numeric(
        base["semana_necessidade"].fillna("").astype(str).str.replace(",", ".", regex=False), errors="coerce"
    )

    inicio = pd.Timestamp(date(data_analise.year, data_analise.month, 1))
    fim = pd.Timestamp(data_analise)
    periodo = base[base["data_cm"].between(inicio, fim, inclusive="both")].copy()

    if periodo.empty:
        raise ValueError(
            f"Nenhuma linha com DATA CM entre {inicio.strftime('%d/%m/%Y')} e {fim.strftime('%d/%m/%Y')}."
        )

    projetos_validos = periodo[periodo["projeto"] != ""].copy()
    programados = int(projetos_validos["projeto"].nunique())
    solicitacoes = int(len(periodo))

    periodo["pendencia_bruta"] = periodo["pendencia"] > 0
    periodo["semana_valida"] = periodo["semana_num"].notna()
    periodo["tipo_ii"] = periodo["tipo"].eq("II")
    periodo["pendencia_efetiva"] = periodo["pendencia_bruta"] & periodo["semana_valida"] & ~periodo["tipo_ii"]

    resumo_projetos = (
        projetos_validos.assign(
            pendencia_bruta=periodo.loc[projetos_validos.index, "pendencia_bruta"],
            pendencia_efetiva=periodo.loc[projetos_validos.index, "pendencia_efetiva"],
        )
        .groupby("projeto", as_index=False)
        .agg(
            solicitacoes=("codigo", "size"),
            pendencias_brutas=("pendencia_bruta", "sum"),
            pendencias_efetivas=("pendencia_efetiva", "sum"),
        )
    )
    resumo_projetos["status"] = resumo_projetos["pendencias_efetivas"].map(lambda x: "ATENDIDO 100%" if int(x) == 0 else "PENDENTE")
    atendidos_100 = int((resumo_projetos["pendencias_efetivas"] == 0).sum())

    sep_preenchida = periodo["data_separacao"].notna()
    entrega_direta = sep_preenchida & (periodo["data_separacao"] <= periodo["data_cm"])
    excecao_ultima_solicitacao = (
        sep_preenchida
        & (periodo["data_separacao"] > periodo["data_cm"])
        & periodo["ultima_solicitacao"].notna()
        & (periodo["ultima_solicitacao"] > periodo["data_cm"])
    )
    sem_separacao_tipo_ii = periodo["data_separacao"].isna() & periodo["tipo_ii"]
    entregue_em_dia = entrega_direta | excecao_ultima_solicitacao | sem_separacao_tipo_ii
    entregues_em_dia = int(entregue_em_dia.sum())

    projetos_atendidos_pct = (atendidos_100 / programados * 100.0) if programados else 0.0
    entregas_em_dia_pct = (entregues_em_dia / solicitacoes * 100.0) if solicitacoes else 0.0
    resultado_final = projetos_atendidos_pct * entregas_em_dia_pct / 100.0

    codigos_sem_cadastro = int(((periodo["codigo_norm"] != "") & (periodo["tipo"] == "")).sum())
    pendencias_brutas = int(periodo["pendencia_bruta"].sum())
    pendencias_sem_semana = int((periodo["pendencia_bruta"] & ~periodo["semana_valida"]).sum())
    pendencias_tipo_ii = int((periodo["pendencia_bruta"] & periodo["semana_valida"] & periodo["tipo_ii"]).sum())
    pendencias_efetivas = int(periodo["pendencia_efetiva"].sum())

    return {
        "periodo_inicio": inicio.date().isoformat(),
        "periodo_fim": fim.date().isoformat(),
        "programados": programados,
        "atendidos_100": atendidos_100,
        "solicitacoes": solicitacoes,
        "entregues_em_dia": entregues_em_dia,
        "projetos_atendidos_pct": projetos_atendidos_pct,
        "entregas_em_dia_pct": entregas_em_dia_pct,
        "resultado_final": resultado_final,
        "entrega_direta": int(entrega_direta.sum()),
        "excecao_ultima_solicitacao": int(excecao_ultima_solicitacao.sum()),
        "sem_separacao_tipo_ii": int(sem_separacao_tipo_ii.sum()),
        "pendencias_brutas": pendencias_brutas,
        "pendencias_sem_semana": pendencias_sem_semana,
        "pendencias_tipo_ii": pendencias_tipo_ii,
        "pendencias_efetivas": pendencias_efetivas,
        "codigos_sem_cadastro": codigos_sem_cadastro,
        "projetos": resumo_projetos.sort_values(["status", "projeto"]).to_dict("records"),
        "relatorio_nome": getattr(relatorio_file, "name", "RelatorioGeral_Tratado.xlsx"),
        "cadastros_nome": getattr(cadastros_file, "name", "CADASTROS.xltx"),
    }


def _ultima_meta(indicadores):
    candidatos = [
        row for row in (indicadores or [])
        if str(row.get("indicador") or "").strip().upper() == INDICADOR and row.get("meta") is not None
    ]
    if not candidatos:
        return 0.0
    candidatos.sort(key=lambda r: pd.to_datetime(r.get("competencia"), errors="coerce"))
    try:
        return float(candidatos[-1].get("meta"))
    except Exception:
        return 0.0


def _salvar_resultado(resultado, data_analise: date, meta: float):
    client = get_client()
    observacao = json.dumps(
        {
            "origem": "calculo_automatico_entregas_no_prazo",
            "periodo_inicio": resultado["periodo_inicio"],
            "periodo_fim": resultado["periodo_fim"],
            "programados": resultado["programados"],
            "atendidos_100": resultado["atendidos_100"],
            "solicitacoes": resultado["solicitacoes"],
            "entregues_em_dia": resultado["entregues_em_dia"],
            "projetos_atendidos_pct": round(resultado["projetos_atendidos_pct"], 4),
            "entregas_em_dia_pct": round(resultado["entregas_em_dia_pct"], 4),
            "entrega_direta": resultado["entrega_direta"],
            "excecao_ultima_solicitacao": resultado["excecao_ultima_solicitacao"],
            "sem_separacao_tipo_ii": resultado["sem_separacao_tipo_ii"],
            "pendencias_brutas": resultado["pendencias_brutas"],
            "pendencias_sem_semana": resultado["pendencias_sem_semana"],
            "pendencias_tipo_ii": resultado["pendencias_tipo_ii"],
            "pendencias_efetivas": resultado["pendencias_efetivas"],
            "codigos_sem_cadastro": resultado["codigos_sem_cadastro"],
            "relatorio": resultado["relatorio_nome"],
            "cadastros": resultado["cadastros_nome"],
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )
    payload = {
        "competencia": data_analise.isoformat(),
        "categoria": "OPERACIONAL",
        "indicador": INDICADOR,
        "valor": round(float(resultado["resultado_final"]), 2),
        "meta": round(float(meta), 2),
        "unidade": "%",
        "observacao": observacao,
        "atualizado_em": datetime.now(timezone.utc).isoformat(),
    }
    existente = (
        client.table("almox_indicadores")
        .select("id")
        .eq("indicador", INDICADOR)
        .eq("competencia", data_analise.isoformat())
        .limit(1)
        .execute()
        .data
        or []
    )
    if existente:
        client.table("almox_indicadores").update(payload).eq("id", existente[0]["id"]).execute()
        acao = "atualizado"
    else:
        client.table("almox_indicadores").insert(payload).execute()
        acao = "salvo"
    try:
        client.table("almox_historico").insert({
            "tipo": "indicador_entregas_no_prazo",
            "descricao": f"Entregas no prazo {acao}: {data_analise.strftime('%d/%m/%Y')}",
            "dados": {
                "competencia": data_analise.isoformat(),
                "valor": payload["valor"],
                "meta": payload["meta"],
                "programados": resultado["programados"],
                "atendidos_100": resultado["atendidos_100"],
                "solicitacoes": resultado["solicitacoes"],
                "entregues_em_dia": resultado["entregues_em_dia"],
                "excecao_ultima_solicitacao": resultado["excecao_ultima_solicitacao"],
            },
        }).execute()
    except Exception:
        pass
    return acao


def render_alimentacao_entregas(indicadores):
    with st.expander("ALIMENTAR · ENTREGAS NO PRAZO", expanded=False):
        st.caption(
            "Período automático: do primeiro dia do mês até a data da análise. "
            "O cálculo usa DATA CM como filtro-base e salva o resultado final no histórico do indicador."
        )
        a, b, c = st.columns([1.2, 1.2, 0.8])
        with a:
            relatorio = st.file_uploader(
                "RelatorioGeral_Tratado",
                type=["xlsx", "xlsm", "xltx"],
                key="entregas_relatorio_geral",
            )
        with b:
            cadastros = st.file_uploader(
                "CADASTROS",
                type=["xlsx", "xlsm", "xltx"],
                key="entregas_cadastros",
            )
        with c:
            data_analise = st.date_input(
                "Data da análise",
                value=date.today(),
                format="DD/MM/YYYY",
                key="entregas_data_analise",
            )
            meta = st.number_input(
                "Meta (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(_ultima_meta(indicadores)),
                step=0.1,
                key="entregas_meta",
            )

        if st.button("CALCULAR ENTREGAS NO PRAZO", type="primary", use_container_width=True, key="calcular_entregas_prazo"):
            if relatorio is None or cadastros is None:
                st.error("Envie o RelatorioGeral_Tratado e a planilha CADASTROS.")
            else:
                try:
                    resultado = calcular_entregas_no_prazo(relatorio, cadastros, data_analise)
                    st.session_state["entregas_prazo_resultado"] = resultado
                    st.session_state["entregas_prazo_data"] = data_analise.isoformat()
                    st.success("Cálculo concluído. Confira os resultados antes de salvar.")
                except Exception as exc:
                    st.session_state.pop("entregas_prazo_resultado", None)
                    st.error(f"Não foi possível calcular o indicador: {exc}")

        resultado = st.session_state.get("entregas_prazo_resultado")
        resultado_data = st.session_state.get("entregas_prazo_data")
        if resultado and resultado_data == data_analise.isoformat():
            st.markdown(
                f"**Período analisado:** {pd.to_datetime(resultado['periodo_inicio']).strftime('%d/%m/%Y')} "
                f"até {pd.to_datetime(resultado['periodo_fim']).strftime('%d/%m/%Y')}"
            )
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Programados", resultado["programados"])
            c2.metric("Atendidos 100%", resultado["atendidos_100"])
            c3.metric("Solicitações", resultado["solicitacoes"])
            c4.metric("Entregues em dia", resultado["entregues_em_dia"])

            p1, p2, p3 = st.columns(3)
            p1.metric("Projetos atendidos", f"{resultado['projetos_atendidos_pct']:.2f}%")
            p2.metric("Entregas em dia", f"{resultado['entregas_em_dia_pct']:.2f}%")
            p3.metric("ENTREGAS NO PRAZO", f"{resultado['resultado_final']:.2f}%")

            st.caption(
                "Entregues em dia: "
                f"{resultado['entrega_direta']} por Data de separação ≤ Data CM + "
                f"{resultado['excecao_ultima_solicitacao']} por Última solicitação > Data CM + "
                f"{resultado['sem_separacao_tipo_ii']} sem separação e Tipo II."
            )
            st.caption(
                "Pendências: "
                f"{resultado['pendencias_brutas']} linhas > 0; "
                f"{resultado['pendencias_sem_semana']} zeradas por não possuir semana numérica; "
                f"{resultado['pendencias_tipo_ii']} zeradas por Tipo II; "
                f"{resultado['pendencias_efetivas']} permanecem como pendência efetiva."
            )
            if resultado["codigos_sem_cadastro"]:
                st.warning(f"Há {resultado['codigos_sem_cadastro']} linha(s) com código não localizado em CADASTROS.")

            with st.expander("CONFERÊNCIA POR PROJETO"):
                conferencia = pd.DataFrame(resultado["projetos"])
                if not conferencia.empty:
                    st.dataframe(conferencia, use_container_width=True, hide_index=True)

            if st.button("SALVAR RESULTADO NO HISTÓRICO", type="primary", use_container_width=True, key="salvar_entregas_prazo"):
                try:
                    acao = _salvar_resultado(resultado, data_analise, meta)
                    st.success(f"Resultado {acao} no Supabase: {resultado['resultado_final']:.2f}%.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Não foi possível salvar o resultado: {exc}")
