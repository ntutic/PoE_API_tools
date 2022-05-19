import time
import datetime
import requests
from bs4 import BeautifulSoup

def sec_since_epoch(date_time, epoch=(2020,1,1), dt_format='%Y-%m-%dT%H:%M:%SZ'):
    date_time = datetime.datetime.strptime(date_time, dt_format)
    return int((date_time-datetime.datetime(epoch[0], epoch[1], epoch[2])).total_seconds())



def timeout(response, current):
    state = response.headers['X-Rate-Limit-Ip-State']
    rules = response.headers['X-Rate-Limit-Ip']
    limit1 = int(rules.split(':')[0])
    state1 = int(state.split(':')[0])
    time1 = int(rules.split(':')[1])
    timeout1 = int(state.split(':')[2].split(',')[0])
    limit2 = int(rules.split(',')[1].split(':')[0])
    state2 = int(state.split(',')[1].split(':')[0])
    time2 = int(rules.split(',')[1].split(':')[1])
    timeout2 = int(state.split(',')[1].split(':')[2])
    if timeout1 or timeout2:
        time.sleep(max([timeout1, timeout2]))
    t_ = time.time()
    cur1 = [t for t in current if t > t_ - time1]
    cur2 = [t for t in current if t > t_ - time2] 
    sleep1 = time1 - (t_ - min(cur1))
    sleep2 = time2 - (t_ - min(cur2))
    sl1 = False
    sl2 = False
    if len(cur1) >= limit1 or state1 >= limit1:
        #print('X '+str(state1)+' ('+str(len(cur1))+'):'+str(limit1)+' / '+str(state2)+' ('+str(len(cur2))+'):'+str(limit2), end='')
        sl1 = True 
    if len(cur2) >= limit2 or state2 >= limit2:
        #print('X '+str(state1)+' ('+str(len(cur1))+'):'+str(limit1)+' / '+str(state2)+' ('+str(len(cur2))+'):'+str(limit2), end='')
        sl2 = True
    if sl1 or sl2:
        #print(' / Sleep '+str(round(max([sleep1, sleep2]),2)))
        time.sleep(max([sleep1, sleep2]))
    return [x for x in current if x in cur1+cur2]


def get_proxies(country='US', port='', protocol='HTTP', anon=[1, 2], avail=70, sort='u'):
    url = 'http://www.freeproxylists.net/?'
    url += 'c=' + country + '&'
    url += 'pt=' + port + '&'
    url += 'pr=' + protocol + '&'
    for a in anon:
        # 0 = No, 1 = Anon, 2 = Very anon
        url += 'a%5B%5D=' + str(a) + '&'
    url += 'u=' + str(avail)
    
    if sort:
        url += '&s=' + sort

    response = requests.get(url)
    soup = BeautifulSoup(response.content)

    table = soup.find('table', {'class': 'DataGrid'})
    rows_odd = soup.find_all('tr', {'class': 'Odd'})
    rows_even = soup.find_all('tr', {'class': 'Even'})

    rows = []
    for row, row_odd in enumerate(rows_odd):
        rows = rows.append(row_odd)
        if row != len(rows_odd) - 1:
            rows = rows.append(rows_odd[row])
        elif len(rows_odd) == len(rows_even):
            rows = rows.append(rows_odd[row])
        
    proxies = {}

