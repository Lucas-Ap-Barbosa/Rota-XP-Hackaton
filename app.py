import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Assessor 360 | RotaXP",
    page_icon="💼",
    layout="wide"
)

# --- 1. MOCK DATA (OPEN FINANCE SIMULADO) ---
# O Dev 3 pode editar este dicionário/JSON para enriquecer os dados
MOCK_OPEN_FINANCE = {
    "cliente": "Carlos Eduardo Silva",
    "perfil": "Moderado",
    "saldo_conta_corrente": 85000.00,  # Caixa ocioso
    "posicoes": [
        {"instituicao": "Banco Tradicional A", "produto": "CDB Pós-fixado", "tipo": "Renda Fixa", "valor": 320000.00, "taxa": "85% CDI"},
        {"instituicao": "Banco Tradicional B", "produto": "Poupança", "tipo": "Renda Fixa", "valor": 45000.00, "taxa": "TR + 0.5%"},
        {"instituicao": "XP Investimentos", "produto": "Tesouro IPCA+ 2035", "tipo": "Renda Fixa", "valor": 150000.00, "taxa": "IPCA + 6.2%"},
        {"instituicao": "XP Investimentos", "produto": "Ações Diversas (IBOV)", "tipo": "Renda Variável", "valor": 60000.00, "taxa": "-18.5% (Mês)"}
    ]
}

# --- 2. INICIALIZAÇÃO DE ESTADO (SESSION STATE) ---
if "open_finance_autorizado" not in st.session_state:
    st.session_state.open_finance_autorizado = False

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá, Carlos! Sou a Sofia, assistente virtual do seu assessor de investimentos. Para prepararmos a sua próxima reunião, você autoriza a sincronização segura dos seus dados via Open Finance?"}
    ]

if "resumo_dores" not in st.session_state:
    st.session_state.resumo_dores = ""

if "agendamento" not in st.session_state:
    st.session_state.agendamento = None


# --- 3. LÓGICA DE SIMULAÇÃO DE IA ---
# O Dev 2 pode plugar aqui a chamada real para uma LLM
def simular_resposta_ia(texto_usuario):
    """
    Gera um teaser curto estimulando curiosidade sem dar recomendação direta.
    """
    texto_lower = texto_usuario.lower()
    if "perder" in texto_lower or "queda" in texto_lower or "risco" in texto_lower:
        return (
            "Compreendo a preocupação com as oscilações recentes. Analisando rapidamente sua carteira, "
            "notamos oportunidades de proteção e rebalanceamento que podem reduzir essa volatilidade. "
            "Seu assessor já foi sinalizado sobre isso. Deseja acrescentar mais alguma dúvida ou já agendamos o bate-papo?"
        )
    else:
        return (
            "Anotado! Identifiquei que você possui capital com potencial de melhor remuneração "
            "e alguns ativos que excedem a garantia de segurança bancária. "
            "Seu assessor terá propostas sob medida para isso. Quer pontuar algo mais ou prefere escolher o melhor horário?"
        )

# --- 4. INTERFACE PRINCIPAL EM ABAS ---
tab_cliente, tab_assessor = st.tabs(["📱 Visão do Investidor (Chat)", "📊 Visão do Assessor (Cockpit)"])

# ==========================================================
# ABA 1: VISÃO DO INVESTIDOR (Dev 1 foca aqui)
# ==========================================================
with tab_cliente:
    st.caption("Protótipo de Triagem Inteligente Pré-Reunião")

    # Passo 1: Consentimento Open Finance
    if not st.session_state.open_finance_autorizado:
        st.info("🔐 Conexão Segura com Banco Central e Open Finance")
        if st.button("🔗 Autorizar compartilhamento de dados financeiros"):
            st.session_state.open_finance_autorizado = True
            st.session_state.messages.append({
                "role": "assistant",
                "content": "✅ Dados sincronizados com sucesso! Identifiquei sua carteira consolidada. Me conte: quais são suas principais dúvidas ou objetivos para a nossa próxima conversa?"
            })
            st.rerun()

    # Exibição do histórico de mensagens
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Passo 2: Input de dores e diálogo
    if st.session_state.open_finance_autorizado:
        user_input = st.chat_input("Digite suas dúvidas, preocupações ou metas...")
        if user_input:
            # Registra mensagem do cliente
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.resumo_dores += f" - {user_input}\n"
            
            # Gera resposta da IA
            resposta_bot = simular_resposta_ia(user_input)
            st.session_state.messages.append({"role": "assistant", "content": resposta_bot})
            st.rerun()

        # Passo 3: Widget de Agendamento Guiado
        st.divider()
        st.subheader("📅 Agendamento com seu Assessor")
        col_data, col_hora, col_mod = st.columns(3)
        with col_data:
            data_escolhida = st.date_input("Data preferida", min_value=datetime.today())
        with col_hora:
            hora_escolhida = st.selectbox("Horário", ["10:00", "14:30", "16:00", "18:30"])
        with col_mod:
            modalidade = st.selectbox("Modalidade", ["Vídeo (Google Meet)", "Ligação Telefônica", "Presencial (Escritório XP)"])

        if st.button("Confirmar Agendamento"):
            st.session_state.agendamento = {
                "data": str(data_escolhida),
                "hora": hora_escolhida,
                "modalidade": modalidade
            }
            st.success(f"🎉 Reunião confirmada para {data_escolhida} às {hora_escolhida} via {modalidade}! O assessor já recebeu seu briefing.")


# ==========================================================
# ABA 2: VISÃO DO ASSESSOR (Dev 3 e Dev 4 focam aqui)
# ==========================================================
with tab_assessor:
    st.header("Briefing Executivo do Cliente")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Cliente", MOCK_OPEN_FINANCE["cliente"])
    col2.metric("Perfil de Investidor", MOCK_OPEN_FINANCE["perfil"])
    status_agenda = f"{st.session_state.agendamento['data']} às {st.session_state.agendamento['hora']}" if st.session_state.agendamento else "Pendente"
    col3.metric("Status da Reunião", status_agenda)

    st.divider()

    col_esq, col_dir = st.columns([1, 1])

    with col_esq:
        st.subheader("📋 Dores e Demandas Captadas pelo Bot")
        if st.session_state.resumo_dores:
            st.info(st.session_state.resumo_dores)
            st.caption("💡 Sugestão para o assessor: abordar a otimização de renda fixa e rebalanceamento cambial/ações.")
        else:
            st.write("O cliente ainda não enviou observações nesta sessão.")

        st.subheader("🚨 Radar de Risco & Alertas (Regras de Negócio)")
        # Regras automáticas simples
        alertas = []
        if MOCK_OPEN_FINANCE["saldo_conta_corrente"] > 50000:
            alertas.append(f"⚠️ **Caixa Ocioso Elevado:** R$ {MOCK_OPEN_FINANCE['saldo_conta_corrente']:,.2f} parados em conta sem remuneração.")
        
        for pos in MOCK_OPEN_FINANCE["posicoes"]:
            if pos["valor"] > 250000 and pos["tipo"] == "Renda Fixa":
                alertas.append(f"⚠️ **Risco de FGC Excedido:** R$ {pos['valor']:,.2f} no {pos['instituicao']} (Teto FGC: R$ 250 mil).")
            if "-18" in pos["taxa"]:
                alertas.append(f"🔻 **Alerta de Volatilidade:** Queda de 18% em {pos['produto']} no último mês.")

        for alerta in alertas:
            st.warning(alerta)

    with col_dir:
        st.subheader("💰 Carteira Consolidada (Open Finance)")
        if st.session_state.open_finance_autorizado:
            df = pd.DataFrame(MOCK_OPEN_FINANCE["posicoes"])
            st.dataframe(df, use_container_width=True)
            
            patrimonio_total = sum(p["valor"] for p in MOCK_OPEN_FINANCE["posicoes"]) + MOCK_OPEN_FINANCE["saldo_conta_corrente"]
            st.metric("Patrimônio Total Rastreado", f"R$ {patrimonio_total:,.2f}")
        else:
            st.warning("Aguardando autorização de Open Finance pelo cliente na aba ao lado.")