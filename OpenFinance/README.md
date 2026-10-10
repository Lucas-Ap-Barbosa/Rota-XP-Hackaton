# Mock Open Finance Brasil — Hybrid Investment Dataset

Projeto de hackathon para simular uma API de Open Finance com foco em investimentos brasileiros.

## Ideia central

A base é híbrida:

- **Clientes, contas, transações e posições são sintéticos** e não representam pessoas reais.
- **Produtos de investimento são reais quando possível**: ações/ETF listados no Brasil, fundos com CNPJ real e títulos reais do Tesouro Direto.
- **CDBs são sintéticos**, porque as ofertas bancárias variam por instituição/canal e não há um catálogo público único equivalente às posições individuais do Open Finance.
- Preços/cotas/taxas possuem uma coluna de origem e uma data de referência.

O dataset foi gerado com seed fixa `20261010`, permitindo reproduzir as mesmas carteiras.

## Arquivos

```text
data/
├── customers.csv
├── accounts.csv
├── bank_transactions.csv
├── investment_products.csv
├── investments.csv
├── investment_transactions.csv
├── sources.csv
└── manifest.json
```

`investment_products.csv` é o catálogo de produtos. `investments.csv` representa quais produtos cada cliente possui. Portanto, um ticker/CNPJ pode ser real mesmo quando a quantidade possuída pelo cliente é sintética.

## Volume da versão incluída

- 80 clientes sintéticos
- 160 contas
- ~2 mil transações bancárias
- 20 produtos de investimento
- 600 posições
- ~1 mil movimentações de investimento

## Investimentos modelados

- Renda variável: ações e ETF
- Fundos de investimento
- Tesouro Direto
- Renda fixa bancária (CDB sintético)

As carteiras são geradas conforme o perfil de risco:

- conservador: maior peso em CDB/Tesouro;
- moderado: distribuição mais balanceada;
- agressivo: maior peso em renda variável.

## Como rodar

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/build_db.py
uvicorn app.main:app --reload
```

Swagger:

```text
http://localhost:8000/docs
```

Autorização:

```text
Authorization: Bearer hackathon-token
```

## Exemplos

```http
GET /customers
GET /accounts?customer_id=CUST_0001
GET /portfolio/summary?customer_id=CUST_0001
GET /investments?customer_id=CUST_0001
GET /investments/{investment_id}/balances
GET /investments/{investment_id}/transactions
GET /dataset/source
```

Aliases inspirados nas famílias de investimento do Open Finance Brasil:

```http
GET /open-banking/variable-incomes/v1/investments?customer_id=CUST_0001
GET /open-banking/funds/v1/investments?customer_id=CUST_0001
GET /open-banking/treasure-titles/v1/investments?customer_id=CUST_0001
GET /open-banking/bank-fixed-incomes/v1/investments?customer_id=CUST_0001
```

O parâmetro `customer_id` é um atalho da hackathon. Em uma implementação real, o cliente seria determinado por consentimento/token e não por uma query livre.

## Recriar a base

```bash
python generate_dataset.py
python scripts/build_db.py
python scripts/validate.py
```

## Atualizar fontes oficiais localmente

O script abaixo baixa os arquivos brutos de CVM e Tesouro para `source_raw/`:

```bash
python scripts/refresh_official_sources.py
```

Ele serve para atualização/auditoria. O snapshot incluído no ZIP permanece estável para a demo.

## Importante

Este projeto **não é uma implementação certificada do Open Finance Brasil**. Ele simula recursos e famílias de endpoints para uma hackathon. Consulte `DATA_PROVENANCE.md` antes de afirmar que um dado é real: a identidade do produto pode ser real enquanto a posição do cliente é sintética.
