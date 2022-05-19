from api_databases import Databases
from api_queries import QueryUnique 
import time



begin = 5
listing = False
db = Databases(listing=listing)
if not listing:
    db.listing = {}
min_ = 10
new = True
while True:
    for index, unique in enumerate(list(db.uniques.index)[begin:]):
        q = QueryUnique(name=unique, new=new, online='any')
        if new:
            q.notes=[]
            new = False
        q.query_price(min=min_)
        q.last_am = ''
        q.next_post = True
        q.min_ = 10
        print(str(index) + ': ' + unique, end="")
        new_post = True
        while q.next_post:
            # Get and parse new ids from post
            q.query_post()
            if new_post:
                q.base_id = q.id
                print(' / Total ' + str(q.total), end="")
                print(' / First: ', end='')
                new_post = False
                q.get_first = True
            if q.total:
                q.get_post_ids()
                q.query_get('query items', db, parse=q.parse_get_result_uniques)
                q.post_check()
                
            else:
                q.next_post = False
        try:
            print(' / Last ' + str(q.amount)+' '+ q.currency, end='')
        except AttributeError:
            print(' / Last: NA', end='')
        print(" / Saved "+str(len(q.ram_ids)),end='')
        q.ram_ids = []
        q.next_post = False
        q.get_missing_ids(db)
        q.fetch_missing_ids(db)
        if (index + 1) % 100 == 0:
            t_ = time.time()
            db.save(['listing', 'listing_sold'])
            print(' / DB save took '+str(round(time.time()-t_)),end='')
        print()
    begin = 0
    t_ = time.time()
    db.save(['listing', 'listing_sold'])
    print(' / DB save took '+str(round(time.time()-t_)))
    

                
