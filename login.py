import streamlit as st
from auth import login, register
from supabase_client import supabase, get_authenticated_client

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background-color: #0a0f1e; }

.stButton > button {
    width: 100%;
    background: #1a56db;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s;
    margin-top: 8px;
}
.stButton > button:hover { background: #1e40af; border: none; }

.stTextInput > div > div > input {
    background: #0d1526 !important;
    border: 1px solid #1f2d45 !important;
    border-radius: 8px !important;
    color: #d1daf0 !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 10px 14px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #1a56db !important;
    box-shadow: 0 0 0 2px rgba(26,86,219,0.2) !important;
}

label[data-testid="stWidgetLabel"] p {
    color: #6b82a8 !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
}

.stRadio > div {
    flex-direction: row !important;
    gap: 8px !important;
    background: #0d1526;
    border-radius: 8px;
    padding: 4px;
    width: 200px;
}
.stRadio > div > label {
    flex: 1;
    text-align: center;
    background: transparent;
    border-radius: 6px;
    padding: 6px 0;
    color: #4a6080 !important;
    font-size: 0.88rem !important;
    cursor: pointer;
    transition: all 0.15s;
}
.stRadio > div > label:has(input:checked) {
    background: #1a56db !important;
    color: white !important;
}
.stRadio > div > label > div:first-child { display: none; }

.success-msg {
    background: #052e16;
    border: 1px solid #166534;
    border-radius: 8px;
    padding: 12px 16px;
    color: #4ade80;
    font-size: 0.88rem;
    margin-top: 16px;
}
.error-msg {
    background: #1c0a0a;
    border: 1px solid #7f1d1d;
    border-radius: 8px;
    padding: 12px 16px;
    color: #f87171;
    font-size: 0.88rem;
    margin-top: 16px;
}
.divider {
    border: none;
    border-top: 1px solid #1f2d45;
    margin: 16px 0;
}
</style>
""", unsafe_allow_html=True)


def show_message():
    if st.session_state.get("msg"):
        css_class = "success-msg" if st.session_state.msg_type == "success" else "error-msg"
        st.markdown(f'<div class="{css_class}">{st.session_state.msg}</div>', unsafe_allow_html=True)
        st.session_state.msg = None
        st.session_state.msg_type = None


def salvar_dados_usuario(user_id, nome, sobrenome, telefone, session=None):
    client = get_authenticated_client(session) if session else supabase
    client.table("usuarios").upsert({
        "user_id": user_id,
        "nome": nome,
        "sobrenome": sobrenome,
        "telefone": telefone
    }, on_conflict="user_id").execute()


# ── Cabeçalho ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 48px 0 32px 0;">
    <p style="font-family:'DM Serif Display',serif; font-size:2.2rem; color:#f0f4ff; margin:0;">📈 Investment Analyst</p>
    <p style="font-size:0.88rem; color:#4a6080; margin:8px 0 0 0;">Análise de ações com inteligência artificial</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    mode = st.radio("Modo", ["Entrar", "Cadastrar"], horizontal=True, label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)

    # ── LOGIN ──────────────────────────────────────────────────────────────────
    if mode == "Entrar":
        email    = st.text_input("E-mail", placeholder="seu@email.com")
        password = st.text_input("Senha", type="password", placeholder="••••••••")

        if st.button("Entrar na conta", use_container_width=True):
            if email and password:
                try:
                    result = login(email, password)
                    st.session_state.user = result.user
                    st.session_state.session = result.session
                    st.rerun()
                except Exception as e:
                    erro = str(e)
                    if "Email not confirmed" in erro:
                        st.session_state.msg = "⚠️ Confirme seu e-mail antes de entrar. Verifique sua caixa de entrada."
                    elif "Invalid login credentials" in erro:
                        st.session_state.msg = "❌ E-mail ou senha incorretos."
                    elif "User already registered" in erro:
                        st.session_state.msg = "⚠️ Este e-mail já está cadastrado. Tente entrar."
                    elif "rate limit" in erro.lower():
                        st.session_state.msg = "⏳ Muitas tentativas. Aguarde alguns minutos."
                    else:
                        st.session_state.msg = f"Erro: {erro}"
                    st.session_state.msg_type = "error"
                    st.rerun()
            else:
                st.session_state.msg = "⚠️ Preencha e-mail e senha."
                st.session_state.msg_type = "error"
                st.rerun()

    # ── CADASTRO ───────────────────────────────────────────────────────────────
    else:
        col_n1, col_n2 = st.columns(2)
        with col_n1:
            nome     = st.text_input("Nome", placeholder="João")
        with col_n2:
            sobrenome = st.text_input("Sobrenome", placeholder="Silva")

        email    = st.text_input("E-mail", placeholder="seu@email.com")
        telefone = st.text_input("Telefone", placeholder="(11) 99999-9999")

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        password  = st.text_input("Senha", type="password", placeholder="Mínimo 6 caracteres")
        password2 = st.text_input("Confirmar senha", type="password", placeholder="Repita a senha")

        if st.button("Criar conta", use_container_width=True):
            # Validações
            if not all([nome, sobrenome, email, password, password2]):
                st.session_state.msg = "⚠️ Preencha todos os campos obrigatórios."
                st.session_state.msg_type = "error"
                st.rerun()
            elif len(password) < 6:
                st.session_state.msg = "⚠️ A senha deve ter pelo menos 6 caracteres."
                st.session_state.msg_type = "error"
                st.rerun()
            elif password != password2:
                st.session_state.msg = "❌ As senhas não coincidem."
                st.session_state.msg_type = "error"
                st.rerun()
            else:
                try:
                    # 1. Criar conta
                    register(email, password)
                    # 2. Login temporário só para salvar dados extras (não loga o usuário)
                    result_login = login(email, password)
                    salvar_dados_usuario(result_login.user.id, nome, sobrenome, telefone, session=result_login.session)
                    # 3. Deslogar — usuário deve fazer login manualmente
                    supabase.auth.sign_out()
                    st.session_state.msg = "✅ Conta criada com sucesso! Faça login para continuar."
                    st.session_state.msg_type = "success"
                    st.rerun()
                except Exception as e:
                    erro = str(e)
                    if "User already registered" in erro:
                        st.session_state.msg = "⚠️ Este e-mail já está cadastrado. Tente entrar."
                    elif "invalid email" in erro.lower():
                        st.session_state.msg = "❌ E-mail inválido."
                    elif "Password should be" in erro:
                        st.session_state.msg = "⚠️ Senha não atende aos requisitos mínimos."
                    elif "rate limit" in erro.lower():
                        st.session_state.msg = "⏳ Muitas tentativas. Aguarde alguns minutos."
                    else:
                        st.session_state.msg = f"Erro: {erro}"
                    st.session_state.msg_type = "error"
                    st.rerun()

    show_message()