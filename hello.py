import streamlit as st
from auth import login, register

st.set_page_config(page_title="Investment Analyst", page_icon="📈", layout="centered")

def init_session():
    if "user" not in st.session_state:
        st.session_state.user = None
    if "msg" not in st.session_state:
        st.session_state.msg = None
    if "msg_type" not in st.session_state:
        st.session_state.msg_type = None

init_session()

login_page   = st.Page("login.py",    title="Login",              icon="🔐", default=True)
perfil_page  = st.Page("page2.py",    title="Meu Perfil",         icon="👤")
analyst_page = st.Page("analyst.py",  title="Investment Analyst", icon="📊")

if st.session_state.user is None:
    pg = st.navigation([login_page], position="hidden")
else:
    pg = st.navigation([perfil_page, analyst_page])

pg.run()