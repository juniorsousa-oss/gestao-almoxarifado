from __future__ import annotations
from datetime import date
import pandas as pd
import streamlit as st
from supabase_client import get_client

st.set_page_config(page_title="GESTÃO OPERACIONAL | SETTA", page_icon="assets/mrp_setta_icon.png", layout="wide")
st.markdown("""
<style>
#MainMenu,footer,header{visibility:hidden}
.stApp{background:#0b0f0e;color:#f4f5f4}
[data-testid="stSidebar"]{background:#090c0b;border-right:1px solid #252b28;min-width:230px;max-width:230px}
[data-testid="stSidebar"] > div:first-child{padding:18px 9px 20px}
.block-container{max-width:1500px;padding:28px 34px 50px}
.brand{font-size:28px;font-weight:900;padding:8px 4px 20px;border-bottom:1px solid #1e2522;margin-bottom:18px}.brand span,.section{color:#ffd20a}.hero{display:flex;justify-content:space-between;align-items:center;margin-bottom:24px}.hero h1{margin:0;font-size:30px}.hero p,.muted{color:#9aa39f}.period{background:#ffd20a;color:#111;padding:10px 15px;border-radius:9px;font-weight:800}.section{font-size:14px;font-weight:900;letter-spacing:1px;text-transform:uppercase;margin:22px 0 10px}.panel{background:linear-gradient(145deg,#141a17,#101513);border:1px solid #35403b;border-radius:15px;padding:19px;margin-top:14px}.notice{padding:12px 14px;border-left:3px solid #ffd20a;background:#171d1a;color:#c7ceca;border-radius:7px;font-size:11px}div[data-testid="stMetric"]{background:linear-gradient(145deg,#141a17,#101513);border:1px solid #35403b;padding:15px;border-radius:12px}

/* MENU LATERAL */
[data-testid="stSidebar"] .stButton{margin:0 0 7px 0}
[data-testid="stSidebar"] .stButton > button{width:100%;min-height:47px;border-radius:12px;border:1px solid transparent;background:transparent;color:#f0f2f1;font-size:14px;font-weight:900;text-align:left;padding:0 14px;box-shadow:none;transition:all .15s ease}
[data-testid="stSidebar"] .stButton > button:hover{background:#171c1a;border-color:#303733;color:#ffffff}
[data-testid="stSidebar"] .stButton > button[kind="primary"]{background:#ffd43d;color:#0b0f0e;border:2px solid #f4f5f4;box-shadow:0 0 0 1px #ffd43d inset}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover{background:#ffd43d;color:#0b0f0e}
[data-testid="stSidebar"] .stButton > button p{font-size:14px;font-weight:900;letter-spacing:.15px}
.sidebar-footer{margin:22px 5px 0;padding-top:16px;border-top:1px solid #1e2522;color:#69736e;font-size:10px;line-height:1.6}
</style>
""",unsafe_allow_html=True)

@st.cache_data(ttl=30)
def rows(table, limit=500, order=None):
    q=get_client().table(table).select("*")
    if order:q=q.order(order,desc=True)
    return q.limit(limit).execute().data or []

def df(data): return pd.DataFrame(data) if data else pd.DataFrame()

if "pagina" not in st.session_state: st.session_state.pagina="Dashboard"
paginas=[("▦","Dashboard"),("✎","Alimentar Indicadores"),("◷","Histórico"),("♟","Gestão de Equipes"),("⇧","Plano de Carreira"),("⚙","Configurações")]

with st.sidebar:
    st.markdown('<div class="brand">GESTÃO<span>.</span></div>',unsafe_allow_html=True)
    for icone,p in paginas:
        ativo=st.session_state.pagina==p
        label=f"{icone}    {p.upper()}"
        if st.button(label,use_container_width=True,type="primary" if ativo else "secondary",key=f"menu_{p}"):
            st.session_state.pagina=p
            st.rerun()
    st.markdown("<div class='sidebar-footer'>Gestão Operacional<br>SETTA • Streamlit + Supabase</div>",unsafe_allow_html=True)

pagina=st.session_state.pagina
st.markdown(f'<div class="hero"><div><h1>{pagina}</h1><p>Gestão operacional do almoxarifado</p></div><div class="period">{date.today().strftime("%d/%m/%Y")}</div></div>',unsafe_allow_html=True)
try:
    get_client(); conectado=True
except Exception:
    conectado=False
if not conectado:
    st.error("Supabase ainda não está configurado no ambiente do Streamlit.")
    st.markdown('<div class="notice">Configure <b>SUPABASE_URL</b> e <b>SUPABASE_KEY</b> em Settings → Secrets do Streamlit Cloud. A chave não é armazenada no GitHub.</div>',unsafe_allow_html=True)
    st.stop()

if pagina=="Dashboard":
    indicadores=rows("almox_indicadores",order="competencia"); colaboradores=rows("almox_colaboradores"); equipes=rows("almox_equipes"); historico=rows("almox_historico",order="criado_em"); snapshots=rows("mrp_snapshots",order="created_at")
    st.markdown('<div class="section">Dados reais do Supabase</div>',unsafe_allow_html=True)
    a,b,c,d=st.columns(4);a.metric("Indicadores",len(indicadores));b.metric("Colaboradores",len(colaboradores));c.metric("Equipes",len(equipes));d.metric("MRP salvos",len(snapshots))
    if indicadores:
        data=df(indicadores)
        st.markdown('<div class="section">Indicadores</div>',unsafe_allow_html=True)
        if "competencia" in data.columns and "valor" in data.columns:
            data["competencia"]=pd.to_datetime(data["competencia"],errors="coerce")
            chart=data.dropna(subset=["competencia"]).pivot_table(index="competencia",columns="indicador",values="valor",aggfunc="last")
            if not chart.empty: st.line_chart(chart)
        st.dataframe(data,use_container_width=True,hide_index=True)
    else: st.info("A tabela almox_indicadores está conectada, mas ainda não possui lançamentos.")
    with st.expander("Diagnóstico"):
        st.write({"Supabase":"conectado","indicadores":len(indicadores),"colaboradores":len(colaboradores),"equipes":len(equipes),"histórico":len(historico),"MRP":len(snapshots)})

elif pagina=="Alimentar Indicadores":
    st.markdown('<div class="notice">Consulta do banco real habilitada. A gravação será liberada junto com autenticação adequada.</div>',unsafe_allow_html=True)
    st.dataframe(df(rows("almox_indicadores",order="competencia")),use_container_width=True,hide_index=True)

elif pagina=="Histórico":
    st.markdown('<div class="section">Histórico real</div>',unsafe_allow_html=True)
    st.dataframe(df(rows("almox_historico",order="criado_em")),use_container_width=True,hide_index=True)

elif pagina=="Gestão de Equipes":
    colaboradores=df(rows("almox_colaboradores"));equipes=df(rows("almox_equipes"));org=df(rows("almox_organograma"))
    a,b,c=st.columns(3);a.metric("Colaboradores",len(colaboradores));b.metric("Equipes",len(equipes));c.metric("Nós do organograma",len(org))
    st.markdown('<div class="section">Colaboradores</div>',unsafe_allow_html=True);st.dataframe(colaboradores,use_container_width=True,hide_index=True)
    st.markdown('<div class="section">Equipes</div>',unsafe_allow_html=True);st.dataframe(equipes,use_container_width=True,hide_index=True)
    st.markdown('<div class="section">Organograma</div>',unsafe_allow_html=True);st.dataframe(org,use_container_width=True,hide_index=True)

elif pagina=="Plano de Carreira":
    st.markdown('<div class="section">Base real de colaboradores</div>',unsafe_allow_html=True);st.dataframe(df(rows("almox_colaboradores")),use_container_width=True,hide_index=True)
    st.info("A lógica específica do Plano de Carreira será migrada na próxima camada.")
else:
    st.markdown('<div class="section">Configurações</div>',unsafe_allow_html=True);st.success("Supabase conectado.");st.write("Projeto: cuixazpxkvniqldmmnth");st.write("As credenciais devem permanecer nos Secrets do Streamlit.")

st.markdown("<br><div class='muted'>Gestão Almoxarifado • Streamlit + Supabase • migração em andamento</div>",unsafe_allow_html=True)