# Mock Open Finance Brasil — Hybrid Investments

API REST para hackathon que simula parte do ecossistema de **Open Finance Brasil**, com foco em contas, transações bancárias e investimentos.

A base combina:

- clientes, contas, carteiras e movimentações **sintéticas**;
- produtos de investimento brasileiros reais quando possível;
- valores em **BRL**;
- fundos, Tesouro, renda variável e renda fixa bancária;
- endpoints simplificados e aliases inspirados nas APIs do Open Finance Brasil.

> **Importante:** este projeto é uma simulação para hackathon. Não é uma implementação oficial nem certificada do Open Finance Brasil.

---

## 1. Conteúdo da base

A versão atual contém aproximadamente:

| Entidade | Quantidade |
|---|---:|
| Clientes | 80 |
| Contas | 160 |
| Transações bancárias | 2.046 |
| Produtos de investimento | 20 |
| Posições de investimento | 600 |
| Movimentações de investimento | 1.038 |

Cada cliente pode possuir:

- conta corrente;
- conta de investimento;
- transações bancárias;
- posições em renda variável;
- fundos;
- Tesouro;
- CDBs;
- histórico de movimentações de investimento;
- resumo consolidado do portfólio.

Os produtos reais e sintéticos são identificados pelos campos `product_origin` e `position_origin`.

---

## 2. Estrutura do projeto

```text
.
├── app/
│   └── main.py
├── data/
│   ├── customers.csv
│   ├── accounts.csv
│   ├── bank_transactions.csv
│   ├── investment_products.csv
│   ├── investments.csv
│   ├── investment_transactions.csv
│   ├── sources.csv
│   └── manifest.json
├── scripts/
│   ├── build_db.py
│   ├── refresh_official_sources.py
│   └── validate.py
├── DATA_PROVENANCE.md
├── generate_dataset.py
├── open_finance_br.db
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## 3. Instalação

Crie um ambiente virtual:

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Se quiser reconstruir o SQLite a partir dos CSVs:

```bash
python scripts/build_db.py
```

Para validar a consistência dos dados:

```bash
python scripts/validate.py
```

---

## 4. Executando a API

Execute:

```bash
uvicorn app.main:app --reload
```

A API ficará disponível em:

```text
http://localhost:8000
```

A documentação Swagger pode ser acessada em:

```text
http://localhost:8000/docs
```

A documentação OpenAPI alternativa fica em:

```text
http://localhost:8000/redoc
```

---

## 5. Autenticação

Todos os endpoints, exceto `/health`, exigem o header:

```http
Authorization: Bearer hackathon-token
```

Exemplo com `curl`:

```bash
curl \
  -H "Authorization: Bearer hackathon-token" \
  http://localhost:8000/customers
```

No Swagger (`/docs`), envie o mesmo header nas requisições.

---

## 6. Formato padrão das respostas

A maior parte dos endpoints retorna um envelope no formato:

```json
{
  "data": {},
  "meta": {
    "totalRecords": 1,
    "totalPages": 1
  }
}
```

Quando `data` é uma lista:

```json
{
  "data": [
    {},
    {}
  ],
  "meta": {
    "totalRecords": 2,
    "totalPages": 1
  }
}
```

---

# 7. Endpoints

## 7.1 Health check

### `GET /health`

Verifica se a API está funcionando e informa o banco SQLite em uso.

**Autenticação:** não exigida.

Exemplo:

```bash
curl http://localhost:8000/health
```

Retorno:

```json
{
  "status": "ok",
  "database": "open_finance_br.db"
}
```

---

## 7.2 Origem dos dados

### `GET /dataset/source`

Retorna informações sobre a geração da base e as fontes utilizadas.

Inclui:

- nome do dataset;
- data de geração;
- data de referência;
- seed;
- quantidade de registros;
- metodologia;
- fontes oficiais e de referência.

Exemplo:

```bash
curl \
  -H "Authorization: Bearer hackathon-token" \
  http://localhost:8000/dataset/source
```

Retorno simplificado:

```json
{
  "manifest": {
    "dataset_name": "Open Finance BR Hybrid Hackathon Dataset",
    "reference_date": "2026-10-09",
    "customers": 80,
    "investments": 600
  },
  "sources": []
}
```

---

# 8. Clientes

## `GET /customers`

Lista clientes sintéticos.

### Parâmetros

| Parâmetro | Tipo | Obrigatório | Descrição |
|---|---|---:|---|
| `limit` | inteiro | não | Número de clientes retornados. Padrão `20`, máximo `100`. |

Exemplo:

```bash
curl \
  -H "Authorization: Bearer hackathon-token" \
  "http://localhost:8000/customers?limit=10"
```

Cada cliente contém campos como:

```json
{
  "customer_id": "CUST_0001",
  "name": "Lucas Pereira Santos",
  "age": 67,
  "state": "BA",
  "monthly_income": 21230.21,
  "risk_profile": "CONSERVATIVE",
  "synthetic": true
}
```

---

## `GET /customers/{customer_id}`

Retorna os dados de um único cliente.

Exemplo:

```bash
curl \
  -H "Authorization: Bearer hackathon-token" \
  http://localhost:8000/customers/CUST_0001
```

Retorna informações como nome, idade, estado, renda mensal e perfil de risco.

---

# 9. Contas

## `GET /accounts`

Lista as contas de um cliente.

### Parâmetros

| Parâmetro | Tipo | Obrigatório |
|---|---|---:|
| `customer_id` | string | sim |

Exemplo:

```bash
curl \
  -H "Authorization: Bearer hackathon-token" \
  "http://localhost:8000/accounts?customer_id=CUST_0001"
```

Retorno típico:

```json
{
  "account_id": "ACC_0001_CHK",
  "customer_id": "CUST_0001",
  "type": "CONTA_CORRENTE",
  "currency": "BRL",
  "balance": 12775.44,
  "status": "ACTIVE",
  "synthetic": true
}
```

---

## `GET /accounts/{account_id}/balances`

Retorna o saldo atual de uma conta.

Exemplo:

```bash
curl \
  -H "Authorization: Bearer hackathon-token" \
  http://localhost:8000/accounts/ACC_0001_CHK/balances
```

Retorno:

```json
{
  "data": {
    "accountId": "ACC_0001_CHK",
    "availableAmount": {
      "amount": 12775.44,
      "currency": "BRL"
    }
  },
  "meta": {
    "totalRecords": 1,
    "totalPages": 1
  }
}
```

---

## `GET /accounts/{account_id}/transactions`

Retorna o histórico de transações bancárias da conta.

### Parâmetros opcionais

| Parâmetro | Formato | Descrição |
|---|---|---|
| `from_date` | `YYYY-MM-DD` | Data inicial. |
| `to_date` | `YYYY-MM-DD` | Data final. |

Exemplo:

```bash
curl \
  -H "Authorization: Bearer hackathon-token" \
  "http://localhost:8000/accounts/ACC_0001_CHK/transactions?from_date=2026-06-01&to_date=2026-06-30"
```

Cada transação pode conter:

```json
{
  "transaction_id": "BTX_e2dd5f746cbf",
  "account_id": "ACC_0001_CHK",
  "customer_id": "CUST_0001",
  "date": "2026-06-11",
  "type": "CARD_PURCHASE",
  "credit_debit": "DEBIT",
  "amount": 478.89,
  "currency": "BRL",
  "description": "Compra - E_COMMERCE",
  "synthetic": true
}
```

---

# 10. Catálogo de produtos de investimento

## `GET /investment-products`

Lista os produtos financeiros disponíveis na base.

Os produtos são independentes das carteiras dos clientes. Esse endpoint funciona como o catálogo de instrumentos financeiros.

### Filtro opcional

```text
type
```

Tipos atualmente usados:

```text
VARIABLE_INCOME
FUND
TREASURY
BANK_FIXED_INCOME
```

Exemplo:

```bash
curl \
  -H "Authorization: Bearer hackathon-token" \
  "http://localhost:8000/investment-products?type=VARIABLE_INCOME"
```

Um produto pode retornar:

```json
{
  "product_id": "STK_PETR4",
  "type": "VARIABLE_INCOME",
  "subtype": "STOCK",
  "name": "Petróleo Brasileiro S.A. PN",
  "ticker": "PETR4",
  "cnpj": "33.000.167/0001-01",
  "current_price": 56.0,
  "currency": "BRL",
  "product_origin": "REAL",
  "price_origin": "PUBLIC_MARKET_SNAPSHOT"
}
```

Campos de proveniência permitem identificar se o produto é real ou sintético.

---

# 11. Carteira de investimentos do cliente

## `GET /investments`

Retorna a carteira de investimentos de um cliente.

### Parâmetros

| Parâmetro | Obrigatório | Descrição |
|---|---:|---|
| `customer_id` | sim | Cliente cuja carteira será consultada. |
| `type` | não | Filtra por classe de investimento. |

Exemplo:

```bash
curl \
  -H "Authorization: Bearer hackathon-token" \
  "http://localhost:8000/investments?customer_id=CUST_0001"
```

Exemplo filtrando apenas renda variável:

```bash
curl \
  -H "Authorization: Bearer hackathon-token" \
  "http://localhost:8000/investments?customer_id=CUST_0001&type=VARIABLE_INCOME"
```

Uma posição pode conter:

```json
{
  "investment_id": "INV_123",
  "customer_id": "CUST_0001",
  "product_id": "STK_PETR4",
  "type": "VARIABLE_INCOME",
  "subtype": "STOCK",
  "product_name": "Petróleo Brasileiro S.A. PN",
  "ticker": "PETR4",
  "quantity": 73,
  "average_price": 50.0,
  "current_unit_price": 56.0,
  "invested_amount": 3650.0,
  "current_amount": 4088.0,
  "unrealized_pnl": 438.0,
  "currency": "BRL",
  "product_origin": "REAL",
  "position_origin": "SYNTHETIC",
  "valuation_date": "2026-10-09"
}
```

### Interpretação

- `product_origin = REAL`: o instrumento representa um produto real brasileiro.
- `position_origin = SYNTHETIC`: a quantidade e a carteira pertencem a um cliente fictício.
- `invested_amount`: custo total da posição.
- `current_amount`: valor atual da posição.
- `unrealized_pnl`: lucro ou prejuízo ainda não realizado.

---

## `GET /investments/{investment_id}`

Retorna os detalhes completos de uma posição específica.

Além dos dados da posição, inclui informações do produto como:

- indexador;
- taxa;
- vencimento;
- ISIN;
- data de preço;
- origem do preço;
- URL da fonte oficial;
- URL da fonte de referência.

Exemplo:

```bash
curl \
  -H "Authorization: Bearer hackathon-token" \
  http://localhost:8000/investments/INV_123
```

---

## `GET /investments/{investment_id}/balances`

Retorna a posição financeira consolidada de um investimento.

Exemplo de retorno:

```json
{
  "data": {
    "investmentId": "INV_123",
    "quantity": 73,
    "grossAmount": {
      "amount": 4088.0,
      "currency": "BRL"
    },
    "investedAmount": {
      "amount": 3650.0,
      "currency": "BRL"
    },
    "unrealizedPnL": {
      "amount": 438.0,
      "currency": "BRL"
    },
    "valuationDate": "2026-10-09"
  },
  "meta": {
    "totalRecords": 1,
    "totalPages": 1
  }
}
```

---

## `GET /investments/{investment_id}/transactions`

Retorna as movimentações que deram origem à posição.

Exemplo:

```bash
curl \
  -H "Authorization: Bearer hackathon-token" \
  http://localhost:8000/investments/INV_123/transactions
```

As movimentações podem conter:

```json
{
  "investment_transaction_id": "ITX_123",
  "investment_id": "INV_123",
  "customer_id": "CUST_0001",
  "date": "2025-05-23",
  "type": "BUY",
  "quantity": 20,
  "unit_price": 48.5,
  "gross_amount": 970.0,
  "currency": "BRL",
  "synthetic": true
}
```

Para produtos como CDB, a movimentação pode utilizar `APPLICATION` e não possuir quantidade ou preço unitário.

---

# 12. Resumo do portfólio

## `GET /portfolio/summary`

Retorna uma visão consolidada do patrimônio financeiro do cliente.

### Parâmetro

```text
customer_id
```

Exemplo:

```bash
curl \
  -H "Authorization: Bearer hackathon-token" \
  "http://localhost:8000/portfolio/summary?customer_id=CUST_0001"
```

Retorno:

```json
{
  "data": {
    "customerId": "CUST_0001",
    "cashBRL": 12775.44,
    "investmentsMarketValueBRL": 204200.0,
    "investmentsCostBasisBRL": 190000.0,
    "unrealizedPnLBRL": 14200.0,
    "totalFinancialAssetsBRL": 216975.44,
    "allocationByType": {
      "BANK_FIXED_INCOME": 85775.0,
      "TREASURY": 71479.0,
      "FUND": 36761.0,
      "VARIABLE_INCOME": 10185.0
    }
  },
  "meta": {
    "totalRecords": 1,
    "totalPages": 1
  }
}
```

### Significado dos campos

| Campo | Significado |
|---|---|
| `cashBRL` | Saldo das contas correntes. |
| `investmentsMarketValueBRL` | Valor atual de todos os investimentos. |
| `investmentsCostBasisBRL` | Total originalmente investido. |
| `unrealizedPnLBRL` | Lucro/prejuízo não realizado. |
| `totalFinancialAssetsBRL` | Caixa + valor atual dos investimentos. |
| `allocationByType` | Distribuição da carteira por classe. |

---

# 13. Endpoints inspirados no Open Finance Brasil

Além dos endpoints simplificados, a API possui aliases com URLs semelhantes às utilizadas no ecossistema Open Finance.

> Nesta implementação, `customer_id` é passado diretamente como parâmetro para facilitar a demonstração. Em um ambiente real, a identidade do cliente seria derivada do consentimento e do token de acesso.

---

## Renda variável

### `GET /open-banking/variable-incomes/v1/investments`

Parâmetro:

```text
customer_id
```

Retorna apenas posições com:

```text
VARIABLE_INCOME
```

Exemplo:

```bash
curl \
  -H "Authorization: Bearer hackathon-token" \
  "http://localhost:8000/open-banking/variable-incomes/v1/investments?customer_id=CUST_0001"
```

---

## Fundos

### `GET /open-banking/funds/v1/investments`

Retorna apenas posições do tipo:

```text
FUND
```

---

## Tesouro

### `GET /open-banking/treasure-titles/v1/investments`

Retorna apenas posições do tipo:

```text
TREASURY
```

---

## Renda fixa bancária

### `GET /open-banking/bank-fixed-incomes/v1/investments`

Retorna apenas posições do tipo:

```text
BANK_FIXED_INCOME
```

---

## Contas — alias Open Finance

### `GET /open-banking/accounts/v2/accounts`

Parâmetro obrigatório:

```text
customer_id
```

Retorna as contas do cliente.

---

### `GET /open-banking/accounts/v2/accounts/{account_id}/balances`

Retorna o saldo da conta.

---

### `GET /open-banking/accounts/v2/accounts/{account_id}/transactions`

Retorna as transações da conta.

Filtros opcionais:

```text
from_date
to_date
```

---

# 14. Fluxo recomendado para utilizar a API

Para consultar todos os dados financeiros de um cliente, um fluxo típico é:

### 1. Buscar clientes

```http
GET /customers
```

Escolha, por exemplo:

```text
CUST_0001
```

### 2. Buscar as contas

```http
GET /accounts?customer_id=CUST_0001
```

### 3. Consultar saldo da conta

```http
GET /accounts/ACC_0001_CHK/balances
```

### 4. Consultar transações bancárias

```http
GET /accounts/ACC_0001_CHK/transactions
```

### 5. Buscar a carteira de investimentos

```http
GET /investments?customer_id=CUST_0001
```

### 6. Consultar uma posição específica

```http
GET /investments/{investment_id}
```

### 7. Consultar movimentações desse investimento

```http
GET /investments/{investment_id}/transactions
```

### 8. Obter o resumo completo do patrimônio

```http
GET /portfolio/summary?customer_id=CUST_0001
```

Esse último endpoint é normalmente o mais útil para dashboards e aplicações de agregação financeira.

---

# 15. Exemplo em Python

```python
import requests

BASE_URL = "http://localhost:8000"
HEADERS = {
    "Authorization": "Bearer hackathon-token"
}

customer_id = "CUST_0001"

portfolio = requests.get(
    f"{BASE_URL}/portfolio/summary",
    params={"customer_id": customer_id},
    headers=HEADERS,
)

portfolio.raise_for_status()

print(portfolio.json())
```

---

# 16. Exemplo em JavaScript

```javascript
const customerId = "CUST_0001";

const response = await fetch(
  `http://localhost:8000/portfolio/summary?customer_id=${customerId}`,
  {
    headers: {
      Authorization: "Bearer hackathon-token"
    }
  }
);

const portfolio = await response.json();
console.log(portfolio);
```

---

# 17. Códigos de erro

### `401 Unauthorized`

O token não foi enviado ou está incorreto.

Use:

```http
Authorization: Bearer hackathon-token
```

### `404 Not Found`

O cliente, conta ou investimento solicitado não existe.

Exemplo:

```json
{
  "detail": "Resource not found"
}
```

### `422 Unprocessable Entity`

Um parâmetro obrigatório está ausente ou possui formato inválido.

Exemplo comum:

```text
GET /accounts
```

sem enviar:

```text
customer_id
```

---

# 18. Proveniência dos investimentos

A base foi construída para diferenciar claramente produtos financeiros reais de carteiras fictícias.

Exemplo:

```text
PETR4
product_origin = REAL
position_origin = SYNTHETIC
```

Isso significa:

- PETR4 representa um instrumento financeiro real;
- o cliente que possui PETR4 é fictício;
- a quantidade possuída é sintética;
- as movimentações do cliente são sintéticas.

Para CDBs criados especificamente para a simulação:

```text
product_origin = SYNTHETIC
position_origin = SYNTHETIC
```

Mais detalhes estão disponíveis em:

```text
DATA_PROVENANCE.md
```

ou pelo endpoint:

```http
GET /dataset/source
```

---

# 19. Uso com Docker

Também é possível executar a API com Docker.

```bash
docker compose up --build
```

Depois acesse:

```text
http://localhost:8000/docs
```

---

# 20. Resumo rápido dos endpoints

| Método | Endpoint | Função |
|---|---|---|
| GET | `/health` | Verifica se a API está online. |
| GET | `/dataset/source` | Retorna origem e metodologia dos dados. |
| GET | `/customers` | Lista clientes. |
| GET | `/customers/{customer_id}` | Retorna um cliente. |
| GET | `/accounts` | Lista contas de um cliente. |
| GET | `/accounts/{account_id}/balances` | Retorna saldo da conta. |
| GET | `/accounts/{account_id}/transactions` | Retorna transações bancárias. |
| GET | `/investment-products` | Lista produtos financeiros disponíveis. |
| GET | `/investments` | Retorna a carteira de um cliente. |
| GET | `/investments/{investment_id}` | Detalha uma posição. |
| GET | `/investments/{investment_id}/balances` | Retorna saldo/valor da posição. |
| GET | `/investments/{investment_id}/transactions` | Retorna movimentações do investimento. |
| GET | `/portfolio/summary` | Retorna patrimônio financeiro consolidado. |
| GET | `/open-banking/variable-incomes/v1/investments` | Lista renda variável do cliente. |
| GET | `/open-banking/funds/v1/investments` | Lista fundos do cliente. |
| GET | `/open-banking/treasure-titles/v1/investments` | Lista Tesouro do cliente. |
| GET | `/open-banking/bank-fixed-incomes/v1/investments` | Lista renda fixa bancária. |
| GET | `/open-banking/accounts/v2/accounts` | Alias Open Finance para contas. |
| GET | `/open-banking/accounts/v2/accounts/{account_id}/balances` | Alias Open Finance para saldo. |
| GET | `/open-banking/accounts/v2/accounts/{account_id}/transactions` | Alias Open Finance para transações. |
