from __future__ import annotations
from fastapi import FastAPI, HTTPException, Depends, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import sqlite3, json

ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'open_finance_br.db'
DATA=ROOT/'data'
TOKEN='hackathon-token'

app=FastAPI(title='Mock Open Finance Brasil - Hybrid Investments',version='3.0.0',description='Hackathon API: Brazilian real product catalog + synthetic customers/positions. Not an official Open Finance implementation.')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_methods=['*'],allow_headers=['*'])

def auth(authorization: str|None=Header(default=None)):
    if authorization != f'Bearer {TOKEN}':
        raise HTTPException(401,'Use Authorization: Bearer hackathon-token')

def con():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def rows(sql,args=()):
    c=con()
    try:return [dict(x) for x in c.execute(sql,args).fetchall()]
    finally:c.close()

def one(sql,args=()):
    x=rows(sql,args)
    if not x: raise HTTPException(404,'Resource not found')
    return x[0]

def envelope(data):
    n=len(data) if isinstance(data,list) else 1
    return {'data':data,'meta':{'totalRecords':n,'totalPages':1}}

@app.get('/health')
def health(): return {'status':'ok','database':DB.name}

@app.get('/dataset/source',dependencies=[Depends(auth)])
def dataset_source():
    manifest=json.loads((DATA/'manifest.json').read_text(encoding='utf-8'))
    return {'manifest':manifest,'sources':rows('select * from sources order by source_id')}

@app.get('/customers',dependencies=[Depends(auth)])
def customers(limit:int=Query(20,ge=1,le=100)):
    return envelope(rows('select * from customers order by customer_id limit ?',(limit,)))

@app.get('/customers/{customer_id}',dependencies=[Depends(auth)])
def customer(customer_id:str): return envelope(one('select * from customers where customer_id=?',(customer_id,)))

@app.get('/accounts',dependencies=[Depends(auth)])
def accounts(customer_id:str): return envelope(rows('select * from accounts where customer_id=? order by type',(customer_id,)))

@app.get('/accounts/{account_id}/balances',dependencies=[Depends(auth)])
def account_balance(account_id:str):
    a=one('select * from accounts where account_id=?',(account_id,))
    return envelope({'accountId':a['account_id'],'availableAmount':{'amount':round(a['balance'],2),'currency':a['currency']}})

@app.get('/accounts/{account_id}/transactions',dependencies=[Depends(auth)])
def account_transactions(account_id:str,from_date:str|None=None,to_date:str|None=None):
    sql='select * from bank_transactions where account_id=?'; args=[account_id]
    if from_date: sql+=' and date>=?'; args.append(from_date)
    if to_date: sql+=' and date<=?'; args.append(to_date)
    sql+=' order by date desc'
    return envelope(rows(sql,args))

@app.get('/investment-products',dependencies=[Depends(auth)])
def products(type:str|None=None):
    if type:return envelope(rows('select * from investment_products where type=? order by product_id',(type,)))
    return envelope(rows('select * from investment_products order by type,product_id'))

@app.get('/investments',dependencies=[Depends(auth)])
def investments(customer_id:str,type:str|None=None):
    sql='select * from investments where customer_id=?'; args=[customer_id]
    if type: sql+=' and type=?'; args.append(type)
    sql+=' order by type, current_amount desc'
    return envelope(rows(sql,args))

@app.get('/investments/{investment_id}',dependencies=[Depends(auth)])
def investment(investment_id:str):
    x=one('''select i.*,p.indexer,p.rate,p.maturity_date,p.isin,p.price_date,p.price_origin,p.official_source_url,p.reference_source_url
             from investments i join investment_products p on p.product_id=i.product_id where i.investment_id=?''',(investment_id,))
    return envelope(x)

@app.get('/investments/{investment_id}/balances',dependencies=[Depends(auth)])
def investment_balance(investment_id:str):
    x=one('select * from investments where investment_id=?',(investment_id,))
    return envelope({'investmentId':x['investment_id'],'quantity':x['quantity'],'grossAmount':{'amount':x['current_amount'],'currency':'BRL'},'investedAmount':{'amount':x['invested_amount'],'currency':'BRL'},'unrealizedPnL':{'amount':x['unrealized_pnl'],'currency':'BRL'},'valuationDate':x['valuation_date']})

@app.get('/investments/{investment_id}/transactions',dependencies=[Depends(auth)])
def investment_transactions(investment_id:str):
    one('select investment_id from investments where investment_id=?',(investment_id,))
    return envelope(rows('select * from investment_transactions where investment_id=? order by date desc',(investment_id,)))

@app.get('/portfolio/summary',dependencies=[Depends(auth)])
def portfolio_summary(customer_id:str):
    cash=rows("select coalesce(sum(balance),0) as x from accounts where customer_id=? and type='CONTA_CORRENTE'",(customer_id,))[0]['x'] or 0
    inv=rows('select type,sum(current_amount) value,sum(invested_amount) cost,sum(unrealized_pnl) pnl from investments where customer_id=? group by type',(customer_id,))
    inv_total=sum(x['value'] or 0 for x in inv); cost=sum(x['cost'] or 0 for x in inv); pnl=sum(x['pnl'] or 0 for x in inv)
    return envelope({'customerId':customer_id,'cashBRL':round(cash,2),'investmentsMarketValueBRL':round(inv_total,2),'investmentsCostBasisBRL':round(cost,2),'unrealizedPnLBRL':round(pnl,2),'totalFinancialAssetsBRL':round(cash+inv_total,2),'allocationByType':{x['type']:round(x['value'],2) for x in inv}})

# Open-Finance-inspired aliases. customer_id is a demo shortcut for consent/token context.
def category(customer_id:str,typ:str): return envelope(rows('select * from investments where customer_id=? and type=? order by current_amount desc',(customer_id,typ)))
@app.get('/open-banking/variable-incomes/v1/investments',dependencies=[Depends(auth)])
def of_variable(customer_id:str): return category(customer_id,'VARIABLE_INCOME')
@app.get('/open-banking/funds/v1/investments',dependencies=[Depends(auth)])
def of_funds(customer_id:str): return category(customer_id,'FUND')
@app.get('/open-banking/treasure-titles/v1/investments',dependencies=[Depends(auth)])
def of_treasury(customer_id:str): return category(customer_id,'TREASURY')
@app.get('/open-banking/bank-fixed-incomes/v1/investments',dependencies=[Depends(auth)])
def of_fixed(customer_id:str): return category(customer_id,'BANK_FIXED_INCOME')
@app.get('/open-banking/accounts/v2/accounts',dependencies=[Depends(auth)])
def of_accounts(customer_id:str): return envelope(rows('select * from accounts where customer_id=?',(customer_id,)))
@app.get('/open-banking/accounts/v2/accounts/{account_id}/balances',dependencies=[Depends(auth)])
def of_bal(account_id:str): return account_balance(account_id)
@app.get('/open-banking/accounts/v2/accounts/{account_id}/transactions',dependencies=[Depends(auth)])
def of_tx(account_id:str,from_date:str|None=None,to_date:str|None=None): return account_transactions(account_id,from_date,to_date)
