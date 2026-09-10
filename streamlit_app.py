import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Gestão Almoxarifado",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

APP_URL = "https://gestao-almoxarifado-two.vercel.app"

st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0 !important; max-width: 100% !important;}
    iframe {border: 0 !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

components.iframe(APP_URL, height=1100, scrolling=True)
