from __future__ import annotations
import csv, json, math, random, hashlib
from pathlib import Path
from datetime import date, timedelta, datetime

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
DATA.mkdir(exist_ok=True)
SEED = 20261010
rng = random.Random(SEED)
REFERENCE_DATE = date(2026,10,9)

# Verified public product snapshot. Product identity is real unless explicitly marked synthetic.
PRODUCTS = [
    # Brazilian listed equities — closing snapshot 2026-10-09 (public market-data mirror of B3 listings)
    dict(product_id='STK_PETR4', type='VARIABLE_INCOME', subtype='STOCK', name='Petróleo Brasileiro S.A. PN', ticker='PETR4', cnpj='33.000.167/0001-01', isin='', indexer='', rate='', maturity_date='', current_price=56.00, price_date='2026-10-09', currency='BRL', product_origin='REAL', price_origin='PUBLIC_MARKET_SNAPSHOT', official_source_url='https://www.b3.com.br/', reference_source_url='https://origin.dadosdemercado.com.br/b3/ibov'),
    dict(product_id='STK_VALE3', type='VARIABLE_INCOME', subtype='STOCK', name='Vale S.A. ON', ticker='VALE3', cnpj='33.592.510/0001-54', isin='', indexer='', rate='', maturity_date='', current_price=67.90, price_date='2026-10-09', currency='BRL', product_origin='REAL', price_origin='PUBLIC_MARKET_SNAPSHOT', official_source_url='https://www.b3.com.br/', reference_source_url='https://origin.dadosdemercado.com.br/b3/ibov'),
    dict(product_id='STK_ITUB4', type='VARIABLE_INCOME', subtype='STOCK', name='Itaú Unibanco Holding S.A. PN', ticker='ITUB4', cnpj='60.872.504/0001-23', isin='', indexer='', rate='', maturity_date='', current_price=50.47, price_date='2026-10-09', currency='BRL', product_origin='REAL', price_origin='PUBLIC_MARKET_SNAPSHOT', official_source_url='https://www.b3.com.br/', reference_source_url='https://origin.dadosdemercado.com.br/b3/ibov'),
    dict(product_id='STK_B3SA3', type='VARIABLE_INCOME', subtype='STOCK', name='B3 S.A. - Brasil, Bolsa, Balcão ON', ticker='B3SA3', cnpj='', isin='', indexer='', rate='', maturity_date='', current_price=23.35, price_date='2026-10-09', currency='BRL', product_origin='REAL', price_origin='PUBLIC_MARKET_SNAPSHOT', official_source_url='https://www.b3.com.br/', reference_source_url='https://origin.dadosdemercado.com.br/b3/ibov'),
    dict(product_id='STK_BBAS3', type='VARIABLE_INCOME', subtype='STOCK', name='Banco do Brasil S.A. ON', ticker='BBAS3', cnpj='', isin='', indexer='', rate='', maturity_date='', current_price=24.64, price_date='2026-10-09', currency='BRL', product_origin='REAL', price_origin='PUBLIC_MARKET_SNAPSHOT', official_source_url='https://www.b3.com.br/', reference_source_url='https://origin.dadosdemercado.com.br/b3/ibov'),
    dict(product_id='STK_ABEV3', type='VARIABLE_INCOME', subtype='STOCK', name='Ambev S.A. ON', ticker='ABEV3', cnpj='', isin='', indexer='', rate='', maturity_date='', current_price=15.99, price_date='2026-10-09', currency='BRL', product_origin='REAL', price_origin='PUBLIC_MARKET_SNAPSHOT', official_source_url='https://www.b3.com.br/', reference_source_url='https://origin.dadosdemercado.com.br/b3/ibov'),
    dict(product_id='STK_WEGE3', type='VARIABLE_INCOME', subtype='STOCK', name='WEG S.A. ON', ticker='WEGE3', cnpj='', isin='', indexer='', rate='', maturity_date='', current_price=51.47, price_date='2026-10-09', currency='BRL', product_origin='REAL', price_origin='PUBLIC_MARKET_SNAPSHOT', official_source_url='https://www.b3.com.br/', reference_source_url='https://origin.dadosdemercado.com.br/b3/ibov'),
    # Real ETF listing
    dict(product_id='ETF_MIDB11', type='VARIABLE_INCOME', subtype='ETF_FIXED_INCOME', name='BTG Pactual Teva ITBR Tesouro IPCA 2035 Fundo de Índice', ticker='MIDB11', cnpj='64.690.760/0001-50', isin='BRMIDBCTF008', indexer='IPCA', rate='0.19% a.a. admin', maturity_date='', current_price=114.19, price_date='2026-10-09', currency='BRL', product_origin='REAL', price_origin='PUBLIC_MARKET_SNAPSHOT', official_source_url='https://www.b3.com.br/', reference_source_url='https://obm.com.br/etfs/midb11'),
    # Real investment funds. Product IDs/CNPJs are real; quota snapshot is public-data based.
    dict(product_id='FUND_TREND_OURO', type='FUND', subtype='MULTIMARKET', name='Trend Ouro Classe de Investimento Multimercado - RL', ticker='', cnpj='22.963.439/0001-52', isin='', indexer='OURO', rate='', maturity_date='', current_price=5.607403, price_date='2026-10-09', currency='BRL', product_origin='REAL', price_origin='PUBLIC_FUND_SNAPSHOT', official_source_url='https://dados.cvm.gov.br/dataset/fi-doc-inf_diario', reference_source_url='https://statusinvest.com.br/fundos-de-investimento/trend-ouro-fim'),
    dict(product_id='FUND_ITAU_SP500', type='FUND', subtype='EQUITY_FUND', name='Itaú Index Ações Estratégia S&P500 FIF da CIC RL', ticker='', cnpj='37.306.536/0001-40', isin='', indexer='S&P 500', rate='0.8% a.a. max admin', maturity_date='', current_price=34.519485, price_date='2026-09-09', currency='BRL', product_origin='REAL', price_origin='PUBLIC_FUND_SNAPSHOT', official_source_url='https://dados.cvm.gov.br/dataset/fi-doc-inf_diario', reference_source_url='https://gorila.com.br/produtos-de-investimento/fundos/itau-index-acoes-estrategia-sp500-fc'),
    dict(product_id='FUND_VERDE_SCENA', type='FUND', subtype='MULTIMARKET', name='Verde AM Scena Advisory FIC de FI Financeiro Multimercado - RL', ticker='', cnpj='24.048.538/0001-34', isin='', indexer='CDI', rate='1.5% a.a. admin; 20% performance', maturity_date='', current_price=2.17424512, price_date='2026-09-08', currency='BRL', product_origin='REAL', price_origin='PUBLIC_FUND_SNAPSHOT', official_source_url='https://dados.cvm.gov.br/dataset/fi-doc-inf_diario', reference_source_url='https://gorila.com.br/produtos-de-investimento/fundos/verde-am-scena-advisory-fic-fim'),
    dict(product_id='FUND_XP_LONG_BIASED', type='FUND', subtype='MULTIMARKET', name='XP Investor Long Biased 30 FIC de FIF Multimercado - RL', ticker='', cnpj='25.224.843/0001-00', isin='', indexer='', rate='', maturity_date='', current_price=2.59033073, price_date='2026-03-03', currency='BRL', product_origin='REAL', price_origin='PUBLIC_FUND_SNAPSHOT', official_source_url='https://dados.cvm.gov.br/dataset/fi-doc-inf_diario', reference_source_url='https://gorila.com.br/produtos-de-investimento/produtos-de-investimento/fundos/xp-investor-long-biased-30-fc-fim'),
    # Real Tesouro Direto products. Prices/rates are reference snapshots derived from public pages whose source is Tesouro Nacional.
    dict(product_id='TES_SELIC_2029', type='TREASURY', subtype='SELIC', name='Tesouro Selic 2029', ticker='', cnpj='', isin='', indexer='SELIC', rate='Selic + 0.05% a.a.', maturity_date='2029-03-01', current_price=20035.30, price_date='2026-10-08', currency='BRL', product_origin='REAL', price_origin='TESOURO_REFERENCE_SNAPSHOT', official_source_url='https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/precotaxatesourodireto.csv', reference_source_url='https://rendometro.com.br/taxas/tesouro-direto/tesouro-selic-2029/'),
    dict(product_id='TES_PREFIX_2029', type='TREASURY', subtype='PREFIXED', name='Tesouro Prefixado 2029', ticker='', cnpj='', isin='', indexer='PREFIXADO', rate='12.30% a.a.', maturity_date='2029-01-01', current_price=774.89, price_date='2026-10-09', currency='BRL', product_origin='REAL', price_origin='TESOURO_REFERENCE_SNAPSHOT', official_source_url='https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/precotaxatesourodireto.csv', reference_source_url='https://www.valr.com.br/fixed-income/'),
    dict(product_id='TES_PREFIX_2032', type='TREASURY', subtype='PREFIXED', name='Tesouro Prefixado 2032', ticker='', cnpj='', isin='', indexer='PREFIXADO', rate='12.83% a.a. (08/10/2026)', maturity_date='2032-01-01', current_price=534.43, price_date='2026-10-08', currency='BRL', product_origin='REAL', price_origin='TESOURO_REFERENCE_SNAPSHOT', official_source_url='https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/precotaxatesourodireto.csv', reference_source_url='https://rendometro.com.br/taxas/tesouro-direto/tesouro-prefixado-2032/'),
    dict(product_id='TES_IPCA_2035', type='TREASURY', subtype='IPCA', name='Tesouro IPCA+ 2035', ticker='', cnpj='', isin='', indexer='IPCA', rate='IPCA + 6.66% a.a.', maturity_date='2035-05-15', current_price=2748.88, price_date='2026-10-09', currency='BRL', product_origin='REAL', price_origin='TESOURO_REFERENCE_SNAPSHOT', official_source_url='https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/precotaxatesourodireto.csv', reference_source_url='https://www.valr.com.br/fixed-income/'),
    # Synthetic bank fixed income offers; realistic terms but NOT real offers.
    dict(product_id='CDB_DEMO_110CDI', type='BANK_FIXED_INCOME', subtype='CDB', name='CDB Banco Horizonte 110% CDI', ticker='', cnpj='', isin='', indexer='CDI', rate='110% CDI', maturity_date='2028-06-15', current_price='', price_date='', currency='BRL', product_origin='SYNTHETIC', price_origin='SYNTHETIC_ACCRUAL', official_source_url='', reference_source_url=''),
    dict(product_id='CDB_DEMO_LIQ', type='BANK_FIXED_INCOME', subtype='CDB', name='CDB Banco Aurora 102% CDI - Liquidez Diária', ticker='', cnpj='', isin='', indexer='CDI', rate='102% CDI', maturity_date='2029-12-31', current_price='', price_date='', currency='BRL', product_origin='SYNTHETIC', price_origin='SYNTHETIC_ACCRUAL', official_source_url='', reference_source_url=''),
    dict(product_id='CDB_DEMO_IPCA', type='BANK_FIXED_INCOME', subtype='CDB', name='CDB Banco Serra IPCA + 7,10%', ticker='', cnpj='', isin='', indexer='IPCA', rate='IPCA + 7.10% a.a.', maturity_date='2030-08-20', current_price='', price_date='', currency='BRL', product_origin='SYNTHETIC', price_origin='SYNTHETIC_ACCRUAL', official_source_url='', reference_source_url=''),
    dict(product_id='CDB_DEMO_PRE', type='BANK_FIXED_INCOME', subtype='CDB', name='CDB Banco Vale Verde 13,20% a.a.', ticker='', cnpj='', isin='', indexer='PREFIXADO', rate='13.20% a.a.', maturity_date='2029-03-10', current_price='', price_date='', currency='BRL', product_origin='SYNTHETIC', price_origin='SYNTHETIC_ACCRUAL', official_source_url='', reference_source_url=''),
]

FIRST_NAMES = ['Ana','Bruno','Camila','Daniel','Eduarda','Felipe','Gabriela','Henrique','Isabela','João','Karen','Lucas','Mariana','Nicolas','Olivia','Pedro','Rafaela','Samuel','Tatiana','Vinicius','Amanda','Caio','Beatriz','Gustavo','Larissa','Matheus','Renata','Thiago','Vitória','Yuri']
LAST_NAMES = ['Silva','Santos','Oliveira','Souza','Rodrigues','Ferreira','Alves','Pereira','Lima','Gomes','Costa','Ribeiro','Martins','Carvalho','Almeida','Lopes','Soares','Fernandes','Vieira','Barbosa']
STATES = ['SP','RJ','MG','PR','SC','RS','BA','PE','GO','DF','ES','CE']
PROFILES = ['CONSERVATIVE','MODERATE','AGGRESSIVE']
PROFILE_WEIGHTS = [0.34,0.44,0.22]
MERCHANTS = [('SUPERMERCADO',35,420),('RESTAURANTE',25,190),('FARMACIA',18,280),('COMBUSTIVEL',80,420),('E_COMMERCE',35,900),('TRANSPORTE',8,95),('SERVICOS',50,650)]

# target portfolio mix by profile
MIX = {
  'CONSERVATIVE': [('BANK_FIXED_INCOME',0.42),('TREASURY',0.35),('FUND',0.18),('VARIABLE_INCOME',0.05)],
  'MODERATE': [('BANK_FIXED_INCOME',0.28),('TREASURY',0.25),('FUND',0.25),('VARIABLE_INCOME',0.22)],
  'AGGRESSIVE': [('BANK_FIXED_INCOME',0.12),('TREASURY',0.13),('FUND',0.25),('VARIABLE_INCOME',0.50)],
}

prod_by_type = {}
for p in PRODUCTS:
    prod_by_type.setdefault(p['type'],[]).append(p)

def stable_id(prefix, *parts):
    h = hashlib.sha1('|'.join(map(str,parts)).encode()).hexdigest()[:12]
    return f'{prefix}_{h}'

def write_csv(name, rows, fields=None):
    path=DATA/name
    if not rows:
        return
    fields = fields or list(rows[0].keys())
    with path.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)

customers=[]; accounts=[]; bank_tx=[]; positions=[]; inv_tx=[]
N=80
for i in range(1,N+1):
    customer_id=f'CUST_{i:04d}'
    name=f'{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)} {rng.choice(LAST_NAMES)}'
    age=rng.randint(21,68)
    income=round(math.exp(rng.uniform(math.log(2800), math.log(32000))),2)
    profile=rng.choices(PROFILES,weights=PROFILE_WEIGHTS,k=1)[0]
    multiplier={'CONSERVATIVE':rng.uniform(4,18),'MODERATE':rng.uniform(5,24),'AGGRESSIVE':rng.uniform(6,30)}[profile]
    investable=round(max(3500, income*multiplier),2)
    checking=round(rng.uniform(0.35,1.8)*income,2)
    state=rng.choice(STATES)
    customers.append(dict(customer_id=customer_id,name=name,age=age,state=state,monthly_income=income,risk_profile=profile,synthetic='true'))
    acc_id=f'ACC_{i:04d}_CHK'
    accounts.append(dict(account_id=acc_id,customer_id=customer_id,type='CONTA_CORRENTE',currency='BRL',balance=checking,status='ACTIVE',synthetic='true'))

    # Banking activity, synthetic but Brazil-shaped (PIX/card/boleto/TED/salary)
    tx_date=REFERENCE_DATE-timedelta(days=120)
    salary_day=rng.randint(2,7)
    for d in range(121):
        day=tx_date+timedelta(days=d)
        if day.day==salary_day:
            amt=round(income*(1+rng.uniform(-0.03,0.03)),2)
            bank_tx.append(dict(transaction_id=stable_id('BTX',customer_id,day,'salary'),account_id=acc_id,customer_id=customer_id,date=day.isoformat(),type='SALARY',credit_debit='CREDIT',amount=amt,currency='BRL',description='Crédito de salário',synthetic='true'))
        if rng.random()<0.10:
            cat,lo,hi=rng.choice(MERCHANTS); amt=round(rng.uniform(lo,hi),2)
            bank_tx.append(dict(transaction_id=stable_id('BTX',customer_id,day,len(bank_tx)),account_id=acc_id,customer_id=customer_id,date=day.isoformat(),type='CARD_PURCHASE',credit_debit='DEBIT',amount=amt,currency='BRL',description=f'Compra - {cat}',synthetic='true'))
        if rng.random()<0.055:
            amt=round(rng.uniform(15,650),2)
            bank_tx.append(dict(transaction_id=stable_id('BTX',customer_id,day,'pix',len(bank_tx)),account_id=acc_id,customer_id=customer_id,date=day.isoformat(),type='PIX',credit_debit=rng.choice(['DEBIT','CREDIT']),amount=amt,currency='BRL',description='Transferência PIX',synthetic='true'))
        if day.day in (10,20) and rng.random()<0.35:
            amt=round(rng.uniform(90,850),2)
            bank_tx.append(dict(transaction_id=stable_id('BTX',customer_id,day,'boleto',len(bank_tx)),account_id=acc_id,customer_id=customer_id,date=day.isoformat(),type='BOLETO',credit_debit='DEBIT',amount=amt,currency='BRL',description='Pagamento de boleto',synthetic='true'))

    # Investment portfolio derived from risk profile + synthetic financial wealth.
    invest_account=f'ACC_{i:04d}_INV'
    accounts.append(dict(account_id=invest_account,customer_id=customer_id,type='CONTA_INVESTIMENTO',currency='BRL',balance=0.0,status='ACTIVE',synthetic='true'))
    for asset_type, weight in MIX[profile]:
        class_budget=investable*weight
        n_products = 1 if class_budget < 18000 else (2 if rng.random()<0.75 else 3)
        choices=rng.sample(prod_by_type[asset_type], k=min(n_products,len(prod_by_type[asset_type])))
        splits=[rng.uniform(.7,1.3) for _ in choices]; ss=sum(splits)
        for p,sw in zip(choices,splits):
            budget=class_budget*sw/ss
            inv_id=stable_id('INV',customer_id,p['product_id'])
            current_price=p['current_price']
            if asset_type=='BANK_FIXED_INCOME':
                days_held=rng.randint(45,700)
                purchase_date=REFERENCE_DATE-timedelta(days=days_held)
                principal=round(budget/rng.uniform(1.02,1.20),2)
                current_amount=round(budget,2)
                quantity=''
                avg_price=''
                current_unit_price=''
                invested_amount=principal
                pnl=round(current_amount-principal,2)
                inv_tx.append(dict(investment_transaction_id=stable_id('ITX',inv_id,'buy'),investment_id=inv_id,customer_id=customer_id,date=purchase_date.isoformat(),type='APPLICATION',quantity='',unit_price='',gross_amount=principal,currency='BRL',synthetic='true'))
            else:
                cp=float(current_price)
                if asset_type=='VARIABLE_INCOME':
                    quantity=max(1, int(budget/cp))
                elif asset_type=='TREASURY':
                    quantity=round(max(0.01,budget/cp),4)
                else:
                    quantity=round(max(1.0,budget/cp),6)
                current_amount=round(float(quantity)*cp,2)
                # two synthetic purchase lots so cost basis is derived from transactions
                q1=round(float(quantity)*rng.uniform(.35,.65),6); q2=round(float(quantity)-q1,6)
                f1=rng.uniform(.78,1.07); f2=rng.uniform(.82,1.08)
                p1=round(cp*f1,6); p2=round(cp*f2,6)
                d1=REFERENCE_DATE-timedelta(days=rng.randint(250,850)); d2=REFERENCE_DATE-timedelta(days=rng.randint(45,240))
                if d2<d1: d1,d2=d2,d1
                inv_tx.append(dict(investment_transaction_id=stable_id('ITX',inv_id,'1'),investment_id=inv_id,customer_id=customer_id,date=d1.isoformat(),type='BUY',quantity=q1,unit_price=p1,gross_amount=round(q1*p1,2),currency='BRL',synthetic='true'))
                inv_tx.append(dict(investment_transaction_id=stable_id('ITX',inv_id,'2'),investment_id=inv_id,customer_id=customer_id,date=d2.isoformat(),type='BUY',quantity=q2,unit_price=p2,gross_amount=round(q2*p2,2),currency='BRL',synthetic='true'))
                invested_amount=round(q1*p1+q2*p2,2)
                avg_price=round(invested_amount/float(quantity),6)
                current_unit_price=cp
                pnl=round(current_amount-invested_amount,2)
            positions.append(dict(investment_id=inv_id,customer_id=customer_id,account_id=invest_account,product_id=p['product_id'],type=asset_type,subtype=p['subtype'],product_name=p['name'],ticker=p['ticker'],cnpj=p['cnpj'],quantity=quantity,average_price=avg_price,current_unit_price=current_unit_price,invested_amount=invested_amount,current_amount=current_amount,unrealized_pnl=pnl,currency='BRL',product_origin=p['product_origin'],position_origin='SYNTHETIC',valuation_date=p['price_date'] or REFERENCE_DATE.isoformat()))

write_csv('investment_products.csv', PRODUCTS)
write_csv('customers.csv', customers)
write_csv('accounts.csv', accounts)
write_csv('bank_transactions.csv', bank_tx)
write_csv('investments.csv', positions)
write_csv('investment_transactions.csv', inv_tx)

sources=[
 {'source_id':'CVM_FUND_CAD','name':'CVM - Informação Cadastral de Fundos','url':'https://dados.cvm.gov.br/dataset/fi-cad','role':'Official fund identity/catalog source','license':'Open Data / ODbL on CVM portal'},
 {'source_id':'CVM_FUND_DAILY','name':'CVM - Informe Diário de Fundos','url':'https://dados.cvm.gov.br/dataset/fi-doc-inf_diario','role':'Official fund quota/PL dataset reference','license':'Open Data / ODbL on CVM portal'},
 {'source_id':'TESOURO_CSV','name':'Tesouro Transparente - Preço e Taxa Tesouro Direto','url':'https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/precotaxatesourodireto.csv','role':'Official Treasury price/rate source','license':'ODbL'},
 {'source_id':'OPEN_FINANCE_SPEC','name':'Open Finance Brasil - APIs de Investimentos','url':'https://openfinancebrasil.atlassian.net/wiki/spaces/OF/pages/17957025','role':'Endpoint/schema inspiration','license':'Reference documentation'},
 {'source_id':'B3_LISTINGS','name':'B3','url':'https://www.b3.com.br/','role':'Real listed instruments identity','license':'See B3 terms'},
 {'source_id':'MARKET_SNAPSHOT','name':'Dados de Mercado - IBOV snapshot','url':'https://origin.dadosdemercado.com.br/b3/ibov','role':'2026-10-09 closing-price snapshot for selected equities','license':'See provider terms'},
 {'source_id':'BRAPI','name':'brapi.dev','url':'https://brapi.dev/docs','role':'Cross-check / refresh option for Brazilian EOD quotes','license':'See provider terms'},
]
write_csv('sources.csv', sources)

manifest={
 'dataset_name':'Open Finance BR Hybrid Hackathon Dataset',
 'generated_at':datetime.now().isoformat(timespec='seconds'),
 'reference_date':REFERENCE_DATE.isoformat(),
 'seed':SEED,
 'customers':len(customers),
 'accounts':len(accounts),
 'bank_transactions':len(bank_tx),
 'products':len(PRODUCTS),
 'investments':len(positions),
 'investment_transactions':len(inv_tx),
 'methodology':'Real Brazilian investment-product identities + public market reference snapshots + synthetic clients, holdings and transactions.',
 'important':'Synthetic positions do not represent any real person. Synthetic CDBs are explicitly marked product_origin=SYNTHETIC.'
}
(DATA/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(manifest,ensure_ascii=False,indent=2))
