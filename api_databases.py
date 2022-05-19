import pandas as pd
from selenium import webdriver
import csv

class Databases:
    def __init__(self, dbs='all', listing=True):
        if dbs == 'all':
            self.mods = pd.read_csv('data/mods.csv', index_col='key') 
            self.uniques = pd.read_csv('data/uniques.csv', index_col='name')
            self.missing_ids = pd.DataFrame([], columns=['search','id'])
            self.currency = pd.read_csv('data/currency.csv', index_col='id')
            self.snipes = pd.read_csv('data/snipes.csv', index_col='id')
            self.proxies = pd.read_csv('data/proxies.csv', index_col='id')
            
            with open('data/listing_sold.csv') as file:
                reader = csv.reader(file)
                self.listing_sold = {row[0]:row[1:] for row in reader}
            mat = [[key] + value for key, value in self.listing_sold.items()]
            self.sold_df = pd.DataFrame(mat[1:], columns=mat[0])
            self.sold_df.set_index(mat[0][0], inplace=True)
            self.sold_df = self.sold_df.loc[:, ~self.sold_df.columns.str.contains('^Unnamed')]
            if listing:
                with open('data/listing.csv') as file:
                    reader = csv.reader(file)
                    self.listing = {row[0]:row[1:] for row in reader}
                mat = [[key] + value for key, value in self.listing.items()]
                self.listing_df = pd.DataFrame(mat[1:], columns=mat[0])
                self.listing_df.set_index(mat[0][0], inplace=True)
                self.listing_df = self.listing_df.loc[:, ~self.listing_df.columns.str.contains('^Unnamed')]
        else:
            if 'snipes' in dbs:
                self.snipes = pd.read_csv('data/snipes.csv', index_col='id')
            if 'proxies' in dbs:
                self.proxies = pd.read_csv('data/proxies.csv', index_col='id')
        
    def save(self, save_, save_all=False):
        if save_all:
            save_ = ['listing', 'currency', 'uniques', 'listing_sold', 'missing_ids', 'mods', 'snipes']
        for save in save_:
            if save == 'listing':
                mat = [[key] + value for key, value in self.listing.items()]
                df = pd.DataFrame(mat[1:], columns=mat[0])
                df.set_index(mat[0][0], inplace=True)
                df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                df.to_csv('data/listing.csv', index='id')
            if save == 'listing_sold':
                mat = [[key] + value for key, value in self.listing_sold.items()]
                df = pd.DataFrame(mat[1:], columns=mat[0])
                df.set_index(mat[0][0], inplace=True)
                df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                df.to_csv('data/listing_sold.csv', index='id')
            if save == 'currency':
                ind = False
            if save == 'uniques':
                ind = 'name'
            if save == 'snipes':
                ind = 'id'
            if save == 'proxies':
                ind = 'id'
            if save in ['mods', 'missing_ids']:
                ind = 'id'
            if save not in ['listing', 'listing_sold']:
                self.db = getattr(self, save)
                self.db.to_csv('data/'+str(save)+'.csv', index=ind)


    def if_uniques_update(self):
        #id,item,indexed,amount,currency,sold,explicits,implicits,ilvl,account

        pass

    def scrape_ninja(self):
        db = pd.DataFrame([], columns=['buy_p', 'buy_c', 'sell_p', 'sell_c'])
        driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver')  # Optional argument, if not specified will search path.
        driver.get('https://poe.ninja/challenge/currency')
        prices = driver.find_elements_by_class_name('text-right')
        for i, price in enumerate(prices):
            if i % 4 in [2, 3]:
                continue
            amount = price.text
            currency = price.find_elements_by_xpath('//span/div/img')[i].get_attribute('title')
            if not i % 2:
                buy, sell = [],[]
                buy += (amount, currency)
            else: 
                sell += (amount, currency)
                db = db.append({'buy_c': buy[1], 'buy_p': buy[0].split('\n')[0], 'sell_c':sell[1], 'sell_p': sell[0].split('\n')[0]}, ignore_index=True)
        db.to_csv('data/currency.csv', index=False)
        driver.close()

