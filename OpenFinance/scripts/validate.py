from pathlib import Path
import csv, sqlite3, math, json, sys
ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'open_finance_br.db'
c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
assert c.execute('select count(*) from customers').fetchone()[0] == 80
assert c.execute('select count(*) from investments').fetchone()[0] >= 500
# Every customer has investments in all four modeled types.
for row in c.execute('select customer_id,count(distinct type) n from investments group by customer_id'):
    assert row['n']==4, row
# Position current values reconcile against quantity*unit price when unit price exists.
for r in c.execute("select * from investments where current_unit_price is not null"):
    calc=round(r['quantity']*r['current_unit_price'],2)
    assert abs(calc-r['current_amount']) <= .02,(r['investment_id'],calc,r['current_amount'])
# Cost basis reconciles against synthetic investment transactions.
for r in c.execute('select investment_id,invested_amount from investments'):
    s=c.execute('select coalesce(sum(gross_amount),0) from investment_transactions where investment_id=?',(r['investment_id'],)).fetchone()[0]
    assert abs(s-r['invested_amount']) <= .03,(r['investment_id'],s,r['invested_amount'])
# No real-person claims: all customer and position origins synthetic.
assert c.execute("select count(*) from customers where synthetic!='true'").fetchone()[0]==0
assert c.execute("select count(*) from investments where position_origin!='SYNTHETIC'").fetchone()[0]==0
print('dataset validation: OK')
