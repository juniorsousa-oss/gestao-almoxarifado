from __future__ import annotations

import pandas as pd

ALIASES = {
    "ACURACIDADE DE ESTOQUE": "ACURÁCIA DE ESTOQUE",
    "ACURÁCIDADE DE ESTOQUE": "ACURÁCIA DE ESTOQUE",
    "ACURÁCIA DE ESTOQUE": "ACURÁCIA DE ESTOQUE",
    "ACURACIA DE ESTOQUE": "ACURÁCIA DE ESTOQUE",
    "ENTREGAS NO PRAZO": "ENTREGAS NO PRAZO",
    "5S": "5S",
}

MESES = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]


def normalizar_indicador(value):
    nome = str(value or "").strip()
    return ALIASES.get(nome.upper(), nome.upper())


def _ordenar_lancamentos(rows):
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame([dict(r) for r in rows])
    if "competencia" not in df.columns:
        return pd.DataFrame()
    df["_competencia"] = pd.to_datetime(df["competencia"], errors="coerce")
    df = df.dropna(subset=["_competencia"]).copy()
    if df.empty:
        return df
    if "created_at" in df.columns:
        df["_created_at"] = pd.to_datetime(df["created_at"], errors="coerce", utc=True)
    elif "updated_at" in df.columns:
        df["_created_at"] = pd.to_datetime(df["updated_at"], errors="coerce", utc=True)
    else:
        df["_created_at"] = pd.NaT
    if "id" in df.columns:
        df["_id_ord"] = pd.to_numeric(df["id"], errors="coerce")
    else:
        df["_id_ord"] = pd.NA
    df["_seq"] = range(len(df))
    return df.sort_values(
        ["_competencia", "_created_at", "_id_ord", "_seq"],
        kind="stable",
        na_position="first",
    )


def consolidar_ultimo_por_mes(rows):
    """Retorna exatamente o último lançamento de cada mês, sem média."""
    df = _ordenar_lancamentos(rows)
    if df.empty:
        return []
    df["_periodo"] = df["_competencia"].dt.to_period("M")
    df = df.groupby("_periodo", sort=True, group_keys=False).tail(1)
    helpers = ["_competencia", "_created_at", "_id_ord", "_seq", "_periodo"]
    return df.drop(columns=[c for c in helpers if c in df.columns]).to_dict("records")


def meses_disponiveis(indicadores):
    df = _ordenar_lancamentos(indicadores)
    if df.empty:
        return []
    periodos = sorted(df["_competencia"].dt.to_period("M").unique(), reverse=True)
    return [str(p) for p in periodos]


def rotulo_mes(periodo):
    try:
        p = pd.Period(str(periodo), freq="M")
        return f"{MESES[p.month-1]}/{p.year}"
    except Exception:
        return str(periodo or "—")


def preparar_exportacao(indicadores, modo="ATUAL", periodo=None):
    """Seleciona um único fechamento mensal por indicador para as imagens exportadas."""
    grupos = {}
    for row in indicadores or []:
        nome = normalizar_indicador(row.get("indicador"))
        if not nome:
            continue
        item = dict(row)
        item["indicador"] = nome
        grupos.setdefault(nome, []).append(item)

    saida = []
    for nome, rows in grupos.items():
        mensais = consolidar_ultimo_por_mes(rows)
        if not mensais:
            continue
        if str(modo).upper().startswith("MÊS") or str(modo).upper().startswith("MES"):
            alvo = str(periodo or "")
            candidatos = []
            for row in mensais:
                dt = pd.to_datetime(row.get("competencia"), errors="coerce")
                if pd.notna(dt) and str(dt.to_period("M")) == alvo:
                    candidatos.append(row)
            if candidatos:
                saida.append(candidatos[-1])
        else:
            saida.append(mensais[-1])
    return saida
