from api_databases import Databases
from api_queries import QueryUnique 
import json
import time
import requests

db = Databases(dbs=['snipes'])


def push_snipe(q, db):
    for i, item in enumerate(q.get_result):
        if not item:
            continue


query = {
   "query":{
      "status":{
         "option":"online"
      },
      "type":"Basalt Flask",
      "stats":[
         {
            "type":"and",
            "filters":[
               
            ]
         }
      ]
   },
   "sort":{
      "price":"asc"
   }
}


proxies_1 = {
    'https': 'socks5://xMjZNYn9KheC1c3k66cBe7Fy:qAyR3YY91UpjhLxXJhrhzxUX@us.socks.nordhold.net:1080'
}






q = QueryUnique(query=query, new=True, online='any')


url = 'https://httpbin.org/ip'
response = requests.get(url, proxies=proxies_1)
actual_ip = response.json()['origin']

connected_1 = check_proxy_connection(proxies_1)
if connected_1:
   q.query_post(proxies=proxies_1)
   print(q.response_post.headers['X-Rate-Limit-Ip-State'])

connected_2 = check_proxy_connection(proxies_2)
if connected_2:
   q.query_post(proxies=proxies_2)
   print(q.response_post.headers['X-Rate-Limit-Ip-State'])

count = 0
while True:
    print('Next run - ' + str(count))
    time.sleep(1)
    for index, row in db.snipes.iterrows():

        with open('data/queries/' + row['query']) as f_json:
            query = json.load(f_json)

        q = QueryUnique(query=query, new=True, online='any')
        q.query_post()
        if q.response_post.status_code != 200:
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
            q.post_check()
            if q.next_post:
                q.query_price(min=q.min_, max=q.amount)
            q.get_missing_ids(db)
            q.fetch_missing_ids(db)


    count += 1
