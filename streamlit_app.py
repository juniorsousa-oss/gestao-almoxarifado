import streamlit as st
from datetime import date
import pandas as pd

st.set_page_config(
    page_title="Gestão Almoxarifado",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# ESTILO — primeira versão nativa do Gestão em Streamlit
# ============================================================
st.markdown(
    """
    <style>
    #MainMenu, footer, header {visibility:hidden;}
    .stApp { background:#0b0f0e; color:#f4f5f4; }
    [data-testid="stSidebar"] { background:#090c0b; border-right:1px solid #252b28; }
    [data-testid="stSidebar"] * { color:#dfe4e1; }
    .block-container { max-width:1500px; padding:28px 34px 50px; }
    .brand { font-size:28px; font-weight:900; letter-spacing:-1px; padding:8px 4px 20px; border-bottom:1px solid #1e2522; margin-bottom:18px; }
    .brand span { color:#ffd20a; }
    .hero { display:flex; justify-content:space-between; align-items:center; margin-bottom:24px; }
    .hero h1 { margin:0; font-size:30px; }
    .hero p { margin:5px 0 0; color:#9aa39f; }
    .period { background:#ffd20a; color:#111; padding:10px 15px; border-radius:9px; font-weight:800; }
    .section { color:#ffd20a; font-size:14px; font-weight:900; letter-spacing:1px; text-transform:uppercase; margin:22px 0 10px; }
    .card { background:linear-gradient(145deg,#141a17,#101513); border:1px solid #35403b; border-radius:15px; padding:18px; min-height:125px; }
    .label { color:#aeb6b2; font-size:10px; font-weight:800; text-transform:uppercase; letter-spacing:.5px; }
    .value { color:#fff; font-size:30px; font-weight:900; margin-top:12px; }
    .sub { color:#9aa39f; font-size:11px; margin-top:5px; }
    .panel { background:linear-gradient(145deg,#141a17,#101513); border:1px solid #35403b; border-radius:15px; padding:19px; margin-top:14px; }
    .panel-title { font-weight:900; font-size:14px; }
    .muted { color:#9aa39f; font-size:11px; }
    .notice { padding:12px 14px; border-left:3px solid #ffd20a; background:#171d1a; color:#c7ceca; border-radius:7px; font-size:11px; }
    div[data-testid="stMetric"] { background:linear-gradient(145deg,#141a17,#101513); border:1px solid #35403b; padding:15px; border-radius:12px; }
    div[data-testid="stMetricLabel"] { color:#aeb6b2; }
    div[data-testid="stMetricValue"] { color:#fff; }
    .stButton button { border:1px solid #424b46; background:#171d1a; color:#d4d8d6; border-radius:8px; font-weight:800; }
    .stButton button:hover { border-color:#ffd20a; color:#ffd20a; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# ESTADO DA NAVEGAÇÃO
# ============================================================
if "pagina" not in st.session_state:
    st.session_state.pagina = "Dashboard"

paginas = [
    "Dashboard",
    "Alimentar Indicadores",
    "Histórico",
    "Gestão de Equipes",
    "Plano de Carreira",
    "Configurações",
]

with st.sidebar:
    st.markdown('<div class="brand">GESTÃO<span>.</span></div>', unsafe_allow_html=True)
    for pagina in paginas:
        if st.button(pagina, use_container_width=True, type="primary" if st.session_state.pagina == pagina else "secondary"):
            st.session_state.pagina = pagina
            st.rerun()
    st.markdown("<br><div class='muted'>Gestão Almoxarifado<br>Versão Streamlit — migração em andamento</div>", unsafe_allow_html=True)

pagina = st.session_state.pagina

# ============================================================
# CABEÇALHO
# ============================================================
st.markdown(
    f"""
    <div class="hero">
      <div><h1>{pagina}</h1><p>Gestão operacional do almoxarifado</p></div>
      <div class="period">{date.today().strftime('%d/%m/%Y')}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# DASHBOARD
# ============================================================
if pagina == "Dashboard":
    st.markdown('<div class="section">Indicadores principais</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Acuracidade do estoque", "98,4%", "+1,2%")
    c2.metric("Atendimentos", "1.248", "+8,5%")
    c3.metric("Pendências", "17", "-12,0%")
    c4.metric("Tempo médio", "18 min", "-6,3%")

    st.markdown('<div class="section">Desempenho</div>', unsafe_allow_html=True)
    left, right = st.columns([1.7, 1])
    with left:
        st.markdown('<div class="panel"><div class="panel-title">Evolução dos indicadores</div><div class="muted">Estrutura preparada para receber os dados reais do Supabase.</div></div>', unsafe_allow_html=True)
        dados = pd.DataFrame({
            "Período": ["Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6"],
            "Acuracidade": [94, 95, 96, 96.8, 97.5, 98.4],
            "Meta": [95, 95, 95, 95, 95, 95],
        }).set_index("Período")
        st.line_chart(dados)
    with right:
        st.markdown('<div class="panel"><div class="panel-title">Resumo operacional</div></div>', unsafe_allow_html=True)
        st.write("**Ordens atendidas** — 1.248")
        st.progress(0.91)
        st.write("**Inventário conferido** — 86%")
        st.progress(0.86)
        st.write("**Pendências resolvidas** — 78%")
        st.progress(0.78)

    st.markdown('<div class="section">Status</div>', unsafe_allow_html=True)
    st.info("A camada visual nativa está pronta. O próximo estágio é conectar estes componentes às tabelas reais do Supabase, preservando os dados existentes.")

# ============================================================
# ALIMENTAR INDICADORES
# ============================================================
elif pagina == "Alimentar Indicadores":
    st.markdown('<div class="notice">Cadastre os resultados dos indicadores. Nesta etapa os campos já estão estruturados para receber a persistência no banco.</div>', unsafe_allow_html=True)
    st.markdown('<div class="section">Novo lançamento</div>', unsafe_allow_html=True)
    with st.form("indicador_form"):
        c1, c2 = st.columns(2)
        with c1:
            indicador = st.selectbox("Indicador", ["Acuracidade do estoque", "Atendimentos", "Pendências", "Tempo médio"])
            periodo = st.date_input("Data", value=date.today())
        with c2:
            valor = st.number_input("Valor", min_value=0.0, step=0.1)
            meta = st.number_input("Meta", min_value=0.0, step=0.1)
        observacao = st.text_area("Observação")
        if st.form_submit_button("Salvar indicador"):
            st.success("Lançamento validado na interface. A persistência no Supabase será conectada na próxima etapa.")

# ============================================================
# HISTÓRICO
# ============================================================
elif pagina == "Histórico":
    st.markdown('<div class="section">Histórico de indicadores</div>', unsafe_allow_html=True)
    historico = pd.DataFrame({
        "Data": ["10/09/2026", "03/09/2026", "27/08/2026", "20/08/2026"],
        "Indicador": ["Acuracidade", "Acuracidade", "Atendimentos", "Pendências"],
        "Valor": [98.4, 97.5, 1180, 19],
        "Meta": [95, 95, 1100, 25],
        "Status": ["Dentro da meta", "Dentro da meta", "Dentro da meta", "Dentro da meta"],
    })
    st.dataframe(historico, use_container_width=True, hide_index=True)

# ============================================================
# GESTÃO DE EQUIPES
# ============================================================
elif pagina == "Gestão de Equipes":
    st.markdown('<div class="section">Equipe</div>', unsafe_allow_html=True)
    equipe = pd.DataFrame({
        "Colaborador": ["Colaborador 01", "Colaborador 02", "Colaborador 03", "Colaborador 04"],
        "Função": ["Almoxarife", "Almoxarife", "Conferente", "Auxiliar"],
        "Status": ["Ativo", "Ativo", "Ativo", "Ativo"],
    })
    st.dataframe(equipe, use_container_width=True, hide_index=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="panel"><div class="panel-title">Organograma</div><p class="muted">Responsável → liderança → equipe operacional.</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="panel"><div class="panel-title">Ações</div></div>', unsafe_allow_html=True)
        st.button("Adicionar colaborador")
        st.button("Editar equipe")

# ============================================================
# PLANO DE CARREIRA
# ============================================================
elif pagina == "Plano de Carreira":
    st.markdown('<div class="section">Desenvolvimento</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Colaboradores", "4")
    c2.metric("Planos ativos", "4")
    c3.metric("Progresso médio", "72%")
    st.markdown('<div class="panel"><div class="panel-title">Matriz de desenvolvimento</div></div>', unsafe_allow_html=True)
    carreira = pd.DataFrame({
        "Colaborador": ["Colaborador 01", "Colaborador 02", "Colaborador 03", "Colaborador 04"],
        "Nível atual": ["I", "I", "II", "I"],
        "Próximo nível": ["II", "II", "III", "II"],
        "Progresso": [80, 65, 75, 68],
    })
    st.dataframe(carreira, use_container_width=True, hide_index=True)

# ============================================================
# CONFIGURAÇÕES
# ============================================================
else:
    st.markdown('<div class="section">Configurações</div>', unsafe_allow_html=True)
    st.checkbox("Atualização automática dos dados", value=True)
    st.checkbox("Exibir indicadores de meta", value=True)
    st.selectbox("Formato de data", ["DD/MM/AAAA", "AAAA-MM-DD"])
    st.info("As configurações específicas do aplicativo atual serão mapeadas durante a migração das funcionalidades.")

st.markdown("<br><div class='muted'>Gestão Almoxarifado • Streamlit • camada nativa em desenvolvimento</div>", unsafe_allow_html=True)
