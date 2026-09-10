from __future__ import annotations
from datetime import date
import base64
from collections import Counter
from io import BytesIO
import pandas as pd
from PIL import Image
import streamlit as st
from supabase_client import get_client

st.set_page_config(page_title="GESTÃO | SETTA", page_icon="assets/mrp_setta_icon.png", layout="wide", initial_sidebar_state="expanded")

DEFAULT_CONFIG = {
    "tema": "Escuro (Padrão)",
    "cor_principal": "Amarelo (Padrão)",
    "estilo_botoes": "Amarelo",
    "logo_base64": None,
    "logo_name": None,
    "logo_mime": None,
    "logo_bg": "#ffffff",
    "textos": {},
    "fontes": {},
}

CORES = {
    "Amarelo (Padrão)": "#ffd43d", "Azul": "#1683ff", "Verde": "#22c55e",
    "Vermelho": "#ff4d4f", "Roxo": "#8b5cf6", "Laranja": "#ff922b",
    "Ciano": "#22c7d6", "Rosa": "#ec4899", "Lima": "#a3e635",
}
TEMAS = ["Escuro (Padrão)", "Claro", "Automático"]
ESTILOS_BOTOES = ["Amarelo", "Colorido"]

TEXTOS_PADRAO = {
    "menu_dashboard": "Dashboard",
    "menu_indicadores": "Alimentar Indicadores",
    "menu_historico": "Histórico",
    "menu_equipes": "Gestão de Equipes",
    "menu_carreira": "Plano de Carreira",
    "menu_configuracoes": "Configurações",
    "titulo_dashboard": "Dashboard",
    "titulo_indicadores": "Alimentar Indicadores",
    "titulo_historico": "Histórico",
    "titulo_equipes": "Gestão de Equipes",
    "titulo_carreira": "Plano de Carreira",
    "titulo_configuracoes": "Configurações",
    "subtitulo_global": "Gestão operacional do almoxarifado",
    "secao_dados_reais": "Dados reais do Supabase",
    "secao_indicadores": "Indicadores",
    "secao_historico": "Histórico real",
    "secao_colaboradores": "Colaboradores",
    "secao_equipes": "Equipes",
    "secao_organograma": "Organograma",
    "secao_configuracoes": "Configurações",
    "secao_plano": "Plano de carreira",
    "mensagem_sem_indicadores": "A tabela almox_indicadores está conectada, mas ainda não possui lançamentos.",
    "diagnostico": "Diagnóstico",
    "mensagem_indicadores": "Consulta do banco real habilitada. A gravação será liberada junto com autenticação adequada.",
    "mensagem_carreira": "Módulo preparado para receber níveis, competências, metas e trilhas de desenvolvimento.",
    "rodape_linha1": "Gestão Operacional",
    "rodape_linha2": "SETTA • Streamlit + Supabase",
    "rodape_linha3": "Gestão Almoxarifado • Streamlit + Supabase • migração em andamento",
}

FONTES_PADRAO = {"menu": "Arial", "titulo": "Arial", "subtitulo": "Arial"}
FONTES = ["Arial", "Verdana", "Trebuchet MS", "Georgia", "Courier New", "Times New Roman"]


def carregar_configuracoes():
    try:
        resultado = get_client().table("almox_app_state").select("estado").eq("id", "global").limit(1).execute()
        if resultado.data:
            estado = resultado.data[0].get("estado") or {}
            config = DEFAULT_CONFIG.copy()
            for k, v in estado.items():
                if k in config:
                    config[k] = v
            config["textos"] = {**TEXTOS_PADRAO, **(estado.get("textos") or {})}
            config["fontes"] = {**FONTES_PADRAO, **(estado.get("fontes") or {})}
            return config
    except Exception as e:
        st.session_state.config_erro = str(e)
    config = DEFAULT_CONFIG.copy()
    config["textos"] = TEXTOS_PADRAO.copy()
    config["fontes"] = FONTES_PADRAO.copy()
    return config


def salvar_configuracoes(config):
    payload = {"id": "global", "estado": config}
    resultado = get_client().table("almox_app_state").upsert(payload, on_conflict="id").execute()
    return bool(resultado.data)


def detectar_cor_fundo_logo(logo_b64, logo_mime=None):
    """Mantida para compatibilidade com logos já salvas."""
    if not logo_b64:
        return "#ffffff"
    try:
        if (logo_mime or "").lower() == "image/svg+xml":
            return "#ffffff"
        imagem = Image.open(BytesIO(base64.b64decode(logo_b64))).convert("RGBA")
        imagem.thumbnail((160, 160))
        pixels = [(r, g, b) for r, g, b, a in imagem.getdata() if a >= 220]
        if not pixels:
            return "#ffffff"
        agrupadas = [((r // 16) * 16, (g // 16) * 16, (b // 16) * 16) for r, g, b in pixels]
        cor = Counter(agrupadas).most_common(1)[0][0]
        return "#{:02x}{:02x}{:02x}".format(*cor)
    except Exception:
        return "#ffffff"


if "config_carregada" not in st.session_state:
    st.session_state.config = carregar_configuracoes()
    st.session_state.config_carregada = True
elif "config" not in st.session_state:
    st.session_state.config = carregar_configuracoes()

config = st.session_state.config
config["textos"] = {**TEXTOS_PADRAO, **(config.get("textos") or {})}
config["fontes"] = {**FONTES_PADRAO, **(config.get("fontes") or {})}
textos = config["textos"]
fontes = config["fontes"]

def txt(chave):
    return textos.get(chave, TEXTOS_PADRAO.get(chave, chave))

PRIMARY = CORES.get(config.get("cor_principal"), CORES["Amarelo (Padrão)"])
IS_LIGHT = config.get("tema") == "Claro"

if IS_LIGHT:
    APP_BG, SIDEBAR_BG, TEXT, MUTED, PANEL, BORDER, INPUT_BG, COLLAPSE = "#f4f6f5", "#ffffff", "#18201d", "#68736e", "#ffffff", "#d7ded9", "#f8faf9", "#68736e"
else:
    APP_BG, SIDEBAR_BG, TEXT, MUTED, PANEL, BORDER, INPUT_BG, COLLAPSE = "#0b0f0e", "#090c0b", "#f4f5f4", "#9aa39f", "#101513", "#35403b", "#101513", "#ffffff"

st.markdown(f"""
<style>
#MainMenu, footer{{visibility:hidden}}
[data-testid="stToolbar"]{{display:none !important;}}
button[data-testid="stSidebarCollapseButton"]{{display:flex !important;visibility:visible !important;pointer-events:auto !important;position:fixed !important;top:10px !important;left:8px !important;right:auto !important;z-index:2147483647 !important;width:40px !important;height:34px !important;min-width:40px !important;min-height:34px !important;padding:0 !important;margin:0 !important;border-radius:8px !important;border:1px solid {BORDER} !important;background:#ffffff !important;color:#1f2937 !important;box-shadow:0 1px 4px rgba(0,0,0,.18) !important;}}
button[data-testid="stSidebarCollapseButton"]:hover{{background:{PRIMARY} !important;color:#111111 !important;border-color:{PRIMARY} !important;}}
button[data-testid="stSidebarCollapseButton"] svg{{width:20px !important;height:20px !important;}}
div[data-testid="collapsedControl"]{{position:fixed !important;top:10px !important;left:8px !important;right:auto !important;bottom:auto !important;inset-inline-start:8px !important;inset-inline-end:auto !important;z-index:2147483647 !important;width:40px !important;height:34px !important;margin:0 !important;padding:0 !important;transform:none !important;}}
div[data-testid="collapsedControl"] button{{display:flex !important;visibility:visible !important;pointer-events:auto !important;position:static !important;width:40px !important;height:34px !important;min-width:40px !important;min-height:34px !important;padding:0 !important;margin:0 !important;border-radius:8px !important;border:1px solid {BORDER} !important;background:#ffffff !important;color:#1f2937 !important;box-shadow:0 1px 4px rgba(0,0,0,.18) !important;}}
div[data-testid="collapsedControl"] button:hover{{background:{PRIMARY} !important;color:#111111 !important;border-color:{PRIMARY} !important;}}
div[data-testid="collapsedControl"] svg{{width:20px !important;height:20px !important;}}
div.st-key-controle_unico_menus{{display:none !important;}}
header[data-testid="stHeader"]{{display:block !important;background:transparent !important;height:0 !important;min-height:0 !important;border:0 !important;box-shadow:none !important;}}
section[data-testid="stSidebar"]{{background:{SIDEBAR_BG} !important;border-right:1px solid {BORDER};width:230px !important;min-width:230px !important;max-width:230px !important;overflow:hidden !important;}}
section[data-testid="stSidebar"] > div:first-child{{width:230px !important;min-width:230px !important;padding:1px 9px 20px;overflow:hidden !important;}}
section[data-testid="stSidebar"][aria-expanded="false"]{{width:0 !important;min-width:0 !important;max-width:0 !important;}}
section[data-testid="stSidebar"][aria-expanded="false"] > div:first-child{{width:0 !important;min-width:0 !important;padding:0 !important;}}
.stApp{{background:{APP_BG};color:{TEXT}}}
.block-container{{max-width:1500px;padding:18px 34px 50px}}
.hero{{display:flex;justify-content:space-between;align-items:center;margin-bottom:24px}}
.hero h1{{margin:0;font-family:{fontes["titulo"]},sans-serif;font-size:30px;color:{TEXT}}}
.hero p,.muted{{font-family:{fontes["subtitulo"]},sans-serif;color:{MUTED}}}
.period{{background:{PRIMARY};color:#111;padding:10px 15px;border-radius:9px;font-weight:800}}
.section{{color:{PRIMARY};font-size:14px;font-weight:900;letter-spacing:1px;text-transform:uppercase;margin:22px 0 10px}}
.panel{{background:linear-gradient(145deg,{PANEL},#0d1210);border:1px solid {BORDER};border-radius:15px;padding:22px;margin-top:14px}}
.notice{{padding:12px 14px;border-left:3px solid {PRIMARY};background:{PANEL};color:{MUTED};border-radius:7px;font-size:11px}}
div[data-testid="stMetric"]{{background:linear-gradient(145deg,{PANEL},#0d1210);border:1px solid {BORDER};padding:15px;border-radius:12px}}
[data-testid="stSidebar"] .stButton{{margin:0 0 8px 0}}
[data-testid="stSidebar"] .stButton > button{{width:100%;min-height:48px;height:48px;border-radius:12px;border:1px solid {BORDER};background:{INPUT_BG};color:{TEXT} !important;font-family:{fontes["menu"]},sans-serif;font-size:14px;font-weight:900;text-align:center;padding:0 10px;box-shadow:none;transition:all .15s ease}}
[data-testid="stSidebar"] .stButton > button:hover{{background:{PRIMARY}22;border-color:{PRIMARY};color:{TEXT} !important}}
[data-testid="stSidebar"] .stButton > button[kind="primary"]{{background:{PRIMARY} !important;color:#0b0f0e !important;border:2px solid #f4f5f4;box-shadow:0 0 0 1px {PRIMARY} inset}}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover{{background:{PRIMARY} !important;color:#0b0f0e !important}}
[data-testid="stSidebar"] .stButton > button p{{font-family:{fontes["menu"]},sans-serif;font-size:14px;font-weight:900;letter-spacing:.15px;color:inherit !important;text-align:center !important;width:100%}}
[data-testid="stSidebar"] .stButton > button div{{justify-content:center !important}}
.sidebar-logo-section{{width:100%;display:flex;flex-direction:column;align-items:center;margin:8px 0 8px;padding:0 0 9px;border-bottom:1px solid {BORDER}}}
.sidebar-logo-wrap{{width:190px;height:82px;box-sizing:border-box;display:flex;justify-content:center;align-items:center;background:var(--logo-bg);border:1px solid var(--logo-border);border-radius:12px;padding:0;box-shadow:0 1px 3px rgba(0,0,0,.08);overflow:hidden}}
.sidebar-logo-img{{display:block;width:100%;height:100%;max-width:none;max-height:none;object-fit:contain;margin:auto}}
.sidebar-logo-placeholder{{width:176px;height:68px;display:flex;align-items:center;justify-content:center;text-align:center;color:#6b7280;background:#ffffff;border-radius:8px;font-size:11px;line-height:1.4}}
.sidebar-footer{{margin:20px 5px 0;padding-top:16px;border-top:1px solid {BORDER};color:{MUTED};font-family:{fontes["subtitulo"]},sans-serif;font-size:10px;line-height:1.6}}
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
    st.session_state.pagina = "dashboard"

paginas_ids = ["dashboard", "indicadores", "historico", "equipes", "carreira", "configuracoes"]
paginas = [txt("menu_" + x) for x in paginas_ids]

with st.sidebar:
    logo_b64 = config.get("logo_base64")
    if logo_b64:
        # Detecta automaticamente o fundo da própria imagem para que o
        # "balão" acompanhe a identidade visual da logo (preto, branco etc.).
        logo_bg = detectar_cor_fundo_logo(logo_b64, config.get("logo_mime"))
        try:
            r, g, b = int(logo_bg[1:3], 16), int(logo_bg[3:5], 16), int(logo_bg[5:7], 16)
            luminancia = (0.299 * r) + (0.587 * g) + (0.114 * b)
            logo_border = "#555555" if luminancia < 150 else "#e5e7eb"
        except Exception:
            logo_border = "#e5e7eb"
    else:
        logo_bg = "#101513" if IS_LIGHT else "#ffffff"
        logo_border = "#e5e7eb"
    if logo_b64:
        mime = config.get("logo_mime") or "image/png"
        logo_html = f'<img class="sidebar-logo-img" src="data:{mime};base64,{logo_b64}" alt="Logo SETTA">'
    else:
        logo_html = '<div class="sidebar-logo-placeholder">SUA LOGO AQUI<br>Configure em Configurações</div>'
    st.markdown(f'<div class="sidebar-logo-section"><div class="sidebar-logo-wrap" style="--logo-bg:{logo_bg};--logo-border:{logo_border};">{logo_html}</div></div>', unsafe_allow_html=True)
    for _id, p in zip(paginas_ids, paginas):
        ativo = st.session_state.pagina == _id
        if st.button(p.upper(), use_container_width=True, type="primary" if ativo else "secondary", key=f"menu_{_id}"):
            st.session_state.pagina = _id
            st.rerun()
    st.markdown(f"<div class='sidebar-footer'>{txt('rodape_linha1')}<br>{txt('rodape_linha2')}</div>", unsafe_allow_html=True)

pagina = st.session_state.pagina
if pagina not in paginas_ids:
    pagina = "dashboard"
    st.session_state.pagina = pagina
MESES_PT = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
competencia_atual = f"{MESES_PT[date.today().month - 1]}/{date.today().strftime('%y')}"
titulo_id = "titulo_" + pagina
st.markdown(f'<div class="hero"><div><h1>{txt(titulo_id)}</h1><p>{txt("subtitulo_global")}</p></div><div class="period">{competencia_atual}</div></div>', unsafe_allow_html=True)

try:
    get_client()
    conectado = True
except Exception:
    conectado = False

if not conectado:
    st.error("Supabase ainda não está configurado no ambiente do Streamlit.")
    st.stop()

if pagina == "dashboard":
    indicadores = rows("almox_indicadores", order="competencia")
    colaboradores = rows("almox_colaboradores")
    equipes = rows("almox_equipes")
    historico = rows("almox_historico", order="criado_em")
    snapshots = rows("mrp_snapshots", order="created_at")
    st.markdown(f'<div class="section">{txt("secao_dados_reais")}</div>', unsafe_allow_html=True)
    a,b,c,d = st.columns(4)
    a.metric(txt("secao_indicadores"), len(indicadores)); b.metric(txt("secao_colaboradores"), len(colaboradores)); c.metric(txt("secao_equipes"), len(equipes)); d.metric("MRP salvos", len(snapshots))
    if indicadores:
        data = df(indicadores)
        st.markdown(f'<div class="section">{txt("secao_indicadores")}</div>', unsafe_allow_html=True)
        if "competencia" in data.columns and "valor" in data.columns:
            data["competencia"] = pd.to_datetime(data["competencia"], errors="coerce")
            chart = data.dropna(subset=["competencia"]).pivot_table(index="competencia", columns="indicador", values="valor", aggfunc="last")
            if not chart.empty:
                st.line_chart(chart)
        st.dataframe(data, use_container_width=True, hide_index=True)
    else:
        st.info(txt("mensagem_sem_indicadores"))
    with st.expander(txt("diagnostico")):
        st.write({"Supabase":"conectado","indicadores":len(indicadores),"colaboradores":len(colaboradores),"equipes":len(equipes),"histórico":len(historico),"MRP":len(snapshots)})

elif pagina == "indicadores":
    st.markdown(f'<div class="notice">{txt("mensagem_indicadores")}</div>', unsafe_allow_html=True)
    st.dataframe(df(rows("almox_indicadores", order="competencia")), use_container_width=True, hide_index=True)

elif pagina == "historico":
    st.markdown(f'<div class="section">{txt("secao_historico")}</div>', unsafe_allow_html=True)
    st.dataframe(df(rows("almox_historico", order="criado_em")), use_container_width=True, hide_index=True)

elif pagina == "equipes":
    client = get_client()

    def carregar_equipes():
        return client.table("almox_equipes").select("*").order("nome").execute().data or []

    def carregar_colaboradores():
        return client.table("almox_colaboradores").select("*").order("nome").execute().data or []

    def registrar_historico(tipo, descricao, dados):
        try:
            client.table("almox_historico").insert({"tipo": tipo, "descricao": descricao, "dados": dados}).execute()
        except Exception:
            pass

    def nome_curto(nome):
        partes = [x for x in (nome or "").split() if x]
        return " ".join(partes[:2]) if partes else "Sem nome"

    def foto_html(c, tamanho=72):
        b64 = c.get("foto_base64")
        mime = c.get("foto_mime") or "image/jpeg"
        if b64:
            return f'<img class="ge-avatar-img" style="width:{tamanho}px;height:{tamanho}px" src="data:{mime};base64,{b64}">' 
        return f'<div class="ge-avatar-fallback" style="width:{tamanho}px;height:{tamanho}px">{nome_curto(c.get("nome"))[:1].upper()}</div>'

    equipes_raw = carregar_equipes()
    colaboradores_raw = carregar_colaboradores()
    ativos_equipes = [x for x in equipes_raw if x.get("ativo", True)]
    ativos_colaboradores = [x for x in colaboradores_raw if x.get("ativo", True)]
    inativos_colaboradores = [x for x in colaboradores_raw if not x.get("ativo", True)]
    nomes_colab = {str(x.get("id")): x for x in colaboradores_raw}
    nomes_eq = {str(x.get("id")): x.get("nome", "") for x in equipes_raw}

    st.markdown("""
    <style>
    .ge-shell{margin-top:4px}
    .ge-tabs-note{color:#8e9893;font-size:12px;margin:0 0 14px 2px}
    .ge-kpi{background:linear-gradient(145deg,#151b18,#0d1110);border:1px solid #34413b;border-radius:15px;padding:18px 20px;min-height:106px;box-shadow:0 6px 18px rgba(0,0,0,.12)}
    .ge-kpi .label{font-size:11px;color:#8f9994;text-transform:uppercase;letter-spacing:1px;font-weight:800}
    .ge-kpi .value{font-size:32px;line-height:1.05;font-weight:900;color:#f4f5f4;margin-top:8px}
    .ge-kpi .sub{font-size:11px;color:#ffd43d;margin-top:7px}
    .ge-overview-panel,.ge-team-card,.ge-person-card{background:linear-gradient(145deg,#111714,#0c100f);border:1px solid #34413b;border-radius:16px}
    .ge-overview-panel{padding:20px;margin-top:16px}
    .ge-panel-title{font-size:15px;font-weight:900;color:#f3f5f4;text-transform:uppercase;letter-spacing:.8px;margin-bottom:15px}
    .ge-mini{display:flex;align-items:center;gap:12px;padding:12px 0;border-bottom:1px solid #26302c}
    .ge-mini:last-child{border-bottom:0}
    .ge-mini .rank{width:28px;height:28px;border-radius:9px;background:#ffd43d;color:#111;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:900}
    .ge-mini .main{flex:1}.ge-mini .name{font-size:12px;font-weight:800;color:#f4f5f4}.ge-mini .desc{font-size:10px;color:#8e9893;margin-top:2px}
    .ge-bar{height:7px;background:#202925;border-radius:99px;overflow:hidden;margin-top:7px}.ge-bar span{display:block;height:100%;background:#ffd43d;border-radius:99px}
    .ge-alert{padding:14px 16px;border-radius:12px;border:1px solid #5b4a13;background:#211c0b;color:#ddd4a7;font-size:12px;line-height:1.5}
    .ge-team-card{padding:20px;margin-top:14px;position:relative;overflow:hidden}
    .ge-team-head{display:flex;justify-content:space-between;gap:18px;align-items:flex-start}
    .ge-team-title{font-size:20px;font-weight:900;color:#f4f5f4;margin:0}.ge-team-title span{color:#ffd43d}
    .ge-team-status{font-size:10px;font-weight:900;border:1px solid #4a5a52;border-radius:999px;padding:6px 10px;color:#ffd43d;white-space:nowrap}
    .ge-team-objective{color:#9ca6a1;font-size:12px;line-height:1.55;margin-top:8px;max-width:900px}
    .ge-team-grid{display:grid;grid-template-columns:1.2fr 1fr 1.6fr;gap:14px;margin-top:18px}
    .ge-info-box{background:#0a0e0d;border:1px solid #26312c;border-radius:12px;padding:14px}.ge-info-label{font-size:9px;text-transform:uppercase;letter-spacing:1px;color:#7f8a84;font-weight:900}.ge-info-value{font-size:12px;color:#f0f2f1;font-weight:800;margin-top:6px}
    .ge-task{font-size:10px;color:#c0c7c3;padding:6px 0;border-bottom:1px solid #202824}.ge-task:last-child{border-bottom:0}
    .ge-member{display:flex;align-items:center;gap:10px;padding:9px 0;border-bottom:1px solid #202824}.ge-member:last-child{border-bottom:0}.ge-member img,.ge-member .ge-avatar-fallback{flex:0 0 36px}.ge-member-name{font-size:11px;font-weight:800;color:#f0f2f1}.ge-member-role{font-size:9px;color:#89938e;margin-top:2px}
    .ge-empty{color:#7f8984;font-size:11px;padding:9px 0}
    .ge-person-card{padding:13px;text-align:center;min-height:220px;margin-bottom:10px;position:relative}
    .ge-person-photo{width:78px;height:78px;margin:2px auto 10px;border-radius:50%;padding:4px;border:2px solid #ffd43d;background:#171d19;box-shadow:0 0 0 3px rgba(255,212,61,.08)}
    .ge-person-photo img,.ge-person-photo .ge-avatar-fallback{width:66px!important;height:66px!important;border-radius:50%;display:block;object-fit:cover}
    .ge-avatar-img{border-radius:50%;object-fit:cover;display:block}.ge-avatar-fallback{border-radius:50%;background:#26302b;color:#ffd43d;display:flex;align-items:center;justify-content:center;font-weight:900}
    .ge-person-name{font-size:12px;font-weight:900;color:#f4f5f4;text-transform:uppercase;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.ge-person-role{font-size:9px;color:#ffd43d;font-weight:800;margin-top:5px;min-height:25px}.ge-person-team{font-size:9px;color:#89938e;margin-top:4px;min-height:25px}.ge-person-status{font-size:9px;color:#89938e;margin-top:9px}
    .ge-form-panel{background:#111714;border:1px solid #34413b;border-radius:16px;padding:18px 20px;margin:12px 0 18px}
    @media(max-width:900px){.ge-team-grid{grid-template-columns:1fr}.ge-person-card{min-height:205px}}
    </style>
    """, unsafe_allow_html=True)

    k1,k2,k3,k4 = st.columns(4)
    k1.markdown(f'<div class="ge-kpi"><div class="label">Equipes ativas</div><div class="value">{len(ativos_equipes)}</div><div class="sub">Estrutura operacional</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="ge-kpi"><div class="label">Colaboradores ativos</div><div class="value">{len(ativos_colaboradores)}</div><div class="sub">Base atual</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="ge-kpi"><div class="label">Colaboradores alocados</div><div class="value">{sum(1 for x in ativos_colaboradores if x.get("equipe_id"))}</div><div class="sub">Com equipe definida</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="ge-kpi"><div class="label">Sem equipe</div><div class="value">{sum(1 for x in ativos_colaboradores if not x.get("equipe_id"))}</div><div class="sub">Aguardando alocação</div></div>', unsafe_allow_html=True)

    tab_geral, tab_equipes, tab_colaboradores = st.tabs(["VISÃO GERAL", "EQUIPES", "COLABORADORES"])

    with tab_geral:
        st.markdown('<div class="ge-tabs-note">Visão consolidada da estrutura do almoxarifado, equipes, pessoas e distribuição atual.</div>', unsafe_allow_html=True)
        a,b = st.columns([1.15, .85])
        with a:
            st.markdown('<div class="ge-overview-panel"><div class="ge-panel-title">Estrutura das equipes</div>', unsafe_allow_html=True)
            total_eq = max(len(ativos_equipes),1)
            for idx, equipe in enumerate(ativos_equipes,1):
                membros = [c for c in ativos_colaboradores if str(c.get("equipe_id")) == str(equipe.get("id"))]
                st.markdown(f'<div class="ge-mini"><div class="rank">{idx:02d}</div><div class="main"><div class="name">{equipe.get("nome","")}</div><div class="desc">{len(membros)} colaborador(es) · {len(equipe.get("tarefas") or [])} tarefa(s)</div><div class="ge-bar"><span style="width:{max(4, int((len(membros)/max(len(ativos_colaboradores),1))*100))}%"></span></div></div></div>', unsafe_allow_html=True)
            if not ativos_equipes:
                st.markdown('<div class="ge-empty">Nenhuma equipe ativa cadastrada.</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with b:
            st.markdown('<div class="ge-overview-panel"><div class="ge-panel-title">Resumo de pessoas</div>', unsafe_allow_html=True)
            funcoes = {}
            for c in ativos_colaboradores:
                f = (c.get("funcao") or "Sem função").strip().upper()
                funcoes[f] = funcoes.get(f,0)+1
            for f,n in sorted(funcoes.items(), key=lambda x:(-x[1],x[0]))[:7]:
                st.markdown(f'<div class="ge-mini"><div class="main"><div class="name">{f}</div><div class="desc">{n} colaborador(es)</div><div class="ge-bar"><span style="width:{max(4,int(n/max(len(ativos_colaboradores),1)*100))}%"></span></div></div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        sem_equipe = [c for c in ativos_colaboradores if not c.get("equipe_id")]
        if sem_equipe:
            st.markdown(f'<div class="ge-alert"><b>Alocação pendente:</b> {len(sem_equipe)} colaborador(es) ativo(s) ainda estão sem equipe definida. O cadastro já está pronto para receber a associação na edição de cada colaborador.</div>', unsafe_allow_html=True)

        st.markdown("""<style>
        .ge-admissions-panel{background:linear-gradient(145deg,#101513,#0d1210);border:1px solid #35403b;border-radius:15px;padding:22px;margin-top:14px}
        .ge-admissions-title{color:#f4f5f4;font-size:16px;font-weight:900;letter-spacing:.4px;text-transform:uppercase;margin:0 0 22px}
        .ge-admissions-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:0;width:100%}
        .ge-admission-item{min-width:0;text-align:center;padding:0 18px;border-left:1px solid #35403b}
        .ge-admission-item:first-child{border-left:0}
        .ge-admission-photo{display:flex;justify-content:center;align-items:center;min-height:58px}
        .ge-admission-name{margin-top:9px;color:#f4f5f4;font-size:11px;font-weight:900;line-height:1.25;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
        .ge-admission-date{margin-top:4px;color:#89938e;font-size:9px}
        @media (max-width:900px){.ge-admissions-grid{grid-template-columns:repeat(2,minmax(0,1fr));row-gap:20px}.ge-admission-item:nth-child(3){border-left:0}}
        @media (max-width:560px){.ge-admissions-grid{grid-template-columns:1fr}.ge-admission-item{border-left:0;border-top:1px solid #35403b;padding:16px 0 0}.ge-admission-item:first-child{border-top:0;padding-top:0}}
        </style>""", unsafe_allow_html=True)

        recentes = sorted(
            [c for c in ativos_colaboradores if c.get("data_admissao")],
            key=lambda x: x.get("data_admissao") or "",
            reverse=True,
        )[:5]

        cards_admissoes = []
        for c in recentes:
            data = pd.to_datetime(c.get("data_admissao"), errors="coerce")
            data_txt = data.strftime("%d/%m/%Y") if not pd.isna(data) else "—"
            cards_admissoes.append(
                '<div class="ge-admission-item">'
                '<div class="ge-admission-photo">' + foto_html(c,54) + '</div>'
                '<div class="ge-admission-name">' + nome_curto(c.get("nome")) + '</div>'
                '<div class="ge-admission-date">' + data_txt + '</div>'
                '</div>'
            )

        if cards_admissoes:
            st.markdown(
                '<div class="ge-admissions-panel">'
                '<div class="ge-admissions-title">Admissões mais recentes</div>'
                '<div class="ge-admissions-grid">'
                + ''.join(cards_admissoes) +
                '</div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="ge-admissions-panel">'
                '<div class="ge-admissions-title">Admissões mais recentes</div>'
                '<div class="ge-empty">Nenhuma data de admissão cadastrada.</div>'
                '</div>',
                unsafe_allow_html=True,
            )
    with tab_equipes:
        st.markdown('<div class="ge-tabs-note">Cada equipe agora aparece como um painel operacional, com objetivo, responsável, tarefas e integrantes.</div>', unsafe_allow_html=True)
        st.markdown('<div class="ge-form-panel">', unsafe_allow_html=True)
        with st.form("form_nova_equipe", clear_on_submit=True):
            ec1, ec2 = st.columns(2)
            with ec1:
                nome_equipe = st.text_input("Nome da equipe *", placeholder="Ex.: Almoxarifado")
                objetivo_equipe = st.text_area("Objetivo", placeholder="Descreva a finalidade da equipe.", height=90)
            with ec2:
                responsaveis = {"Nenhum": None}
                for c in ativos_colaboradores:
                    responsaveis[f"{c.get('nome', '')} — {c.get('funcao') or 'Sem função'}"] = c.get("id")
                resp_label = st.selectbox("Responsável", list(responsaveis.keys()))
                tarefas_texto = st.text_area("Tarefas principais", placeholder="Uma tarefa por linha", height=90)
            criar_equipe = st.form_submit_button("CRIAR EQUIPE", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if criar_equipe:
            nome_limpo = nome_equipe.strip()
            if not nome_limpo:
                st.error("Informe o nome da equipe.")
            elif any((x.get("nome") or "").strip().casefold() == nome_limpo.casefold() and x.get("ativo", True) for x in equipes_raw):
                st.error("Já existe uma equipe ativa com esse nome.")
            else:
                try:
                    novo = client.table("almox_equipes").insert({"nome": nome_limpo, "objetivo": objetivo_equipe.strip() or None, "tarefas": [x.strip() for x in tarefas_texto.splitlines() if x.strip()], "responsavel_id": responsaveis[resp_label], "ativo": True}).execute().data
                    if novo:
                        registrar_historico("equipe_criada", f"Equipe criada: {nome_limpo}", {"equipe_id": novo[0].get("id"), "nome": nome_limpo})
                        st.success(f"Equipe '{nome_limpo}' criada com sucesso.")
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro ao criar equipe: {e}")

        filtro_eq = st.text_input("Buscar equipe", placeholder="Digite parte do nome...", key="busca_equipe")
        equipes_exibicao = [x for x in equipes_raw if filtro_eq.strip().casefold() in (x.get("nome") or "").casefold()]
        for equipe in equipes_exibicao:
            eid = str(equipe.get("id"))
            membros = [c for c in ativos_colaboradores if str(c.get("equipe_id")) == eid]
            resp = nomes_colab.get(str(equipe.get("responsavel_id")))
            resp_html = f'{foto_html(resp,42)}<div><div class="ge-member-name">{resp.get("nome","")}</div><div class="ge-member-role">{resp.get("funcao") or "Sem função"}</div></div>' if resp else '<div class="ge-empty">Nenhum responsável definido.</div>'
            tarefas = ''.join([f'<div class="ge-task">{t}</div>' for t in (equipe.get("tarefas") or [])]) or '<div class="ge-empty">Nenhuma tarefa cadastrada.</div>'
            membros_html = ''.join([f'<div class="ge-member">{foto_html(c,36)}<div><div class="ge-member-name">{c.get("nome","")}</div><div class="ge-member-role">{c.get("funcao") or "Sem função"}</div></div></div>' for c in membros]) or '<div class="ge-empty">Nenhum colaborador associado a esta equipe.</div>'
            st.markdown(f'<div class="ge-team-card"><div class="ge-team-head"><div><div class="ge-team-title"><span>●</span> {equipe.get("nome","")}</div><div class="ge-team-objective">{equipe.get("objetivo") or "Objetivo não informado."}</div></div><div class="ge-team-status">{"ATIVA" if equipe.get("ativo",True) else "INATIVA"}</div></div><div class="ge-team-grid"><div class="ge-info-box"><div class="ge-info-label">Responsável</div><div style="margin-top:9px;display:flex;align-items:center;gap:10px">{resp_html}</div></div><div class="ge-info-box"><div class="ge-info-label">Integrantes</div><div class="ge-info-value">{len(membros)} colaborador(es)</div><div class="ge-info-label" style="margin-top:12px">Tarefas</div><div class="ge-info-value">{len(equipe.get("tarefas") or [])} atividade(s)</div></div><div class="ge-info-box"><div class="ge-info-label">Tarefas principais</div>{tarefas}</div></div><div class="ge-info-box" style="margin-top:14px"><div class="ge-info-label">Equipe</div>{membros_html}</div></div>', unsafe_allow_html=True)
            ca,cb = st.columns(2)
            with ca:
                if st.button("EDITAR EQUIPE", key=f"editar_eq_{eid}", use_container_width=True):
                    st.session_state["editar_equipe_id"] = eid
                    st.rerun()
            with cb:
                if st.button("INATIVAR EQUIPE" if equipe.get("ativo", True) else "REATIVAR EQUIPE", key=f"status_eq_{eid}", use_container_width=True):
                    try:
                        client.table("almox_equipes").update({"ativo": not equipe.get("ativo", True)}).eq("id", eid).execute()
                        registrar_historico("equipe_status", f"Status alterado: {equipe.get('nome', '')}", {"equipe_id": eid, "ativo": not equipe.get("ativo", True)})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao alterar status: {e}")
            if st.session_state.get("editar_equipe_id") == eid:
                with st.form(f"form_editar_eq_{eid}"):
                    nome_edit = st.text_input("Nome", value=equipe.get("nome") or "")
                    obj_edit = st.text_area("Objetivo", value=equipe.get("objetivo") or "", height=90)
                    tarefas_edit = st.text_area("Tarefas — uma por linha", value="\\n".join(equipe.get("tarefas") or []), height=90)
                    resp_opts = {"Nenhum": None}
                    for c in ativos_colaboradores:
                        resp_opts[f"{c.get('nome', '')} — {c.get('funcao') or 'Sem função'}"] = c.get("id")
                    ids_resp = list(resp_opts.values())
                    atual_resp = equipe.get("responsavel_id")
                    idx_resp = ids_resp.index(atual_resp) if atual_resp in ids_resp else 0
                    resp_edit = st.selectbox("Responsável", list(resp_opts.keys()), index=idx_resp)
                    salvar_eq = st.form_submit_button("SALVAR ALTERAÇÕES", type="primary")
                if salvar_eq:
                    try:
                        client.table("almox_equipes").update({"nome": nome_edit.strip(), "objetivo": obj_edit.strip() or None, "tarefas": [x.strip() for x in tarefas_edit.splitlines() if x.strip()], "responsavel_id": resp_opts[resp_edit]}).eq("id", eid).execute()
                        registrar_historico("equipe_editada", f"Equipe editada: {nome_edit.strip()}", {"equipe_id": eid, "nome": nome_edit.strip()})
                        st.session_state.pop("editar_equipe_id", None)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao editar equipe: {e}")

    with tab_colaboradores:
        st.markdown('<div class="ge-tabs-note">Visual em cartões com foto, função, equipe e status, mantendo cadastro e edição completos abaixo.</div>', unsafe_allow_html=True)
        st.markdown('<div class="ge-form-panel">', unsafe_allow_html=True)
        equipes_opts = {x.get("nome", ""): x.get("id") for x in ativos_equipes}
        with st.form("form_novo_colaborador", clear_on_submit=True):
            cc1, cc2 = st.columns(2)
            with cc1:
                nome_colab = st.text_input("Nome completo *", placeholder="Nome do colaborador")
                matricula = st.text_input("Matrícula", placeholder="Matrícula / registro interno")
                funcao = st.text_input("Função / cargo", placeholder="Ex.: Almoxarife")
            with cc2:
                data_adm = st.date_input("Data de admissão", value=None, format="DD/MM/YYYY", key="data_adm_novo")
                equipe_label = st.selectbox("Equipe", ["Sem equipe"] + list(equipes_opts.keys()))
                foto_arquivo = st.file_uploader("Foto do colaborador *", type=["png", "jpg", "jpeg", "webp"], help="Inclua a foto do colaborador. Tamanho máximo: 2 MB.")
            criar_colab = st.form_submit_button("CADASTRAR COLABORADOR", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if criar_colab:
            nome_limpo = nome_colab.strip()
            mat = matricula.strip() or None
            if not nome_limpo:
                st.error("Informe o nome do colaborador.")
            elif mat and any((x.get("matricula") or "").strip().casefold() == mat.casefold() for x in colaboradores_raw):
                st.error("Essa matrícula já está cadastrada.")
            elif foto_arquivo is None:
                st.error("Inclua a foto do colaborador.")
            elif foto_arquivo.size > 2 * 1024 * 1024:
                st.error("A foto deve ter no máximo 2 MB.")
            else:
                try:
                    foto_bytes = foto_arquivo.getvalue()
                    foto_b64 = base64.b64encode(foto_bytes).decode("ascii")
                    novo = client.table("almox_colaboradores").insert({"nome": nome_limpo, "matricula": mat, "funcao": funcao.strip() or None, "data_admissao": data_adm.isoformat() if data_adm else None, "equipe_id": equipes_opts.get(equipe_label), "equipe_atual": equipe_label if equipe_label != "Sem equipe" else None, "foto_base64": foto_b64, "foto_mime": foto_arquivo.type or "image/jpeg", "foto_nome": foto_arquivo.name, "ativo": True}).execute().data
                    if novo:
                        registrar_historico("colaborador_criado", f"Colaborador criado: {nome_limpo}", {"colaborador_id": novo[0].get("id"), "nome": nome_limpo})
                        st.success(f"Colaborador '{nome_limpo}' cadastrado com sucesso.")
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro ao cadastrar colaborador: {e}")

        cf1, cf2 = st.columns([2, 1])
        with cf1:
            busca = st.text_input("Buscar colaborador", placeholder="Nome, matrícula ou função...", key="busca_colab")
        with cf2:
            status = st.selectbox("Status", ["Todos", "Ativos", "Inativos"], key="filtro_status_colab")
        filtrados = []
        for c in colaboradores_raw:
            texto = " ".join([str(c.get("nome") or ""), str(c.get("matricula") or ""), str(c.get("funcao") or "")]).casefold()
            ok = status == "Todos" or (status == "Ativos" and c.get("ativo", True)) or (status == "Inativos" and not c.get("ativo", True))
            if busca.strip().casefold() in texto and ok:
                filtrados.append(c)

        if filtrados:
            for base in range(0, len(filtrados), 5):
                cols = st.columns(5)
                for col,c in zip(cols,filtrados[base:base+5]):
                    eq_nome = nomes_eq.get(str(c.get("equipe_id")), c.get("equipe_atual") or "Sem equipe")
                    with col:
                        st.markdown(f'<div class="ge-person-card"><div class="ge-person-photo">{foto_html(c,66)}</div><div class="ge-person-name" title="{c.get("nome","")}">{nome_curto(c.get("nome"))}</div><div class="ge-person-role">{c.get("funcao") or "Sem função"}</div><div class="ge-person-team">{eq_nome}</div><div class="ge-person-status">{"ATIVO" if c.get("ativo",True) else "INATIVO"} · {c.get("matricula") or "sem matrícula"}</div></div>', unsafe_allow_html=True)
        else:
            st.info("Nenhum colaborador encontrado.")

        if filtrados:
            opcoes = {f"{c.get('nome', '')} — {c.get('matricula') or 'sem matrícula'}": c for c in filtrados}
            escolhido = opcoes[st.selectbox("Selecione um colaborador para ações", list(opcoes.keys()), key="colab_acao")]
            cid = str(escolhido.get("id"))
            ca, cb = st.columns(2)
            with ca:
                if st.button("EDITAR COLABORADOR", key=f"editar_colab_{cid}", use_container_width=True):
                    st.session_state["editar_colaborador_id"] = cid
                    st.rerun()
            with cb:
                if st.button("INATIVAR COLABORADOR" if escolhido.get("ativo", True) else "REATIVAR COLABORADOR", key=f"status_colab_{cid}", use_container_width=True):
                    try:
                        client.table("almox_colaboradores").update({"ativo": not escolhido.get("ativo", True)}).eq("id", cid).execute()
                        registrar_historico("colaborador_status", f"Status alterado: {escolhido.get('nome', '')}", {"colaborador_id": cid, "ativo": not escolhido.get("ativo", True)})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao alterar status: {e}")
            if st.session_state.get("editar_colaborador_id") == cid:
                with st.form(f"form_editar_colab_{cid}"):
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        nome_e = st.text_input("Nome completo", value=escolhido.get("nome") or "")
                        mat_e = st.text_input("Matrícula", value=escolhido.get("matricula") or "")
                        func_e = st.text_input("Função / cargo", value=escolhido.get("funcao") or "")
                    with ec2:
                        try:
                            data_val = pd.to_datetime(escolhido.get("data_admissao")).date() if escolhido.get("data_admissao") else None
                        except Exception:
                            data_val = None
                        data_e = st.date_input("Data de admissão", value=data_val, format="DD/MM/YYYY", key=f"data_edit_{cid}")
                        eqids = [None] + list(equipes_opts.values())
                        atual = escolhido.get("equipe_id")
                        idx = eqids.index(atual) if atual in eqids else 0
                        eq_e_label = st.selectbox("Equipe", ["Sem equipe"] + list(equipes_opts.keys()), index=idx, key=f"eq_edit_{cid}")
                        if escolhido.get("foto_base64"):
                            st.image(f"data:{escolhido.get('foto_mime') or 'image/jpeg'};base64,{escolhido['foto_base64']}", width=140)
                            st.caption(f"Foto atual: {escolhido.get('foto_nome') or 'arquivo salvo'}")
                        foto_e = st.file_uploader("Substituir foto", type=["png", "jpg", "jpeg", "webp"], help="Opcional. Se selecionar um arquivo, a foto atual será substituída.", key=f"foto_edit_{cid}")
                    salvar_c = st.form_submit_button("SALVAR COLABORADOR", type="primary")
                if salvar_c:
                    mat_e = mat_e.strip() or None
                    if not nome_e.strip():
                        st.error("O nome é obrigatório.")
                    elif mat_e and any(str(x.get("id")) != cid and (x.get("matricula") or "").strip().casefold() == mat_e.casefold() for x in colaboradores_raw):
                        st.error("Essa matrícula já está cadastrada para outro colaborador.")
                    else:
                        try:
                            eqid = equipes_opts.get(eq_e_label)
                            dados_update = {"nome": nome_e.strip(), "matricula": mat_e, "funcao": func_e.strip() or None, "data_admissao": data_e.isoformat() if data_e else None, "equipe_id": eqid, "equipe_atual": eq_e_label if eqid else None}
                            if foto_e is not None:
                                if foto_e.size > 2 * 1024 * 1024:
                                    st.error("A foto deve ter no máximo 2 MB.")
                                    st.stop()
                                dados_update.update({"foto_base64": base64.b64encode(foto_e.getvalue()).decode("ascii"), "foto_mime": foto_e.type or "image/jpeg", "foto_nome": foto_e.name})
                            client.table("almox_colaboradores").update(dados_update).eq("id", cid).execute()
                            registrar_historico("colaborador_editado", f"Colaborador editado: {nome_e.strip()}", {"colaborador_id": cid, "nome": nome_e.strip()})
                            st.session_state.pop("editar_colaborador_id", None)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao editar colaborador: {e}")

elif pagina == "carreira":
    st.markdown(f'<div class="section">{txt("secao_plano")}</div>', unsafe_allow_html=True)
    st.info(txt("mensagem_carreira"))

elif pagina == "configuracoes":
    st.markdown(f'<div class="section">{txt("secao_configuracoes")}</div>', unsafe_allow_html=True)
    st.write("As configurações abaixo ficam salvas no Supabase e são carregadas novamente quando o aplicativo abre.")

    st.markdown("### Personalização de textos")
    st.caption("Edite os nomes dos menus, títulos, subtítulo e seções. As alterações ficam salvas no Supabase.")
    novo_textos = textos.copy()
    novo_fontes = fontes.copy()
    pc1, pc2 = st.columns(2)

    with pc1:
        st.markdown("**Menus da barra lateral**")
        for _id, _rotulo in [
            ("dashboard", "Dashboard"), ("indicadores", "Alimentar Indicadores"),
            ("historico", "Histórico"), ("equipes", "Gestão de Equipes"),
            ("carreira", "Plano de Carreira"), ("configuracoes", "Configurações")
        ]:
            _chave = "menu_" + _id
            novo_textos[_chave] = st.text_input(_rotulo, value=textos[_chave], key="edit_" + _chave)

        st.markdown("**Títulos das páginas**")
        for _id, _rotulo in [
            ("dashboard", "Título Dashboard"), ("indicadores", "Título Alimentar Indicadores"),
            ("historico", "Título Histórico"), ("equipes", "Título Gestão de Equipes"),
            ("carreira", "Título Plano de Carreira"), ("configuracoes", "Título Configurações")
        ]:
            _chave = "titulo_" + _id
            novo_textos[_chave] = st.text_input(_rotulo, value=textos[_chave], key="edit_" + _chave)

    with pc2:
        st.markdown("**Subtítulos e seções**")
        novo_textos["subtitulo_global"] = st.text_input("Subtítulo principal", value=textos["subtitulo_global"], key="edit_subtitulo_global")
        for _chave, _rotulo in [
            ("secao_dados_reais", "Seção: Dados reais"), ("secao_indicadores", "Seção: Indicadores"),
            ("secao_historico", "Seção: Histórico"), ("secao_colaboradores", "Seção: Colaboradores"),
            ("secao_equipes", "Seção: Equipes"), ("secao_organograma", "Seção: Organograma"),
            ("secao_plano", "Seção: Plano de carreira"),
        ]:
            novo_textos[_chave] = st.text_input(_rotulo, value=textos[_chave], key="edit_" + _chave)

        st.markdown("**Fontes**")
        fonte_index = {x: i for i, x in enumerate(FONTES)}
        novo_fontes["menu"] = st.selectbox("Fonte dos menus", FONTES, index=fonte_index.get(fontes.get("menu"), 0), key="font_menu")
        novo_fontes["titulo"] = st.selectbox("Fonte dos títulos", FONTES, index=fonte_index.get(fontes.get("titulo"), 0), key="font_titulo")
        novo_fontes["subtitulo"] = st.selectbox("Fonte dos subtítulos", FONTES, index=fonte_index.get(fontes.get("subtitulo"), 0), key="font_subtitulo")

    if st.button("SALVAR TEXTOS E FONTES", type="primary", use_container_width=True):
        novo = config.copy()
        novo["textos"] = novo_textos
        novo["fontes"] = novo_fontes
        try:
            if salvar_configuracoes(novo):
                st.session_state.config = novo
                st.success("Textos e fontes salvos no Supabase.")
                st.rerun()
            else:
                st.error("Não foi possível salvar textos e fontes.")
        except Exception as e:
            st.error(f"Erro ao salvar textos e fontes: {e}")

    st.markdown("---")
    st.markdown("### Aparência")
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

st.markdown(f"<br><div class='muted'>{txt('rodape_linha3')}</div>", unsafe_allow_html=True)
