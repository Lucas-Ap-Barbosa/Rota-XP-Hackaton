from __future__ import annotations
import csv, sqlite3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
DB=ROOT/'open_finance_br.db'

SCHEMAS={
'customers':'''CREATE TABLE customers(customer_id TEXT PRIMARY KEY,name TEXT,age INTEGER,state TEXT,monthly_income REAL,risk_profile TEXT,synthetic TEXT)''',
'accounts':'''CREATE TABLE accounts(account_id TEXT PRIMARY KEY,customer_id TEXT,type TEXT,currency TEXT,balance REAL,status TEXT,synthetic TEXT)''',
'bank_transactions':'''CREATE TABLE bank_transactions(transaction_id TEXT PRIMARY KEY,account_id TEXT,customer_id TEXT,date TEXT,type TEXT,credit_debit TEXT,amount REAL,currency TEXT,description TEXT,synthetic TEXT)''',
'investment_products':'''CREATE TABLE investment_products(product_id TEXT PRIMARY KEY,type TEXT,subtype TEXT,name TEXT,ticker TEXT,cnpj TEXT,isin TEXT,indexer TEXT,rate TEXT,maturity_date TEXT,current_price REAL,price_date TEXT,currency TEXT,product_origin TEXT,price_origin TEXT,official_source_url TEXT,reference_source_url TEXT)''',
'investments':'''CREATE TABLE investments(investment_id TEXT PRIMARY KEY,customer_id TEXT,account_id TEXT,product_id TEXT,type TEXT,subtype TEXT,product_name TEXT,ticker TEXT,cnpj TEXT,quantity REAL,average_price REAL,current_unit_price REAL,invested_amount REAL,current_amount REAL,unrealized_pnl REAL,currency TEXT,product_origin TEXT,position_origin TEXT,valuation_date TEXT)''',
'investment_transactions':'''CREATE TABLE investment_transactions(investment_transaction_id TEXT PRIMARY KEY,investment_id TEXT,customer_id TEXT,date TEXT,type TEXT,quantity REAL,unit_price REAL,gross_amount REAL,currency TEXT,synthetic TEXT)''',
'sources':'''CREATE TABLE sources(source_id TEXT PRIMARY KEY,name TEXT,url TEXT,role TEXT,license TEXT)'''
}

FILES={
'customers':'customers.csv','accounts':'accounts.csv','bank_transactions':'bank_transactions.csv','investment_products':'investment_products.csv','investments':'investments.csv','investment_transactions':'investment_transactions.csv','sources':'sources.csv'}

NUMERIC={
'customers':{'age':int,'monthly_income':float},
'accounts':{'balance':float},
'bank_transactions':{'amount':float},
'investment_products':{'current_price':float},
'investments':{'quantity':float,'average_price':float,'current_unit_price':float,'invested_amount':float,'current_amount':float,'unrealized_pnl':float},
'investment_transactions':{'quantity':float,'unit_price':float,'gross_amount':float}
}

def conv(table,k,v):
    if v=='': return None
    fn=NUMERIC.get(table,{}).get(k)
    return fn(v) if fn else v

def main():
    if DB.exists(): DB.unlink()
    con=sqlite3.connect(DB)
    cur=con.cursor()
    for table,schema in SCHEMAS.items():
        cur.execute(schema)
        with (DATA/FILES[table]).open(encoding='utf-8',newline='') as f:
            r=csv.DictReader(f); rows=list(r)
        if not rows: continue
        cols=list(rows[0].keys())
        q=','.join('?'*len(cols))
        vals=[[conv(table,c,row[c]) for c in cols] for row in rows]
        cur.executemany(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({q})",vals)
    cur.executescript('''
      CREATE INDEX idx_accounts_customer ON accounts(customer_id);
      CREATE INDEX idx_btx_customer_date ON bank_transactions(customer_id,date);
      CREATE INDEX idx_inv_customer_type ON investments(customer_id,type);
      CREATE INDEX idx_itx_investment_date ON investment_transactions(investment_id,date);
    ''')
    con.commit(); con.close()
    print(DB)
if __name__=='__main__': main()
