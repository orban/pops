#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os, sys, time, re, json, pdb
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
mongo_players = db_bbref['players'] # collection players

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

# df_links = psql.read_frame('SELECT * FROM players_bbref;', cnx)

# counter = 0
# for i in range(len(df_links)):
#     player_id = df_links.iloc[i,:]['player_bbr_id']
#     name = df_links.iloc[i,:]['player']
#     pos = df_links.iloc[i,:]['pos']    
#     link = df_links.iloc[i,:]['link']
    
#     url = 'http://www.basketball-reference.com' + link
    
#     print '-' * 30
#     counter += 1
#     print counter
#     print url
#     print '-'*30

    
#     # http request
#     time.sleep(.5)
#     data = requests.get(url, headers=headers)
#     page_content = data.content
# doc = {'link': link, 
#        'player_id': player_id,
#        'name': name,
#        'pos': pos,
#        'html': unicode(page_content, errors='ignore')}
#     mongo_players.find_and_modify(query={'link': link},
#                                   update=doc, upsert=True)


# ---------------------------
# helper functions
# --------------------------
def format_ot(txt):
    if txt:
        return txt
    else:
        return "-"

def format_date(txt):
    return pd.to_datetime(txt).date().isoformat()

# print format_date('June 24, 1968')
# print format_date('November 15, 1962')

def format_college(txt):
    if txt:
        return txt
    else: 
        return '-'

def format_to_float(txt):
    try: 
        return float(txt)
    except:
        return 1.0
    
# ---------------------------------------


# ----------------------------------------
# extracting information for all players
# that ever play in the NBA
# ----------------------------------------
df_links = psql.read_frame('SELECT * FROM players_bbref;', cnx)
counter = 0
df_counter = 0
df = pd.DataFrame(columns=['FT',
                           '3P',
                           'TOV',
                           'pos',
                           '2PA',
                           'FG',
                           'player_id',
                           '3PA',
                           'DRB',
                           'AST',
                           '2P_PER',
                           'PF',
                           'PTS',
                           'FGA',
                           '2P',
                           'STL',
                           'TRB',
                           'FTA',
                           'link',
                           'BLK',
                           'handle',
                           'name',
                           '3P_PER',
                           'FG_PER',
                           'FT_PER',
                           'MP',
                           'ORB'])

for i in range(len(df_links)):
    counter += 1    
    player_id = df_links.iloc[i,:]['player_bbr_id']
    name = df_links.iloc[i,:]['player']
    pos = df_links.iloc[i,:]['pos']    
    link = df_links.iloc[i,:]['link']


    # # ---------------------------------------
    # # for testing; use Sir Charles
    # if name != 'Charles Barkley*': continue
    # # ---------------------------------------
    
    print '-' * 30
    print counter, name, pos, link
    print '-' * 30    

    player_dict = {}
    player_dict['player_id'] = player_id
    player_dict['name'] = name
    player_dict['pos'] = pos
    player_dict['link'] = link    
    

    data = mongo_players.find_one({'link':link})    
    soup_data = Soup(data['html'])

    # -----------
    # per game
    # -----------    
    '''
Per Game Glossary  · SHARE  · Embed  · CSV  · PRE  · LINK  · 
Season	Age	Tm	Lg	Pos	G	GS	MP	FG	FGA	FG%	3P	3PA	3P%	2P	2PA	2P%	FT	FTA	FT%	ORB	DRB	TRB	AST	STL	BLK	TOV	PF	PTS
1984-85	21	PHI	NBA	PF	82	60	28.6	5.2	9.5	.545	0.0	0.1	.167	5.2	9.5	.548	3.6	4.9	.733	3.2	5.3	8.6	1.9	1.2	1.0	2.5	3.7	14.0
1985-86	22	PHI	NBA	PF	80	80	36.9	7.4	13.0	.572	0.2	0.9	.227	7.2	12.1	.598	5.0	7.2	.685	4.4	8.4	12.8	3.9	2.2	1.6	4.4	4.2	20.0
1986-87 	23	PHI	NBA	PF	68	62	40.3	8.2	13.8	.594	0.3	1.5	.202	7.9	12.3	.643	6.3	8.3	.761	5.7	8.9	14.6	4.9	1.8	1.5	4.7	3.7	23.0
1987-88 	24	PHI	NBA	PF	80	80	39.6	9.4	16.0	.587	0.6	2.0	.280	8.9	14.1	.630	8.9	11.9	.751	4.8	7.1	11.9	3.2	1.3	1.3	3.8	3.5	28.3
1988-89 	25	PHI	NBA	PF	79	79	39.1	8.9	15.3	.579	0.4	2.1	.216	8.4	13.2	.636	7.6	10.1	.753	5.1	7.4	12.5	4.1	1.6	0.8	3.2	3.3	25.8
1989-90 	26	PHI	NBA	PF	79	79	39.1	8.9	14.9	.600	0.3	1.2	.217	8.7	13.7	.632	7.1	9.4	.749	4.6	6.9	11.5	3.9	1.9	0.6	3.1	3.2	25.2
1990-91 	27	PHI	NBA	PF	67	67	37.3	9.9	17.4	.570	0.7	2.3	.284	9.3	15.1	.614	7.1	9.8	.722	3.9	6.3	10.1	4.2	1.6	0.5	3.1	2.6	27.6
1991-92 	28	PHI	NBA	PF	75	75	38.4	8.3	15.0	.552	0.4	1.8	.234	7.9	13.2	.597	6.1	8.7	.695	3.6	7.5	11.1	4.1	1.8	0.6	3.1	2.6	23.1
1992-93 	29	PHO	NBA	PF	76	76	37.6	9.4	18.1	.520	0.9	2.9	.305	8.5	15.2	.561	5.9	7.7	.765	3.1	9.1	12.2	5.1	1.6	1.0	3.1	2.6	25.6
1993-94 	30	PHO	NBA	PF	65	65	35.4	8.0	16.1	.495	0.7	2.7	.270	7.2	13.4	.541	4.9	7.0	.704	3.0	8.1	11.2	4.6	1.6	0.6	3.2	2.5	21.6
1994-95 	31	PHO	NBA	PF	68	66	35.0	8.1	16.8	.486	1.1	3.2	.338	7.1	13.6	.521	5.6	7.5	.748	3.0	8.1	11.1	4.1	1.6	0.7	2.2	3.0	23.0
1995-96 	32	PHO	NBA	PF	71	71	37.1	8.2	16.3	.500	0.7	2.5	.280	7.5	13.9	.539	6.2	8.0	.777	3.4	8.1	11.6	3.7	1.6	0.8	3.1	2.9	23.2
1996-97 	33	HOU	NBA	PF	53	53	37.9	6.3	13.1	.484	1.1	3.9	.283	5.2	9.2	.569	5.4	7.8	.694	4.0	9.5	13.5	4.7	1.3	0.5	2.8	2.9	19.2
1997-98	34	HOU	NBA	PF	68	41	33.0	5.3	10.9	.485	0.3	1.2	.214	5.0	9.7	.520	4.4	5.8	.746	3.5	8.1	11.7	3.2	1.0	0.4	2.2	2.8	15.2
1998-99	35	HOU	NBA	PF	42	40	36.3	5.7	12.0	.478	0.1	0.6	.160	5.6	11.4	.495	4.6	6.4	.719	4.0	8.3	12.3	4.6	1.0	0.3	2.4	2.1	16.1
1999-00	36	HOU	NBA	PF	20	18	31.0	5.3	11.1	.477	0.3	1.3	.231	5.0	9.8	.510	3.6	5.5	.645	3.6	6.9	10.5	3.2	0.7	0.2	2.2	2.4	14.5
Career			NBA		1073	1012	36.7	7.9	14.5	.541	0.5	1.9	.266	7.4	12.7	.581	5.9	8.1	.735	4.0	7.7	11.7	3.9	1.5	0.8	3.1	3.1	22.1
8 seasons		PHI	NBA		610	582	37.3	8.2	14.3	.576	0.4	1.5	.241	7.9	12.8	.614	6.4	8.8	.733	4.4	7.2	11.6	3.7	1.7	1.0	3.5	3.4	23.3
4 seasons		PHO	NBA		280	278	36.3	8.5	16.9	.501	0.9	2.8	.301	7.6	14.0	.542	5.7	7.5	.751	3.1	8.4	11.5	4.4	1.6	0.8	2.9	2.7	23.4
4 seasons		HOU	NBA		183	152	35.0	5.7	11.8	.482	0.5	1.9	.253	5.2	9.9	.525	4.6	6.5	.712	3.8	8.4	12.2	3.9	1.1	0.4	2.4	2.6	16.5
    '''
    row = soup_data.find('div', {'id':'all_per_game'}).find('tfoot').find('tr', {'class': 'stat_total'})
    cells = [c.text for c in row.find_all('td')]

    _list = ['MP', 
             'FG',
             'FGA',
             'FG_PER',
             '3P',
             '3PA',
             '3P_PER',
             '2P',
             '2PA',
             '2P_PER',
             'FT',
             'FTA',
             'FT_PER',
             'ORB',
             'DRB',
             'TRB',
             'AST',
             'STL',
             'BLK',
             'TOV',
             'PF',
             'PTS']
    
    for i,field in enumerate(_list):
        j = i + 7
        player_dict[field] = format_to_float(cells[j])
    
    #df = df.append(pd.Series(away_team_dict), ignore_index=True)

    # ---------------
    # social media
    # ---------------
    try:
        _p = soup_data.find('p', {'class':'margin_top'})
        _a = _p.find_all('a')[1]
        twitter_handle = _a.text
        player_dict['handle'] = twitter_handle
    except:
        player_dict['handle'] = '-'
        

    # add data into data frame
    df = df.append(pd.Series(player_dict), ignore_index=True)

df[_list] = df[_list].applymap(float)    
df.columns = [u'FT', 
              u'THREE',
              u'TOV',
              u'pos',
              u'TWO_A',
              u'FG',
              u'player_id',
              u'THREE_A',
              u'DRB',
              u'AST',
              u'TWO_PER',
              u'PF',
              u'PTS',
              u'FGA',
              u'TWO',
              u'STL',
              u'TRB',
              u'FTA',
              u'link',
              u'BLK',
              u'handle',
              u'name',
              u'THREE_PER',
              u'FG_PER',
              u'FT_PER',
              u'MP',
              u'ORB']
    
# --------------------------------------
# putting data into the psql database
# --------------------------------------

table_name = 'df_players'
cnx.reset();
cnx_exe('DROP TABLE if EXISTS %s' %table_name)
pdpsql.write_frame(df, table_name, cnx)
