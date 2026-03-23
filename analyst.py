import streamlit as st
import yfinance as yf
import os
from dotenv import load_dotenv
from openai import OpenAI
from supabase_client import supabase

st.set_page_config(page_title="AI Investment Analyst", page_icon="📊", layout="centered")

if "user" not in st.session_state or st.session_state.user is None:
    st.warning("Você precisa estar logado.")
    st.stop()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600&family=DM+Serif+Display&display=swap');
html, body, [class*="css"] { font-family: 'Sora', sans-serif; }
.stApp { background-color: #080d1a; }
.stTextInput > div > div > input {
    background: #0d1a2e !important; border: 1px solid #1e3a5f !important;
    border-radius: 8px !important; color: #d1daf0 !important;
}
.stButton > button {
    background: #1a56db; color: white; border: none;
    border-radius: 8px; font-family: 'Sora', sans-serif; font-weight: 500;
}
.card { background: #0d1a2e; border: 1px solid #1e3a5f; border-radius: 16px; padding: 24px; margin-bottom: 16px; }
label[data-testid="stWidgetLabel"] p { color: #6b82a8 !important; font-size: 0.8rem !important; text-transform: uppercase !important; letter-spacing: 0.05em !important; }
</style>
""", unsafe_allow_html=True)

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

# ── Carregar perfil e carteira do usuário ─────────────────────────────────────
def carregar_contexto_usuario():
    user_id = st.session_state.user.id
    perfil_res = supabase.table("perfis").select("perfil").eq("user_id", user_id).execute()
    ativos_res = supabase.table("ativos").select("*").eq("user_id", user_id).execute()
    perfil = perfil_res.data[0]["perfil"] if perfil_res.data else "Não definido"
    ativos = ativos_res.data or []
    return perfil, ativos

perfil, ativos = carregar_contexto_usuario()

# ── Cabeçalho ─────────────────────────────────────────────────────────────────
st.markdown('<p style="font-family:\'DM Serif Display\',serif; font-size:1.8rem; color:#e8f4ff; margin-bottom:4px;">📊 AI Investment Analyst</p>', unsafe_allow_html=True)
st.markdown(f'<p style="color:#4a7090; font-size:0.88rem; margin-bottom:24px;">Perfil do investidor: <strong style="color:#7dd3fc;">{perfil}</strong></p>', unsafe_allow_html=True)

# ── Contexto da carteira ──────────────────────────────────────────────────────
carteira_texto = ""
if ativos:
    linhas = [f"- {a['ticker']}: {a['quantidade']:.0f} cotas a R$ {a['preco_medio']:.2f} (total: R$ {a['quantidade']*a['preco_medio']:,.2f})" for a in ativos]
    carteira_texto = "\n".join(linhas)
    total = sum(a['quantidade'] * a['preco_medio'] for a in ativos)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:0.75rem; color:#2d6aad; font-weight:600; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:12px;">Carteira atual</p>', unsafe_allow_html=True)
    for a in ativos:
        t = a['quantidade'] * a['preco_medio']
        pct = t / total * 100
        st.markdown(f'<div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #1e3a5f; font-size:0.85rem; color:#a8c4e0;"><span style="color:#7dd3fc; font-weight:600;">{a["ticker"]}</span><span>R$ {t:,.2f} ({pct:.1f}%)</span></div>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align:right; font-size:0.85rem; color:#4a7090; margin-top:10px;">Total: <strong style="color:#7dd3fc;">R$ {total:,.2f}</strong></p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Análise de ativo ──────────────────────────────────────────────────────────
st.markdown("---")
ticker_input = st.text_input("Digite o ticker para análise", placeholder="Ex: PETR4.SA, AAPL, ITUB4.SA")

if ticker_input:
    with st.spinner("Buscando dados e gerando análise..."):
        try:
            stock = yf.Ticker(ticker_input)
            info = stock.info
            data = {
                "company":    info.get("longName"),
                "sector":     info.get("sector"),
                "market_cap": info.get("marketCap"),
                "pe_ratio":   info.get("trailingPE"),
                "revenue":    info.get("totalRevenue"),
                "roe":        info.get("returnOnEquity"),
                "debt_equity":info.get("debtToEquity"),
                "dividend":   info.get("dividendYield"),
                "price":      info.get("currentPrice"),
                "52w_high":   info.get("fiftyTwoWeekHigh"),
                "52w_low":    info.get("fiftyTwoWeekLow"),
            }

            prompt = f"""
Você é um analista de investimentos profissional especializado no mercado brasileiro.

PERFIL DO INVESTIDOR: {perfil}
{"CARTEIRA ATUAL DO INVESTIDOR:" + chr(10) + carteira_texto if carteira_texto else "O investidor ainda não possui carteira cadastrada."}

DADOS DA EMPRESA A ANALISAR:
{data}

Com base no perfil do investidor e na carteira atual, forneça uma análise completa em português (Brasil) com:

1. **Visão Geral** — o que a empresa faz
2. **Modelo de Negócios** — como gera receita
3. **Snapshot Financeiro** — principais métricas e o que significam
4. **Riscos** — principais riscos para este investidor especificamente
5. **Tese de Investimento** — se este ativo faz sentido para o perfil {perfil}, considerando a carteira atual

Seja direto, objetivo e personalize a análise para o perfil {perfil}.
"""

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )

            st.markdown("---")
            st.markdown(f'<p style="font-family:\'DM Serif Display\',serif; font-size:1.4rem; color:#e8f4ff; margin-bottom:4px;">Análise: {data.get("company", ticker_input)}</p>', unsafe_allow_html=True)
            st.markdown(response.choices[0].message.content)

        except Exception as e:
            st.error(f"Erro ao analisar: {str(e)}")