
import requests
import time
from api_misc_functions import *



class QueryUnique:
    def __init__(self, name='', query='', new=False, online="any", ident=True, indexed="", sort="desc", api="trade/search/", server="Ultimatum"):
        if query:
            self.query = query
        elif not query and not name:
            exit()
        else:
            self.query = {"query": {"status": {"option": online}},"sort": {"price": sort}}
            self.query["query"]["filters"] = {"misc_filters": {"disabled": "false", "filters": {"identified": {"option": ident}}}}
            self.query["query"]["filters"]["trade_filters"] = {"filters": {"sale_type": {"option": "priced"}}}
            if indexed:
                self.query["query"]["filters"]["trade_filters"]["filters"]['indexed'] = {"option": indexed}
            if name:
                self.name = name
                self.query["query"]["name"] = self.name

        self.url = "https://www.pathofexile.com/api/" + api + server
        self.ram_ids = []   
        self.proxy = {}
        self.user_agent = 'NA'

        response = requests.get('https://httpbin.org/ip')
        self.base_ip = response.json()['origin']

        if new:
            self.current_get = []
            self.current_post = []
            self.notes = []


    def query_price(self, min="", max="", cur=""):
        """
        min, max default is undefined
        cur default is chaos equivalents
        """
        if min or max or cur:
            self.query["query"]["filters"]["trade_filters"]["filters"]["price"] = {}
        if min:
            self.query["query"]["filters"]["trade_filters"]["filters"]["price"]["min"] = min
        if max:
            self.query["query"]["filters"]["trade_filters"]["filters"]["price"]["max"] = max
        if cur:
            self.query["query"]["filters"]["trade_filters"]["filters"]["price"]["option"] = cur


    def query_pure(self, query=''):
        if query:
            self.query["query"]["filters"] = query
        else:
            self.query["query"]["filters"] = {
                "misc_filters": {
                    "filters": {
                        "corrupted": {
                            "option": "false"
                        }, "crafted": {
                            "option": "false"
                        }, "enchanted": {
                            "option": "false"
                        }, "identified": {
                            "option": "true"
                        }
                    }
                }
            }


    def set_proxy(self, proxy_i, db):
        if self.proxy:
            if self.proxy['https'] == db.proxies.loc[int(proxy_i)]['proxy']:
                return True


        self.proxy = {
            'https': db.proxies.loc[int(proxy_i)]['proxy']
        }

        self.user_agent = db.proxies.loc[int(proxy_i)]['agent']
        self.headers = {"User-Agent": self.user_agent}

        url = 'https://httpbin.org/ip'
        try:
            response = requests.get(url, proxies=self.proxy)
            actual_ip = response.json()['origin']
            if actual_ip != self.base_ip:
                return True
            else:
                return False

        except requests.exceptions.ProxyError:
            return False
        

    def query_post(self):
        self.no_listing = False

        self.response_post = requests.post(url=self.url, json=self.query, headers=self.headers, proxies=self.proxy)
        if self.response_post.status_code != 200:
            print("Status code post "+str(self.response_post.status_code))
            return

        try:
            self.current_post += [time.time()]
        except AttributeError:
            self.current_post = [time.time()]

        self.current_post = timeout(self.response_post, self.current_post)
        self.total = self.response_post.json()['total']
        self.id = self.response_post.json()['id']
        self.post_result = self.response_post.json()['result']


    def get_post_ids(self, trim=True):
        if trim:
            self.post_ids_trim = [x for x in self.post_result if x not in self.ram_ids]
        self.post_ids = {}

        for i in range(len(self.post_ids_trim) // 10 + (len(self.post_ids_trim) % 10 > 0)):
            self.post_ids[i] = ""
            for id_ in self.post_ids_trim[i * 10: (i + 1) * 10]:
                self.post_ids[i] += id_ + ','
                self.ram_ids += [id_]
            self.post_ids[i] = self.post_ids[i][:-1]


    def post_check(self, total_ = 100):
        if not self.last_am:
            pass
        elif self.last_am <= self.min_:
            #print('Break: Minium price')
            self.next_post = False
            return
        if self.currency == 'exalted':
            self.amount *= 150
        elif self.currency in ['fusing', 'alch']:
            self.amount //= 2
        elif self.currency == 'mirror':
            self.amount *= 10000
        elif self.currency == 'alt':
            self.amount //= 10
        self.last_am = self.amount
        if self.total - total_ < 1:
            #print('Break: total < 1')
            self.next_post = False
            return

        if self.currency in ['chaos', 'exalted', 'vaal', 'mirror', 'fusing', 'alch','regret']:
            if self.last_am == self.amount and self.amount > self.min_:
                self.amount -= 1
                self.last_am = self.amount
            self.next_post = True
        else:
            #print('Break: NA currency - ' + self.currency)
            try:
                self.notes += 'NA currency break' + self.currency
            except AttributeError:
                self.notes = ['NA currency break' + self.currency]
                
            self.next_post = False
            return


    def query_get(self, api, db, parse='', account='',character=''):
        '''
        query items, account char, char items
        '''
        for ids in list(self.post_ids.values()):
            if api == 'query items':
                self.response_get = requests.get("https://www.pathofexile.com/api/trade/fetch/"+ids+"?query="+self.id, headers=self.headers)#, cookies=cookies)
            elif api == 'account char':
                self.response_get = requests.get("https://www.pathofexile.com/character-window/get-characters?accountName="+account, headers=self.headers)#, cookies=cookies)
            elif api == 'char items':
                self.response_get = requests.get("https://www.pathofexile.com/character-window/get-items?accountName="+account+"&character="+character, headers=self.headers)#, cookies=cookies)
            try:
                self.current_get += [time.time()]
            except AttributeError:
                self.current_get = [time.time()]

            if self.response_get.status_code != 200:
                print('Status code get ' + str(self.response_get.status_code))
                self.get_result = []
            self.current_get = timeout(self.response_get, self.current_get)
            try:
                self.get_result = self.response_get.json()['result']
            except KeyError:
                self.get_result = []
            
            if parse:
                parse(self, db)



    def parse_get_result_uniques(self, db):
        for index, i in enumerate(self.get_result):
            if not i:
                continue
            i_id = i['id']
            indexed = sec_since_epoch(i['listing']['indexed'])
            sold = not i['item']['verified']
            account = i['listing']['account']['name']
            if i['listing']['price']:
                self.amount = i['listing']['price']['amount']
                self.currency = i['listing']['price']['currency']
            else:
                self.amount, self.currency = 0,"NA"
            if self.get_first:
                print(str(self.amount) + str(self.currency), end='')
                self.get_first = False
            ilvl = i['item']['ilvl']
            if i['item']['identified'] == 'false':
                continue

            ## EXPLICIT KEYS MIN MAX i['item']['extended']['mods']['explicit'][i]['magnitudes']
            try:
                explicits = [x.replace('+', '') for x in i['item']['explicitMods']]
            except KeyError:
                explicits = []
            try:
                implicits = [x.replace('+', '') for x in i['item']['implicitMods']]
            except KeyError:
                implicits = []

            
            self.listing_dict = {"item": self.name, "indexed": indexed, "amount": self.amount, "currency": self.currency, "sold": sold, "explicits": explicits, "implicits": implicits, "ilvl": ilvl, "account": account}
            if sold:
                self.listing_dict['confirmed'] = False
                self.listing_dict['search'] = self.id
                db.listing_sold[i_id] = list(self.listing_dict.values())
                try:
                    del db.listing[i_id]
                except KeyError:
                    pass
            else:
                db.listing[i_id] = list(self.listing_dict.values())
        

    def get_missing_ids(self, db):
        db.missing_ids = db.missing_ids.append([{'id':x, 'search':self.base_id} for x in db.listing_df[db.listing_df['item'] == self.name].index if x not in self.ram_ids])


    def fetch_missing_ids(self, db):
        for search in list(db.missing_ids["search"].unique()):
            self.id = search
            self.post_ids_trim = list(db.missing_ids[db.missing_ids['search'] == search]['id'])
            self.get_first = False
            self.get_post_ids(trim=False)
            self.query_get('query items', db)
            self.parse_get_result(db)
        db.missing_ids.drop(db.missing_ids.index, inplace=True)


    def parse_characters(self, account, db, items, league='Heist'):
        self.query_get('account char', db, account=account)
        self.characters = []
        for character in self.get_result:
            if character['league'] == league:
                self.characters += character['name']
        for character in self.characters:
            self.query_get('char items', db, account=account, character=character)
            for item in self.get_result['items']:
                pass

            
    
