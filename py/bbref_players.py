#!/usr/bin/env python
import os, sys, time, re, json, pdb
import datetime
# -----------------------------------------
import numpy as np
import pandas as pd
from pandas.io import sql # use for read_frame
import scipy as sp
import requests
from requests_oauthlib import OAuth1Session
from pymongo import MongoClient
from bson.objectid import ObjectId
from bs4 import BeautifulSoup as Soup
import pandas_psql as pdpsql # use to write_frame
import psycopg2

# ------------------------------------------
# connecting to the PostgreSQL database
# ------------------------------------------
try:
    try:
        cnx.close()
    except:
        print sys.exc_info()[0]     
    cnx = psycopg2.connect(host='localhost', database='popsfundamental', 
                           user='jhuang')
    cur = cnx.cursor()
    cnx_exe = cur.execute
    print sql.read_frame("SELECT VERSION()",cnx)
except:
    print sys.exc_info()[0]
cnx.reset()

# ------------------
# helper functions
# ------------------
def format_ot(txt):
    if txt:
        return txt
    else:
        return "-"

def format_date(txt):
    return pd.to_datetime(txt).date().isoformat()

print format_date('June 24, 1968')
print format_date('November 15, 1962')

def format_college(txt):
    if txt:
        return txt
    else: 
        return '-'
print format_college('Michigan State University')
print format_college('')

user_agent_info = """Jin Huang (huangjinf@gmail.com)\n
Please let me know if there is any rate limit information.
I am not colelcting data for any commercial use.
I am doing a simple demonstration project using graphical 
causal inference model.
"""
headers = {'user_agent': user_agent_info}

table_name = 'players_bbref'
table_index = 'players_bbref_idx'

df = pd.read_csv('players_bbref.csv', index_col=0)
df = df.applymap(unicode)
cnx.reset()
cnx_exe('DROP TABLE if EXISTS players_bbref;')
pdpsql.write_frame(df, table_name, cnx)

cnx_exe('DROP INDEX if exists %s;' % table_index)
cnx_exe('CREATE UNIQUE INDEX %s ON %s (player_bbr_id);' % (table_index, table_name))

'''
# -------------------------------------
# importing the list of name team names
# -------------------------------------
from string import ascii_lowercase
link_list = ['/'+x+'/' for x in list(ascii_lowercase)]

df = pd.DataFrame(columns=range(10))
for link in link_list[24:26]:
    url = 'http://www.basketball-reference.com/players'+link
    print '-' * 30
    print url
    print '-'*30
    # ----------------
    # http request
    time.sleep(1)
    data = requests.get(url, headers=headers)
    soup_data = Soup(data.text)
    table_body = soup_data.find(id='div_players').find('tbody')
    # ----------------
    for row in table_body.find_all('tr'):
        _row = {i: x.text for i,x in enumerate(row.find_all('td'))}
        player = _row[0]
        first = _row[1]
        last = _row[2]
        pos = _row[3][0]
        ht = _row[4]
        wt = _row[5]
        birth = format_date(_row[6])
        college = format_college(_row[7])
        link = row.find('a', href=True)['href']
        player_bbr_id = re.search('(?<=/)[a-z0-9]+(?=\.html)', link).group()
        row = [player_bbr_id, player, pos, first, last, ht, wt, birth, college, link]
        df = df.append(pd.Series(row), ignore_index=True)    

df.columns = ['player_bbr_id', 'player', 'pos', 
              'first', 'last', 'ht', 'wt', 'birth', 'college', 'link']

cnx_exe('DROP TABLE if EXISTS players_bbref')
psql.write_frame(df, players_bbref, cnx, 'postgresql', 'fail')
'''
