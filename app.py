import streamlit as st
import pandas as pd
from datetime import datetime

# Tenta integrar com os módulos dos colegas, com fallback seguro
try:
    from ai_service import gerar_teaser_cliente, gerar_briefing_assessor
except ImportError:
    def gerar_teaser_cliente(mensagem_usuario):
        return (
            "Analisando o que você compartilhou com a sua carteira consolidada, identificamos oportunidades "
            "relevantes de otimização de caixa e proteção contra volatilidade que seu assessor pode explorar com você."
        )
    def gerar_briefing_assessor(historico_dores):
        return f"**Resumo do Cliente:**\n{historico_dores}"

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Assessor 360 | RotaXP",
    page_icon="💼",
    layout="wide"
)

# --- 1. MOCK DATA (OPEN FINANCE SIMULADO) ---
MOCK_OPEN_FINANCE = {
    "cliente": "Carlos Eduardo Silva",
    "perfil": "Moderado",
    "saldo_conta_corrente": 85000.00,
    "posicoes": [
        {"instituicao": "Banco Tradicional A", "produto": "CDB Pós-fixado", "tipo": "Renda Fixa", "valor": 320000.00, "taxa": "85% CDI"},
        {"instituicao": "Banco Tradicional B", "produto": "Poupança", "tipo": "Renda Fixa", "valor": 45000.00, "taxa": "TR + 0.5%"},
        {"instituicao": "XP Investimentos", "produto": "Tesouro IPCA+ 2035", "tipo": "Renda Fixa", "valor": 150000.00, "taxa": "IPCA + 6.2%"},
        {"instituicao": "XP Investimentos", "produto": "Ações Diversas (IBOV)", "tipo": "Renda Variável", "valor": 60000.00, "taxa": "-18.5% (Mês)"}
    ]
}

# --- 2. INICIALIZAÇÃO DE ESTADO (SESSION STATE) ---
if "identificacao_concluida" not in st.session_state:
    st.session_state.identificacao_concluida = False

if "cliente_dados" not in st.session_state:
    st.session_state.cliente_dados = {"nome": "", "cpf": ""}

if "open_finance_autorizado" not in st.session_state:
    st.session_state.open_finance_autorizado = False

if "etapa_chat" not in st.session_state:
    # Etapas: "panorama" -> "metas" -> "revisao" -> "agendamento_liberado"
    st.session_state.etapa_chat = "panorama"

if "respostas_cliente" not in st.session_state:
    st.session_state.respostas_cliente = {
        "panorama": "",
        "metas": "",
        "adicionais": []
    }

if "messages" not in st.session_state:
    st.session_state.messages = []

if "resumo_dores" not in st.session_state:
    st.session_state.resumo_dores = ""

if "agendamento" not in st.session_state:
    st.session_state.agendamento = None


# --- 3. FUNÇÕES AUXILIARES DE FORMATAÇÃO ---
def compilar_resumo_cliente():
    panorama = st.session_state.respostas_cliente["panorama"]
    metas = st.session_state.respostas_cliente["metas"]
    adicionais = st.session_state.respostas_cliente["adicionais"]

    texto = f"📌 **Panorama dos Investimentos:**\n{panorama}\n\n📌 **Metas e Preocupações:**\n{metas}"
    if adicionais:
        texto += "\n\n📌 **Observações Complementares:**\n" + "\n".join([f"• {item}" for item in adicionais])
    return texto


# --- 4. INTERFACE PRINCIPAL ---
tab_cliente, tab_assessor = st.tabs(["📱 Visão do Investidor (Chat)", "📊 Visão do Assessor (Cockpit)"])

# ==========================================================
# ABA 1: VISÃO DO INVESTIDOR
# ==========================================================
with tab_cliente:
    st.caption("Protótipo de Triagem Inteligente Pré-Reunião")

    # ETAPA PRÉVIA: IDENTIFICAÇÃO DO INVESTIDOR (NOME E CPF)
    if not st.session_state.identificacao_concluida:
        st.info("👋 Seja bem-vindo ao atendimento preparatório! Por favor, informe seus dados para iniciar.")
        with st.form("form_identificacao"):
            col_nome, col_cpf = st.columns(2)
            with col_nome:
                nome_input = st.text_input("Nome Completo", placeholder="Ex: Carlos Eduardo Silva")
            with col_cpf:
                cpf_input = st.text_input("CPF", placeholder="000.000.000-00")

            btn_continuar = st.form_submit_button("Continuar", type="primary")
            if btn_continuar:
                if nome_input.strip() and cpf_input.strip():
                    st.session_state.cliente_dados = {
                        "nome": nome_input.strip(),
                        "cpf": cpf_input.strip()
                    }
                    st.session_state.identificacao_concluida = True
                    primeiro_nome = nome_input.strip().split()[0]
                    st.session_state.messages = [
                        {
                            "role": "assistant",
                            "content": f"Olá, {primeiro_nome}! Sou a Sofia, assistente virtual do seu assessor de investimentos. Para prepararmos a sua próxima reunião, você autoriza a sincronização segura dos seus dados via Open Finance?"
                        }
                    ]
                    st.rerun()
                else:
                    st.error("Por favor, preencha o Nome e o CPF para continuar.")

    # ETAPAS SEGUINTES (APÓS A IDENTIFICAÇÃO)
    else:
        # HISTÓRICO DE MENSAGENS
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # ETAPA 0: AUTORIZAÇÃO OPEN FINANCE DIRETA NO CHAT
        if not st.session_state.open_finance_autorizado:
            st.info("🔐 Conexão Segura com Banco Central e Open Finance")
            if st.button("🔗 Autorizar compartilhamento de dados financeiros", type="primary"):
                st.session_state.open_finance_autorizado = True
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "✅ **Dados sincronizados com sucesso!** Consegui mapear suas posições financeiras.\n\nPara iniciarmos nossa preparação: me conte um pouco sobre o **panorama geral dos seus investimentos atuais** (onde costuma investir e como se sente com sua alocação hoje)?"
                })
                st.session_state.etapa_chat = "panorama"
                st.rerun()

        # FLUXO CONVERSACIONAL GUIADO
        if st.session_state.open_finance_autorizado:
            
            # Etapa 1: Panorama Geral
            if st.session_state.etapa_chat == "panorama":
                user_input = st.chat_input("Descreva o panorama geral dos seus investimentos...")
                if user_input:
                    st.session_state.messages.append({"role": "user", "content": user_input})
                    st.session_state.respostas_cliente["panorama"] = user_input
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "Perfeito, devidamente anotado! Agora me diga: você possui **metas específicas** para os próximos meses/anos (ex: viagens, projetos, reserva) ou **preocupações** (ex: inflação, volatilidade da bolsa, taxas) que gostaria de discutir com seu assessor?"
                    })
                    st.session_state.etapa_chat = "metas"
                    st.rerun()

            # Etapa 2: Metas e Preocupações
            elif st.session_state.etapa_chat == "metas":
                user_input = st.chat_input("Compartilhe suas metas ou preocupações...")
                if user_input:
                    st.session_state.messages.append({"role": "user", "content": user_input})
                    st.session_state.respostas_cliente["metas"] = user_input
                    
                    # Compila o primeiro resumo
                    resumo_texto = compilar_resumo_cliente()
                    st.session_state.resumo_dores = resumo_texto

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Excelente! Preparei uma síntese do que você me passou até agora:\n\n{resumo_texto}\n\n*Seu assessor terá acesso completo a este resumo para chegarem à reunião com foco total no que importa.*\n\nVocê deseja **acrescentar mais alguma observação** ou podemos **prosseguir** para o agendamento?"
                    })
                    st.session_state.etapa_chat = "revisao"
                    st.rerun()

            # Etapa 3: Revisão (Escrever mais OU Prosseguir)
            elif st.session_state.etapa_chat == "revisao":
                if st.button("➡️ Prosseguir para o Agendamento", type="primary"):
                    teaser = gerar_teaser_cliente(st.session_state.resumo_dores)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"💡 **Insight da Sofia:** {teaser}\n\nVamos agora escolher o melhor dia, horário e modalidade para o seu encontro com o assessor!"
                    })
                    st.session_state.etapa_chat = "agendamento_liberado"
                    st.rerun()

                user_input_extra = st.chat_input("Digite aqui se quiser acrescentar mais alguma dúvida ou observação...")
                if user_input_extra:
                    st.session_state.messages.append({"role": "user", "content": user_input_extra})
                    st.session_state.respostas_cliente["adicionais"].append(user_input_extra)
                    
                    # Atualiza o resumo
                    resumo_atualizado = compilar_resumo_cliente()
                    st.session_state.resumo_dores = resumo_atualizado
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Anotado e incluído! Aqui está seu resumo atualizado:\n\n{resumo_atualizado}\n\nQuando estiver pronto, basta clicar em **Prosseguir para o Agendamento** acima!"
                    })
                    st.rerun()

            # Etapa 4: Agendamento Liberado
            elif st.session_state.etapa_chat == "agendamento_liberado":
                st.divider()
                st.subheader("📅 Agendamento com seu Assessor")
                col_data, col_hora, col_mod = st.columns(3)
                with col_data:
                    data_escolhida = st.date_input("Data preferida", min_value=datetime.today())
                with col_hora:
                    hora_escolhida = st.selectbox("Horário", ["10:00", "14:30", "16:00", "18:30"])
                with col_mod:
                    modalidade = st.selectbox(
                        "Modalidade do Encontro",
                        ["Vídeo (Google Meet)", "Presencial (Escritório XP)", "Ligação Telefônica"]
                    )

                if st.button("Confirmar Agendamento", type="primary"):
                    st.session_state.agendamento = {
                        "data": str(data_escolhida),
                        "hora": hora_escolhida,
                        "modalidade": modalidade
                    }
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"🎉 **Reunião confirmada com sucesso!**\n- **Data:** {data_escolhida}\n- **Horário:** {hora_escolhida}\n- **Modalidade:** {modalidade}\n\nSeu assessor já recebeu o briefing com suas prioridades e a análise da sua carteira."
                    })
                    st.success(f"🎉 Reunião confirmada para {data_escolhida} às {hora_escolhida} via {modalidade}!")
                    st.rerun()


# ==========================================================
# ABA 2: VISÃO DO ASSESSOR (COCKPIT)
# ==========================================================
with tab_assessor:
    st.header("Briefing Executivo do Cliente")
    
    # Grid de métricas do topo (incluindo a Modalidade)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cliente", MOCK_OPEN_FINANCE["cliente"])
    col2.metric("Perfil de Investidor", MOCK_OPEN_FINANCE["perfil"])
    
    status_data_hora = f"{st.session_state.agendamento['data']} às {st.session_state.agendamento['hora']}" if st.session_state.agendamento else "Pendente"
    col3.metric("Data e Horário", status_data_hora)
    
    modalidade_status = st.session_state.agendamento["modalidade"] if st.session_state.agendamento else "Aguardando definição"
    col4.metric("Modalidade", modalidade_status)

    st.divider()

    col_esq, col_dir = st.columns([1, 1])

    with col_esq:
        st.subheader("📋 Dores e Demandas Captadas pelo Bot")
        if st.session_state.resumo_dores:
            st.info(st.session_state.resumo_dores)
            st.caption("💡 Sugestão para o assessor: abordar pontos de liquidez imediata e rebalanceamento de ativos.")
        else:
            st.write("O cliente ainda não enviou observações nesta sessão.")

        st.subheader("🚨 Radar de Risco & Alertas (Regras de Negócio)")
        alertas = []
        if MOCK_OPEN_FINANCE["saldo_conta_corrente"] > 50000:
            alertas.append(f"⚠️ **Caixa Ocioso Elevado:** R$ {MOCK_OPEN_FINANCE['saldo_conta_corrente']:,.2f} parados em conta corrente sem rendimento.")
        
        for pos in MOCK_OPEN_FINANCE["posicoes"]:
            if pos["valor"] > 250000 and pos["tipo"] == "Renda Fixa":
                alertas.append(f"⚠️ **Risco de FGC Excedido:** R$ {pos['valor']:,.2f} no {pos['instituicao']} (Teto de R$ 250 mil).")
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