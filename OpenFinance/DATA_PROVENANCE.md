# Proveniência dos dados

Data de referência da base: **09/10/2026** (com alguns fundos usando a última cota pública disponível indicada no catálogo).

## O que é real

### Produtos de renda variável
Os tickers do catálogo representam instrumentos brasileiros reais. O snapshot de fechamento usado em vários ativos foi obtido de páginas públicas de mercado para 09/10/2026. O projeto guarda `official_source_url` e `reference_source_url` por produto.

### Fundos
Nome e CNPJ são de fundos reais. A referência oficial para cadastro e informe diário é a CVM:

- https://dados.cvm.gov.br/dataset/fi-cad
- https://dados.cvm.gov.br/dataset/fi-doc-inf_diario

As cotas do snapshot incluído foram obtidas em páginas públicas que republicam/organizam informações de fundos; cada linha informa `reference_source_url`. Para uma atualização oficial, use o script em `scripts/refresh_official_sources.py` e reconcilie o CNPJ com o Informe Diário da CVM.

### Tesouro Direto
Os títulos são reais. A fonte oficial de preço/taxa é:

- https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/precotaxatesourodireto.csv

O snapshot incluído registra a data e uma referência pública para os valores usados.

## O que é sintético

- nome/CPF/idade/UF/renda dos clientes;
- saldo em conta;
- PIX, boletos, compras e salários;
- perfil de risco;
- patrimônio investido;
- produtos que cada cliente possui;
- quantidades, datas de compra e preço médio;
- CDBs e suas condições comerciais.

Os CPFs são gerados sinteticamente com dígitos verificadores válidos e não pertencem a pessoas reais.

Nenhuma carteira é uma carteira real anonimizada. As carteiras foram **criadas do zero** com regras determinísticas.

## Campos-chave

`product_origin`:
- `REAL`: a identidade do produto corresponde a um produto real;
- `SYNTHETIC`: produto inventado para a demo.

`position_origin`:
- sempre `SYNTHETIC` nesta base.

`price_origin` informa se o valor veio de snapshot público, referência do Tesouro ou cálculo sintético.

## Relação com Open Finance Brasil

As famílias de endpoints foram inspiradas na documentação pública do Open Finance Brasil, especialmente as APIs de renda variável, fundos, renda fixa bancária e títulos do Tesouro. O contrato desta hackathon é deliberadamente simplificado e não implementa FAPI, mTLS, consentimento regulatório, certificados ou todos os campos oficiais.
