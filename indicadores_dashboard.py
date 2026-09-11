from __future__ import annotations

import html
import pandas as pd
import streamlit as st


def _pct(v):
    try:
        return f"{float(v):.2f}%".replace('.', ',')
    except Exception:
        return "—"


def _pct_diff(v):
    try:
        n = float(v)
        return f"{n:+.2f}%".replace('.', ',')
    except Exception:
        return "—"


def _safe(v):
    return html.escape(str(v))


def _month_label(value):
    d = pd.to_datetime(value, errors="coerce")
    if pd.isna(d):
        return _safe(value or "—")
    meses = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]
    return f"{meses[d.month-1]}/{d.year}"


def _prepare_rows(rows, view):
    ordered = sorted(rows, key=lambda r: pd.to_datetime(r.get("competencia"), errors="coerce"))
    if view != "month" or not ordered:
        return ordered
    df = pd.DataFrame(ordered)
    df["_date"] = pd.to_datetime(df["competencia"], errors="coerce")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df["meta"] = pd.to_numeric(df["meta"], errors="coerce")
    df = df.dropna(subset=["_date"])
    if df.empty:
        return ordered
    df["_periodo"] = df["_date"].dt.to_period("M")
    grouped = df.groupby("_periodo", sort=True).agg(valor=("valor", "mean"), meta=("meta", "mean")).reset_index()
    return [
        {"competencia": row["_periodo"].to_timestamp(), "valor": row["valor"], "meta": row["meta"]}
        for _, row in grouped.iterrows()
    ]


def _kpis(rows, selected_index=None):
    ordered = rows or []
    if not ordered:
        valor = meta = diff = None
        status = "Sem histórico"
        status_cls = "neutral"
        selected_label = "Nenhum lançamento"
    else:
        idx = selected_index if selected_index is not None and 0 <= selected_index < len(ordered) else len(ordered) - 1
        selected = ordered[idx]
        valor = float(selected.get("valor")) if selected.get("valor") is not None else None
        meta = float(selected.get("meta")) if selected.get("meta") is not None else None
        diff = valor - meta if valor is not None and meta is not None else None
        status = "Acima da meta" if diff is not None and diff >= 0 else ("Abaixo da meta" if diff is not None else "Sem meta")
        status_cls = "ok" if diff is not None and diff >= 0 else ("bad" if diff is not None else "neutral")
        selected_label = _month_label(selected.get("competencia"))
    return f'''<div class="ind-kpis">
      <div class="ind-kpi"><div class="ind-kpi-label">RESULTADO SELECIONADO</div><div class="ind-kpi-value">{_pct(valor)}</div><div class="ind-kpi-sub">{selected_label}</div></div>
      <div class="ind-kpi"><div class="ind-kpi-label">META</div><div class="ind-kpi-value">{_pct(meta) if meta is not None else '—'}</div><div class="ind-kpi-sub">Referência do lançamento</div></div>
      <div class="ind-kpi"><div class="ind-kpi-label">DIFERENÇA</div><div class="ind-kpi-value">{_pct_diff(diff) if diff is not None else '—'}</div><div class="ind-kpi-sub">Resultado − meta</div></div>
      <div class="ind-kpi ind-status {status_cls}"><div class="ind-status-arrow">{'↑' if status_cls=='ok' else ('↓' if status_cls=='bad' else '—')}</div><div><div class="ind-kpi-label">STATUS</div><div class="ind-status-text">{status}</div><div class="ind-kpi-sub">{selected_label}</div></div></div>
    </div>'''


def _chart(rows, title, chart_key):
    if not rows:
        st.markdown('<div class="ind-empty">Nenhum lançamento histórico.</div>', unsafe_allow_html=True)
        return None

    try:
        import plotly.graph_objects as go
    except Exception:
        st.error("Não foi possível carregar o componente gráfico.")
        return None

    labels = [_month_label(r.get("competencia")) for r in rows]
    values = [float(r.get("valor") or 0) for r in rows]
    metas = [float(r.get("meta") or 0) for r in rows]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(range(len(rows))),
        y=values,
        name="Resultado",
        marker=dict(color="#ffd43d", line=dict(color="#ffd43d", width=0)),
        text=[_pct(v) for v in values],
        textposition="outside",
        textfont=dict(color="#f4f5f4", size=10),
        customdata=[[labels[i], metas[i]] for i in range(len(rows))],
        hovertemplate="%{customdata[0]}<br>Resultado: %{y:.2f}%<br>Meta: %{customdata[1]:.2f}%<extra>Clique para selecionar</extra>",
        cliponaxis=False,
        selected=dict(marker=dict(opacity=1, line=dict(color="#ffffff", width=2))),
        unselected=dict(marker=dict(opacity=.72)),
    ))
    fig.add_trace(go.Scatter(
        x=list(range(len(rows))), y=metas, name="Meta", mode="lines+markers",
        line=dict(color="#f4f5f4", width=3), marker=dict(color="#f4f5f4", size=5),
        hovertemplate="%{customdata[0]}<br>Meta: %{y:.2f}%<extra></extra>",
        customdata=[[labels[i]] for i in range(len(rows))],
    ))
    fig.update_layout(
        height=285,
        margin=dict(l=35, r=15, t=28, b=45),
        paper_bgcolor="#0b100e", plot_bgcolor="#0b100e",
        font=dict(color="#b5bcb8", size=10),
        hoverlabel=dict(bgcolor="#111714", font_color="#f4f5f4"),
        bargap=0.28, showlegend=False, clickmode="event+select",
        xaxis=dict(tickmode="array", tickvals=list(range(len(rows))), ticktext=labels,
                   showgrid=False, zeroline=False, fixedrange=True, tickfont=dict(size=9)),
        yaxis=dict(range=[0, 105], tickmode="array", tickvals=[0,20,40,60,80,100],
                   ticksuffix="%", gridcolor="#25302b", zeroline=False, fixedrange=True),
        dragmode=False,
    )
    event = st.plotly_chart(
        fig, use_container_width=True, key=chart_key,
        on_select="rerun", selection_mode="points",
        config={"displayModeBar": False, "responsive": True, "scrollZoom": False, "doubleClick": False},
    )
    if event is not None:
        try:
            points = event.selection.point_indices
            if points:
                return int(points[0])
        except Exception:
            pass
    return None


def _render_indicator(name, rows, index):
    state_key = f"ind_view_{index}"
    selected_key = f"ind_selected_{index}"
    if state_key not in st.session_state:
        st.session_state[state_key] = "all"
    if selected_key not in st.session_state:
        st.session_state[selected_key] = None

    view = st.session_state[state_key]
    chart_rows = _prepare_rows(rows, view)
    if not chart_rows:
        st.session_state[selected_key] = None

    # Um único container Streamlit envolve título, controles, banners e gráfico.
    # Assim os controles pertencem visualmente ao indicador e não ficam soltos no Dashboard.
    with st.container(border=True):
        st.markdown(f'<div class="ind-section-title">{index:02d} · {_safe(name)}</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1.25, 1.25, 5], gap="small")
        with c1:
            if st.button("TOTAL DE LANÇAMENTOS", key=f"ind_all_{index}", use_container_width=True,
                         type="primary" if view == "all" else "secondary"):
                st.session_state[state_key] = "all"
                st.session_state[selected_key] = None
                st.rerun()
        with c2:
            if st.button("AGRUPADO MÊS A MÊS", key=f"ind_month_{index}", use_container_width=True,
                         type="primary" if view == "month" else "secondary"):
                st.session_state[state_key] = "month"
                st.session_state[selected_key] = None
                st.rerun()

        selected_index = st.session_state.get(selected_key)
        if selected_index is not None and selected_index >= len(chart_rows):
            selected_index = None
            st.session_state[selected_key] = None

        st.markdown(_kpis(chart_rows, selected_index), unsafe_allow_html=True)
        st.markdown('''<div class="ind-chart-panel">
          <div class="ind-chart-head"><div><div class="ind-chart-title">Comparativo histórico</div>
          <div class="ind-legend"><span><i class="ind-dot result"></i>Resultado</span>
          <span><i class="ind-dot target"></i>Meta</span></div></div></div>''', unsafe_allow_html=True)
        clicked = _chart(chart_rows, name, f"ind_chart_{index}_{view}")
        st.markdown('</div>', unsafe_allow_html=True)

        if clicked is not None:
            st.session_state[selected_key] = clicked
            st.rerun()


def render_indicadores(indicadores):
    groups = {"ACURÁCIA DE ESTOQUE": [], "ENTREGAS NO PRAZO": [], "5S": []}
    aliases = {
        "ACURACIDADE DE ESTOQUE": "ACURÁCIA DE ESTOQUE",
        "ACURÁCIDADE DE ESTOQUE": "ACURÁCIA DE ESTOQUE",
        "ACURÁCIA DE ESTOQUE": "ACURÁCIA DE ESTOQUE",
        "ACURACIA DE ESTOQUE": "ACURÁCIA DE ESTOQUE",
        "ENTREGAS NO PRAZO": "ENTREGAS NO PRAZO",
        "5S": "5S",
    }
    for row in indicadores or []:
        key = aliases.get(str(row.get("indicador") or "").strip().upper())
        if key in groups:
            groups[key].append(row)

    st.markdown('''<style>
    .ind-page-title{font-size:22px;font-weight:900;color:#f4f5f4;text-transform:uppercase;letter-spacing:.4px;margin:2px 0 3px}
    .ind-page-sub{font-size:12px;color:#9aa39f;margin-bottom:18px}
    .ind-section-title{font-size:16px;font-weight:900;color:#ffd43d;text-transform:uppercase;letter-spacing:.5px;margin:0 0 8px;padding:0 2px}
    .ind-kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:9px;margin:0 0 9px}
    .ind-kpi{position:relative;min-height:78px;border:1px solid #304039;border-radius:11px;background:linear-gradient(145deg,#151b18,#0d1110);padding:12px 14px;box-sizing:border-box;overflow:hidden}
    .ind-kpi:after{content:"";position:absolute;width:68px;height:68px;border-radius:50%;right:-25px;bottom:-34px;background:rgba(255,212,61,.06)}
    .ind-kpi-label{font-size:9px;font-weight:900;color:#a8b0ac;letter-spacing:.5px;text-transform:uppercase}
    .ind-kpi-value{font-size:25px;line-height:1.05;font-weight:900;color:#f4f5f4;margin-top:7px}
    .ind-kpi-sub{font-size:9px;color:#8c9691;margin-top:4px}
    .ind-status{display:flex;align-items:center;gap:10px}.ind-status:after{background:rgba(34,197,94,.08)}
    .ind-status.bad:after{background:rgba(255,77,79,.08)}.ind-status.neutral:after{background:rgba(140,150,145,.06)}
    .ind-status-arrow{width:38px;height:38px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:rgba(34,197,94,.12);color:#4ade80;font-size:23px;font-weight:900;flex:0 0 38px}
    .ind-status.bad .ind-status-arrow{background:rgba(255,77,79,.12);color:#ff6668}.ind-status.neutral .ind-status-arrow{background:rgba(140,150,145,.12);color:#aab2ae}
    .ind-status-text{font-size:14px;font-weight:900;color:#4ade80;margin-top:4px}.ind-status.bad .ind-status-text{color:#ff6668}.ind-status.neutral .ind-status-text{color:#aab2ae}
    .ind-chart-panel{border:1px solid #26342e;border-radius:11px;background:#0b100e;padding:12px 10px 7px;margin-bottom:0}
    .ind-chart-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;border-bottom:1px solid #202a26;padding:0 1px 9px;margin-bottom:0}
    .ind-chart-title{font-size:13px;font-weight:900;color:#f4f5f4}.ind-legend{display:flex;gap:15px;margin-top:7px;font-size:9px;color:#9ba49f}.ind-legend span{display:flex;align-items:center;gap:5px}.ind-dot{display:inline-block;width:15px;height:4px;border-radius:4px}.ind-dot.result{background:#ffd43d}.ind-dot.target{background:#f4f5f4}
    .ind-empty{height:150px;display:flex;align-items:center;justify-content:center;color:#7f8a85;font-size:11px;border:1px solid #26342e;border-radius:11px;background:#0b100e;margin-bottom:0}
    div[data-testid="stPlotlyChart"]{margin-top:-2px!important;margin-bottom:-4px!important}
    div[data-testid="stVerticalBlockBorderWrapper"]{border-color:#34413b!important;background:linear-gradient(145deg,#101513,#0b0f0e)!important;border-radius:16px!important}
    @media(max-width:900px){.ind-kpis{grid-template-columns:repeat(2,minmax(0,1fr))}}
    </style>''', unsafe_allow_html=True)

    st.markdown('<div class="ind-page-title">INDICADORES OPERACIONAIS</div><div class="ind-page-sub">Acompanhamento dos principais indicadores do almoxarifado.</div>', unsafe_allow_html=True)
    for i, (name, rows) in enumerate(groups.items(), 1):
        _render_indicator(name, rows, i)
