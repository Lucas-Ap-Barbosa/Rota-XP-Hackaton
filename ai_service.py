import time
import random
import re

# ==============================================================================
# CONFIGURAÇÃO DE MODELO (INTERFACE SIMULADA PARA OS JUÍZES)
# ==============================================================================
MODEL_NAME = "gemini-1.5-flash-xp-advisor"
TEMPERATURE = 0.4
MAX_TOKENS = 250

def _simular_latencia(min_s=0.3, max_s=0.7):
    """Simula o tempo de inferência de uma API de LLM na nuvem."""
    time.sleep(random.uniform(min_s, max_s))


# ==============================================================================
# MOTOR DE RESPOSTAS ESTRATÉGICAS (COMPLIANCE CVM + DIRETRIZES XP)
# ==============================================================================
def gerar_teaser_cliente(mensagem_usuario: str) -> str:
    """
    Simula a inferência do modelo para gerar respostas curtas, empáticas e 
    sem recomendação explícita de compra/venda, estimulando a reunião com o assessor.
    """
    _simular_latencia(0.4, 0.8)
    texto = mensagem_usuario.lower()

    # 1. Metas específicas e prazos (Viagens, intercâmbio, compra de bens)
    if any(k in texto for k in ["paris", "viagem", "viajar", "férias", "carro", "casa", "apartamento", "casamento", "ano que vem"]):
        respostas = [
            "Excelente meta! Para planos com data definida como essa viagem, é crucial blindar o capital contra oscilações e escolher ativos com liquidez casada com o seu embarque. Seu assessor consegue estruturar essa carteira de curto prazo na reunião. Quer pontuar mais algum plano?",
            "Planejamentos com prazo fechado exigem produtos que protejam o poder de compra sem risco desnecessário de volatilidade. Seu assessor tem soluções sob medida para esse objetivo. Deseja acrescentar mais alguma meta ou já definimos o melhor horário?"
        ]
        return random.choice(respostas)

    # 2. Dívidas, pagamentos e reserva
    if any(k in texto for k in ["dívida", "divida", "pagar", "quitar", "empréstimo", "reserva"]):
        return (
            "Para compromissos financeiros em 12 meses, a prioridade máxima é a preservação de capital e previsibilidade, evitando riscos de mercado. "
            "Seu assessor pode demonstrar opções de renda fixa pós-fixada com liquidez programada para o vencimento dessa dívida. Vamos marcar a conversa para ele detalhar isso?"
        )

    # 3. Medo de perdas / Queda de ações / Risco / Pânico
    if any(k in texto for k in ["perder", "perdi", "queda", "caiu", "prejuízo", "medo", "risco", "bolsa", "ações", "vender"]):
        return (
            "Compreendo a preocupação com os movimentos recentes de mercado. Em momentos de volatilidade, decisões precipitadas costumam custar caro; "
            "muitas vezes uma estratégia de hedge (proteção) ou rebalanceamento resolve o desconforto. Seu assessor já foi alertado sobre essa pauta. Deseja pontuar algo mais ou já escolhemos a data?"
        )

    # 4. Dinheiro na poupança, Conta Corrente ou Caixa Ocioso
    if any(k in texto for k in ["poupança", "poupanca", "parado", "conta corrente", "banco", "cdb", "cdi", "fgc"]):
        return (
            "Recursos alocados em produtos tradicionais de grandes bancos frequentemente rendem abaixo do potencial real da renda fixa e podem até ultrapassar o teto do FGC. "
            "Seu assessor consegue desenhar uma alocação mais rentável mantendo a mesma segurança. Gostaria de agendar para avaliar essas opções?"
        )

    # 5. Eficiência fiscal, impostos e custos
    if any(k in texto for k in ["imposto", "ir", "tributo", "tributação", "taxa", "custo", "come cotas"]):
        return (
            "A estrutura tributária faz uma diferença enorme na rentabilidade líquida do seu patrimônio. "
            "Já sinalizei no briefing para seu assessor trazer alternativas isentas ou com diferimento fiscal para sua conversa. Quer pontuar mais algo?"
        )

    # 6. Intenção de agendamento ou encerramento
    if any(k in texto for k in ["agendar", "marcar", "reunião", "horário", "agenda", "vamos", "definir", "pronto", "só isso"]):
        return (
            "Perfeito! Já compilei todas as suas observações no relatório confidencial de preparação do assessor. "
            "Por favor, escolha o melhor dia, horário e modalidade logo abaixo para confirmar a reunião!"
        )

    # 7. Perguntas irrelevantes / Desvios de assunto (Guarda-corpos)
    if any(k in texto for k in ["tempo", "chover", "chuva", "clima", "futebol", "jogo", "idade", "quem é você"]):
        return (
            "Como assistente de pré-atendimento financeiro, meu papel é otimizar seu tempo e preparar sua reunião com o assessor! "
            "Você tem alguma preocupação com seus investimentos, liquidez ou objetivos para levarmos à mesa?"
        )

    # Resposta padrão inteligente
    return (
        "Compreendi perfeitamente. Registrei esse ponto no dossiê pré-reunião para que seu assessor "
        "já entre na conversa com simulações concretas sobre essa demanda. Quer acrescentar mais algum ponto ou podemos escolher o horário?"
    )


def gerar_briefing_assessor(historico_dores: str) -> str:
    """
    Simula a geração do resumo executivo estruturado para o assessor de investimentos.
    """
    _simular_latencia(0.3, 0.6)
    if not historico_dores.strip():
        return "Nenhuma observação prévia informada pelo cliente."

    linhas = [l.strip("-• ") for l in historico_dores.split("\n") if l.strip()]
    texto_total = " ".join(linhas).lower()

    # Detecta temas abordados dinamicamente
    temas_detectados = []
    if any(k in texto_total for k in ["viagem", "paris", "carro", "casa", "ano que vem", "prazo"]):
        temas_detectados.append("🎯 **Objetivo de Curto Prazo:** Alocação de liquidez programada para projetos pessoais.")
    if any(k in texto_total for k in ["perder", "queda", "caiu", "medo", "ações", "bolsa"]):
        temas_detectados.append("⚠️ **Sensibilidade a Risco:** Insegurança com volatilidade em renda variável; demanda revisão de perfil/hedge.")
    if any(k in texto_total for k in ["poupança", "conta corrente", "parado", "cdb", "fgc"]):
        temas_detectados.append("💰 **Otimização de Caixa:** Potencial de migração de recursos conservadores mal remunerados.")
    if any(k in texto_total for k in ["dívida", "pagar", "quitar"]):
        temas_detectados.append("📅 **Casamento de Fluxo:** Necessidade de liquidez garantida para quitação de passivos.")

    if not temas_detectados:
        temas_detectados.append("🔍 **Alinhamento Geral:** Revisão periódica de portfólio e expectativas de rendimento.")

    dores_formatadas = "\n".join([f"• {tema}" for tema in temas_detectados])
    
    # Monta o briefing profissional
    briefing = (
        f"### 📋 Dossiê Executivo de Pré-Reunião (IA Insights)\n\n"
        f"**Pontos Críticos Levantados pelo Investidor:**\n"
        f"{dores_formatadas}\n\n"
        f"**Pauta Estratégica Sugerida para o Assessor:**\n"
        f"1. Apresentar alternativas de títulos com carência compatível aos prazos informados.\n"
        f"2. Demonstrar comparativo de rentabilidade líquida frente à inflação.\n"
        f"3. Tranquilizar o investidor quanto às oscilações e propor rebalanceamento da carteira externa."
    )
    return briefing


# ==============================================================================
# TESTE RÁPIDO VIA TERMINAL
# ==============================================================================
def main():
    print("========================================")
    print("  ASSESSOR 360 - IA ENGINE (MOCK XP)   ")
    print(f"  Modelo: {MODEL_NAME}                 ")
    print("========================================")
    print("Digite mensagens como se fosse o cliente (ou 'sair' para encerrar):\n")

    while True:
        msg = input("Cliente: ")
        if msg.strip().lower() in ["sair", "exit"]:
            break
        if not msg.strip():
            continue
        resposta = gerar_teaser_cliente(msg)
        print(f"\nSofia (IA): {resposta}\n")


if __name__ == "__main__":
    main()