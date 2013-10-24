#!/usr/bin/env python
import os, sys, time, re, json, pdb
import datetime
# -----------------------------------------
import numpy as np
import pandas as pd
from pandas.io import sql
import scipy as sp
import requests
from requests_oauthlib import OAuth1Session
from pymongo import MongoClient
from bson.objectid import ObjectId
from bs4 import BeautifulSoup as Soup
# ------------------------------------------
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
cnx_exe("""
DROP TABLE if EXISTS abc;
CREATE TABLE abc AS
SELECT VERSION();
""")
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

def get_team_tag(txt):
    if txt == 'New Orleans Hornets':
        return 'NOH'
    df = pd.read_csv('bbref_team_names.txt')
    return df[df['name']==txt]['tag'].values[0]

def format_point(txt):
    if txt:
        return int(ixt)
    else:
        return -1

def acquire_all_games_of_a_season(season):
    # -------------------------------
    # links for schedule and results
    # -------------------------------
    # basic http request setup
    user_agent_info = """Jin Huang (huangjinf@gmail.com)\n
    Please let me know if there is any rate limit information.
    I am not colelcting data for any commercial use.
    """
    headers = {'user_agent': user_agent_info}
    url = 'http://www.basketball-reference.com/leagues/NBA_'+season+'_games.html'
    print '-'*30
    print 'season is: ', season
    print url
    print '-'*30

    # http request
    data = requests.get(url, headers=headers)
    soup_data = Soup(data.text)
    table_body = soup_data.find(id='div_games').find('tbody')

    for row in table_body.find_all('tr'):
        _row = {i: x.text for i,x in enumerate(row.find_all('td'))}
        date = format_date(_row[0])
        home = _row[4]
        pts_home = format_point(_row[5])
        visitor = _row[2]
        pts_visitor = format_point(_row[3])
        ot = format_ot(_row[6])
        link = row.find_all('a', href=True)[1]['href']
        game_id = re.search('(?<=/)[A-Za-z0-9]+(?=\.html)',link).group()
        print 'game_id,date,home,pts_home,visitor,pts_visitor,ot,link'
        print game_id,date,home,pts_home,visitor,pts_visitor,ot,link    
        cnx_exe("""
        INSERT INTO %s (game_id,date,home,pts_home,visitor,pts_visitor,ot,link )
        VALUES           ('%s',   '%s','%s', %s,     '%s',   %s,      '%s','%s');
        """%(table_name,game_id,date,home,pts_home,visitor,pts_visitor,ot,link))
    return None
def acquire_all_games_of_a_future_season(season):
    # -------------------------------
    # links for schedule and results
    # -------------------------------
    # basic http request setup
    user_agent_info = """Jin Huang (huangjinf@gmail.com)\n
    Please let me know if there is any rate limit information.
    I am not colelcting data for any commercial use.
    """
    headers = {'user_agent': user_agent_info}
    url = 'http://www.basketball-reference.com/leagues/NBA_'+season+'_games.html'
    print '-'*30
    print 'season is: ', season
    print url
    print '-'*30

    # http request
    data = requests.get(url, headers=headers)
    soup_data = Soup(data.text)
    table_body = soup_data.find(id='div_games').find('tbody')

    for row in table_body.find_all('tr'):
        _row = {i: x.text for i,x in enumerate(row.find_all('td'))}
        date = format_date(_row[0])
        home = _row[4]
        pts_home = format_point(_row[5])
        visitor = _row[2]
        pts_visitor = format_point(_row[3])
        ot = format_ot(_row[6])
        visitor_symbol = df_team_names[df_team_names['name']==visitor]['tag'].values[0]
        home_symbol = df_team_names[df_team_names['name']==home]['tag'].values[0]
        game_id = date+'_'+visitor_symbol+'_'+home_symbol
        link = '-'
        print 'game_id,date,home,pts_home,visitor,pts_visitor,ot,link'
        print game_id,date,home,pts_home,visitor,pts_visitor,ot,link    
        cnx_exe("""
        INSERT INTO %s (game_id,date,home,pts_home,visitor,pts_visitor,ot,link )
        VALUES           ('%s',   '%s','%s', %s,     '%s',   %s,      '%s','%s');
        """%(table_name,game_id,date,home,pts_home,visitor,pts_visitor,ot,link))
    return None

# -------------------------------------
# loop over seasons for games of
# -------------------------------------
table_name = 'games_id_links_1999_to_2013' # for 1999 to 2013
season_list = ['1999',
'2000',
'2001',
'2002',
'2003',
'2004',
'2005',
'2006',
'2007',
'2008',
'2009',
'2010',
'2011',
'2012',
'2013',]
table_name = 'games_id_links_2014' # for 1999 to 2013
cnx.reset()
'''
game_id | date | home | pts_home | visitor | pts_visitor | ot | link 
'''
cnx_exe('DROP TABLE if EXISTS %s;' % table_name)    
cnx_exe("""
CREATE TABLE %(table)s(
game_id VARCHAR(20) PRIMARY KEY,  
date DATE NOT NULL,
home VARCHAR(50) NOT NULL,
pts_home SMALLINT NOT NULL,
visitor VARCHAR(50) NOT NULL,
pts_visitor SMALLINT NOT NULL,
ot VARCHAR(5) NOT NULL,
link VARCHAR(50) NOT NULL)
""" % {'table': table_name})
# for season in ['2014']:
#     acquire_all_games_of_a_season(season)
#     time.sleep(1)
# cnx.commit()

df_team_names = pd.read_csv('bbref_team_names.txt')
for season in ['2014']:
    acquire_all_games_of_a_future_season(season)
    time.sleep(1)
cnx.commit()

# # ------------------------
# # getting team results
# # ------------------------
# def get_team_results(team_name,season):
#     # basic http request setup
#     user_agent_info = '''Jin Huang (huangjinf@gmail.com)\n
#     Please let me know if there is any rate limit information.
#     I am not colelcting data for any commercial use.
#     '''
#     headers = {'user_agent': user_agent_info}
#     base_url = "http://www.basketball-reference.com/teams/"
#     url = base_url+team_name+'/'+season+'_games.html'
#     print url
#     data = requests.get(test_url, headers=headers)
#     soup_data = Soup(data.text)
#     table_body = soup_data.find(id='div_teams_games').find('tbody')

#     table_name = "result_"+team_name+"_"+season
#     # --------
#     cnx.reset()
#     cnx_exe("""
#     DROP TABLE if EXISTS %(table)s;
#     """ % {'table': table_name})
#     cnx_exe("""
#     CREATE TABLE %(table)s (g SMALLINT PRIMARY KEY,  
#                         date DATE NOT NULL,
#                         home SMALLINT NOT NULL,
#                         opp VARCHAR(25) NOT NULL,
#                         result CHAR(1) NOT NULL,
#                         ot VARCHAR(5) NOT NULL,
#                         score_t SMALLINT NOT NULL,
#                         score_o SMALLINT NOT NULL,
#                         w SMALLINT NOT NULL,
#                         l SMALLINT NOT NULL,
#                         streak SMALLINT NOT NULL);
#     """ % {'table': table_name})
#     # --------
#     for row in table_body.find_all('tr'):
#         if not(re.search('Box Score', row.text)):
#             continue
#         _row = {i: x.text for i,x in enumerate(row.find_all('td'))}
#         g = int(_row[0])
#         date = pd.to_datetime(_row[1]).date().isoformat()
#         home = format_home(_row[2])
#         opp = _row[4]
#         result = _row[5]
#         ot = format_ot(_row[6])
#         score_t = int(_row[7])
#         score_o = int(_row[8])
#         w = int(_row[9])
#         l = int(_row[10])
#         streak = format_streak(_row[11])
#         cnx_exe("""
#         INSERT INTO %s (g, date, home, opp, result, ot, score_t, score_o, w, l, streak) 
#         VALUES           (%s, '%s', %s,  '%s',  '%s',   '%s','%s',    %s,    %s, %s, %s); 
#         """ % (table_name, g, date, home, opp, result, ot, score_t, score_o, w, l, streak))
#     cnx.commit()
#     print team_name, season
#     print 'done'
#     print '----'
    


