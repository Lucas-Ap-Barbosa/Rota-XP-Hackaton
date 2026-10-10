import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- IMPORTAÇÃO DOS MÓDULOS DE IA / MOCK ---
try:
    from ai_service import (
        gerar_teaser_cliente,
        gerar_briefing_assessor,
        criar_resumo,
        determinar_perfil,
    )
except ImportError:
    def gerar_teaser_cliente(mensagem_usuario):
        return (
            "Analisando o que você compartilhou com a sua carteira consolidada, identificamos oportunidades "
            "relevantes de otimização de caixa e proteção contra volatilidade que seu assessor pode explorar com você."
        )
    def gerar_briefing_assessor(historico_dores):
        return f"**Resumo do Cliente:**\n{historico_dores}"
    def criar_resumo(cpf, qtd_observacoes=0):
        return "Resumo preliminar gerado com base nas informações recebidas."
    def determinar_perfil(cpf, qtd_observacoes=0):
        return "Indeterminado"

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Assessor 360 | RotaXP",
    page_icon="💼",
    layout="wide"
)

# --- ESTILIZAÇÃO VISUAL (CORES DOS ÍCONES E DA ABA DO ASSESSOR) ---
st.markdown("""
    <style>
    /* 1. Ícone do Utilizador em Amarelo */
    div[data-testid="chatAvatarIcon-user"] {
        background-color: #FFB800 !important;
        color: #000000 !important;
    }
    div[data-testid="chatAvatarIcon-user"] svg {
        fill: #000000 !important;
        stroke: #000000 !important;
    }

    /* 2. Ícone do Bot (Sofia) em Branco */
    div[data-testid="chatAvatarIcon-assistant"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    div[data-testid="chatAvatarIcon-assistant"] svg {
        fill: #000000 !important;
        stroke: #000000 !important;
    }

    /* 3. Caixa Azul do Assessor transformada em Roxo */
    div[role="tabpanel"]:nth-of-type(2) div[data-testid="stAlert"]:first-of-type,
    div[data-testid="stTabContent"]:nth-of-type(2) div[data-testid="stAlert"]:first-of-type {
        background-color: #2b124c !important;
        border: 1px solid #7928ca !important;
        color: #f3e8ff !important;
    }
    div[role="tabpanel"]:nth-of-type(2) div[data-testid="stAlert"]:first-of-type svg,
    div[data-testid="stTabContent"]:nth-of-type(2) div[data-testid="stAlert"]:first-of-type svg {
        fill: #c77dff !important;
    }
    </style>
""", unsafe_allow_html=True)


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


# --- 3. INTEGRAÇÃO COM A API OPEN FINANCE + OVER CP ---
API_URL = "http://localhost:8000"
API_TOKEN = "hackathon-token"
API_HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

PROFILE_LABELS = {
    "CONSERVATIVE": "Conservador",
    "MODERATE": "Moderado",
    "AGGRESSIVE": "Agressivo",
}

RISK_BY_TYPE = {
    "BANK_FIXED_INCOME": 1.0,
    "TREASURY": 2.0,
    "FUND": 3.0,
    "VARIABLE_INCOME": 5.0,
}

PROFILE_LIMIT = {
    "CONSERVATIVE": 2.0,
    "MODERATE": 3.5,
    "AGGRESSIVE": 5.0,
}


def api_get(endpoint, params=None):
    response = requests.get(
        f"{API_URL}{endpoint}",
        headers=API_HEADERS,
        params=params,
        timeout=5,
    )
    response.raise_for_status()
    body = response.json()
    return body.get("data", body)


def carregar_cliente_open_finance(nome, cpf):
    cliente = api_get(
        "/customers/search",
        params={"cpf": cpf, "name": nome},
    )

    customer_id = cliente["customer_id"]

    investimentos = api_get(
        "/investments",
        params={"customer_id": customer_id},
    )

    resumo = api_get(
        "/portfolio/summary",
        params={"customer_id": customer_id},
    )

    return cliente, investimentos, resumo


def calcular_over_cp(cliente, investimentos):
    total = sum(float(inv.get("current_amount") or 0) for inv in investimentos)
    perfil = cliente["risk_profile"]
    limite = PROFILE_LIMIT.get(perfil, 3.0)

    detalhes = []

    if total <= 0:
        return {
            "over_cp": False,
            "portfolio_risk": 0.0,
            "allowed_risk": limite,
            "total_investido": 0.0,
            "detalhes": detalhes,
        }

    risco_carteira = 0.0

    for inv in investimentos:
        valor = float(inv.get("current_amount") or 0)
        peso = valor / total
        risco_produto = RISK_BY_TYPE.get(inv.get("type"), 3.0)
        contribuicao = peso * risco_produto
        risco_carteira += contribuicao

        detalhes.append({
            "Produto": inv.get("product_name", "-"),
            "Classe": inv.get("type", "-"),
            "Valor (R$)": round(valor, 2),
            "Peso (%)": round(peso * 100, 2),
            "Risco": risco_produto,
            "Contribuição": round(contribuicao, 3),
        })

    return {
        "over_cp": risco_carteira > limite,
        "portfolio_risk": round(risco_carteira, 2),
        "allowed_risk": limite,
        "total_investido": round(total, 2),
        "detalhes": detalhes,
    }


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
                nome_input = st.text_input("Nome Completo", placeholder="Ex: Lucas Pereira Santos")
            with col_cpf:
                cpf_input = st.text_input("CPF", placeholder="29925594316")

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
            cpf_atual = st.session_state.cliente_dados["cpf"]
            
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

            # Etapa 2: Metas e Preocupações -> Dispara o resumo mockado inicial (qtd_observacoes = 0)
            elif st.session_state.etapa_chat == "metas":
                user_input = st.chat_input("Compartilhe suas metas ou preocupações...")
                if user_input:
                    st.session_state.messages.append({"role": "user", "content": user_input})
                    st.session_state.respostas_cliente["metas"] = user_input
                    
                    # Busca o resumo pronto do JSON usando o CPF informado
                    resumo_ia = criar_resumo(cpf_atual, qtd_observacoes=0)
                    perfil_preliminar = determinar_perfil(cpf_atual, qtd_observacoes=0)

                    texto_sintese = (
                        f"{resumo_ia}\n\n"
                        f"📊 **Perfil preliminar estimado pela IA:** {perfil_preliminar}"
                    )
                    st.session_state.resumo_dores = texto_sintese

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": (
                            f"Excelente! Preparei uma síntese do que você me passou até agora:\n\n"
                            f"> {resumo_ia}\n\n"
                            f"📊 **Perfil preliminar:** {perfil_preliminar}\n\n"
                            f"*Seu assessor terá acesso completo a este resumo para chegarem à reunião com foco total no que importa.*\n\n"
                            f"Você deseja **acrescentar mais alguma observação** ou podemos **prosseguir** para o agendamento?"
                        )
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
                    
                    # Recalcula com a quantidade de observações extras feitas
                    qtd_obs = len(st.session_state.respostas_cliente["adicionais"])
                    resumo_atualizado = criar_resumo(cpf_atual, qtd_observacoes=qtd_obs)
                    perfil_atualizado = determinar_perfil(cpf_atual, qtd_observacoes=qtd_obs)

                    texto_sintese_atualizado = (
                        f"{resumo_atualizado}\n\n"
                        f"📊 **Perfil preliminar estimado pela IA:** {perfil_atualizado}"
                    )
                    st.session_state.resumo_dores = texto_sintese_atualizado
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": (
                            f"Anotado e incluído! Aqui está seu resumo atualizado:\n\n"
                            f"> {resumo_atualizado}\n\n"
                            f"📊 **Perfil preliminar:** {perfil_atualizado}\n\n"
                            f"Quando estiver pronto, basta clicar em **Prosseguir para o Agendamento** acima!"
                        )
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
# ABA 2: VISÃO DO ASSESSOR — SESSÃO OVER CP (TOTALMENTE INTACTA)
# ==========================================================
with tab_assessor:
    st.header("Análise de Compatibilidade da Carteira — OVER CP")

    if not st.session_state.identificacao_concluida:
        st.info("Identifique o investidor na aba ao lado para liberar a análise.")
    elif not st.session_state.open_finance_autorizado:
        st.warning("Aguardando autorização de compartilhamento via Open Finance.")
    else:
        nome = st.session_state.cliente_dados["nome"]
        cpf = st.session_state.cliente_dados["cpf"]

        try:
            cliente, investimentos, resumo = carregar_cliente_open_finance(nome, cpf)
            over_cp = calcular_over_cp(cliente, investimentos)

            perfil_codigo = cliente["risk_profile"]
            perfil_label = PROFILE_LABELS.get(perfil_codigo, perfil_codigo)

            # ------------------------------
            # Cabeçalho executivo
            # ------------------------------
            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Cliente", cliente["name"])
            col2.metric("Perfil", perfil_label)
            col3.metric("Risco da Carteira", f"{over_cp['portfolio_risk']:.2f}")
            col4.metric("Limite do Perfil", f"{over_cp['allowed_risk']:.2f}")

            st.divider()

            # ------------------------------
            # Status OVER CP
            # ------------------------------
            st.subheader("🚦 Status de Suitability")

            if over_cp["over_cp"]:
                st.error(
                    f"🚨 **OVER CP IDENTIFICADO** — o score de risco da carteira "
                    f"({over_cp['portfolio_risk']:.2f}) está acima do limite "
                    f"definido para o perfil {perfil_label} "
                    f"({over_cp['allowed_risk']:.2f})."
                )
            else:
                st.success(
                    f"✅ **Carteira compatível com o perfil** — o score de risco "
                    f"({over_cp['portfolio_risk']:.2f}) está dentro do limite "
                    f"do perfil {perfil_label} ({over_cp['allowed_risk']:.2f})."
                )

            st.caption(
                "Regra demonstrativa para hackathon. O cálculo não representa "
                "a metodologia oficial de suitability/OVER CP da XP."
            )

            st.divider()

            # ------------------------------
            # Visão financeira + alocação
            # ------------------------------
            col_esq, col_dir = st.columns([1, 1])

            with col_esq:
                st.subheader("💰 Resumo do Patrimônio")

                st.metric(
                    "Investimentos",
                    f"R$ {float(resumo.get('investmentsMarketValueBRL', 0)):,.2f}",
                )
                st.metric(
                    "Saldo em Conta",
                    f"R$ {float(resumo.get('cashBRL', 0)):,.2f}",
                )
                st.metric(
                    "Patrimônio Financeiro Total",
                    f"R$ {float(resumo.get('totalFinancialAssetsBRL', 0)):,.2f}",
                )

                pnl = float(resumo.get("unrealizedPnLBRL", 0))
                st.metric(
                    "P&L Não Realizado",
                    f"R$ {pnl:,.2f}",
                )

                st.subheader("📊 Alocação por Classe")

                allocation = resumo.get("allocationByType", {})
                if allocation:
                    df_alloc = pd.DataFrame(
                        [
                            {"Classe": classe, "Valor (R$)": valor}
                            for classe, valor in allocation.items()
                        ]
                    )
                    total_alloc = df_alloc["Valor (R$)"].sum()
                    if total_alloc > 0:
                        df_alloc["Peso (%)"] = (
                            df_alloc["Valor (R$)"] / total_alloc * 100
                        ).round(2)

                    st.dataframe(
                        df_alloc,
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info("Nenhuma alocação disponível.")

            with col_dir:
                st.subheader("🧮 Composição do Score de Risco")

                if over_cp["detalhes"]:
                    df_risco = pd.DataFrame(over_cp["detalhes"])

                    st.dataframe(
                        df_risco,
                        use_container_width=True,
                        hide_index=True,
                    )

                    st.caption(
                        "Score da carteira = Σ (peso da posição × risco atribuído à classe)."
                    )
                else:
                    st.info("Cliente sem posições de investimento.")

                st.subheader("📋 Escala usada na demonstração")

                df_regras = pd.DataFrame([
                    {"Classe": "Renda Fixa Bancária", "Código": "BANK_FIXED_INCOME", "Risco": 1.0},
                    {"Classe": "Tesouro", "Código": "TREASURY", "Risco": 2.0},
                    {"Classe": "Fundos", "Código": "FUND", "Risco": 3.0},
                    {"Classe": "Renda Variável", "Código": "VARIABLE_INCOME", "Risco": 5.0},
                ])

                st.dataframe(
                    df_regras,
                    use_container_width=True,
                    hide_index=True,
                )

            # ------------------------------
            # Dores captadas / reunião
            # ------------------------------
            st.divider()
            st.subheader("📋 Contexto para o Assessor")

            col_contexto, col_reuniao = st.columns([2, 1])

            with col_contexto:
                if st.session_state.resumo_dores:
                    st.info(st.session_state.resumo_dores)
                else:
                    st.write("O cliente ainda não concluiu o briefing conversacional.")

            with col_reuniao:
                if st.session_state.agendamento:
                    st.write(
                        f"**Data:** {st.session_state.agendamento['data']}\n\n"
                        f"**Horário:** {st.session_state.agendamento['hora']}\n\n"
                        f"**Modalidade:** {st.session_state.agendamento['modalidade']}"
                    )
                else:
                    st.write("**Reunião:** ainda não agendada.")

        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 404:
                st.error(
                    "Cliente não encontrado na API. Confira se o nome e CPF "
                    "informados correspondem a um cliente da base."
                )
            else:
                st.error(f"Erro retornado pela API Open Finance: {exc}")

        except requests.RequestException as exc:
            st.error(
                "Não foi possível comunicar com a API Open Finance. "
                "Confirme se ela está rodando em http://localhost:8000."
            )
            st.caption(str(exc))