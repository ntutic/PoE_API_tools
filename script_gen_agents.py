import pandas as pd
from fake_useragent import UserAgent

ua = UserAgent()
db = pd.read_csv('data/proxies.csv', index_col='id')
db['agent'] = ''

for i, row in db.iterrows():
    db.at[i, 'agent'] = ua.random

db.to_csv('data/proxies.csv', index='id')
