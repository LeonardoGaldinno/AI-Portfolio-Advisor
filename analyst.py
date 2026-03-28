import streamlit as st
import yfinance as yf
import os
from dotenv import load_dotenv
from openai import OpenAI
from supabase_client import supabase

# ── Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="AI Portfolio Strategist", page_icon="📊", layout="centered")

load_dotenv()
client = ""

# ── Auth check ───────────────────────────────────────────────────────────
if "user" not in st.session_state or st.session_state.user is None:
    st.warning("Você precisa estar logado.")
    st.stop()

# ── CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600&family=DM+Serif+Display&display=swap');
html, body, [class*="css"] { font-family: 'Sora', sans-serif; }
.stApp { background-color: #080d1a; }
.stButton > button {
    background: #1a56db; color: white;
    border-radius: 8px; font-weight: 500;
}
.card {
    background: #0d1a2e;
    border: 1px solid #1e3a5f;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

# ── Load user data ───────────────────────────────────────────────────────
def carregar_contexto_usuario():
    user_id = st.session_state.user.id

    perfil_res = supabase.table("perfis").select("perfil").eq("user_id", user_id).execute()
    ativos_res = supabase.table("ativos").select("*").eq("user_id", user_id).execute()

    perfil = perfil_res.data[0]["perfil"] if perfil_res.data else "Não definido"
    ativos = ativos_res.data or []

    return perfil, ativos

perfil, ativos = carregar_contexto_usuario()

# ── Header ───────────────────────────────────────────────────────────────
st.markdown(
    "<p style='font-family:DM Serif Display; font-size:1.8rem; color:#e8f4ff;'>📊 AI Portfolio Strategist</p>",
    unsafe_allow_html=True
)
st.markdown(
    f"<p style='color:#4a7090;'>Perfil: <strong style='color:#7dd3fc;'>{perfil}</strong></p>",
    unsafe_allow_html=True
)

# ── Portfolio display ────────────────────────────────────────────────────
carteira_texto = ""
total = 0

if not ativos:
    st.warning("Adicione ativos à carteira para gerar análise.")
    st.stop()

linhas = []
for a in ativos:
    valor = a["quantidade"] * a["preco_medio"]
    total += valor
    linhas.append(f"- {a['ticker']}: {a['quantidade']} cotas a R$ {a['preco_medio']:.2f}")

carteira_texto = "\n".join(linhas)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### Carteira atual")

for a in ativos:
    valor = a["quantidade"] * a["preco_medio"]
    pct = (valor / total * 100) if total > 0 else 0
    st.markdown(f"**{a['ticker']}** — R$ {valor:,.2f} ({pct:.1f}%)")

st.markdown(f"**Total:** R$ {total:,.2f}")
st.markdown("</div>", unsafe_allow_html=True)

# ── Sector exposure ──────────────────────────────────────────────────────
setores = {}

for a in ativos:
    try:
        ticker = yf.Ticker(a["ticker"])
        sector = ticker.info.get("sector", "Desconhecido")
    except:
        sector = "Desconhecido"

    valor = a["quantidade"] * a["preco_medio"]
    setores[sector] = setores.get(sector, 0) + valor

setor_texto = "\n".join([f"{k}: R$ {v:,.2f}" for k, v in setores.items()])

# ── Button ───────────────────────────────────────────────────────────────
st.markdown("---")

if st.button("🧠 Gerar análise da carteira"):
    with st.spinner("Analisando cenário macro e sua carteira..."):

        prompt = f"""
Você é um estrategista macro e gestor de portfólio profissional.

PERFIL DO INVESTIDOR: {perfil}

CARTEIRA ATUAL:
{carteira_texto}

EXPOSIÇÃO POR SETOR:
{setor_texto}

CONTEXTO MACRO ATUAL:
- Tensões geopolíticas elevadas (Oriente Médio)
- Petróleo em alta → pressão inflacionária
- Juros globais elevados por mais tempo
- Brasil com crescimento moderado (~2%)
- SELIC elevada (~12%)

TAREFA:

1. Analise a alocação atual da carteira
2. Identifique concentrações e riscos
3. Avalie vulnerabilidade ao cenário macro
4. Identifique oportunidades não exploradas

Depois forneça:

5. RECOMENDAÇÕES CLARAS:
   - REDUZIR:
   - AUMENTAR:
   - MANTER:

6. ALOCAÇÃO IDEAL (%)

7. Sugestões de:
   - setores
   - ativos
   - proteção (hedge, dólar, commodities, etc.)

Seja direto, específico e acionável.
"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )

            st.markdown("---")
            st.markdown("## 📊 Estratégia recomendada")
            st.markdown(response.choices[0].message.content)

        except Exception as e:
            st.error(f"Erro ao gerar análise: {str(e)}")