from __future__ import annotations
from datetime import date
import pandas as pd
import streamlit as st
from supabase_client import get_client

st.set_page_config(page_title="GESTÃO OPERACIONAL | SETTA", page_icon="assets/mrp_setta_icon.png", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
#MainMenu,footer{visibility:hidden}
.stApp{background:#0b0f0e;color:#f4f5f4}
[data-testid="stSidebar"]{background:#090c0b !important;border-right:1px solid #252b28;min-width:230px;max-width:230px}
[data-testid="stSidebar"] > div:first-child{padding:18px 9px 20px}
.block-container{max-width:1500px;padding:28px 34px 50px}
.hero{display:flex;justify-content:space-between;align-items:center;margin-bottom:24px}.hero h1{margin:0;font-size:30px}.hero p,.muted{color:#9aa39f}.period{background:#ffd20a;color:#111;padding:10px 15px;border-radius:9px;font-weight:800}.section{color:#ffd20a;font-size:14px;font-weight:900;letter-spacing:1px;text-transform:uppercase;margin:22px 0 10px}.panel{background:linear-gradient(145deg,#141a17,#101513);border:1px solid #35403b;border-radius:15px;padding:22px;margin-top:14px}.notice{padding:12px 14px;border-left:3px solid #ffd20a;background:#171d1a;color:#c7ceca;border-radius:7px;font-size:11px}div[data-testid="stMetric"]{background:linear-gradient(145deg,#141a17,#101513);border:1px solid #35403b;padding:15px;border-radius:12px}

/* MENU LATERAL */
[data-testid="stSidebar"] .stButton{margin:0 0 10px 0}
[data-testid="stSidebar"] .stButton > button{width:100%;min-height:48px;height:48px;border-radius:12px;border:1px solid #2d3531;background:#101513;color:#f4f5f4 !important;font-size:14px;font-weight:900;text-align:center;padding:0 10px;box-shadow:none;transition:all .15s ease}
[data-testid="stSidebar"] .stButton > button:hover{background:#171c1a;border-color:#46504b;color:#ffffff !important}
[data-testid="stSidebar"] .stButton > button[kind="primary"]{background:#ffd43d !important;color:#0b0f0e !important;border:2px solid #f4f5f4;box-shadow:0 0 0 1px #ffd43d inset}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover{background:#ffd43d !important;color:#0b0f0e !important}
[data-testid="stSidebar"] .stButton > button p{font-size:14px;font-weight:900;letter-spacing:.15px;color:inherit !important;text-align:center !important;width:100%}
[data-testid="stSidebar"] .stButton > button div{justify-content:center !important}

/* LOGO */
.sidebar-logo-wrap{width:100%;display:flex;justify-content:center;align-items:center;min-height:112px;margin:0 0 18px;padding:6px 0 18px;border-bottom:1px solid #1e2522}
.sidebar-logo-img{max-width:190px;max-height:90px;width:auto;height:auto;object-fit:contain}
.sidebar-logo-placeholder{width:190px;height:90px;border:1px dashed #46504b;border-radius:10px;display:flex;align-items:center;justify-content:center;text-align:center;color:#69736e;font-size:11px;line-height:1.4}
.sidebar-footer{margin:22px 5px 0;padding-top:16px;border-top:1px solid #1e2522;color:#69736e;font-size:10px;line-height:1.6}

/* CONFIGURAÇÕES */
.settings-tabs{display:flex;width:100%;border:1px solid #2d3531;border-radius:10px;overflow:hidden;margin:22px 0}
.logo-preview{min-height:250px;border:1px solid #35403b;border-radius:12px;background:#101513;display:flex;align-items:center;justify-content:center;padding:20px}
.logo-preview img{max-width:100%;max-height:210px;object-fit:contain}
.tip{background:#101b27;border:1px solid #284a68;border-radius:10px;padding:15px;color:#b8c8d8;margin-top:18px;font-size:13px;line-height:1.6}
</style>
""",unsafe_allow_html=True)

@st.cache_data(ttl=30)
def rows(table, limit=500, order=None):
    q=get_client().table(table).select("*")
    if order:q=q.order(order,desc=True)
    return q.limit(limit).execute().data or []

def df(data): return pd.DataFrame(data) if data else pd.DataFrame()

if "pagina" not in st.session_state: st.session_state.pagina="Dashboard"
if "logo_bytes" not in st.session_state: st.session_state.logo_bytes=None
if "logo_name" not in st.session_state: st.session_state.logo_name=None

paginas=["Dashboard","Alimentar Indicadores","Histórico","Gestão de Equipes","Plano de Carreira","Configurações"]

with st.sidebar:
    if st.session_state.logo_bytes:
        st.markdown('<div class="sidebar-logo-wrap"><img class="sidebar-logo-img" src="data:image/png;base64,' + __import__('base64').b64encode(st.session_state.logo_bytes).decode() + '"></div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="sidebar-logo-wrap"><div class="sidebar-logo-placeholder">SUA LOGO AQUI<br><br>Configure em<br>Configurações</div></div>',unsafe_allow_html=True)
    for p in paginas:
        ativo=st.session_state.pagina==p
        if st.button(p.upper(),use_container_width=True,type="primary" if ativo else "secondary",key=f"menu_{p}"):
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
    st.markdown('<div class="section">Configurações gerais</div>',unsafe_allow_html=True)
    st.markdown('<div class="panel">',unsafe_allow_html=True)
    st.subheader("Logo da Empresa")
    st.write("Defina a imagem que será exibida no menu lateral do sistema.")
    esquerda,direita=st.columns(2)
    with esquerda:
        st.markdown("**Imagem atual**")
        if st.session_state.logo_bytes:
            st.image(st.session_state.logo_bytes,use_container_width=True)
            st.caption(st.session_state.logo_name or "Logo configurada")
        else:
            st.markdown('<div class="logo-preview"><div style="text-align:center;color:#69736e;font-size:14px">Nenhuma imagem configurada<br><br>A logo será exibida no menu lateral</div></div>',unsafe_allow_html=True)
    with direita:
        st.markdown("**Selecionar nova imagem**")
        arquivo=st.file_uploader("Arraste e solte um arquivo aqui ou clique para selecionar",type=["png","jpg","jpeg","svg"],key="logo_uploader",label_visibility="visible")
        if arquivo is not None:
            if arquivo.size>2*1024*1024:
                st.error("A imagem deve ter no máximo 2 MB.")
            else:
                st.image(arquivo,use_container_width=True)
                if st.button("SALVAR LOGO",use_container_width=True,type="primary",key="salvar_logo"):
                    st.session_state.logo_bytes=arquivo.getvalue()
                    st.session_state.logo_name=arquivo.name
                    st.success("Logo atualizada no menu lateral.")
                    st.rerun()
    st.markdown('</div>',unsafe_allow_html=True)
    st.markdown('<div class="tip"><b>Dicas</b><br>• Utilize preferencialmente PNG com fundo transparente.<br>• Tamanho recomendado: aproximadamente 200 × 80 pixels.<br>• A imagem será ajustada automaticamente para caber no menu lateral.<br>• Para melhor resultado, utilize uma logo em formato horizontal.</div>',unsafe_allow_html=True)

    st.markdown('<div class="panel">',unsafe_allow_html=True)
    st.subheader("Outras configurações")
    st.write("Ajustes gerais do sistema serão adicionados nesta área.")
    st.selectbox("Tema do sistema",["Escuro (Padrão)"],disabled=True)
    st.markdown('</div>',unsafe_allow_html=True)

st.markdown("<br><div class='muted'>Gestão Almoxarifado • Streamlit + Supabase • migração em andamento</div>",unsafe_allow_html=True)