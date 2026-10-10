"""Optional local refresh helper.
Downloads the official source files used as provenance references.
This does NOT replace synthetic holdings automatically; it gives you raw sources to rebuild/refresh the catalog.
"""
from pathlib import Path
from urllib.request import urlretrieve
from datetime import date
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'source_raw'; OUT.mkdir(exist_ok=True)
urls={
 'cvm_fund_registry.csv':'https://dados.cvm.gov.br/dados/FI/CAD/DADOS/cad_fi.csv',
 'tesouro_prices.csv':'https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/precotaxatesourodireto.csv',
}
month=date.today().strftime('%Y%m')
urls[f'cvm_fund_daily_{month}.zip']=f'https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_{month}.zip'
for name,url in urls.items():
    print('downloading',url)
    urlretrieve(url,OUT/name)
    print('saved',OUT/name)
