from __future__ import annotations
from datetime import date
import base64
import pandas as pd
import streamlit as st
from supabase_client import get_client

st.set_page_config(page_title="GESTÃO OPERACIONAL | SETTA", page_icon="assets/mrp_setta_icon.png", layout="wide", initial_sidebar_state="expanded")

DEFAULT_CONFIG = {
    "tema": "Escuro (Padrão)",
    "cor_principal": "Amarelo (Padrão)",
    "estilo_botoes": "Amarelo",
    "logo_base64": None,
    "logo_name": None,
    "logo_mime": None,
}

CORES = {
    "Amarelo (Padrão)": "#ffd43d", "Azul": "#1683ff", "Verde": "#22c55e",
    "Vermelho": "#ff4d4f", "Roxo": "#8b5cf6", "Laranja": "#ff922b",
    "Ciano": "#22c7d6", "Rosa": "#ec4899", "Lima": "#a3e635",
}
TEMAS = ["Escuro (Padrão)", "Claro", "Automático"]
ESTILOS_BOTOES = ["Amarelo", "Colorido"]


def carregar_configuracoes():
    try:
        resultado = get_client().table("almox_app_state").select("estado").eq("id", "global").limit(1).execute()
        if resultado.data:
            estado = resultado.data[0].get("estado") or {}
            config = DEFAULT_CONFIG.copy()
            config.update({k: v for k, v in estado.items() if k in config})
            return config
    except Exception as e:
        st.session_state.config_erro = str(e)
    return DEFAULT_CONFIG.copy()


def salvar_configuracoes(config):
    payload = {"id": "global", "estado": config}
    resultado = get_client().table("almox_app_state").upsert(payload, on_conflict="id").execute()
    return bool(resultado.data)


if "config_carregada" not in st.session_state:
    st.session_state.config = carregar_configuracoes()
    st.session_state.config_carregada = True
elif "config" not in st.session_state:
    st.session_state.config = DEFAULT_CONFIG.copy()

config = st.session_state.config
PRIMARY = CORES.get(config.get("cor_principal"), CORES["Amarelo (Padrão)"])
IS_LIGHT = config.get("tema") == "Claro"

if IS_LIGHT:
    APP_BG, SIDEBAR_BG, TEXT, MUTED, PANEL, BORDER, INPUT_BG, COLLAPSE = "#f4f6f5", "#ffffff", "#18201d", "#68736e", "#ffffff", "#d7ded9", "#f8faf9", "#68736e"
else:
    APP_BG, SIDEBAR_BG, TEXT, MUTED, PANEL, BORDER, INPUT_BG, COLLAPSE = "#0b0f0e", "#090c0b", "#f4f5f4", "#9aa39f", "#101513", "#35403b", "#101513", "#ffffff"

# ============================================================
# UM ÚNICO CONTROLE: BOTÃO NATIVO DO STREAMLIT
# ============================================================
# Não criamos outro st.button. O próprio botão nativo da sidebar é o único
# controle. O CSS usa o estado aria-expanded da sidebar para esconder/mostrar
# o menu superior junto com ela.
st.markdown(f"""
<style>
#MainMenu, footer{{visibility:hidden}}

/* ============================================================
   CONTROLE ÚNICO - CANTO SUPERIOR ESQUERDO
   ============================================================ */
button[data-testid="stSidebarCollapseButton"]{{
    display:flex !important;
    position:fixed !important;
    top:8px !important;
    left:10px !important;
    z-index:1000000 !important;
    width:40px !important;
    height:34px !important;
    min-width:40px !important;
    min-height:34px !important;
    padding:0 !important;
    margin:0 !important;
    border-radius:8px !important;
    border:1px solid {BORDER} !important;
    background:{SIDEBAR_BG} !important;
    color:{TEXT} !important;
    box-shadow:0 1px 4px rgba(0,0,0,.18) !important;
}}
button[data-testid="stSidebarCollapseButton"]:hover{{
    background:{PRIMARY} !important;
    color:#111 !important;
    border-color:{PRIMARY} !important;
}}
button[data-testid="stSidebarCollapseButton"] svg{{
    width:20px !important;
    height:20px !important;
}}

/* O MESMO botão controla visualmente o menu superior.
   Quando a sidebar fica recolhida, o toolbar também desaparece. */
[data-testid="stToolbar"]{{
    display:flex !important;
    align-items:center !important;
}}
body:has(section[data-testid="stSidebar"][aria-expanded="false"]) [data-testid="stToolbar"]{{
    display:none !important;
}}

header[data-testid="stHeader"]{{
    background:transparent !important;
}}

/* ============================================================
   SIDEBAR
   ============================================================ */
section[data-testid="stSidebar"]{{
    background:{SIDEBAR_BG} !important;
    border-right:1px solid {BORDER};
}}
section[data-testid="stSidebar"] > div:first-child{{
    width:230px !important;
    min-width:230px !important;
    padding:1px 9px 20px;
}}

.stApp{{background:{APP_BG};color:{TEXT}}}
.block-container{{max-width:1500px;padding:38px 34px 50px}}
.hero{{display:flex;justify-content:space-between;align-items:center;margin-bottom:24px}}
.hero h1{{margin:0;font-size:30px;color:{TEXT}}}
.hero p,.muted{{color:{MUTED}}}
.period{{background:{PRIMARY};color:#111;padding:10px 15px;border-radius:9px;font-weight:800}}
.section{{color:{PRIMARY};font-size:14px;font-weight:900;letter-spacing:1px;text-transform:uppercase;margin:22px 0 10px}}
.panel{{background:linear-gradient(145deg,{PANEL},#0d1210);border:1px solid {BORDER};border-radius:15px;padding:22px;margin-top:14px}}
.notice{{padding:12px 14px;border-left:3px solid {PRIMARY};background:{PANEL};color:{MUTED};border-radius:7px;font-size:11px}}
div[data-testid="stMetric"]{{background:linear-gradient(145deg,{PANEL},#0d1210);border:1px solid {BORDER};padding:15px;border-radius:12px}}

[data-testid="stSidebar"] .stButton{{margin:0 0 8px 0}}
[data-testid="stSidebar"] .stButton > button{{width:100%;min-height:48px;height:48px;border-radius:12px;border:1px solid {BORDER};background:{INPUT_BG};color:{TEXT} !important;font-size:14px;font-weight:900;text-align:center;padding:0 10px;box-shadow:none;transition:all .15s ease}}
[data-testid="stSidebar"] .stButton > button:hover{{background:{PRIMARY}22;border-color:{PRIMARY};color:{TEXT} !important}}
[data-testid="stSidebar"] .stButton > button[kind="primary"]{{background:{PRIMARY} !important;color:#0b0f0e !important;border:2px solid #f4f5f4;box-shadow:0 0 0 1px {PRIMARY} inset}}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover{{background:{PRIMARY} !important;color:#0b0f0e !important}}
[data-testid="stSidebar"] .stButton > button p{{font-size:14px;font-weight:900;letter-spacing:.15px;color:inherit !important;text-align:center !important;width:100%}}
[data-testid="stSidebar"] .stButton > button div{{justify-content:center !important}}
.sidebar-logo-section{{width:100%;display:flex;flex-direction:column;align-items:center;margin:0 0 8px;padding:0 0 9px;border-bottom:1px solid {BORDER}}}
.sidebar-logo-wrap{{width:190px;height:82px;box-sizing:border-box;display:flex;justify-content:center;align-items:center;background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;padding:6px;box-shadow:0 1px 3px rgba(0,0,0,.08);overflow:hidden}}
.sidebar-logo-img{{display:block;max-width:176px;max-height:70px;width:auto;height:auto;object-fit:contain;margin:auto}}
.sidebar-logo-placeholder{{width:176px;height:68px;display:flex;align-items:center;justify-content:center;text-align:center;color:#6b7280;background:#ffffff;border-radius:8px;font-size:11px;line-height:1.4}}
.sidebar-footer{{margin:20px 5px 0;padding-top:16px;border-top:1px solid {BORDER};color:{MUTED};font-size:10px;line-height:1.6}}
.logo-preview{{min-height:250px;border:1px solid {BORDER};border-radius:12px;background:{INPUT_BG};display:flex;align-items:center;justify-content:center;padding:20px}}
.logo-preview img{{max-width:100%;max-height:210px;object-fit:contain}}
.tip{{background:#101b27;border:1px solid #284a68;border-radius:10px;padding:15px;color:#b8c8d8;margin-top:18px;font-size:13px;line-height:1.6}}
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=30)
def rows(table, limit=500, order=None):
    q = get_client().table(table).select("*")
    if order:
        q = q.order(order, desc=True)
    return q.limit(limit).execute().data or []


def df(data):
    return pd.DataFrame(data) if data else pd.DataFrame()


if "pagina" not in st.session_state:
    st.session_state.pagina = "Dashboard"

paginas = ["Dashboard", "Alimentar Indicadores", "Histórico", "Gestão de Equipes", "Plano de Carreira", "Configurações"]

with st.sidebar:
    logo_b64 = config.get("logo_base64")
    if logo_b64:
        mime = config.get("logo_mime") or "image/png"
        logo_html = f'<img class="sidebar-logo-img" src="data:{mime};base64,{logo_b64}" alt="Logo SETTA">'
    else:
        logo_html = '<div class="sidebar-logo-placeholder">SUA LOGO AQUI<br>Configure em Configurações</div>'

    st.markdown(f'<div class="sidebar-logo-section"><div class="sidebar-logo-wrap">{logo_html}</div></div>', unsafe_allow_html=True)

    for p in paginas:
        ativo = st.session_state.pagina == p
        if st.button(p.upper(), use_container_width=True, type="primary" if ativo else "secondary", key=f"menu_{p}"):
            st.session_state.pagina = p
            st.rerun()

    st.markdown("<div class='sidebar-footer'>Gestão Operacional<br>SETTA • Streamlit + Supabase</div>", unsafe_allow_html=True)

pagina = st.session_state.pagina
st.markdown(f'<div class="hero"><div><h1>{pagina}</h1><p>Gestão operacional do almoxarifado</p></div><div class="period">{date.today().strftime("%d/%m/%Y")}</div></div>', unsafe_allow_html=True)

try:
    get_client()
    conectado = True
except Exception:
    conectado = False

if not conectado:
    st.error("Supabase ainda não está configurado no ambiente do Streamlit.")
    st.stop()

if pagina == "Dashboard":
    indicadores = rows("almox_indicadores", order="competencia")
    colaboradores = rows("almox_colaboradores")
    equipes = rows("almox_equipes")
    historico = rows("almox_historico", order="criado_em")
    snapshots = rows("mrp_snapshots", order="created_at")
    st.markdown('<div class="section">Dados reais do Supabase</div>', unsafe_allow_html=True)
    a,b,c,d = st.columns(4)
    a.metric("Indicadores", len(indicadores)); b.metric("Colaboradores", len(colaboradores)); c.metric("Equipes", len(equipes)); d.metric("MRP salvos", len(snapshots))
    if indicadores:
        data = df(indicadores)
        st.markdown('<div class="section">Indicadores</div>', unsafe_allow_html=True)
        if "competencia" in data.columns and "valor" in data.columns:
            data["competencia"] = pd.to_datetime(data["competencia"], errors="coerce")
            chart = data.dropna(subset=["competencia"]).pivot_table(index="competencia", columns="indicador", values="valor", aggfunc="last")
            if not chart.empty:
                st.line_chart(chart)
        st.dataframe(data, use_container_width=True, hide_index=True)
    else:
        st.info("A tabela almox_indicadores está conectada, mas ainda não possui lançamentos.")
    with st.expander("Diagnóstico"):
        st.write({"Supabase":"conectado","indicadores":len(indicadores),"colaboradores":len(colaboradores),"equipes":len(equipes),"histórico":len(historico),"MRP":len(snapshots)})

elif pagina == "Alimentar Indicadores":
    st.markdown('<div class="notice">Consulta do banco real habilitada. A gravação será liberada junto com autenticação adequada.</div>', unsafe_allow_html=True)
    st.dataframe(df(rows("almox_indicadores", order="competencia")), use_container_width=True, hide_index=True)

elif pagina == "Histórico":
    st.markdown('<div class="section">Histórico real</div>', unsafe_allow_html=True)
    st.dataframe(df(rows("almox_historico", order="criado_em")), use_container_width=True, hide_index=True)

elif pagina == "Gestão de Equipes":
    colaboradores = df(rows("almox_colaboradores"))
    equipes = df(rows("almox_equipes"))
    org = df(rows("almox_organograma"))
    a,b,c = st.columns(3)
    a.metric("Colaboradores",len(colaboradores)); b.metric("Equipes",len(equipes)); c.metric("Nós do organograma",len(org))
    st.markdown('<div class="section">Colaboradores</div>', unsafe_allow_html=True); st.dataframe(colaboradores,use_container_width=True,hide_index=True)
    st.markdown('<div class="section">Equipes</div>', unsafe_allow_html=True); st.dataframe(equipes,use_container_width=True,hide_index=True)
    st.markdown('<div class="section">Organograma</div>', unsafe_allow_html=True); st.dataframe(org,use_container_width=True,hide_index=True)

elif pagina == "Plano de Carreira":
    st.markdown('<div class="section">Plano de carreira</div>', unsafe_allow_html=True)
    st.info("Módulo preparado para receber níveis, competências, metas e trilhas de desenvolvimento.")

elif pagina == "Configurações":
    st.markdown('<div class="section">Configurações</div>', unsafe_allow_html=True)
    st.write("As configurações abaixo ficam salvas no Supabase e são carregadas novamente quando o aplicativo abre.")
    col1,col2 = st.columns(2)
    with col1:
        tema = st.selectbox("Tema", TEMAS, index=TEMAS.index(config.get("tema", TEMAS[0])))
        cor = st.selectbox("Cor principal", list(CORES.keys()), index=list(CORES.keys()).index(config.get("cor_principal", "Amarelo (Padrão)")))
        estilo = st.radio("Estilo dos botões", ESTILOS_BOTOES, index=ESTILOS_BOTOES.index(config.get("estilo_botoes", "Amarelo")))
        if st.button("SALVAR CONFIGURAÇÕES", type="primary", use_container_width=True):
            novo = config.copy(); novo.update({"tema":tema,"cor_principal":cor,"estilo_botoes":estilo})
            try:
                if salvar_configuracoes(novo):
                    st.session_state.config = novo
                    st.success("Configurações salvas.")
                    st.rerun()
                else:
                    st.error("Não foi possível salvar as configurações.")
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")
    with col2:
        arquivo = st.file_uploader("Logo da empresa", type=["png","jpg","jpeg","svg"], help="Até 2 MB")
        if arquivo is not None:
            if arquivo.size > 2 * 1024 * 1024:
                st.error("A logo deve ter no máximo 2 MB.")
            else:
                dados = base64.b64encode(arquivo.getvalue()).decode("ascii")
                novo = config.copy(); novo.update({"logo_base64":dados,"logo_name":arquivo.name,"logo_mime":arquivo.type or "image/png"})
                try:
                    if salvar_configuracoes(novo):
                        st.session_state.config = novo
                        st.success("Logo salva no Supabase.")
                        st.rerun()
                    else:
                        st.error("Não foi possível salvar a logo.")
                except Exception as e:
                    st.error(f"Erro ao salvar a logo: {e}")
        if config.get("logo_base64"):
            mime = config.get("logo_mime") or "image/png"
            st.markdown(f'<div class="logo-preview"><img src="data:{mime};base64,{config["logo_base64"]}"></div>', unsafe_allow_html=True)
        else:
            st.info("Nenhuma logo configurada.")

st.markdown("<br><div class='muted'>Gestão Almoxarifado • Streamlit + Supabase • migração em andamento</div>", unsafe_allow_html=True)
