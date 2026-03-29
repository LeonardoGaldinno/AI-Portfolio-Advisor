import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from openai import OpenAI
from supabase_client import supabase

# ── CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WealthAI",
    page_icon="📊",
    layout="wide"
)

load_dotenv()
client = OpenAI(api_key="")

# ── AUTH ─────────────────────────────────────────────────────────────────
if "user" not in st.session_state or st.session_state.user is None:
    st.warning("Você precisa estar logado.")
    st.stop()

# ── CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

html, body {
    font-family: 'Inter', sans-serif;
    background-color: #f8fafc;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: white;
    border-right: 1px solid #e5e7eb;
}

/* Title */
.title {
    font-size: 2rem;
    font-weight: 600;
    color: #0f172a;
}

.subtitle {
    color: #64748b;
    margin-bottom: 20px;
}

/* Card */
.card {
    background: white;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #eef2f7;
    box-shadow: 0 6px 18px rgba(0,0,0,0.04);
}

/* KPI */
.kpi {
    font-size: 1.6rem;
    font-weight: 600;
}

/* Section */
.section {
    font-size: 1.2rem;
    font-weight: 600;
    margin-top: 25px;
    margin-bottom: 10px;
}

/* Button */
.stButton > button {
    background: #2563eb;
    color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ────────────────────────────────────────────────────────────
def load_data():
    user_id = st.session_state.user.id

    perfil = supabase.table("perfis").select("perfil").eq("user_id", user_id).execute()
    ativos = supabase.table("ativos").select("*").eq("user_id", user_id).execute()

    perfil = perfil.data[0]["perfil"] if perfil.data else "Não definido"
    ativos = ativos.data or []

    return perfil, ativos

perfil, ativos = load_data()

if not ativos:
    st.warning("Adicione ativos.")
    st.stop()

# ── PROCESS ──────────────────────────────────────────────────────────────
data = []
total = 0

for a in ativos:
    valor = a["quantidade"] * a["preco_medio"]
    total += valor
    data.append({
        "Ticker": a["ticker"],
        "Valor": valor
    })

df = pd.DataFrame(data)
df["%"] = df["Valor"] / total * 100

# ── MÉTRICAS AVANÇADAS ───────────────────────────────────────────────────
concentracao = df["%"].max()
diversificacao = len(df)

if concentracao > 40:
    risco = "Alto"
elif concentracao > 25:
    risco = "Médio"
else:
    risco = "Baixo"

# ── SIDEBAR (APP NAV) ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 WealthAI")
    page = st.radio("", ["Dashboard", "Insights", "AI Advisor"])

    st.markdown("---")
    st.markdown("### Perfil")
    st.write(perfil)

# ── HEADER ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div class='title'>Wealth Dashboard</div>
<div class='subtitle'>Visão estratégica da sua carteira</div>
""", unsafe_allow_html=True)

# ── DASHBOARD ────────────────────────────────────────────────────────────
if page == "Dashboard":

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💰 Total", f"R$ {total:,.0f}")
    col2.metric("📦 Ativos", len(df))
    col3.metric("⚠️ Concentração", f"{concentracao:.1f}%")
    col4.metric("🧠 Risco", risco)

    st.markdown("<div class='section'>Alocação</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        fig = px.pie(df, values="Valor", names="Ticker", hole=0.6)
        st.plotly_chart(fig, use_container_width=True)

    # setores
    setores = {}
    for a in ativos:
        try:
            sector = yf.Ticker(a["ticker"]).info.get("sector", "Desconhecido")
        except:
            sector = "Desconhecido"

        valor = a["quantidade"] * a["preco_medio"]
        setores[sector] = setores.get(sector, 0) + valor

    setor_df = pd.DataFrame(setores.items(), columns=["Setor", "Valor"])

    with col2:
        fig2 = px.bar(setor_df, x="Setor", y="Valor", color="Valor")
        st.plotly_chart(fig2, use_container_width=True)

# ── INSIGHTS ─────────────────────────────────────────────────────────────
elif page == "Insights":

    st.markdown("<div class='section'>Diagnóstico automático</div>", unsafe_allow_html=True)

    if concentracao > 40:
        st.error("Carteira muito concentrada")
    elif concentracao > 25:
        st.warning("Concentração moderada")
    else:
        st.success("Boa diversificação")

    if diversificacao < 5:
        st.warning("Pouca diversificação")

# ── AI ADVISOR ───────────────────────────────────────────────────────────
elif page == "AI Advisor":

    st.markdown("<div class='section'>Análise com IA</div>", unsafe_allow_html=True)

    if st.button("Gerar análise"):
        with st.spinner("Analisando carteira..."):

            carteira = "\n".join([f"{r['Ticker']}" for _, r in df.iterrows()])

            prompt = f"""
Perfil: {perfil}

Carteira:
{carteira}

Analise como gestor profissional, forneça insights considerando cenário geopolítico e econômico atual e sugira alocações e/ou uma carteira melhor.
"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )

            st.markdown(f"""
            <div class='card'>
            {response.choices[0].message.content}
            </div>
            """, unsafe_allow_html=True)