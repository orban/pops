#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os, sys, time, re, json, pdb, pickle
import datetime
# -----------------------------------------
import numpy as np
import pandas as pd
import pandas.io.sql as psql
import scipy as sp
import requests
from requests_oauthlib import OAuth1Session
from pymongo import MongoClient
from bson.objectid import ObjectId
from bs4 import BeautifulSoup as Soup
import psycopg2

sys.path.append('~/zipfian/pops/bin/utils')
import pandas_psql as pdpsql


# ------------------------------------------
# connecting to the PostgreSQL database
# ------------------------------------------
try:
    cnx = psycopg2.connect(host='localhost', database='popsfundamental', 
                           user='jhuang')
    cur = cnx.cursor()
    cnx_exe = cur.execute
except:
    print sys.exc_info()[0]
cnx.reset()

# ------------------------------------------
# MongoDB
# ------------------------------------------
client = MongoClient('localhost', 27017)
client = MongoClient('mongodb://localhost:27017/')
db_bbref = client['bbref'] # database bbref
mongo_rosters = db_bbref['team_roster']

# # -------------------------------------------------------------
# # downloading documents from basketball-reference.com
# # -------------------------------------------------------------
# user_agent_info = """Jin Huang (huangjinf@gmail.com)\n
# Please let me know if there is any rate limit information.
# I am not colelcting data for any commercial use.
# I am doing a simple demonstration project using graphical 
# causal inference model. Please see: popfactors.com
# """
# headers = {'user_agent': user_agent_info}
# df_teams = pd.read_csv('bbref_team_names_2014.txt')

# counter = 0
# for i in range(len(df_teams)):
#     team = df_teams.iloc[i,2]
#     team_name = df_teams.iloc[i,1]
#     url = 'http://www.basketball-reference.com/teams/'+team+'/2014.html'
    
#     print '-' * 30
#     counter += 1
#     print counter
#     print url
#     print '-'*30

#     # http request
#     time.sleep(.5)
#     data = requests.get(url, headers=headers)
#     page_content = data.content

#     doc = {'team': team, 
#            'team_name': team_name,
#            'html': unicode(page_content, errors='ignore')}
#     mongo_rosters.find_and_modify(query={'team': team},
#                                   update=doc, upsert=True)


# --------------------------
# formatting functions
# --------------------------
def get_player_pos(player_bbref_id):
    return psql.read_frame("""SELECT pos FROM players_bbref 
    WHERE player_bbr_id = '%s';""" 
    %player_bbref_id, cnx).values[0,0]

df_teams = pd.read_csv('bbref_team_names_2014.txt')
counter = 0

team_dict = {}
for i in range(len(df_teams)):
    team = df_teams.iloc[i,2]
    df = pd.DataFrame(columns=['id', 'name', 'salary'])
    
    data = mongo_rosters.find_one({'team':team})    
    soup_data = Soup(data['html'])

    table = soup_data.find('div', {'id': 'div_salaries'}).find('tbody')
    rows = table.find_all('tr')
    
    for i in range(len(rows)):
        player_infor = {}
        row = rows[i]
        cells = row.find_all('td')

        player_link = cells[1].find('a').get('href')
        player_infor['id'] = re.search('(?<=/)[a-z0-9]+(?=\.html)', player_link).group()
        player_infor['name'] = cells[1].text
        player_infor['salary'] = cells[2].text

        df = df.append(pd.Series(player_infor), ignore_index=True)

    # print df
    team_dict[team] = df

with open('../bin/app_data/team_roster_dict.pkl', 'wb') as f:
    pickle.dump(team_dict, f)

    
