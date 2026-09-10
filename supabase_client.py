from __future__ import annotations

import os
from typing import Any

import streamlit as st
from supabase import Client, create_client

PROJECT_URL = "https://cuixazpxkvniqldmmnth.supabase.co"


def _secret(name: str, default: str = "") -> str:
    try:
        value = st.secrets.get(name, default)
        if value is not None and str(value).strip():
            return str(value).strip().lstrip("\ufeff")
    except Exception:
        pass
    value = os.getenv(name, default)
    return str(value).strip().lstrip("\ufeff") if value is not None else default


def get_client() -> Client:
    url = _secret("SUPABASE_URL", PROJECT_URL)
    key = _secret("SUPABASE_KEY") or _secret("SUPABASE_ANON_KEY")

    # Evita problemas de cópia/cola de aspas ou caracteres invisíveis nos Secrets.
    url = url.strip().strip('"').strip("'")
    key = key.strip().strip('"').strip("'")

    if not url:
        raise RuntimeError("SUPABASE_URL não configurada.")
    if not key:
        raise RuntimeError(
            "SUPABASE_KEY não configurada. No Streamlit Cloud, adicione "
            "SUPABASE_URL e SUPABASE_KEY em Settings > Secrets."
        )

    if not url.startswith("https://"):
        raise RuntimeError("SUPABASE_URL inválida: use a URL https://...supabase.co")

    try:
        return create_client(url, key)
    except UnicodeEncodeError as exc:
        raise RuntimeError(
            "Não foi possível inicializar o cliente Supabase. "
            "Verifique se SUPABASE_URL e SUPABASE_KEY foram coladas sem "
            "caracteres especiais/ocultos. Também recomendamos Python 3.13 "
            "no Streamlit Community Cloud."
        ) from exc


def select_rows(
    table: str,
    *,
    limit: int = 500,
    order_by: str | None = None,
) -> list[dict[str, Any]]:
    client = get_client()
    query = client.table(table).select("*")
    if order_by:
        query = query.order(order_by, desc=True)
    response = query.limit(limit).execute()
    return response.data or []


def select_one(
    table: str,
    row_id: Any,
    *,
    id_column: str = "id",
) -> dict[str, Any] | None:
    client = get_client()
    response = client.table(table).select("*").eq(id_column, row_id).limit(1).execute()
    rows = response.data or []
    return rows[0] if rows else None
