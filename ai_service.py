import json
from pathlib import Path

# Carrega a base de dados de mocks estruturada
CAMINHO_JSON = Path(__file__).with_name("perfis_mock.json")

DADOS_MOCK = {}
if CAMINHO_JSON.exists():
    with open(CAMINHO_JSON, "r", encoding="utf-8") as f:
        DADOS_MOCK = json.load(f)


def _limpar_cpf(cpf: str) -> str:
    """Remove pontos, traços e espaços do CPF."""
    return "".join(c for c in str(cpf) if c.isdigit())


def obter_cliente_mock(cpf: str):
    """Retorna os dados do cliente cadastrado pelo CPF."""
    cpf_limpo = _limpar_cpf(cpf)
    return DADOS_MOCK.get(cpf_limpo)


def obter_respostas_iniciais_sugeridas(cpf: str):
    """
    Retorna as respostas pré-definidas para as duas primeiras perguntas do bot.
    Útil caso queira sugerir ou preencher automaticamente na demonstração.
    """
    cliente = obter_cliente_mock(cpf)
    if cliente:
        return {
            "panorama": cliente.get("investimentos_iniciais", ""),
            "metas": cliente.get("metas_preocupacoes_iniciais", "")
        }
    return {"panorama": "", "metas": ""}


def criar_resumo(cpf: str, qtd_observacoes: int = 0) -> str:
    """
    Gera o resumo evolutivo baseado no CPF e na quantidade de observações adicionais feitas.
    """
    cliente = obter_cliente_mock(cpf)
    if not cliente:
        return "Resumo preliminar em elaboração: dados gerais recebidos pelo assessor."

    historico = cliente.get("historico_resumos", [])
    if not historico:
        return "Resumo em elaboração."

    # Seleciona o resumo correspondente à quantidade de observações ou o último disponível
    indice = min(qtd_observacoes, len(historico) - 1)
    item = historico[indice]
    return item["resumo"]


def determinar_perfil(cpf: str, qtd_observacoes: int = 0) -> str:
    """
    Retorna o perfil preliminar determinado pela IA com base nas interações.
    """
    cliente = obter_cliente_mock(cpf)
    if not cliente:
        return "Indeterminado"

    historico = cliente.get("historico_resumos", [])
    if not historico:
        return "Indeterminado"

    indice = min(qtd_observacoes, len(historico) - 1)
    return historico[indice].get("perfil_preliminar", "Indeterminado")


def gerar_teaser_cliente(resumo_ou_mensagem: str) -> str:
    """
    Retorna um insight provocativo para instigar o agendamento.
    """
    return (
        "Analisando suas posições e objetivos declarados, identificamos oportunidades "
        "importantes de alinhamento entre rentabilidade e segurança que seu assessor detalhará na conversa."
    )


def gerar_briefing_assessor(historico_dores: str) -> str:
    """Mantido para compatibilidade com o app."""
    return f"**Síntese Executiva:**\n{historico_dores}"