import streamlit as st
from supabase_client import supabase

st.set_page_config(page_title="AI Portfolio Advisor", page_icon="📈", layout="centered")

if "user" not in st.session_state or st.session_state.user is None:
    st.warning("Você precisa estar logado.")
    st.stop()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600&family=DM+Serif+Display:ital@0;1&display=swap');
html, body, [class*="css"] { font-family: 'Sora', sans-serif; }
.stApp { background-color: #080d1a; }
.stButton > button {
    background: transparent; border: 1px solid #1e3a5f; border-radius: 10px;
    color: #a8c4e0; font-family: 'Sora', sans-serif; font-size: 0.9rem;
    padding: 14px 20px; width: 100%; text-align: left; transition: all 0.2s; margin-bottom: 8px;
}
.stButton > button:hover { background: #0f2040; border-color: #2d6aad; color: #e8f4ff; }
.stRadio > div { flex-direction: column !important; gap: 8px !important; }
.stRadio > div > label {
    background: #0d1a2e; border: 1px solid #1e3a5f; border-radius: 10px;
    padding: 14px 18px; color: #a8c4e0 !important; font-size: 0.9rem !important;
    cursor: pointer; transition: all 0.2s; width: 100%;
}
.stRadio > div > label:hover { border-color: #2d6aad; background: #0f2040; }
.stRadio > div > label:has(input:checked) { border-color: #2d6aad !important; background: #0f2040 !important; color: #7dd3fc !important; }
.stRadio > div > label > div:first-child { display: none; }
label[data-testid="stWidgetLabel"] { display: none !important; }
.stProgress > div > div { background: #2d6aad; border-radius: 4px; }
.stProgress > div { background: #0d1a2e; border-radius: 4px; }
.hero { text-align: center; padding: 60px 0 48px; }
.hero-title { font-family: 'DM Serif Display', serif; font-size: 2.6rem; color: #e8f4ff; line-height: 1.2; margin: 0 0 12px; }
.hero-sub { font-size: 0.92rem; color: #4a7090; margin: 0; }
.card { background: #0d1a2e; border: 1px solid #1e3a5f; border-radius: 16px; padding: 32px; margin-bottom: 16px; }
.question-label { font-family: 'DM Serif Display', serif; font-size: 1.5rem; color: #e8f4ff; margin: 0 0 8px; line-height: 1.3; }
.question-sub { font-size: 0.82rem; color: #4a7090; margin: 0 0 24px; }
.step-indicator { font-size: 0.75rem; color: #2d6aad; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 8px; }
.result-card { background: #0d1a2e; border: 1px solid #1e3a5f; border-radius: 20px; padding: 40px 32px; text-align: center; }
.perfil-badge { display: inline-block; font-size: 0.72rem; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; padding: 6px 16px; border-radius: 20px; margin-bottom: 20px; }
.badge-conservador { background: #052e16; color: #4ade80; border: 1px solid #166534; }
.badge-moderado    { background: #1c2a05; color: #a3e635; border: 1px solid #3a5c0a; }
.badge-arrojado    { background: #1c0a05; color: #fb923c; border: 1px solid #7c2d12; }
.asset-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #1e3a5f; font-size: 0.88rem; color: #a8c4e0; }
.metric-box { background: #0d1a2e; border: 1px solid #1e3a5f; border-radius: 12px; padding: 20px; text-align: center; }
.metric-label { font-size: 0.72rem; color: #4a7090; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px; }
.metric-value { font-size: 1.4rem; font-weight: 600; color: #7dd3fc; }
.nav-bar { display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; background: #0d1a2e; border: 1px solid #1e3a5f; border-radius: 10px; margin-bottom: 24px; }
</style>
""", unsafe_allow_html=True)


# ── CLIENTE AUTENTICADO ───────────────────────────────────────────────────────
def get_client():
    """Injeta o token do usuário logado no cliente Supabase."""
    session = st.session_state.get("session")
    if session:
        try:
            supabase.auth.set_session(session.access_token, session.refresh_token)
        except Exception:
            pass
    return supabase


# ── SUPABASE QUERIES ──────────────────────────────────────────────────────────
def carregar_usuario():
    user_id = st.session_state.user.id
    res = get_client().table("usuarios").select("nome, sobrenome").eq("user_id", user_id).execute()
    return res.data[0] if res.data else None

def carregar_perfil_usuario():
    user_id = st.session_state.user.id
    res = get_client().table("perfis").select("*").eq("user_id", user_id).execute()
    return res.data[0] if res.data else None

def carregar_ativos_usuario():
    user_id = st.session_state.user.id
    res = get_client().table("ativos").select("*").eq("user_id", user_id).execute()
    return res.data or []

def salvar_perfil(perfil, tem_carteira):
    user_id = st.session_state.user.id
    get_client().table("perfis").upsert({
        "user_id": user_id,
        "perfil": perfil,
        "tem_carteira": tem_carteira
    }, on_conflict="user_id").execute()

def salvar_ativo(ticker, quantidade, preco_medio):
    user_id = st.session_state.user.id
    get_client().table("ativos").insert({
        "user_id": user_id,
        "ticker": ticker,
        "quantidade": quantidade,
        "preco_medio": preco_medio
    }).execute()

def deletar_ativo(ativo_id):
    get_client().table("ativos").delete().eq("id", ativo_id).execute()

def resetar_perfil():
    user_id = st.session_state.user.id
    get_client().table("perfis").delete().eq("user_id", user_id).execute()
    get_client().table("ativos").delete().eq("user_id", user_id).execute()


# ── INICIALIZAÇÃO ─────────────────────────────────────────────────────────────
def init():
    if "onboarding_carregado" not in st.session_state:
        perfil_db = carregar_perfil_usuario()
        if perfil_db:
            st.session_state.onboarding_step = "concluido"
            st.session_state.perfil = perfil_db["perfil"]
            st.session_state.tem_carteira = perfil_db["tem_carteira"]
        else:
            st.session_state.onboarding_step = "inicio"
            st.session_state.perfil = None
            st.session_state.tem_carteira = None
        st.session_state.respostas = {}
        st.session_state.onboarding_carregado = True

init()

dados_usuario = carregar_usuario()
user_name = dados_usuario["nome"] if dados_usuario and dados_usuario.get("nome") else st.session_state.user.email.split("@")[0].capitalize()


# ── PERGUNTAS ─────────────────────────────────────────────────────────────────
PERGUNTAS = [
    {"id": "idade", "titulo": "Qual é a sua faixa de idade?", "sub": "Sua idade influencia o horizonte de investimento ideal.",
     "opcoes": ["Menos de 25 anos", "25 a 35 anos", "36 a 50 anos", "Acima de 50 anos"], "pontos": [4, 3, 2, 1]},
    {"id": "renda", "titulo": "Qual é a sua renda mensal aproximada?", "sub": "Usamos isso para entender sua capacidade de investimento.",
     "opcoes": ["Até R$ 3.000", "R$ 3.000 a R$ 8.000", "R$ 8.000 a R$ 20.000", "Acima de R$ 20.000"], "pontos": [1, 2, 3, 4]},
    {"id": "objetivo", "titulo": "Qual é o seu principal objetivo com os investimentos?", "sub": "Seu objetivo define a estratégia mais adequada.",
     "opcoes": ["Preservar meu capital com segurança", "Gerar renda complementar", "Crescimento do patrimônio no longo prazo", "Maximizar retornos, mesmo com mais risco"], "pontos": [1, 2, 3, 4]},
    {"id": "prazo", "titulo": "Por quanto tempo pretende deixar o dinheiro investido?", "sub": "O prazo é fundamental para escolher os melhores ativos.",
     "opcoes": ["Menos de 1 ano", "1 a 3 anos", "3 a 10 anos", "Mais de 10 anos"], "pontos": [1, 2, 3, 4]},
    {"id": "risco", "titulo": "Se seus investimentos caíssem 20% em um mês, o que faria?", "sub": "Isso revela sua real tolerância a volatilidade.",
     "opcoes": ["Venderia tudo imediatamente para evitar mais perdas", "Ficaria preocupado, mas aguardaria recuperação", "Manteria a calma e esperaria o mercado se recuperar", "Aproveitaria para comprar mais"], "pontos": [1, 2, 3, 4]},
    {"id": "conhecimento", "titulo": "Como você avalia seu conhecimento em investimentos?", "sub": "Isso nos ajuda a calibrar as recomendações.",
     "opcoes": ["Nenhum — nunca investi", "Básico — conheço poupança e CDB", "Intermediário — já investi em fundos e ações", "Avançado — opero derivativos e mercado internacional"], "pontos": [1, 2, 3, 4]},
]

def calcular_perfil(respostas):
    total = sum(respostas.values())
    pct = total / (len(PERGUNTAS) * 4)
    if pct <= 0.40: return "Conservador"
    elif pct <= 0.70: return "Moderado"
    else: return "Arrojado"


# ── TELA: INÍCIO ──────────────────────────────────────────────────────────────
if st.session_state.onboarding_step == "inicio":
    st.markdown(f'<div class="hero"><p class="hero-title">Olá, {user_name} 👋</p><p class="hero-sub">Vamos configurar sua experiência de investimentos</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<p class="question-label">Você já tem uma carteira de investimentos?</p>', unsafe_allow_html=True)
    st.markdown('<p class="question-sub">Isso nos ajuda a personalizar sua experiência desde o início.</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅  Sim, já tenho investimentos", use_container_width=True):
            st.session_state.tem_carteira = True
            st.session_state.onboarding_step = "cadastrar_ativos"
            st.rerun()
    with col2:
        if st.button("🌱  Não, estou começando agora", use_container_width=True):
            st.session_state.tem_carteira = False
            st.session_state.onboarding_step = "suitability"
            st.session_state.suitability_idx = 0
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ── TELA: SUITABILITY ─────────────────────────────────────────────────────────
elif st.session_state.onboarding_step == "suitability":
    idx = st.session_state.get("suitability_idx", 0)
    pergunta = PERGUNTAS[idx]
    st.progress(idx / len(PERGUNTAS))
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<p class="step-indicator">Pergunta {idx + 1} de {len(PERGUNTAS)}</p>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<p class="question-label">{pergunta["titulo"]}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="question-sub">{pergunta["sub"]}</p>', unsafe_allow_html=True)
    escolha = st.radio("opcao", pergunta["opcoes"], index=None, label_visibility="collapsed")
    col1, col2 = st.columns(2)
    with col1:
        if idx > 0:
            if st.button("← Voltar", use_container_width=True):
                st.session_state.suitability_idx -= 1
                st.rerun()
    with col2:
        if escolha:
            if st.button("Próximo →", use_container_width=True):
                ponto = pergunta["pontos"][pergunta["opcoes"].index(escolha)]
                st.session_state.respostas[pergunta["id"]] = ponto
                if idx + 1 >= len(PERGUNTAS):
                    perfil = calcular_perfil(st.session_state.respostas)
                    st.session_state.perfil = perfil
                    salvar_perfil(perfil, st.session_state.get("tem_carteira", False))
                    st.session_state.onboarding_step = "resultado_perfil"
                else:
                    st.session_state.suitability_idx += 1
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ── TELA: RESULTADO DO PERFIL ─────────────────────────────────────────────────
elif st.session_state.onboarding_step == "resultado_perfil":
    perfil = st.session_state.perfil
    descricoes = {
        "Conservador": {"emoji": "🛡️", "desc": "Você prioriza a segurança do seu capital. Prefere rentabilidades menores, mas com baixo risco.", "ativos": ["Tesouro Selic", "CDB de grandes bancos", "Fundos DI", "LCI / LCA"], "badge": "badge-conservador"},
        "Moderado":    {"emoji": "⚖️", "desc": "Você busca equilíbrio entre segurança e rentabilidade. Aceita alguma volatilidade em troca de retornos superiores.", "ativos": ["Fundos Multimercado", "Ações de grandes empresas", "FIIs", "Tesouro IPCA+"], "badge": "badge-moderado"},
        "Arrojado":    {"emoji": "🚀", "desc": "Você tem alta tolerância ao risco e busca maximizar seus retornos no longo prazo.", "ativos": ["Ações de crescimento", "BDRs e ETFs internacionais", "Small Caps", "Criptomoedas"], "badge": "badge-arrojado"}
    }
    info = descricoes[perfil]
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="result-card">
        <span class="perfil-badge {info['badge']}">{perfil}</span>
        <p style="font-family:'DM Serif Display',serif; font-size:2.2rem; color:#e8f4ff; margin:0 0 16px;">{info['emoji']} Perfil {perfil}</p>
        <p style="font-size:0.92rem; color:#6a90b0; line-height:1.7; max-width:480px; margin:0 auto 28px;">{info['desc']}</p>
        <p style="font-size:0.75rem; color:#2d6aad; font-weight:600; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:12px;">Ativos recomendados</p>
        {''.join([f'<div class="asset-item" style="justify-content:center; border:none; color:#7dd3fc;">• {a}</div>' for a in info["ativos"]])}
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Ir para meu painel →", use_container_width=True):
        st.session_state.onboarding_step = "concluido"
        st.rerun()


# ── TELA: CADASTRAR ATIVOS ────────────────────────────────────────────────────
elif st.session_state.onboarding_step == "cadastrar_ativos":
    st.markdown('<div class="hero" style="padding:40px 0 32px;"><p class="hero-title" style="font-size:2rem;">Sua carteira atual</p><p class="hero-sub">Adicione seus ativos para começarmos a análise</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        ticker = st.text_input("Ticker", placeholder="Ex: PETR4, AAPL", label_visibility="visible")
    with col2:
        quantidade = st.number_input("Quantidade", min_value=0.0, step=1.0, label_visibility="visible")
    with col3:
        preco_medio = st.number_input("Preço médio (R$)", min_value=0.0, step=0.01, label_visibility="visible")
    if st.button("+ Adicionar ativo", use_container_width=True):
        if ticker and quantidade > 0 and preco_medio > 0:
            salvar_ativo(ticker.upper(), quantidade, preco_medio)
            st.rerun()
        else:
            st.warning("Preencha todos os campos corretamente.")
    ativos_db = carregar_ativos_usuario()
    if ativos_db:
        st.markdown("<br>", unsafe_allow_html=True)
        total_carteira = sum(a["quantidade"] * a["preco_medio"] for a in ativos_db)
        for a in ativos_db:
            total_ativo = a["quantidade"] * a["preco_medio"]
            pct = (total_ativo / total_carteira * 100) if total_carteira > 0 else 0
            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.markdown(f'<div class="asset-item"><span style="font-weight:600; color:#7dd3fc;">{a["ticker"]}</span><span>{a["quantidade"]:.0f} cotas × R$ {a["preco_medio"]:.2f}</span><span style="color:#e8f4ff;">R$ {total_ativo:,.2f} <span style="color:#4a7090; font-size:0.78rem;">({pct:.1f}%)</span></span></div>', unsafe_allow_html=True)
            with col_b:
                if st.button("🗑️", key=f"del_{a['id']}"):
                    deletar_ativo(a["id"])
                    st.rerun()
        st.markdown(f'<div style="padding:16px 0 0; text-align:right;"><span style="font-size:0.8rem; color:#4a7090;">Total: </span><span style="font-size:1.1rem; font-weight:600; color:#7dd3fc;">R$ {total_carteira:,.2f}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if ativos_db:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Continuar → Descobrir meu perfil", use_container_width=True):
            st.session_state.onboarding_step = "suitability"
            st.session_state.suitability_idx = 0
            st.rerun()


# ── TELA: PAINEL PRINCIPAL ────────────────────────────────────────────────────
elif st.session_state.onboarding_step == "concluido":
    perfil = st.session_state.get("perfil", "Moderado")
    emojis = {"Conservador": "🛡️", "Moderado": "⚖️", "Arrojado": "🚀"}
    badges = {"Conservador": "badge-conservador", "Moderado": "badge-moderado", "Arrojado": "badge-arrojado"}
    cores  = {"Conservador": "#4ade80", "Moderado": "#a3e635", "Arrojado": "#fb923c"}

    ativos_db      = carregar_ativos_usuario()
    total_carteira = sum(a["quantidade"] * a["preco_medio"] for a in ativos_db)

    col_nav1, col_nav2 = st.columns([4, 1])
    with col_nav1:
        st.markdown(f'<div class="nav-bar"><span style="color:#6b82a8; font-size:0.85rem;">{emojis.get(perfil,"")} <strong style="color:{cores.get(perfil,"#7dd3fc")};">Perfil {perfil}</strong> &nbsp;·&nbsp; {st.session_state.user.email}</span></div>', unsafe_allow_html=True)
    with col_nav2:
        if st.button("Sair", use_container_width=True):
            for key in ["user", "session", "onboarding_carregado", "perfil", "tem_carteira", "respostas"]:
                st.session_state.pop(key, None)
            st.rerun()

    st.markdown(f'<div style="padding:16px 0 32px;"><p style="font-family:\'DM Serif Display\',serif; font-size:2rem; color:#e8f4ff; margin:0 0 4px;">Olá, {user_name} {emojis.get(perfil,"📊")}</p><p style="font-size:0.88rem; color:#4a7090; margin:0;">Aqui está um resumo da sua carteira</p></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-box"><div class="metric-label">Total investido</div><div class="metric-value">R$ {total_carteira:,.0f}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-box"><div class="metric-label">Ativos</div><div class="metric-value">{len(ativos_db)}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-box"><div class="metric-label">Perfil</div><div class="metric-value" style="font-size:1rem;">{emojis.get(perfil,"")} {perfil}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if ativos_db:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<p class="question-label" style="font-size:1.1rem; margin-bottom:16px;">Minha carteira</p>', unsafe_allow_html=True)
        for a in ativos_db:
            total_ativo = a["quantidade"] * a["preco_medio"]
            pct = (total_ativo / total_carteira * 100) if total_carteira > 0 else 0
            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.markdown(f'<div class="asset-item"><span style="font-weight:600; color:#7dd3fc; min-width:80px;">{a["ticker"]}</span><span style="color:#6a90b0;">{a["quantidade"]:.0f} cotas × R$ {a["preco_medio"]:.2f}</span><span style="color:#e8f4ff;">R$ {total_ativo:,.2f}<span style="color:#4a7090; font-size:0.78rem;"> ({pct:.1f}%)</span></span></div>', unsafe_allow_html=True)
            with col_b:
                if st.button("🗑️", key=f"rm_{a['id']}"):
                    deletar_ativo(a["id"])
                    st.rerun()
        st.markdown(f'<div style="padding:16px 0 0; text-align:right;"><span style="font-size:0.8rem; color:#4a7090;">Total investido: </span><span style="font-size:1.1rem; font-weight:600; color:#7dd3fc;">R$ {total_carteira:,.2f}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        with st.expander("+ Adicionar ativo"):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                ticker_new = st.text_input("Ticker", placeholder="Ex: PETR4", key="new_ticker", label_visibility="visible")
            with col2:
                qtd_new = st.number_input("Quantidade", min_value=0.0, step=1.0, key="new_qtd", label_visibility="visible")
            with col3:
                preco_new = st.number_input("Preço médio", min_value=0.0, step=0.01, key="new_preco", label_visibility="visible")
            if st.button("Adicionar", use_container_width=True):
                if ticker_new and qtd_new > 0 and preco_new > 0:
                    salvar_ativo(ticker_new.upper(), qtd_new, preco_new)
                    st.rerun()
    else:
        st.markdown('<div class="card" style="text-align:center; padding:40px;"><p style="font-size:2rem; margin:0 0 12px;">📭</p><p style="color:#e8f4ff; font-size:1rem; margin:0 0 8px;">Carteira vazia</p><p style="color:#4a7090; font-size:0.85rem; margin:0;">Adicione seus ativos para começar a análise</p></div>', unsafe_allow_html=True)
        if st.button("+ Adicionar ativos à carteira", use_container_width=True):
            st.session_state.onboarding_step = "cadastrar_ativos"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("⚙️ Configurações do perfil"):
        st.markdown('<p style="color:#6a90b0; font-size:0.85rem; margin-bottom:16px;">Refazer o questionário irá apagar seu perfil e carteira atuais.</p>', unsafe_allow_html=True)
        if st.button("🔄 Refazer questionário de perfil", use_container_width=True):
            resetar_perfil()
            for key in ["onboarding_step", "perfil", "tem_carteira", "respostas", "onboarding_carregado"]:
                st.session_state.pop(key, None)
            st.rerun()