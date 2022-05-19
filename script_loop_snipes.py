from api_databases import Databases
from api_queries import QueryUnique 
import json
import time
import numpy as np

db = Databases(dbs=['snipes', 'proxies'])
snipe_group = 'custom_1'
snipes = db.snipes.loc[db.snipes['group'] == snipe_group]

def push_snipe(q, db):
    for i, item in enumerate(q.get_result):
        if not item:
            continue

proxy_list = np.unique(snipes['proxy'])


count = 0
while True:
    print('Next run - ' + str(count))
    for proxy in proxy_list:

        
        for index, row in snipes.loc[snipes['proxy'] == proxy].iterrows():
            q = QueryUnique(query='a', new=True)
            q.connection = q.set_proxy(row['proxy'], db)

            if not q.connection:
                print("Can't connect to proxy " + str(proxy))
                break

            with open('data/queries/' + row['query']) as f_json:
                query = json.load(f_json)

            q.query = query
                                
            q.query_post()

            if q.response_post.status_code != 200:
                break
                print(q.response_post.status_code + ' : ')
                print(q.response_post.headers['X-Rate-Limit-Ip'])
                print(q.response_post.headers['X-Rate-Limit-Ip-State'])
                if int(q.response_post.headers['Retry-After']) > 0:
                    print('Exceeded limit, sleeping for : ' + q.response_post.headers['Retry-After'])
                    time.sleep(int(q.response_post.headers['Retry-After']))
                else:
                    a = input('wut')

            if q.total:
                q.get_post_ids()
                q.query_get('query items', db, parse=push_snipe)


    count += 1
