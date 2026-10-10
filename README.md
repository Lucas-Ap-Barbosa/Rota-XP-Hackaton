# Rota-XP-Hackaton

![Status: protótipo](https://img.shields.io/badge/status-prot%C3%B3tipo-orange)
![Foco: chatbot](https://img.shields.io/badge/foco-chatbot-2ea44f)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)
![Streamlit](https://img.shields.io/badge/Streamlit-interface-FF4B4B)
![PandaDB](https://img.shields.io/badge/dados-PandaDB-150458)

## Sumário do projeto
O Rota-XP-Hackaton é um protótipo de chatbot para apoiar o assessor de investimentos no atendimento inicial aos seus clientes. O chatbot será o ponto principal do projeto: ele conversará com o cliente, responderá dúvidas gerais de rotina e realizará uma triagem antes do contato direto com o assessor.
O projeto será desenvolvido sob a perspectiva do assessor de investimentos, buscando organizar as informações recebidas antes de uma conversa por chat ou de uma reunião. Em uma evolução posterior, o chatbot poderá consultar a agenda do assessor e permitir que o próprio cliente agende um horário disponível.
> O chatbot não substitui o assessor de investimentos. Ele facilita a comunicação, coleta informações preliminares e trata perguntas gerais, enquanto a análise e a decisão sobre investimentos permanecem sob responsabilidade do profissional habilitado.

## Objetivo principal: chatbot

![Etapa principal](https://img.shields.io/badge/etapa-principal-2ea44f)

O objetivo principal é criar um chatbot capaz de:

- Conversar com clientes por um canal de atendimento, como Telegram ou WhatsApp.
- Responder perguntas gerais e recorrentes sobre o processo de atendimento.
- Fazer perguntas-chave para entender o contexto inicial do cliente.
- Realizar uma triagem com informações como objetivos, experiência, prazo e tolerância a riscos.
- Organizar as respostas em um resumo para o assessor.
- Encaminhar o cliente para um contato direto por chat ou para uma reunião.
- Apoiar, futuramente, o agendamento de reuniões conforme a disponibilidade do assessor.

## Fluxo de atendimento

![Fluxo](https://img.shields.io/badge/fluxo-conversa%20%7C%20triagem%20%7C%20encaminhamento-0366d6)

1. O cliente inicia uma conversa com o chatbot.
2. O chatbot responde dúvidas gerais e apresenta o fluxo de atendimento.
3. O cliente responde às perguntas de triagem.
4. As respostas são armazenadas e organizadas para consulta do assessor.
5. O assessor analisa o resumo antes do contato com o cliente.
6. O cliente é direcionado para uma conversa por chat ou para uma reunião.
7. Em uma etapa futura, o chatbot consulta a agenda do assessor e permite o agendamento de um horário disponível.

## Visão do assessor de investimentos

![Perspectiva](https://img.shields.io/badge/perspectiva-assessor%20de%20investimentos-6f42c1)

O sistema deve reduzir o tempo gasto com perguntas repetitivas e melhorar a qualidade das informações disponíveis antes do atendimento. O assessor deverá receber um resumo objetivo do cliente, sem que o chatbot faça recomendações definitivas ou tome decisões de investimento.

O chatbot servirá como uma etapa de preparação para o atendimento, permitindo que o assessor concentre a reunião na compreensão do caso, na validação das informações e na orientação adequada ao cliente.

## Tecnologias previstas

![Stack](https://img.shields.io/badge/stack-Python%20%7C%20PandaDB%20%7C%20Streamlit-24292f)

- **Python:** desenvolvimento da lógica do chatbot, regras de triagem, tratamento das respostas e integrações.
- **PandaDB:** armazenamento e consulta dos dados do protótipo, incluindo respostas dos clientes e informações utilizadas nos testes.
- **Streamlit:** criação da interface do protótipo, visualização do fluxo conversacional e apresentação dos dados ao assessor.
- **Telegram ou WhatsApp:** canais previstos para a comunicação com os clientes, conforme a integração escolhida para o protótipo.
- **Agenda do assessor:** integração futura para consultar horários disponíveis e permitir a criação de reuniões.

## Escopo inicial
O primeiro ciclo deve priorizar:

- Fluxo básico de conversa.
- Perguntas de triagem e validação das respostas.
- Persistência dos dados no PandaDB.
- Resumo das informações para o assessor.
- Atendimento de perguntas gerais e recorrentes.
- Protótipo da interface em Streamlit.

Integrações com Telegram, WhatsApp, Microsoft Teams, Google Meet e a agenda do assessor poderão ser implementadas de forma incremental após a validação do fluxo principal.

## Apêndice: alertas e notificações

![Funcionalidade complementar](https://img.shields.io/badge/fun%C3%A7%C3%A3o-complementar-lightgrey)

Os alertas de notificações são uma funcionalidade complementar e não representam o objetivo principal do projeto. Eles poderão apoiar o assessor e o cliente em situações como:

- Aviso de nova triagem concluída.
- Notificação de solicitação de contato.
- Lembrete de reunião agendada.
- Confirmação ou alteração de horário.
- Aviso de pendência no atendimento.

Essa funcionalidade deverá ser integrada depois que o fluxo principal do chatbot estiver validado.

## Limites do protótipo

- O chatbot não substitui o assessor de investimentos.
- As respostas do chatbot não constituem recomendação financeira definitiva.
- A análise do perfil e a orientação ao cliente devem ser validadas pelo assessor.
- Os dados utilizados nos testes devem ser controlados e, quando necessário, anonimizados.

## Instalação

![Setup](https://img.shields.io/badge/setup-ambiente%20Python-yellow)

### Pré-requisitos

- Python 3.10 ou superior.
- Git.
- Acesso ao ambiente ou serviço utilizado pelo PandaDB.

### Configuração do ambiente

Clone o repositório e acesse a pasta do projeto:

```bash
git clone <url-do-repositorio>
cd Rota-XP-Hackaton
```

Crie e ative um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

No Windows, a ativação pode ser feita com:

```powershell
.venv\Scripts\Activate.ps1
```

Instale as dependências do projeto:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

As dependências devem incluir o Streamlit, o driver ou biblioteca utilizada pelo PandaDB e as demais bibliotecas de integração do chatbot.

### Variáveis de ambiente

Quando necessário, crie um arquivo `.env` com as credenciais e configurações de acesso ao PandaDB e aos canais de comunicação. Não versionar tokens, senhas ou dados reais de clientes.

### Execução

Inicie a interface do protótipo com:

```bash
streamlit run app.py
```

O arquivo `app.py` representa o ponto de entrada previsto para a aplicação. Caso o projeto utilize outro arquivo principal, substitua o nome no comando acima.

## Estratégia de branches

![Git Flow](https://img.shields.io/badge/Git-branches%20organizadas-F05032)

As branches do projeto devem seguir os três tipos abaixo:

| Tipo | Padrão | Objetivo | Origem | Destino |
| --- | --- | --- | --- | --- |
| Versão | `version/<versao>` | Preparar uma entrega, como `version/1.0.0` | `main` | `main` |
| Feature | `feature/<descricao>` | Desenvolver uma nova funcionalidade, como `feature/login` | `main` | `main` |
| Hotfix | `hotfix/<descricao>` | Corrigir um problema urgente, como `hotfix/corrigir-login` | `main` | `main` |

## Fluxo de trabalho

![Colaboração](https://img.shields.io/badge/colabora%C3%A7%C3%A3o-Pull%20Request-8957e5)

1. Atualize a branch principal:

	```bash
	git checkout main
	git pull origin main
	```

2. Crie uma branch com o prefixo adequado:

	```bash
	git checkout -b feature/nome-da-feature
	```

3. Faça commits pequenos e objetivos.
4. Publique a branch e abra um Pull Request para `main`:

	```bash
	git push -u origin feature/nome-da-feature
	```

5. Após a aprovação e a validação dos testes, faça o merge e remova a branch utilizada.

## Regras

- Não fazer commits diretamente em `main`.
- Usar nomes em minúsculas, sem espaços e separados por hífen.
- Uma branch deve tratar apenas uma feature, versão ou correção.
- A branch `version/*` deve conter apenas ajustes necessários para preparar a versão.
- A branch `hotfix/*` deve ser usada somente para correções urgentes.
- Todo Pull Request deve descrever a alteração e informar como ela foi validada.
