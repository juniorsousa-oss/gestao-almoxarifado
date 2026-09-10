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
[data-testid="stToolbar"]{{display:flex !important;align-items:center !important;}}
button[data-testid="stSidebarCollapseButton"]{{display:flex !important;visibility:visible !important;pointer-events:auto !important;position:fixed !important;top:25px !important;left:8px !important;right:auto !important;z-index:2147483647 !important;width:40px !important;height:34px !important;min-width:40px !important;min-height:34px !important;padding:0 !important;margin:0 !important;border-radius:8px !important;border:1px solid {BORDER} !important;background:#ffffff !important;color:#1f2937 !important;box-shadow:0 1px 4px rgba(0,0,0,.18) !important;}}
button[data-testid="stSidebarCollapseButton"]:hover{{background:{PRIMARY} !important;color:#111111 !important;border-color:{PRIMARY} !important;}}
button[data-testid="stSidebarCollapseButton"] svg{{width:20px !important;height:20px !important;}}
div[data-testid="collapsedControl"]{{position:fixed !important;top:25px !important;left:8px !important;right:auto !important;bottom:auto !important;inset-inline-start:8px !important;inset-inline-end:auto !important;z-index:2147483647 !important;width:40px !important;height:34px !important;margin:0 !important;padding:0 !important;transform:none !important;}}
div[data-testid="collapsedControl"] button{{display:flex !important;visibility:visible !important;pointer-events:auto !important;position:static !important;width:40px !important;height:34px !important;min-width:40px !important;min-height:34px !important;padding:0 !important;margin:0 !important;border-radius:8px !important;border:1px solid {BORDER} !important;background:#ffffff !important;color:#1f2937 !important;box-shadow:0 1px 4px rgba(0,0,0,.18) !important;}}
div[data-testid="collapsedControl"] button:hover{{background:{PRIMARY} !important;color:#111111 !important;border-color:{PRIMARY} !important;}}
div[data-testid="collapsedControl"] svg{{width:20px !important;height:20px !important;}}
div.st-key-controle_unico_menus{{display:none !important;}}
header[data-testid="stHeader"]{{background:transparent !important;}}
section[data-testid="stSidebar"]{{background:{SIDEBAR_BG} !important;border-right:1px solid {BORDER};width:230px !important;min-width:230px !important;max-width:230px !important;overflow:hidden !important;}}
section[data-testid="stSidebar"] > div:first-child{{width:230px !important;min-width:230px !important;padding:1px 9px 20px;overflow:hidden !important;}}
section[data-testid="stSidebar"][aria-expanded="false"]{{width:0 !important;min-width:0 !important;max-width:0 !important;}}
section[data-testid="stSidebar"][aria-expanded="false"] > div:first-child{{width:0 !important;min-width:0 !important;padding:0 !important;}}
.stApp{{background:{APP_BG};color:{TEXT}}}
.block-container{{max-width:1500px;padding:38px 34px 50px}}
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
.sidebar-logo-section{{width:100%;display:flex;flex-direction:column;align-items:center;margin:-35px 0 8px;padding:0 0 9px;border-bottom:1px solid {BORDER}}}
.sidebar-logo-wrap{{width:190px;height:82px;box-sizing:border-box;display:flex;justify-content:center;align-items:center;background:var(--logo-bg);border:1px solid #e5e7eb;border-radius:12px;padding:6px;box-shadow:0 1px 3px rgba(0,0,0,.08);overflow:hidden}}
.sidebar-logo-img{{display:block;max-width:176px;max-height:70px;width:auto;height:auto;object-fit:contain;margin:auto}}
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
    logo_bg = "#101513" if IS_LIGHT else "#ffffff"
    if logo_b64:
        mime = config.get("logo_mime") or "image/png"
        logo_html = f'<img class="sidebar-logo-img" src="data:{mime};base64,{logo_b64}" alt="Logo SETTA">'
    else:
        logo_html = '<div class="sidebar-logo-placeholder">SUA LOGO AQUI<br>Configure em Configurações</div>'
    st.markdown(f'<div class="sidebar-logo-section"><div class="sidebar-logo-wrap" style="--logo-bg:{logo_bg};">{logo_html}</div></div>', unsafe_allow_html=True)
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
    colaboradores = df(rows("almox_colaboradores"))
    equipes = df(rows("almox_equipes"))
    org = df(rows("almox_organograma"))
    a,b,c = st.columns(3)
    a.metric(txt("secao_colaboradores"),len(colaboradores)); b.metric(txt("secao_equipes"),len(equipes)); c.metric(txt("secao_organograma"),len(org))
    st.markdown(f'<div class="section">{txt("secao_colaboradores")}</div>', unsafe_allow_html=True); st.dataframe(colaboradores,use_container_width=True,hide_index=True)
    st.markdown(f'<div class="section">{txt("secao_equipes")}</div>', unsafe_allow_html=True); st.dataframe(equipes,use_container_width=True,hide_index=True)
    st.markdown(f'<div class="section">{txt("secao_organograma")}</div>', unsafe_allow_html=True); st.dataframe(org,use_container_width=True,hide_index=True)

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
