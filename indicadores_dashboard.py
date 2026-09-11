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
    if view != "month":
        return ordered
    if not ordered:
        return []
    df = pd.DataFrame(ordered)
    df["_date"] = pd.to_datetime(df["competencia"], errors="coerce")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df["meta"] = pd.to_numeric(df["meta"], errors="coerce")
    df = df.dropna(subset=["_date"])
    if df.empty:
        return ordered
    df["_periodo"] = df["_date"].dt.to_period("M")
    grouped = df.groupby("_periodo", sort=True).agg(valor=("valor", "mean"), meta=("meta", "mean")).reset_index()
    result = []
    for _, row in grouped.iterrows():
        result.append({"competencia": row["_periodo"].to_timestamp(), "valor": row["valor"], "meta": row["meta"]})
    return result


def _chart(rows, title):
    if not rows:
        return '<div class="ind-empty">Nenhum lançamento histórico.</div>'
    values = [float(r.get("valor") or 0) for r in rows]
    metas = [float(r.get("meta") or 0) for r in rows if r.get("meta") is not None]
    maxv = max([100.0] + values + metas)
    bars = []
    for r in rows:
        valor = float(r.get("valor") or 0)
        meta = float(r.get("meta") or 0)
        h = max(3, min(100, valor / maxv * 100))
        meta_pos = max(2, min(98, meta / maxv * 100))
        date_txt = _month_label(r.get("competencia")) if len(rows) != 1 else _month_label(r.get("competencia"))
        bars.append(f'''<div class="ind-bar-item">
          <div class="ind-bar-value" style="bottom:{h:.2f}%">{_pct(valor)}</div>
          <div class="ind-bar-track"><div class="ind-bar" style="height:{h:.2f}%"></div><div class="ind-meta-line" style="bottom:{meta_pos:.2f}%"><span>{_pct(meta)}</span></div></div>
          <div class="ind-bar-date">{date_txt}</div>
        </div>''')
    n = len(rows)
    return f'''<div class="ind-chart-scroll"><div class="ind-chart" style="--ind-n:{n}">
      <div class="ind-grid"><span>100%</span><span>80%</span><span>60%</span><span>40%</span><span>20%</span><span>0%</span></div>
      <div class="ind-bars">{"".join(bars)}</div>
    </div></div>'''


def _indicator_card(name, rows, index, view):
    ordered = sorted(rows, key=lambda r: pd.to_datetime(r.get("competencia"), errors="coerce"))
    latest = ordered[-1] if ordered else {}
    valor = float(latest.get("valor") or 0) if latest else 0
    meta = float(latest.get("meta")) if latest.get("meta") is not None else None
    diff = valor - meta if meta is not None else None
    status = "Acima da meta" if diff is not None and diff >= 0 else ("Abaixo da meta" if diff is not None else "Sem histórico")
    status_cls = "ok" if diff is not None and diff >= 0 else ("bad" if diff is not None else "neutral")
    title_num = f"{index:02d}"
    cards = f'''<div class="ind-kpis">
      <div class="ind-kpi"><div class="ind-kpi-label">ÚLTIMO RESULTADO</div><div class="ind-kpi-value">{_pct(valor) if ordered else '—'}</div><div class="ind-kpi-sub">Último lançamento</div></div>
      <div class="ind-kpi"><div class="ind-kpi-label">META ATUAL</div><div class="ind-kpi-value">{_pct(meta) if meta is not None else '—'}</div><div class="ind-kpi-sub">Meta do último lançamento</div></div>
      <div class="ind-kpi"><div class="ind-kpi-label">DIFERENÇA</div><div class="ind-kpi-value">{_pct_diff(diff) if diff is not None else '—'}</div><div class="ind-kpi-sub">Resultado − meta</div></div>
      <div class="ind-kpi ind-status {status_cls}"><div class="ind-status-arrow">{'↑' if status_cls=='ok' else ('↓' if status_cls=='bad' else '—')}</div><div><div class="ind-kpi-label">STATUS</div><div class="ind-status-text">{status}</div><div class="ind-kpi-sub">{len(rows)} lançamento(s) histórico(s)</div></div></div>
    </div>'''
    chart_rows = _prepare_rows(rows, view)
    return f'''<section class="ind-section">
      <div class="ind-section-title">{title_num} · {_safe(name)}</div>
      {cards}
      <div class="ind-chart-panel">
        <div class="ind-chart-head"><div><div class="ind-chart-title">Comparativo histórico</div><div class="ind-legend"><span><i class="ind-dot result"></i>Resultado</span><span><i class="ind-dot target"></i>Meta</span></div></div></div>
        {_chart(chart_rows, name)}
      </div>
    </section>'''


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
    .ind-section{background:linear-gradient(145deg,#101513,#0b0f0e);border:1px solid #34413b;border-radius:16px;padding:10px 10px 12px;margin:0 0 14px;overflow:hidden}
    .ind-section-title{font-size:16px;font-weight:900;color:#ffd43d;text-transform:uppercase;letter-spacing:.5px;margin:0 0 10px;padding:0 2px}
    .ind-kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:9px;margin-bottom:9px}
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
    .ind-chart-panel{border:1px solid #26342e;border-radius:11px;background:#0b100e;padding:12px 10px 7px}
    .ind-chart-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;border-bottom:1px solid #202a26;padding:0 1px 9px;margin-bottom:5px}
    .ind-chart-title{font-size:13px;font-weight:900;color:#f4f5f4}.ind-legend{display:flex;gap:15px;margin-top:7px;font-size:9px;color:#9ba49f}.ind-legend span{display:flex;align-items:center;gap:5px}.ind-dot{display:inline-block;width:15px;height:4px;border-radius:4px}.ind-dot.result{background:#ffd43d}.ind-dot.target{background:#f4f5f4}
    .ind-chart-scroll{overflow-x:auto;overflow-y:hidden;padding-bottom:2px}.ind-chart{position:relative;min-width:max(100%,calc(var(--ind-n) * 82px + 55px));height:205px;padding:13px 6px 0 36px;box-sizing:border-box}
    .ind-grid{position:absolute;left:36px;right:6px;top:13px;bottom:30px;display:flex;flex-direction:column;justify-content:space-between;pointer-events:none}.ind-grid:after{content:"";position:absolute;inset:0;background:repeating-linear-gradient(to bottom,transparent 0,transparent calc(20% - 1px),#25302b calc(20% - 1px),#25302b 20%)}.ind-grid span{font-size:8px;color:#68736e;position:relative;z-index:2;transform:translateX(-30px)}
    .ind-bars{position:absolute;left:50px;right:10px;top:13px;bottom:30px;display:flex;align-items:flex-end;justify-content:space-around;gap:17px}.ind-bar-item{height:100%;flex:0 0 50px;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;position:relative}.ind-bar-track{height:100%;width:44px;position:relative;display:flex;align-items:flex-end}.ind-bar{width:44px;background:linear-gradient(180deg,#ffd84d,#f7ca2c);border-radius:7px 7px 0 0;box-shadow:0 0 16px rgba(255,212,61,.12)}.ind-bar-value{position:absolute;font-size:8px;font-weight:900;color:#f4f5f4;white-space:nowrap;z-index:5;transform:translateY(-100%)}
    .ind-meta-line{position:absolute;left:-7px;right:-7px;height:3px;background:#f4f5f4;border-radius:5px;box-shadow:0 0 7px rgba(255,255,255,.55);z-index:4}.ind-meta-line span{position:absolute;left:50%;transform:translate(-50%,3px);background:#f4f5f4;color:#111;border-radius:3px;padding:2px 4px;font-size:7px;font-weight:900;white-space:nowrap}
    .ind-bar-date{font-size:8px;color:#b5bcb8;font-weight:900;margin-top:6px;white-space:nowrap}.ind-empty{height:150px;display:flex;align-items:center;justify-content:center;color:#7f8a85;font-size:11px}
    @media(max-width:900px){.ind-kpis{grid-template-columns:repeat(2,minmax(0,1fr))}}
    </style>''', unsafe_allow_html=True)

    st.markdown('<div class="ind-page-title">INDICADORES OPERACIONAIS</div><div class="ind-page-sub">Acompanhamento dos principais indicadores do almoxarifado.</div>', unsafe_allow_html=True)
    for i, (name, rows) in enumerate(groups.items(), 1):
        state_key = f"ind_view_{i}"
        if state_key not in st.session_state:
            st.session_state[state_key] = "all"
        c1, c2, c3 = st.columns([1, 1, 5])
        with c1:
            if st.button("TOTAL DE LANÇAMENTOS", key=f"ind_all_{i}", use_container_width=True, type="primary" if st.session_state[state_key] == "all" else "secondary"):
                st.session_state[state_key] = "all"
                st.rerun()
        with c2:
            if st.button("AGRUPADO MÊS A MÊS", key=f"ind_month_{i}", use_container_width=True, type="primary" if st.session_state[state_key] == "month" else "secondary"):
                st.session_state[state_key] = "month"
                st.rerun()
        with c3:
            pass
        st.markdown(_indicator_card(name, rows, i, st.session_state[state_key]), unsafe_allow_html=True)
