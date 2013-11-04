#!/usr/bin/env python
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
import pandas_psql as pdpsql

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
except:
    print sys.exc_info()[0]
cnx.reset()

# ------------------------------------------
# MongoDB
# ------------------------------------------
client = MongoClient('localhost', 27017)
client = MongoClient('mongodb://localhost:27017/')
db_bbref = client['bbref'] #database bbref
mongo_box_score = db_bbref['box_score_1999_2013']

# ---------------------
# formatting functions
# ---------------------
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

def get_player_pos(player_bbref_id):
    return psql.read_frame("""SELECT pos FROM players_bbref 
    WHERE player_bbr_id = '%s';""" 
    %player_bbref_id, cnx).values[0,0]

def format_to_float(txt):
    try: 
        return float(txt)
    except:
        return 0.0

def format_to_int(txt):
    try: 
        return int(txt)
    except:
        return 0
# # -------------------------------------------------------------
# # acquiring the documents from basketball-reference.com
# # -------------------------------------------------------------
# user_agent_info = """Jin Huang (huangjinf@gmail.com)\n
# Please let me know if there is any rate limit information.
# I am not colelcting data for any commercial use.
# I am doing a simple demonstration project using graphical 
# causal inference model.
# """
# headers = {'user_agent': user_agent_info}

# df_links = psql.read_frame('SELECT game, link from results_id_links_2013', cnx)
# counter = 0
# for i in range(len(df_links)):
#     game = df_links.iloc[i,:]['game']
#     link = df_links.iloc[i,:]['link']
#     url = 'http://www.basketball-reference.com' + link
    
#     print '-' * 30
#     counter += 1
#     print counter
#     print url
#     print '-'*30

    
#     # http request
#     time.sleep(1)
#     data = requests.get(url, headers=headers)
#     page_content = data.content
#     doc = {'link': link, 'html': page_content}
#     mongo_box_score.find_and_modify(query=doc,
#                                     update=doc, upsert=True)

# ----------------------------------------
# extracting information from the page to 
# engineer features for each game
# ----------------------------------------
df_links = psql.read_frame('SELECT game_id, link from games_id_links_1999_to_2013', cnx)
counter = 0
df_counter = 0
df = pd.DataFrame(columns=['starters_TRB_home',
 'reserves_FT_away',
 'Reserve_F_AST_per_home',
 'Starting_F_ORB_per_away',
 'Starting_F_AST_home',
 'Reserve_G_ORB_home',
 'Reserve_F_FT_home',
 'Starting_G_PF_away',
 'Reserve_C_3P_away',
 'team_FTA_away',
 'Reserve_G_TRB_per_home',
 'Starting_F_STL_home',
 'ORtg_away',
 'Starting_C_STL_per_away',
 'reserves_3P_per_away',
 'Starting_G_FT_per_home',
 'scoring_2nd_away',
 'starters_BLK_away',
 'opp_home',
 'Reserve_C_AST_home',
 'Starting_F_ORB_home',
 'Reserve_C_FTA_away',
 'Starting_F_FT_away',
 'Reserve_G_PF_away',
 'Reserve_G_BLK_per_home',
 'starters_PF_home',
 'opp_away',
 'Reserve_F_FG_away',
 'Starting_F_STL_away',
 'team_TOV_home',
 'Starting_F_TRB_home',
 'Reserve_F_FT_per_away',
 'team_3P_home',
 'team_STL_away',
 'Starting_F_PF_home',
 'reserves_TRB_away',
 'Starting_G_STL_per_home',
 'Starting_F_BLK_per_away',
 'starters_FT_per_away',
 'Reserve_C_AST_per_home',
 'Starting_F_DRB_per_home',
 'Starting_C_DRB_per_away',
 'Starting_F_BLK_away',
 'Starting_G_TRB_away',
 'Reserve_G_FT_away',
 'eFG_per_home',
 'Reserve_C_ORB_per_home',
 'scoring_3rd_home',
 'reserves_FT_per_away',
 'Reserve_C_FG_home',
 'Reserve_G_FGA_away',
 'team_DRB_home',
 'Starting_C_ORB_per_home',
 'Starting_F_AST_away',
 'Reserve_C_PF_home',
 'starters_AST_away',
 'Starting_F_3PA_away',
 'Reserve_C_DRB_per_home',
 'Reserve_F_FG_per_home',
 'Reserve_C_STL_per_home',
 'Starting_C_USG_per_home',
 'Reserve_G_BLK_home',
 'Reserve_C_TOV_away',
 'Starting_C_PF_home',
 'scoring_4th_away',
 'Starting_G_BLK_per_away',
 'reserves_PF_away',
 'Reserve_F_AST_away',
 'starters_3PA_home',
 'starters_FG_per_away',
 'starters_ORB_away',
 'Starting_G_AST_per_away',
 'Reserve_F_FG_home',
 'Reserve_G_AST_per_home',
 'reserves_FG_away',
 'starters_STL_away',
 'Starting_G_AST_home',
 'Reserve_F_3P_per_home',
 'Starting_C_3P_away',
 'team_3P_away',
 'Starting_G_PTS_home',
 'Reserve_G_BLK_away',
 'Starting_F_STL_per_home',
 'Reserve_C_3PA_home',
 'Starting_G_STL_per_away',
 'Starting_C_TRB_per_away',
 'Starting_F_FT_per_home',
 'starters_STL_per_away',
 'Starting_C_AST_per_away',
 'Starting_C_PTS_home',
 'Reserve_C_STL_away',
 'Starting_G_3PA_away',
 'starters_AST_home',
 'Starting_C_TOV_home',
 'Reserve_F_TRB_away',
 'starters_USG_per_home',
 'team_DRB_away',
 'reserves_3P_away',
 'Starting_G_3P_away',
 'team_USG_per_home',
 'Starting_F_ORB_away',
 'Reserve_G_FG_home',
 'Reserve_G_PTS_home',
 'Reserve_G_FG_per_home',
 'reserves_STL_per_home',
 'reserves_3P_home',
 'Starting_C_DRB_home',
 'Reserve_G_AST_home',
 'Reserve_G_3P_per_away',
 'Starting_F_FTA_away',
 'Starting_F_FG_away',
 'Reserve_G_MP_home',
 'Reserve_F_3PA_away',
 'starters_STL_home',
 'Starting_G_FG_away',
 'starters_FG_away',
 'Starting_F_FGA_home',
 'Reserve_F_PF_away',
 'Starting_C_FTA_away',
 'Reserve_C_BLK_away',
 'team_FT_per_away',
 'ORB_per_home',
 'Reserve_G_FTA_away',
 'Reserve_C_AST_per_away',
 'Starting_C_DRB_per_home',
 'Reserve_C_TRB_per_away',
 'reserves_PTS_away',
 'reserves_TOV_home',
 'ORtg_home',
 'team_BLK_away',
 'Reserve_G_ORB_per_away',
 'Starting_G_FG_per_home',
 'Reserve_G_USG_per_away',
 'Reserve_G_DRB_away',
 'Starting_G_FTA_home',
 'Starting_C_TRB_home',
 'reserves_FTA_home',
 'starters_3P_home',
 'Reserve_F_TOV_home',
 'Reserve_G_USG_per_home',
 'Reserve_C_3P_home',
 'Starting_F_DRB_per_away',
 'team_TRB_away',
 'reserves_FG_per_home',
 'starters_TRB_per_away',
 'Starting_F_ORB_per_home',
 'Reserve_G_AST_away',
 'TOV_per_away',
 'Reserve_C_DRB_home',
 'Starting_G_3P_per_away',
 'Reserve_G_3P_per_home',
 'result_home',
 'Starting_C_STL_per_home',
 'Reserve_G_TRB_away',
 'team_FGA_home',
 'Starting_F_BLK_home',
 'Reserve_F_3P_away',
 'reserves_BLK_away',
 'Reserve_G_TOV_home',
 'starters_AST_per_home',
 'team_home',
 'reserves_3PA_home',
 'reserves_AST_per_away',
 'game_id_away',
 'Starting_C_FG_home',
 'Starting_G_FT_away',
 'Reserve_C_FG_per_home',
 'Starting_C_AST_home',
 'starters_FTA_home',
 'starters_TOV_home',
 'Starting_G_BLK_per_home',
 'Starting_C_FT_per_home',
 'Reserve_F_ORB_per_home',
 'Starting_G_ORB_home',
 'reserves_PTS_home',
 'starters_FT_home',
 'Starting_F_TRB_per_away',
 'Starting_C_TOV_away',
 'team_TRB_per_home',
 'Starting_C_TRB_per_home',
 'starters_FT_per_home',
 'starters_TRB_per_home',
 'Starting_G_USG_per_away',
 'Starting_C_FG_away',
 'reserves_USG_per_home',
 'Starting_G_BLK_away',
 'team_ORB_per_home',
 'Reserve_F_FTA_home',
 'Starting_G_TOV_home',
 'Reserve_G_FG_away',
 'starters_3PA_away',
 'TOV_per_home',
 'Reserve_C_DRB_away',
 'Reserve_G_3P_home',
 'Starting_F_DRB_home',
 'Reserve_F_TOV_away',
 'reserves_FTA_away',
 'team_FTA_home',
 'team_FT_per_home',
 'team_TRB_per_away',
 'Starting_G_DRB_per_away',
 'game_id_home',
 'Reserve_G_STL_home',
 'team_FG_home',
 'result_away',
 'Reserve_F_STL_per_away',
 'Starting_F_PTS_away',
 'scoring_1st_away',
 'team_3PA_away',
 'starters_STL_per_home',
 'reserves_FG_home',
 'team_away',
 'Pace_home',
 'Reserve_F_STL_per_home',
 'Starting_F_DRB_away',
 'reserves_TOV_away',
 'team_FG_away',
 'Starting_F_USG_per_away',
 'Reserve_F_DRB_home',
 'starters_FTA_away',
 'Starting_G_TRB_home',
 'Reserve_F_TRB_per_home',
 'Starting_G_ORB_per_home',
 'Starting_G_STL_home',
 'team_STL_per_away',
 'Starting_F_STL_per_away',
 'Reserve_C_3PA_away',
 'starters_BLK_per_away',
 'Starting_G_DRB_away',
 'Reserve_F_ORB_away',
 'team_FT_away',
 'Starting_G_FG_per_away',
 'Starting_C_3P_per_away',
 'Starting_G_TOV_away',
 'team_USG_per_away',
 'reserves_BLK_per_away',
 'Starting_F_FG_per_away',
 'Starting_F_3P_per_home',
 'reserves_STL_home',
 'starters_PTS_home',
 'team_AST_away',
 'Starting_F_3PA_home',
 'Reserve_F_ORB_per_away',
 'Starting_C_FTA_home',
 'Reserve_F_TRB_per_away',
 'team_STL_per_home',
 'Reserve_F_STL_away',
 'Reserve_G_BLK_per_away',
 'Reserve_G_PF_home',
 'starters_USG_per_away',
 'Reserve_G_ORB_per_home',
 'Reserve_F_FT_per_home',
 'starters_FG_per_home',
 'Reserve_F_DRB_per_away',
 'Reserve_C_FT_per_away',
 'reserves_FT_home',
 'Reserve_G_TOV_away',
 'reserves_TRB_per_away',
 'Starting_G_PTS_away',
 'Reserve_G_TRB_per_away',
 'starters_AST_per_away',
 'Reserve_C_TOV_home',
 'starters_FGA_away',
 'Reserve_G_FT_per_home',
 'Reserve_F_3PA_home',
 'Reserve_C_FG_away',
 'Reserve_F_BLK_per_home',
 'reserves_TRB_per_home',
 'Reserve_G_FT_per_away',
 'team_DRtg_away',
 'Starting_C_AST_away',
 'Reserve_F_FTA_away',
 'Starting_C_ORB_home',
 'starters_FT_away',
 'Reserve_G_MP_away',
 'Reserve_C_ORB_per_away',
 'Starting_G_DRB_per_home',
 'starters_PTS_away',
 'Starting_F_FT_home',
 'eFG_per_away',
 'Starting_C_USG_per_away',
 'Reserve_C_STL_per_away',
 'starters_ORB_per_away',
 'Starting_C_MP_home',
 'reserves_STL_away',
 'starters_3P_per_home',
 'reserves_USG_per_away',
 'team_ORB_per_away',
 'Starting_G_PF_home',
 'team_ORB_home',
 'starters_3P_away',
 'Reserve_C_STL_home',
 'Reserve_F_BLK_away',
 'team_AST_per_home',
 'team_3P_per_home',
 'Reserve_F_TRB_home',
 'Reserve_F_FGA_home',
 'Starting_G_3P_home',
 'FT_FGA_home',
 'starters_DRB_per_away',
 'Reserve_C_FGA_home',
 'Starting_G_FGA_home',
 'Reserve_F_AST_per_away',
 'reserves_DRB_home',
 'starters_FGA_home',
 'Pace_away',
 'Starting_G_ORB_per_away',
 'Starting_F_PF_away',
 'reserves_TRB_home',
 'Starting_C_ORB_away',
 'Reserve_F_PF_home',
 'Starting_G_FG_home',
 'reserves_FT_per_home',
 'team_ORB_away',
 'Starting_F_3P_away',
 'Starting_F_PTS_home',
 'Starting_F_MP_home',
 'Starting_F_AST_per_home',
 'reserves_ORB_per_home',
 'Reserve_G_STL_per_away',
 'team_3P_per_away',
 'Reserve_C_ORB_away',
 'reserves_FGA_away',
 'Reserve_G_DRB_per_away',
 'team_BLK_per_away',
 'Reserve_G_3PA_away',
 'Reserve_G_TRB_home',
 'Starting_G_DRB_home',
 'Starting_C_ORB_per_away',
 'Starting_C_DRB_away',
 'Starting_C_FG_per_away',
 'Starting_F_FGA_away',
 'Reserve_C_PTS_home',
 'starters_TOV_away',
 'Starting_G_MP_away',
 'Starting_G_USG_per_home',
 'starters_FG_home',
 'Reserve_C_USG_per_away',
 'Reserve_F_3P_home',
 'Reserve_F_MP_away',
 'Starting_F_BLK_per_home',
 'Starting_F_FG_home',
 'reserves_BLK_home',
 'Starting_C_FGA_home',
 'Reserve_G_FTA_home',
 'Reserve_C_FTA_home',
 'starters_ORB_per_home',
 'Starting_C_TRB_away',
 'Reserve_C_MP_home',
 'Reserve_C_MP_away',
 'Starting_G_FT_per_away',
 'Starting_G_BLK_home',
 'Starting_G_AST_away',
 'Starting_G_AST_per_home',
 'Reserve_C_FT_away',
 'Starting_F_USG_per_home',
 'Reserve_G_PTS_away',
 'reserves_FG_per_away',
 'Reserve_G_3PA_home',
 'Reserve_F_PTS_away',
 'Reserve_F_USG_per_home',
 'Reserve_C_ORB_home',
 'starters_DRB_per_home',
 'Starting_C_MP_away',
 'Starting_C_PTS_away',
 'starters_3P_per_away',
 'Reserve_C_PTS_away',
 'Starting_C_3PA_home',
 'Reserve_C_FGA_away',
 'Starting_G_STL_away',
 'Reserve_G_AST_per_away',
 'starters_PF_away',
 'Starting_F_TOV_home',
 'team_DRtg_home',
 'team_ORtg_home',
 'FT_FGA_away',
 'Starting_C_STL_home',
 'Reserve_F_DRB_away',
 'Starting_G_3PA_home',
 'Reserve_G_FG_per_away',
 'Reserve_F_PTS_home',
 'reserves_ORB_per_away',
 'Reserve_F_MP_home',
 'reserves_AST_away',
 'Reserve_C_3P_per_home',
 'Starting_F_3P_per_away',
 'Reserve_F_FGA_away',
 'Starting_G_MP_home',
 'Reserve_C_PF_away',
 'Starting_G_ORB_away',
 'Starting_C_BLK_per_home',
 'reserves_3PA_away',
 'Starting_C_BLK_away',
 'Starting_G_FTA_away',
 'reserves_STL_per_away',
 'team_PTS_away',
 'Starting_G_TRB_per_home',
 'Reserve_C_BLK_per_away',
 'Starting_C_3P_home',
 'team_AST_per_away',
 'starters_BLK_home',
 'Starting_F_FG_per_home',
 'reserves_BLK_per_home',
 'Starting_C_3P_per_home',
 'starters_BLK_per_home',
 'Starting_C_FG_per_home',
 'Starting_F_3P_home',
 'Reserve_F_FT_away',
 'Reserve_C_FT_home',
 'Reserve_G_ORB_away',
 'Starting_F_MP_away',
 'Reserve_C_TRB_per_home',
 'Starting_G_3P_per_home',
 'team_BLK_home',
 'Starting_F_FT_per_away',
 'scoring_2nd_home',
 'Reserve_G_DRB_home',
 'Starting_C_FT_home',
 'Reserve_G_3P_away',
 'reserves_DRB_away',
 'Starting_C_FT_away',
 'Reserve_C_DRB_per_away',
 'Reserve_F_DRB_per_home',
 'Reserve_C_TRB_away',
 'Reserve_G_STL_away',
 'team_TOV_away',
 'team_PTS_home',
 'team_STL_home',
 'Reserve_C_FT_per_home',
 'team_FG_per_away',
 'scoring_1st_home',
 'team_PF_home',
 'Reserve_F_USG_per_away',
 'Reserve_G_FGA_home',
 'scoring_4th_home',
 'team_FT_home',
 'Reserve_C_BLK_home',
 'Reserve_F_STL_home',
 'Reserve_C_FG_per_away',
 'Starting_C_BLK_per_away',
 'starters_ORB_home',
 'Starting_C_FGA_away',
 'Reserve_F_ORB_home',
 'team_AST_home',
 'reserves_DRB_per_away',
 'Reserve_C_BLK_per_home',
 'Reserve_C_TRB_home',
 'Starting_G_TRB_per_away',
 'Starting_G_FT_home',
 'starters_DRB_away',
 'Starting_C_FT_per_away',
 'Starting_C_PF_away',
 'team_FG_per_home',
 'Reserve_G_STL_per_home',
 'Starting_F_TOV_away',
 'Reserve_C_AST_away',
 'Starting_G_FGA_away',
 'starters_DRB_home',
 'reserves_DRB_per_home',
 'Reserve_F_AST_home',
 'Reserve_F_3P_per_away',
 'reserves_3P_per_home',
 'team_FGA_away',
 'reserves_ORB_away',
 'Reserve_F_BLK_per_away',
 'ORB_per_away',
 'team_PF_away',
 'team_TRB_home',
 'Starting_F_FTA_home',
 'Starting_F_TRB_per_home',
 'team_DRB_per_home',
 'Reserve_F_BLK_home',
 'starters_TRB_away',
 'Starting_F_TRB_away',
 'reserves_AST_home',
 'team_BLK_per_home',
 'Reserve_G_DRB_per_home',
 'Reserve_F_FG_per_away',
 'reserves_PF_home',
 'scoring_3rd_away',
 'Starting_C_3PA_away',
 'reserves_AST_per_home',
 'reserves_ORB_home',
 'Reserve_C_USG_per_home',
 'Starting_C_STL_away',
 'team_3PA_home',
 'reserves_FGA_home',
 'Starting_F_AST_per_away',
 'team_DRB_per_away',
 'team_ORtg_away',
 'Starting_C_AST_per_home',
 'Reserve_C_3P_per_away',
 'Starting_C_BLK_home',
 'Reserve_G_FT_home'])

for i in range(len(df_links)):
    link = df_links.iloc[i,:]['link']
    game = df_links.iloc[i,:]['game_id']

    print '-' * 30
    counter += 1
    print counter

    # --------------------------------
    # retrieve the data from MongoDB
    # --------------------------------

    data = mongo_box_score.find_one({'link':link})
    print link
    print data['link']
    print '-' * 30

    soup_data = Soup(data['html'])
    
    table = soup_data.find('table', {'class':'nav_table stats_table'})
    home_team = table.find_all('a', href=True)[1].text
    away_team = table.find_all('a', href=True)[0].text
    date = game[0:8]

    print 'home team is: ', home_team
    print 'aways team is: ', away_team
    print 'date is: ', date

    # ======================================================================
    # away team entry
    # ======================================================================
    away_team_dict = {}
    away_team_dict['team'] = away_team
    away_team_dict['opp'] = home_team
    print '++++++++++++++'* 3
    print 'processing the away team entry'
    print '++++++++++++++'* 3
    game_id = date + '_' + away_team    
    print 'game id is : ', game_id
    print 'the team is : ', away_team
    away_team_dict['game_id'] = game_id

    # --scoring box--    
    '''
Scoring
    1   2   3   4   T
WAS 24  15  23  22  84
CLE 31  19  24  20  94
    '''
    table = soup_data.find('table', {'class':'nav_table stats_table'})
    table_rows = [row for row in table.find_all('td')]
    starting_index = [i for (i,x) in enumerate(table_rows) if re.search(away_team, x.text)][0]
    away_team_dict['scoring_1st'] = table_rows[starting_index+1].text
    away_team_dict['scoring_2nd'] = table_rows[starting_index+2].text
    away_team_dict['scoring_3rd'] = table_rows[starting_index+3].text
    away_team_dict['scoring_4th'] = table_rows[starting_index+4].text

    # --four factors--    
    '''
Four Factors    
Pace    eFG%    TOV%    ORB%    FT/FGA  ORtg
WAS 87.9    .400    10.8    33.3    .133    95.5
CLE 87.9    .500    18.4    46.2    .190    106.9
    '''
    table = soup_data.find('div', {'id':'div_four_factors'}).find('tbody')
    tbl_rows = [r for r in table.find_all('td')]
    idx = [i for (i,x) in enumerate(tbl_rows) if re.search(away_team, x.text)][0]
    away_team_dict['Pace'] = tbl_rows[idx+1].text
    away_team_dict['eFG_per'] = tbl_rows[idx+2].text
    away_team_dict['TOV_per'] = tbl_rows[idx+3].text
    away_team_dict['ORB_per'] = tbl_rows[idx+4].text
    away_team_dict['FT_FGA'] = tbl_rows[idx+5].text
    away_team_dict['ORtg'] = tbl_rows[idx+6].text
    
    # ---------------------------------------
    # starting players, basic box scores
    # ---------------------------------------
    '''
Starters    MP  FG  FGA FG% 3P  3PA 3P% FT  FTA FT% ORB DRB TRB AST STL BLK TOV PF  PTS +/-
A.J. Price  29:24   2   13  .154    2   9   .222    1   1   1.000   1   1   2   6   0   0   1   1   7   -11
Emeka Okafor    24:35   4   10  .400    0   0       2   4   .500    5   2   7   0   0   4   1   1   10  -5
Trevor Ariza    24:35   3   8   .375    2   4   .500    1   2   .500    1   2   3   4   3   2   0   0   9   -9
Bradley Beal    21:33   2   8   .250    2   4   .500    2   2   1.000   0   3   3   3   1   0   2   1   8   -16
Trevor Booker   16:45   2   9   .222    0   1   .000    0   0       1   0   1   1   1   1   4   4   4   -15
'''
    div_id = 'div_'+away_team+'_basic'
    table = soup_data.find('div', {'id':div_id}).find('tbody')
    tbl_rows = [r for r in table.find_all('tr')]
    # starting guards
    away_team_dict['Starting_G_MP'] = 10.0 ** (-9)
    away_team_dict['Starting_G_FG'] = 10.0 ** (-9) 
    away_team_dict['Starting_G_FGA'] = 10.0 ** (-9)    
    away_team_dict['Starting_G_3P'] = 10.0 ** (-9) 
    away_team_dict['Starting_G_3PA'] = 10.0 ** (-9)    
    away_team_dict['Starting_G_FT'] = 10.0 ** (-9) 
    away_team_dict['Starting_G_FTA'] = 10.0 ** (-9)    
    away_team_dict['Starting_G_ORB'] = 10.0 ** (-9)    
    away_team_dict['Starting_G_DRB'] = 10.0 ** (-9)    
    away_team_dict['Starting_G_TRB'] = 10.0 ** (-9)    
    away_team_dict['Starting_G_AST'] = 10.0 ** (-9)    
    away_team_dict['Starting_G_STL'] = 10.0 ** (-9)    
    away_team_dict['Starting_G_BLK'] = 10.0 ** (-9)    
    away_team_dict['Starting_G_TOV'] = 10.0 ** (-9)    
    away_team_dict['Starting_G_PF'] = 10.0 ** (-9) 
    away_team_dict['Starting_G_PTS'] = 10.0 ** (-9)    
    away_team_dict['Starting_G_ORB_per'] = 10.0 ** (-9)
    away_team_dict['Starting_G_DRB_per'] = 10.0 ** (-9)
    away_team_dict['Starting_G_TRB_per'] = 10.0 ** (-9)
    away_team_dict['Starting_G_AST_per'] = 10.0 ** (-9)
    away_team_dict['Starting_G_STL_per'] = 10.0 ** (-9)
    away_team_dict['Starting_G_BLK_per'] = 10.0 ** (-9)
    away_team_dict['Starting_G_USG_per'] = 10.0 ** (-9)
    # starting forwards
    away_team_dict['Starting_F_MP'] = 10.0 ** (-9) 
    away_team_dict['Starting_F_FG'] = 10.0 ** (-9) 
    away_team_dict['Starting_F_FGA'] = 10.0 ** (-9)    
    away_team_dict['Starting_F_3P'] = 10.0 ** (-9) 
    away_team_dict['Starting_F_3PA'] = 10.0 ** (-9)    
    away_team_dict['Starting_F_FT'] = 10.0 ** (-9) 
    away_team_dict['Starting_F_FTA'] = 10.0 ** (-9)    
    away_team_dict['Starting_F_ORB'] = 10.0 ** (-9)    
    away_team_dict['Starting_F_DRB'] = 10.0 ** (-9)    
    away_team_dict['Starting_F_TRB'] = 10.0 ** (-9)    
    away_team_dict['Starting_F_AST'] = 10.0 ** (-9)    
    away_team_dict['Starting_F_STL'] = 10.0 ** (-9)    
    away_team_dict['Starting_F_BLK'] = 10.0 ** (-9)    
    away_team_dict['Starting_F_TOV'] = 10.0 ** (-9)    
    away_team_dict['Starting_F_PF'] = 10.0 ** (-9) 
    away_team_dict['Starting_F_PTS'] = 10.0 ** (-9)    
    away_team_dict['Starting_F_ORB_per'] = 10.0 ** (-9)
    away_team_dict['Starting_F_DRB_per'] = 10.0 ** (-9)
    away_team_dict['Starting_F_TRB_per'] = 10.0 ** (-9)
    away_team_dict['Starting_F_AST_per'] = 10.0 ** (-9)
    away_team_dict['Starting_F_STL_per'] = 10.0 ** (-9)
    away_team_dict['Starting_F_BLK_per'] = 10.0 ** (-9)
    away_team_dict['Starting_F_USG_per'] = 10.0 ** (-9)
    # starting center
    away_team_dict['Starting_C_MP'] = 10.0 ** (-9) 
    away_team_dict['Starting_C_FG'] = 10.0 ** (-9) 
    away_team_dict['Starting_C_FGA'] = 10.0 ** (-9)    
    away_team_dict['Starting_C_3P'] = 10.0 ** (-9) 
    away_team_dict['Starting_C_3PA'] = 10.0 ** (-9)    
    away_team_dict['Starting_C_FT'] = 10.0 ** (-9) 
    away_team_dict['Starting_C_FTA'] = 10.0 ** (-9)    
    away_team_dict['Starting_C_ORB'] = 10.0 ** (-9)    
    away_team_dict['Starting_C_DRB'] = 10.0 ** (-9)    
    away_team_dict['Starting_C_TRB'] = 10.0 ** (-9)    
    away_team_dict['Starting_C_AST'] = 10.0 ** (-9)    
    away_team_dict['Starting_C_STL'] = 10.0 ** (-9)    
    away_team_dict['Starting_C_BLK'] = 10.0 ** (-9)    
    away_team_dict['Starting_C_TOV'] = 10.0 ** (-9)    
    away_team_dict['Starting_C_PF'] = 10.0 ** (-9) 
    away_team_dict['Starting_C_PTS'] = 10.0 ** (-9)    
    away_team_dict['Starting_C_ORB_per'] = 10.0 ** (-9)
    away_team_dict['Starting_C_DRB_per'] = 10.0 ** (-9)
    away_team_dict['Starting_C_TRB_per'] = 10.0 ** (-9)
    away_team_dict['Starting_C_AST_per'] = 10.0 ** (-9)
    away_team_dict['Starting_C_STL_per'] = 10.0 ** (-9)
    away_team_dict['Starting_C_BLK_per'] = 10.0 ** (-9)
    away_team_dict['Starting_C_USG_per'] = 10.0 ** (-9)

    # starters
    for i in range(5):
        row = tbl_rows[i]
        cells = row.find_all('td')
        player_link = row.find('a', href=True)['href']
        player_bbr_id = re.search('(?<=/)[a-z0-9]+(?=\.html)', player_link).group()
        player_pos = get_player_pos(player_bbr_id)
        away_team_dict['Starting_'+player_pos+'_MP'] += format_to_float(cells[1].text)
        away_team_dict['Starting_'+player_pos+'_FG'] += format_to_float(cells[2].text)
        away_team_dict['Starting_'+player_pos+'_FGA'] += format_to_float(cells[3].text)
        away_team_dict['Starting_'+player_pos+'_3P'] += format_to_float(cells[5].text)
        away_team_dict['Starting_'+player_pos+'_3PA'] += format_to_float(cells[6].text)
        away_team_dict['Starting_'+player_pos+'_FT'] += format_to_float(cells[8].text)
        away_team_dict['Starting_'+player_pos+'_FTA'] += format_to_float(cells[9].text)
        away_team_dict['Starting_'+player_pos+'_ORB'] += format_to_float(cells[11].text)
        away_team_dict['Starting_'+player_pos+'_DRB'] += format_to_float(cells[12].text)
        away_team_dict['Starting_'+player_pos+'_TRB'] += format_to_float(cells[13].text)
        away_team_dict['Starting_'+player_pos+'_AST'] += format_to_float(cells[14].text)
        away_team_dict['Starting_'+player_pos+'_STL'] += format_to_float(cells[15].text)
        away_team_dict['Starting_'+player_pos+'_BLK'] += format_to_float(cells[16].text)
        away_team_dict['Starting_'+player_pos+'_TOV'] += format_to_float(cells[17].text)
        away_team_dict['Starting_'+player_pos+'_PF'] += format_to_float(cells[18].text)
        away_team_dict['Starting_'+player_pos+'_PTS'] += format_to_float(cells[19].text)

    # ----------------------------------
    # box scores for reserves
    # ----------------------------------
    '''
Reserves    MP  FG  FGA FG% 3P  3PA 3P% FT  FTA FT% ORB DRB TRB AST STL BLK TOV PF  PTS +/-
Jordan Crawford 28:42   4   13  .308    0   6   .000    3   4   .750    1   2   3   5   1   1   1   1   11  0
Martell Webster 23:25   4   6   .667    1   3   .333    0   0       0   3   3   1   2   0   0   1   9   -1
Jan Vesely  21:14   3   4   .750    0   0       1   4   .250    3   1   4   1   0   1   1   3   7   -2
Chris Singleton 17:11   2   7   .286    0   1   .000    0   0       2   2   4   2   2   0   1   2   4   +1
Jannero Pargo   16:21   2   6   .333    1   4   .250    2   2   1.000   0   1   1   3   0   0   1   3   7   +7
Earl Barron 16:15   4   6   .667    0   0       0   1   .000    4   4   8   0   1   1   0   2   8   +1
    '''
    div_id = 'div_'+away_team+'_basic'
    table = soup_data.find('div', {'id':div_id}).find('tbody')
    tbl_rows = [r for r in table.find_all('tr')][6:]
    # reserved guards
    away_team_dict['Reserve_G_MP'] = 10.0 ** (-9)
    away_team_dict['Reserve_G_FG'] = 10.0 ** (-9) 
    away_team_dict['Reserve_G_FGA'] = 10.0 ** (-9)    
    away_team_dict['Reserve_G_3P'] = 10.0 ** (-9) 
    away_team_dict['Reserve_G_3PA'] = 10.0 ** (-9)    
    away_team_dict['Reserve_G_FT'] = 10.0 ** (-9) 
    away_team_dict['Reserve_G_FTA'] = 10.0 ** (-9)    
    away_team_dict['Reserve_G_ORB'] = 10.0 ** (-9)    
    away_team_dict['Reserve_G_DRB'] = 10.0 ** (-9)    
    away_team_dict['Reserve_G_TRB'] = 10.0 ** (-9)    
    away_team_dict['Reserve_G_AST'] = 10.0 ** (-9)    
    away_team_dict['Reserve_G_STL'] = 10.0 ** (-9)    
    away_team_dict['Reserve_G_BLK'] = 10.0 ** (-9)    
    away_team_dict['Reserve_G_TOV'] = 10.0 ** (-9)    
    away_team_dict['Reserve_G_PF'] = 10.0 ** (-9) 
    away_team_dict['Reserve_G_PTS'] = 10.0 ** (-9)    
    away_team_dict['Reserve_G_ORB_per'] = 10.0 ** (-9)
    away_team_dict['Reserve_G_DRB_per'] = 10.0 ** (-9)
    away_team_dict['Reserve_G_TRB_per'] = 10.0 ** (-9)
    away_team_dict['Reserve_G_AST_per'] = 10.0 ** (-9)
    away_team_dict['Reserve_G_STL_per'] = 10.0 ** (-9)
    away_team_dict['Reserve_G_BLK_per'] = 10.0 ** (-9)
    away_team_dict['Reserve_G_USG_per'] = 10.0 ** (-9)
    # reserved forwards
    away_team_dict['Reserve_F_MP'] = 10.0 ** (-9) 
    away_team_dict['Reserve_F_FG'] = 10.0 ** (-9) 
    away_team_dict['Reserve_F_FGA'] = 10.0 ** (-9)    
    away_team_dict['Reserve_F_3P'] = 10.0 ** (-9) 
    away_team_dict['Reserve_F_3PA'] = 10.0 ** (-9)    
    away_team_dict['Reserve_F_FT'] = 10.0 ** (-9) 
    away_team_dict['Reserve_F_FTA'] = 10.0 ** (-9)    
    away_team_dict['Reserve_F_ORB'] = 10.0 ** (-9)    
    away_team_dict['Reserve_F_DRB'] = 10.0 ** (-9)    
    away_team_dict['Reserve_F_TRB'] = 10.0 ** (-9)    
    away_team_dict['Reserve_F_AST'] = 10.0 ** (-9)    
    away_team_dict['Reserve_F_STL'] = 10.0 ** (-9)    
    away_team_dict['Reserve_F_BLK'] = 10.0 ** (-9)    
    away_team_dict['Reserve_F_TOV'] = 10.0 ** (-9)    
    away_team_dict['Reserve_F_PF'] = 10.0 ** (-9) 
    away_team_dict['Reserve_F_PTS'] = 10.0 ** (-9)    
    away_team_dict['Reserve_F_ORB_per'] = 10.0 ** (-9)
    away_team_dict['Reserve_F_DRB_per'] = 10.0 ** (-9)
    away_team_dict['Reserve_F_TRB_per'] = 10.0 ** (-9)
    away_team_dict['Reserve_F_AST_per'] = 10.0 ** (-9)
    away_team_dict['Reserve_F_STL_per'] = 10.0 ** (-9)
    away_team_dict['Reserve_F_BLK_per'] = 10.0 ** (-9)
    away_team_dict['Reserve_F_USG_per'] = 10.0 ** (-9)
    # reserved center
    away_team_dict['Reserve_C_MP'] = 10.0 ** (-9) 
    away_team_dict['Reserve_C_FG'] = 10.0 ** (-9) 
    away_team_dict['Reserve_C_FGA'] = 10.0 ** (-9)    
    away_team_dict['Reserve_C_3P'] = 10.0 ** (-9) 
    away_team_dict['Reserve_C_3PA'] = 10.0 ** (-9)    
    away_team_dict['Reserve_C_FT'] = 10.0 ** (-9) 
    away_team_dict['Reserve_C_FTA'] = 10.0 ** (-9)    
    away_team_dict['Reserve_C_ORB'] = 10.0 ** (-9)    
    away_team_dict['Reserve_C_DRB'] = 10.0 ** (-9)    
    away_team_dict['Reserve_C_TRB'] = 10.0 ** (-9)    
    away_team_dict['Reserve_C_AST'] = 10.0 ** (-9)    
    away_team_dict['Reserve_C_STL'] = 10.0 ** (-9)    
    away_team_dict['Reserve_C_BLK'] = 10.0 ** (-9)    
    away_team_dict['Reserve_C_TOV'] = 10.0 ** (-9)    
    away_team_dict['Reserve_C_PF'] = 10.0 ** (-9) 
    away_team_dict['Reserve_C_PTS'] = 10.0 ** (-9)    
    away_team_dict['Reserve_C_ORB_per'] = 10.0 ** (-9)
    away_team_dict['Reserve_C_DRB_per'] = 10.0 ** (-9)
    away_team_dict['Reserve_C_TRB_per'] = 10.0 ** (-9)
    away_team_dict['Reserve_C_AST_per'] = 10.0 ** (-9)
    away_team_dict['Reserve_C_STL_per'] = 10.0 ** (-9)
    away_team_dict['Reserve_C_BLK_per'] = 10.0 ** (-9)
    away_team_dict['Reserve_C_USG_per'] = 10.0 ** (-9)

    # reserves
    for i in range(len(tbl_rows)):
        row = tbl_rows[i]
        cells = row.find_all('td')
        player_link = row.find('a', href=True)['href']
        player_bbr_id = re.search('(?<=/)[a-z0-9]+(?=\.html)', player_link).group()
        player_pos = get_player_pos(player_bbr_id)
        away_team_dict['Reserve_'+player_pos+'_MP'] += format_to_float(cells[1].text)
        away_team_dict['Reserve_'+player_pos+'_FG'] += format_to_float(cells[2].text)
        away_team_dict['Reserve_'+player_pos+'_FGA'] += format_to_float(cells[3].text)
        away_team_dict['Reserve_'+player_pos+'_3P'] += format_to_float(cells[5].text)
        away_team_dict['Reserve_'+player_pos+'_3PA'] += format_to_float(cells[6].text)
        away_team_dict['Reserve_'+player_pos+'_FT'] += format_to_float(cells[8].text)
        away_team_dict['Reserve_'+player_pos+'_FTA'] += format_to_float(cells[9].text)
        away_team_dict['Reserve_'+player_pos+'_ORB'] += format_to_float(cells[11].text)
        away_team_dict['Reserve_'+player_pos+'_DRB'] += format_to_float(cells[12].text)
        away_team_dict['Reserve_'+player_pos+'_TRB'] += format_to_float(cells[13].text)
        away_team_dict['Reserve_'+player_pos+'_AST'] += format_to_float(cells[14].text)
        away_team_dict['Reserve_'+player_pos+'_STL'] += format_to_float(cells[15].text)
        away_team_dict['Reserve_'+player_pos+'_BLK'] += format_to_float(cells[16].text)
        away_team_dict['Reserve_'+player_pos+'_TOV'] += format_to_float(cells[17].text)
        away_team_dict['Reserve_'+player_pos+'_PF'] += format_to_float(cells[18].text)
        away_team_dict['Reserve_'+player_pos+'_PTS'] += format_to_float(cells[19].text)

    # -------------------------------------------
    # advanced stats for starting players
    # -------------------------------------------
    div_id = 'div_'+away_team+'_advanced'
    table = soup_data.find('div', {'id':div_id}).find('tbody')
    tbl_rows = [r for r in table.find_all('tr')]
    '''
Starters    MP  TS% eFG%    ORB%    DRB%    TRB%    AST%    STL%    BLK%    TOV%    USG%    ORtg    DRtg
A.J. Price  29:24   .260    .231    3.0 4.2 3.5 34.1    0.0 0.0 6.9 21.3    78  118
Emeka Okafor    24:35   .425    .400    18.1    10.0    14.7    0.0 0.0 13.2    7.8 22.5    95  110
Trevor Ariza    24:35   .507    .500    3.6 10.0    6.3 29.9    6.7 6.6 0.0 15.6    125 98
Bradley Beal    21:33   .450    .375    0.0 17.1    7.2 24.3    2.5 0.0 18.4    21.9    89  106
Trevor Booker   16:45   .222    .222    5.3 0.0 3.1 10.9    3.3 4.9 30.8    33.6    39  110
    '''
    # starters
    for i in range(5):
        row = tbl_rows[i]
        cells = row.find_all('td')
        player_link = row.find('a', href=True)['href']
        player_bbr_id = re.search('(?<=/)[a-z0-9]+(?=\.html)', player_link).group()
        player_pos = get_player_pos(player_bbr_id)
        away_team_dict['Starting_'+player_pos+'_ORB_per'] += format_to_float(cells[4].text)
        away_team_dict['Starting_'+player_pos+'_DRB_per'] += format_to_float(cells[5].text)
        away_team_dict['Starting_'+player_pos+'_TRB_per'] += format_to_float(cells[6].text)
        away_team_dict['Starting_'+player_pos+'_AST_per'] += format_to_float(cells[7].text)
        away_team_dict['Starting_'+player_pos+'_STL_per'] += format_to_float(cells[8].text)
        away_team_dict['Starting_'+player_pos+'_BLK_per'] += format_to_float(cells[9].text)
        away_team_dict['Starting_'+player_pos+'_USG_per'] += format_to_float(cells[11].text)

    # -------------------------------------------
    # advanced stats for reserved players
    # -------------------------------------------
    div_id = 'div_'+away_team+'_advanced'
    table = soup_data.find('div', {'id':div_id}).find('tbody')
    tbl_rows = [r for r in table.find_all('tr')][6:]
    '''
Reserves    MP  TS% eFG%    ORB%    DRB%    TRB%    AST%    STL%    BLK%    TOV%    USG%    ORtg    DRtg
Jordan Crawford 28:42   .373    .308    3.1 8.6 5.4 33.0    1.9 2.8 6.3 23.8    93  110
Martell Webster 23:25   .750    .750    0.0 15.8    6.6 8.6 4.7 0.0 0.0 11.1    149 102
Jan Vesely  21:14   .608    .750    12.6    5.8 9.7 9.0 0.0 3.8 14.8    13.8    107 115
Chris Singleton 17:11   .286    .286    10.3    14.3    12.0    21.2    6.4 0.0 12.5    20.2    74  98
Jannero Pargo   16:21   .509    .417    0.0 7.5 3.2 33.7    0.0 0.0 12.7    20.9    108 115
Earl Barron 16:15   .621    .667    21.9    30.3    25.4    0.0 3.4 5.0 0.0 17.2    134 95
    '''
    # reserved players
    for i in range(len(tbl_rows)):
        row = tbl_rows[i]
        cells = row.find_all('td')
        player_link = row.find('a', href=True)['href']
        player_bbr_id = re.search('(?<=/)[a-z0-9]+(?=\.html)', player_link).group()
        player_pos = get_player_pos(player_bbr_id)
        away_team_dict['Reserve_'+player_pos+'_ORB_per'] += format_to_float(cells[4].text)
        away_team_dict['Reserve_'+player_pos+'_DRB_per'] += format_to_float(cells[5].text)
        away_team_dict['Reserve_'+player_pos+'_TRB_per'] += format_to_float(cells[6].text)
        away_team_dict['Reserve_'+player_pos+'_AST_per'] += format_to_float(cells[7].text)
        away_team_dict['Reserve_'+player_pos+'_STL_per'] += format_to_float(cells[8].text)
        away_team_dict['Reserve_'+player_pos+'_BLK_per'] += format_to_float(cells[9].text)
        away_team_dict['Reserve_'+player_pos+'_USG_per'] += format_to_float(cells[11].text)

    # -------------------------------------------
    # team total
    # -------------------------------------------
    div_id = 'div_'+away_team+'_advanced'
    table = soup_data.find('div', {'id':div_id}).find('tfoot')
    away_team_dict['team_ORtg'] = format_to_float([r.text for r in table.find_all('td')][12])
    away_team_dict['team_DRtg'] = format_to_float([r.text for r in table.find_all('td')][13])
        

    # -----------------------
    # calculate starters stats
    # -----------------------
    away_team_dict['starters_FG'] = 10.0 ** (-9) 
    away_team_dict['starters_FGA'] = 10.0 ** (-9)    
    away_team_dict['starters_3P'] = 10.0 ** (-9) 
    away_team_dict['starters_3PA'] = 10.0 ** (-9)    
    away_team_dict['starters_FT'] = 10.0 ** (-9) 
    away_team_dict['starters_FTA'] = 10.0 ** (-9)    
    away_team_dict['starters_ORB'] = 10.0 ** (-9)    
    away_team_dict['starters_DRB'] = 10.0 ** (-9)    
    away_team_dict['starters_TRB'] = 10.0 ** (-9)    
    away_team_dict['starters_AST'] = 10.0 ** (-9)    
    away_team_dict['starters_STL'] = 10.0 ** (-9)    
    away_team_dict['starters_BLK'] = 10.0 ** (-9)    
    away_team_dict['starters_TOV'] = 10.0 ** (-9)    
    away_team_dict['starters_PF'] = 10.0 ** (-9) 
    away_team_dict['starters_PTS'] = 10.0 ** (-9)    
    away_team_dict['starters_ORB_per'] = 10.0 ** (-9)
    away_team_dict['starters_DRB_per'] = 10.0 ** (-9)
    away_team_dict['starters_TRB_per'] = 10.0 ** (-9)
    away_team_dict['starters_AST_per'] = 10.0 ** (-9)
    away_team_dict['starters_STL_per'] = 10.0 ** (-9)
    away_team_dict['starters_BLK_per'] = 10.0 ** (-9)
    away_team_dict['starters_USG_per'] = 10.0 ** (-9)

    for pos in {'G', 'F', 'C'}:
        away_team_dict['starters_FG'] += away_team_dict['Starting_'+pos+'_FG']
        away_team_dict['starters_FGA'] += away_team_dict['Starting_'+pos+'_FGA']
        away_team_dict['starters_3P'] += away_team_dict['Starting_'+pos+'_3P']
        away_team_dict['starters_3PA'] += away_team_dict['Starting_'+pos+'_3PA']
        away_team_dict['starters_FT'] += away_team_dict['Starting_'+pos+'_FT']
        away_team_dict['starters_FTA'] += away_team_dict['Starting_'+pos+'_FTA']
        away_team_dict['starters_ORB'] += away_team_dict['Starting_'+pos+'_ORB']
        away_team_dict['starters_DRB'] += away_team_dict['Starting_'+pos+'_DRB']
        away_team_dict['starters_TRB'] += away_team_dict['Starting_'+pos+'_TRB']
        away_team_dict['starters_AST'] += away_team_dict['Starting_'+pos+'_AST']
        away_team_dict['starters_STL'] += away_team_dict['Starting_'+pos+'_STL']
        away_team_dict['starters_BLK'] += away_team_dict['Starting_'+pos+'_BLK']
        away_team_dict['starters_TOV'] += away_team_dict['Starting_'+pos+'_TOV']
        away_team_dict['starters_PF'] += away_team_dict['Starting_'+pos+'_PF']
        away_team_dict['starters_PTS'] += away_team_dict['Starting_'+pos+'_PTS']
        away_team_dict['starters_ORB_per'] += away_team_dict['Starting_'+pos+'_ORB_per']
        away_team_dict['starters_DRB_per'] += away_team_dict['Starting_'+pos+'_DRB_per']
        away_team_dict['starters_TRB_per'] += away_team_dict['Starting_'+pos+'_TRB_per']
        away_team_dict['starters_AST_per'] += away_team_dict['Starting_'+pos+'_AST_per']
        away_team_dict['starters_STL_per'] += away_team_dict['Starting_'+pos+'_STL_per']
        away_team_dict['starters_BLK_per'] += away_team_dict['Starting_'+pos+'_BLK_per']
        away_team_dict['starters_USG_per'] += away_team_dict['Starting_'+pos+'_USG_per']

    # -----------------------
    # calculate reserves stats
    # -----------------------
    away_team_dict['reserves_FG'] = 10.0 ** (-9) 
    away_team_dict['reserves_FGA'] = 10.0 ** (-9)    
    away_team_dict['reserves_3P'] = 10.0 ** (-9) 
    away_team_dict['reserves_3PA'] = 10.0 ** (-9)    
    away_team_dict['reserves_FT'] = 10.0 ** (-9) 
    away_team_dict['reserves_FTA'] = 10.0 ** (-9)    
    away_team_dict['reserves_ORB'] = 10.0 ** (-9)    
    away_team_dict['reserves_DRB'] = 10.0 ** (-9)    
    away_team_dict['reserves_TRB'] = 10.0 ** (-9)    
    away_team_dict['reserves_AST'] = 10.0 ** (-9)    
    away_team_dict['reserves_STL'] = 10.0 ** (-9)    
    away_team_dict['reserves_BLK'] = 10.0 ** (-9)    
    away_team_dict['reserves_TOV'] = 10.0 ** (-9)    
    away_team_dict['reserves_PF'] = 10.0 ** (-9) 
    away_team_dict['reserves_PTS'] = 10.0 ** (-9)    
    away_team_dict['reserves_ORB_per'] = 10.0 ** (-9)
    away_team_dict['reserves_DRB_per'] = 10.0 ** (-9)
    away_team_dict['reserves_TRB_per'] = 10.0 ** (-9)
    away_team_dict['reserves_AST_per'] = 10.0 ** (-9)
    away_team_dict['reserves_STL_per'] = 10.0 ** (-9)
    away_team_dict['reserves_BLK_per'] = 10.0 ** (-9)
    away_team_dict['reserves_USG_per'] = 10.0 ** (-9)

    for pos in {'G', 'F', 'C'}:
        away_team_dict['reserves_FG'] += away_team_dict['Reserve_'+pos+'_FG']
        away_team_dict['reserves_FGA'] += away_team_dict['Reserve_'+pos+'_FGA']
        away_team_dict['reserves_3P'] += away_team_dict['Reserve_'+pos+'_3P']
        away_team_dict['reserves_3PA'] += away_team_dict['Reserve_'+pos+'_3PA']
        away_team_dict['reserves_FT'] += away_team_dict['Reserve_'+pos+'_FT']
        away_team_dict['reserves_FTA'] += away_team_dict['Reserve_'+pos+'_FTA']
        away_team_dict['reserves_ORB'] += away_team_dict['Reserve_'+pos+'_ORB']
        away_team_dict['reserves_DRB'] += away_team_dict['Reserve_'+pos+'_DRB']
        away_team_dict['reserves_TRB'] += away_team_dict['Reserve_'+pos+'_TRB']
        away_team_dict['reserves_AST'] += away_team_dict['Reserve_'+pos+'_AST']
        away_team_dict['reserves_STL'] += away_team_dict['Reserve_'+pos+'_STL']
        away_team_dict['reserves_BLK'] += away_team_dict['Reserve_'+pos+'_BLK']
        away_team_dict['reserves_TOV'] += away_team_dict['Reserve_'+pos+'_TOV']
        away_team_dict['reserves_PF'] += away_team_dict['Reserve_'+pos+'_PF']
        away_team_dict['reserves_PTS'] += away_team_dict['Reserve_'+pos+'_PTS']
        away_team_dict['reserves_ORB_per'] += away_team_dict['Reserve_'+pos+'_ORB_per']
        away_team_dict['reserves_DRB_per'] += away_team_dict['Reserve_'+pos+'_DRB_per']
        away_team_dict['reserves_TRB_per'] += away_team_dict['Reserve_'+pos+'_TRB_per']
        away_team_dict['reserves_AST_per'] += away_team_dict['Reserve_'+pos+'_AST_per']
        away_team_dict['reserves_STL_per'] += away_team_dict['Reserve_'+pos+'_STL_per']
        away_team_dict['reserves_BLK_per'] += away_team_dict['Reserve_'+pos+'_BLK_per']
        away_team_dict['reserves_USG_per'] += away_team_dict['Reserve_'+pos+'_USG_per']
        
    # -----------------------
    # calculate team stats
    # -----------------------
    away_team_dict['team_FG'] = 10.0 ** (-9) 
    away_team_dict['team_FGA'] = 10.0 ** (-9)    
    away_team_dict['team_3P'] = 10.0 ** (-9) 
    away_team_dict['team_3PA'] = 10.0 ** (-9)    
    away_team_dict['team_FT'] = 10.0 ** (-9) 
    away_team_dict['team_FTA'] = 10.0 ** (-9)    
    away_team_dict['team_ORB'] = 10.0 ** (-9)    
    away_team_dict['team_DRB'] = 10.0 ** (-9)    
    away_team_dict['team_TRB'] = 10.0 ** (-9)    
    away_team_dict['team_AST'] = 10.0 ** (-9)    
    away_team_dict['team_STL'] = 10.0 ** (-9)    
    away_team_dict['team_BLK'] = 10.0 ** (-9)    
    away_team_dict['team_TOV'] = 10.0 ** (-9)    
    away_team_dict['team_PF'] = 10.0 ** (-9) 
    away_team_dict['team_PTS'] = 10.0 ** (-9)    
    away_team_dict['team_ORB_per'] = 10.0 ** (-9)
    away_team_dict['team_DRB_per'] = 10.0 ** (-9)
    away_team_dict['team_TRB_per'] = 10.0 ** (-9)
    away_team_dict['team_AST_per'] = 10.0 ** (-9)
    away_team_dict['team_STL_per'] = 10.0 ** (-9)
    away_team_dict['team_BLK_per'] = 10.0 ** (-9)
    away_team_dict['team_USG_per'] = 10.0 ** (-9)

    for pos in {'G', 'F', 'C'}:
        away_team_dict['team_FG'] += away_team_dict['Starting_'+pos+'_FG']
        away_team_dict['team_FG'] += away_team_dict['Reserve_'+pos+'_FG']
        away_team_dict['team_FGA'] += away_team_dict['Starting_'+pos+'_FGA']
        away_team_dict['team_FGA'] += away_team_dict['Reserve_'+pos+'_FGA']
        away_team_dict['team_3P'] += away_team_dict['Starting_'+pos+'_3P']
        away_team_dict['team_3P'] += away_team_dict['Reserve_'+pos+'_3P']
        away_team_dict['team_3PA'] += away_team_dict['Starting_'+pos+'_3PA']
        away_team_dict['team_3PA'] += away_team_dict['Reserve_'+pos+'_3PA']
        away_team_dict['team_FT'] += away_team_dict['Starting_'+pos+'_FT']
        away_team_dict['team_FT'] += away_team_dict['Reserve_'+pos+'_FT']
        away_team_dict['team_FTA'] += away_team_dict['Starting_'+pos+'_FTA']
        away_team_dict['team_FTA'] += away_team_dict['Reserve_'+pos+'_FTA']
        away_team_dict['team_ORB'] += away_team_dict['Starting_'+pos+'_ORB']
        away_team_dict['team_ORB'] += away_team_dict['Reserve_'+pos+'_ORB']
        away_team_dict['team_DRB'] += away_team_dict['Starting_'+pos+'_DRB']
        away_team_dict['team_DRB'] += away_team_dict['Reserve_'+pos+'_DRB']
        away_team_dict['team_TRB'] += away_team_dict['Starting_'+pos+'_TRB']
        away_team_dict['team_TRB'] += away_team_dict['Reserve_'+pos+'_TRB']
        away_team_dict['team_AST'] += away_team_dict['Starting_'+pos+'_AST']
        away_team_dict['team_AST'] += away_team_dict['Reserve_'+pos+'_AST']
        away_team_dict['team_STL'] += away_team_dict['Starting_'+pos+'_STL']
        away_team_dict['team_STL'] += away_team_dict['Reserve_'+pos+'_STL']
        away_team_dict['team_BLK'] += away_team_dict['Starting_'+pos+'_BLK']
        away_team_dict['team_BLK'] += away_team_dict['Reserve_'+pos+'_BLK']
        away_team_dict['team_TOV'] += away_team_dict['Starting_'+pos+'_TOV']
        away_team_dict['team_TOV'] += away_team_dict['Reserve_'+pos+'_TOV']
        away_team_dict['team_PF'] += away_team_dict['Starting_'+pos+'_PF']
        away_team_dict['team_PF'] += away_team_dict['Reserve_'+pos+'_PF']
        away_team_dict['team_PTS'] += away_team_dict['Starting_'+pos+'_PTS']
        away_team_dict['team_PTS'] += away_team_dict['Reserve_'+pos+'_PTS']
        away_team_dict['team_ORB_per'] += away_team_dict['Starting_'+pos+'_ORB_per']
        away_team_dict['team_ORB_per'] += away_team_dict['Reserve_'+pos+'_ORB_per']
        away_team_dict['team_DRB_per'] += away_team_dict['Starting_'+pos+'_DRB_per']
        away_team_dict['team_DRB_per'] += away_team_dict['Reserve_'+pos+'_DRB_per']
        away_team_dict['team_TRB_per'] += away_team_dict['Starting_'+pos+'_TRB_per']
        away_team_dict['team_TRB_per'] += away_team_dict['Reserve_'+pos+'_TRB_per']
        away_team_dict['team_AST_per'] += away_team_dict['Starting_'+pos+'_AST_per']
        away_team_dict['team_AST_per'] += away_team_dict['Reserve_'+pos+'_AST_per']
        away_team_dict['team_STL_per'] += away_team_dict['Starting_'+pos+'_STL_per']
        away_team_dict['team_STL_per'] += away_team_dict['Reserve_'+pos+'_STL_per']
        away_team_dict['team_BLK_per'] += away_team_dict['Starting_'+pos+'_BLK_per']
        away_team_dict['team_BLK_per'] += away_team_dict['Reserve_'+pos+'_BLK_per']
        away_team_dict['team_USG_per'] += away_team_dict['Starting_'+pos+'_USG_per']
        away_team_dict['team_USG_per'] += away_team_dict['Reserve_'+pos+'_USG_per']

    # ----------------------------------------------
    # calculate percentages
    # ----------------------------------------------
    for pos in {'G', 'F', 'C'}:
        away_team_dict['Starting_'+pos+'_FG_per'] = away_team_dict['Starting_'+pos+'_FG'] / away_team_dict['Starting_'+pos+'_FGA']
        away_team_dict['Starting_'+pos+'_3P_per'] = away_team_dict['Starting_'+pos+'_3P'] / away_team_dict['Starting_'+pos+'_3PA']
        away_team_dict['Starting_'+pos+'_FT_per'] = away_team_dict['Starting_'+pos+'_FT'] / away_team_dict['Starting_'+pos+'_FTA']
        away_team_dict['Reserve_'+pos+'_FG_per'] = away_team_dict['Reserve_'+pos+'_FG'] / away_team_dict['Reserve_'+pos+'_FGA']
        away_team_dict['Reserve_'+pos+'_3P_per'] = away_team_dict['Reserve_'+pos+'_3P'] / away_team_dict['Reserve_'+pos+'_3PA']
        away_team_dict['Reserve_'+pos+'_FT_per'] = away_team_dict['Reserve_'+pos+'_FT'] / away_team_dict['Reserve_'+pos+'_FTA']

    away_team_dict['starters_FG_per'] = away_team_dict['starters_FG'] / away_team_dict['starters_FGA']
    away_team_dict['starters_3P_per'] = away_team_dict['starters_3P'] / away_team_dict['starters_3PA']
    away_team_dict['starters_FT_per'] = away_team_dict['starters_FT'] / away_team_dict['starters_FTA']

    away_team_dict['reserves_FG_per'] = away_team_dict['reserves_FG'] / away_team_dict['reserves_FGA']
    away_team_dict['reserves_3P_per'] = away_team_dict['reserves_3P'] / away_team_dict['reserves_3PA']
    away_team_dict['reserves_FT_per'] = away_team_dict['reserves_FT'] / away_team_dict['reserves_FTA']

    away_team_dict['team_FG_per'] = away_team_dict['team_FG'] / away_team_dict['team_FGA']
    away_team_dict['team_3P_per'] = away_team_dict['team_3P'] / away_team_dict['team_3PA']
    away_team_dict['team_FT_per'] = away_team_dict['team_FT'] / away_team_dict['team_FTA']


    print '\n'
    # ======================================================================
    # home team entry
    # ======================================================================
    home_team_dict = {}
    home_team_dict['team'] = home_team
    home_team_dict['opp'] = away_team
    print '++++++++++++++'* 3
    print 'processing the home team entry'
    print '++++++++++++++'* 3
    game_id = date + '_' + home_team    
    print 'game id is : ', game_id
    print 'the team is : ', home_team
    home_team_dict['game_id'] = game_id

    # --scoring box--    
    '''
Scoring
    1   2   3   4   T
WAS 24  15  23  22  84
CLE 31  19  24  20  94
    '''
    table = soup_data.find('table', {'class':'nav_table stats_table'})
    table_rows = [row for row in table.find_all('td')]
    starting_index = [i for (i,x) in enumerate(table_rows) if re.search(home_team, x.text)][0]
    home_team_dict['scoring_1st'] = table_rows[starting_index+1].text
    home_team_dict['scoring_2nd'] = table_rows[starting_index+2].text
    home_team_dict['scoring_3rd'] = table_rows[starting_index+3].text
    home_team_dict['scoring_4th'] = table_rows[starting_index+4].text

    # --four factors--    
    '''
Four Factors    
Pace    eFG%    TOV%    ORB%    FT/FGA  ORtg
WAS 87.9    .400    10.8    33.3    .133    95.5
CLE 87.9    .500    18.4    46.2    .190    106.9
    '''
    table = soup_data.find('div', {'id':'div_four_factors'}).find('tbody')
    tbl_rows = [r for r in table.find_all('td')]
    idx = [i for (i,x) in enumerate(tbl_rows) if re.search(home_team, x.text)][0]
    home_team_dict['Pace'] = tbl_rows[idx+1].text
    home_team_dict['eFG_per'] = tbl_rows[idx+2].text
    home_team_dict['TOV_per'] = tbl_rows[idx+3].text
    home_team_dict['ORB_per'] = tbl_rows[idx+4].text
    home_team_dict['FT_FGA'] = tbl_rows[idx+5].text
    home_team_dict['ORtg'] = tbl_rows[idx+6].text
    
    # ---------------------------------------
    # starting players, basic box scores
    # ---------------------------------------
    '''
Starters    MP  FG  FGA FG% 3P  3PA 3P% FT  FTA FT% ORB DRB TRB AST STL BLK TOV PF  PTS +/-
Anderson Varejao    37:22   3   7   .429    0   0       3   3   1.000   12  11  23  9   0   2   1   4   9   +7
Kyrie Irving    34:34   11  20  .550    3   6   .500    4   5   .800    0   6   6   3   0   1   4   4   29  +23
Alonzo Gee  33:53   2   9   .222    0   2   .000    0   0       2   1   3   2   2   0   3   5   4   +14
Tristan Thompson    31:31   5   8   .625    0   0       2   4   .500    3   7   10  5   1   0   2   2   12  +20
Dion Waiters    28:14   6   14  .429    2   5   .400    3   4   .750    0   2   2   0   3   0   3   0   17  +13
'''
    div_id = 'div_'+home_team+'_basic'
    table = soup_data.find('div', {'id':div_id}).find('tbody')
    tbl_rows = [r for r in table.find_all('tr')]
    # starting guards
    home_team_dict['Starting_G_MP'] = 10.0 ** (-9)
    home_team_dict['Starting_G_FG'] = 10.0 ** (-9) 
    home_team_dict['Starting_G_FGA'] = 10.0 ** (-9)    
    home_team_dict['Starting_G_3P'] = 10.0 ** (-9) 
    home_team_dict['Starting_G_3PA'] = 10.0 ** (-9)    
    home_team_dict['Starting_G_FT'] = 10.0 ** (-9) 
    home_team_dict['Starting_G_FTA'] = 10.0 ** (-9)    
    home_team_dict['Starting_G_ORB'] = 10.0 ** (-9)    
    home_team_dict['Starting_G_DRB'] = 10.0 ** (-9)    
    home_team_dict['Starting_G_TRB'] = 10.0 ** (-9)    
    home_team_dict['Starting_G_AST'] = 10.0 ** (-9)    
    home_team_dict['Starting_G_STL'] = 10.0 ** (-9)    
    home_team_dict['Starting_G_BLK'] = 10.0 ** (-9)    
    home_team_dict['Starting_G_TOV'] = 10.0 ** (-9)    
    home_team_dict['Starting_G_PF'] = 10.0 ** (-9) 
    home_team_dict['Starting_G_PTS'] = 10.0 ** (-9)    
    home_team_dict['Starting_G_ORB_per'] = 10.0 ** (-9)
    home_team_dict['Starting_G_DRB_per'] = 10.0 ** (-9)
    home_team_dict['Starting_G_TRB_per'] = 10.0 ** (-9)
    home_team_dict['Starting_G_AST_per'] = 10.0 ** (-9)
    home_team_dict['Starting_G_STL_per'] = 10.0 ** (-9)
    home_team_dict['Starting_G_BLK_per'] = 10.0 ** (-9)
    home_team_dict['Starting_G_USG_per'] = 10.0 ** (-9)
    # starting forwards
    home_team_dict['Starting_F_MP'] = 10.0 ** (-9) 
    home_team_dict['Starting_F_FG'] = 10.0 ** (-9) 
    home_team_dict['Starting_F_FGA'] = 10.0 ** (-9)    
    home_team_dict['Starting_F_3P'] = 10.0 ** (-9) 
    home_team_dict['Starting_F_3PA'] = 10.0 ** (-9)    
    home_team_dict['Starting_F_FT'] = 10.0 ** (-9) 
    home_team_dict['Starting_F_FTA'] = 10.0 ** (-9)    
    home_team_dict['Starting_F_ORB'] = 10.0 ** (-9)    
    home_team_dict['Starting_F_DRB'] = 10.0 ** (-9)    
    home_team_dict['Starting_F_TRB'] = 10.0 ** (-9)    
    home_team_dict['Starting_F_AST'] = 10.0 ** (-9)    
    home_team_dict['Starting_F_STL'] = 10.0 ** (-9)    
    home_team_dict['Starting_F_BLK'] = 10.0 ** (-9)    
    home_team_dict['Starting_F_TOV'] = 10.0 ** (-9)    
    home_team_dict['Starting_F_PF'] = 10.0 ** (-9) 
    home_team_dict['Starting_F_PTS'] = 10.0 ** (-9)    
    home_team_dict['Starting_F_ORB_per'] = 10.0 ** (-9)
    home_team_dict['Starting_F_DRB_per'] = 10.0 ** (-9)
    home_team_dict['Starting_F_TRB_per'] = 10.0 ** (-9)
    home_team_dict['Starting_F_AST_per'] = 10.0 ** (-9)
    home_team_dict['Starting_F_STL_per'] = 10.0 ** (-9)
    home_team_dict['Starting_F_BLK_per'] = 10.0 ** (-9)
    home_team_dict['Starting_F_USG_per'] = 10.0 ** (-9)
    # starting center
    home_team_dict['Starting_C_MP'] = 10.0 ** (-9) 
    home_team_dict['Starting_C_FG'] = 10.0 ** (-9) 
    home_team_dict['Starting_C_FGA'] = 10.0 ** (-9)    
    home_team_dict['Starting_C_3P'] = 10.0 ** (-9) 
    home_team_dict['Starting_C_3PA'] = 10.0 ** (-9)    
    home_team_dict['Starting_C_FT'] = 10.0 ** (-9) 
    home_team_dict['Starting_C_FTA'] = 10.0 ** (-9)    
    home_team_dict['Starting_C_ORB'] = 10.0 ** (-9)    
    home_team_dict['Starting_C_DRB'] = 10.0 ** (-9)    
    home_team_dict['Starting_C_TRB'] = 10.0 ** (-9)    
    home_team_dict['Starting_C_AST'] = 10.0 ** (-9)    
    home_team_dict['Starting_C_STL'] = 10.0 ** (-9)    
    home_team_dict['Starting_C_BLK'] = 10.0 ** (-9)    
    home_team_dict['Starting_C_TOV'] = 10.0 ** (-9)    
    home_team_dict['Starting_C_PF'] = 10.0 ** (-9) 
    home_team_dict['Starting_C_PTS'] = 10.0 ** (-9)    
    home_team_dict['Starting_C_ORB_per'] = 10.0 ** (-9)
    home_team_dict['Starting_C_DRB_per'] = 10.0 ** (-9)
    home_team_dict['Starting_C_TRB_per'] = 10.0 ** (-9)
    home_team_dict['Starting_C_AST_per'] = 10.0 ** (-9)
    home_team_dict['Starting_C_STL_per'] = 10.0 ** (-9)
    home_team_dict['Starting_C_BLK_per'] = 10.0 ** (-9)
    home_team_dict['Starting_C_USG_per'] = 10.0 ** (-9)

    # starters
    for i in range(5):
        row = tbl_rows[i]
        cells = row.find_all('td')
        player_link = row.find('a', href=True)['href']
        player_bbr_id = re.search('(?<=/)[a-z0-9]+(?=\.html)', player_link).group()
        player_pos = get_player_pos(player_bbr_id)
        home_team_dict['Starting_'+player_pos+'_MP'] += format_to_float(cells[1].text)
        home_team_dict['Starting_'+player_pos+'_FG'] += format_to_float(cells[2].text)
        home_team_dict['Starting_'+player_pos+'_FGA'] += format_to_float(cells[3].text)
        home_team_dict['Starting_'+player_pos+'_3P'] += format_to_float(cells[5].text)
        home_team_dict['Starting_'+player_pos+'_3PA'] += format_to_float(cells[6].text)
        home_team_dict['Starting_'+player_pos+'_FT'] += format_to_float(cells[8].text)
        home_team_dict['Starting_'+player_pos+'_FTA'] += format_to_float(cells[9].text)
        home_team_dict['Starting_'+player_pos+'_ORB'] += format_to_float(cells[11].text)
        home_team_dict['Starting_'+player_pos+'_DRB'] += format_to_float(cells[12].text)
        home_team_dict['Starting_'+player_pos+'_TRB'] += format_to_float(cells[13].text)
        home_team_dict['Starting_'+player_pos+'_AST'] += format_to_float(cells[14].text)
        home_team_dict['Starting_'+player_pos+'_STL'] += format_to_float(cells[15].text)
        home_team_dict['Starting_'+player_pos+'_BLK'] += format_to_float(cells[16].text)
        home_team_dict['Starting_'+player_pos+'_TOV'] += format_to_float(cells[17].text)
        home_team_dict['Starting_'+player_pos+'_PF'] += format_to_float(cells[18].text)
        home_team_dict['Starting_'+player_pos+'_PTS'] += format_to_float(cells[19].text)

    # ----------------------------------
    # box scores for reserves
    # ----------------------------------
    '''
Reserves    MP  FG  FGA FG% 3P  3PA 3P% FT  FTA FT% ORB DRB TRB AST STL BLK TOV PF  PTS +/-
C.J. Miles  17:42   1   5   .200    0   1   .000    0   0       0   4   4   1   0   0   3   0   2   +2
Daniel Gibson   16:11   3   5   .600    2   4   .500    2   4   .500    1   2   3   1   0   1   0   2   10  -9
Tyler Zeller    14:53   2   4   .500    0   0       1   2   .500    0   2   2   0   1   1   0   2   5   +4
Donald Sloan    13:26   2   5   .400    0   1   .000    0   0       0   0   0   1   0   0   2   2   4   -13
Luke Walton 12:14   1   2   .500    0   1   .000    0   0       0   1   1   0   0   0   2   0   2   -11
    '''
    div_id = 'div_'+home_team+'_basic'
    table = soup_data.find('div', {'id':div_id}).find('tbody')
    tbl_rows = [r for r in table.find_all('tr')][6:]
    # reserved guards
    home_team_dict['Reserve_G_MP'] = 10.0 ** (-9)
    home_team_dict['Reserve_G_FG'] = 10.0 ** (-9) 
    home_team_dict['Reserve_G_FGA'] = 10.0 ** (-9)    
    home_team_dict['Reserve_G_3P'] = 10.0 ** (-9) 
    home_team_dict['Reserve_G_3PA'] = 10.0 ** (-9)    
    home_team_dict['Reserve_G_FT'] = 10.0 ** (-9) 
    home_team_dict['Reserve_G_FTA'] = 10.0 ** (-9)    
    home_team_dict['Reserve_G_ORB'] = 10.0 ** (-9)    
    home_team_dict['Reserve_G_DRB'] = 10.0 ** (-9)    
    home_team_dict['Reserve_G_TRB'] = 10.0 ** (-9)    
    home_team_dict['Reserve_G_AST'] = 10.0 ** (-9)    
    home_team_dict['Reserve_G_STL'] = 10.0 ** (-9)    
    home_team_dict['Reserve_G_BLK'] = 10.0 ** (-9)    
    home_team_dict['Reserve_G_TOV'] = 10.0 ** (-9)    
    home_team_dict['Reserve_G_PF'] = 10.0 ** (-9) 
    home_team_dict['Reserve_G_PTS'] = 10.0 ** (-9)    
    home_team_dict['Reserve_G_ORB_per'] = 10.0 ** (-9)
    home_team_dict['Reserve_G_DRB_per'] = 10.0 ** (-9)
    home_team_dict['Reserve_G_TRB_per'] = 10.0 ** (-9)
    home_team_dict['Reserve_G_AST_per'] = 10.0 ** (-9)
    home_team_dict['Reserve_G_STL_per'] = 10.0 ** (-9)
    home_team_dict['Reserve_G_BLK_per'] = 10.0 ** (-9)
    home_team_dict['Reserve_G_USG_per'] = 10.0 ** (-9)
    # reserved forwards
    home_team_dict['Reserve_F_MP'] = 10.0 ** (-9) 
    home_team_dict['Reserve_F_FG'] = 10.0 ** (-9) 
    home_team_dict['Reserve_F_FGA'] = 10.0 ** (-9)    
    home_team_dict['Reserve_F_3P'] = 10.0 ** (-9) 
    home_team_dict['Reserve_F_3PA'] = 10.0 ** (-9)    
    home_team_dict['Reserve_F_FT'] = 10.0 ** (-9) 
    home_team_dict['Reserve_F_FTA'] = 10.0 ** (-9)    
    home_team_dict['Reserve_F_ORB'] = 10.0 ** (-9)    
    home_team_dict['Reserve_F_DRB'] = 10.0 ** (-9)    
    home_team_dict['Reserve_F_TRB'] = 10.0 ** (-9)    
    home_team_dict['Reserve_F_AST'] = 10.0 ** (-9)    
    home_team_dict['Reserve_F_STL'] = 10.0 ** (-9)    
    home_team_dict['Reserve_F_BLK'] = 10.0 ** (-9)    
    home_team_dict['Reserve_F_TOV'] = 10.0 ** (-9)    
    home_team_dict['Reserve_F_PF'] = 10.0 ** (-9) 
    home_team_dict['Reserve_F_PTS'] = 10.0 ** (-9)    
    home_team_dict['Reserve_F_ORB_per'] = 10.0 ** (-9)
    home_team_dict['Reserve_F_DRB_per'] = 10.0 ** (-9)
    home_team_dict['Reserve_F_TRB_per'] = 10.0 ** (-9)
    home_team_dict['Reserve_F_AST_per'] = 10.0 ** (-9)
    home_team_dict['Reserve_F_STL_per'] = 10.0 ** (-9)
    home_team_dict['Reserve_F_BLK_per'] = 10.0 ** (-9)
    home_team_dict['Reserve_F_USG_per'] = 10.0 ** (-9)
    # reserved center
    home_team_dict['Reserve_C_MP'] = 10.0 ** (-9) 
    home_team_dict['Reserve_C_FG'] = 10.0 ** (-9) 
    home_team_dict['Reserve_C_FGA'] = 10.0 ** (-9)    
    home_team_dict['Reserve_C_3P'] = 10.0 ** (-9) 
    home_team_dict['Reserve_C_3PA'] = 10.0 ** (-9)    
    home_team_dict['Reserve_C_FT'] = 10.0 ** (-9) 
    home_team_dict['Reserve_C_FTA'] = 10.0 ** (-9)    
    home_team_dict['Reserve_C_ORB'] = 10.0 ** (-9)    
    home_team_dict['Reserve_C_DRB'] = 10.0 ** (-9)    
    home_team_dict['Reserve_C_TRB'] = 10.0 ** (-9)    
    home_team_dict['Reserve_C_AST'] = 10.0 ** (-9)    
    home_team_dict['Reserve_C_STL'] = 10.0 ** (-9)    
    home_team_dict['Reserve_C_BLK'] = 10.0 ** (-9)    
    home_team_dict['Reserve_C_TOV'] = 10.0 ** (-9)    
    home_team_dict['Reserve_C_PF'] = 10.0 ** (-9) 
    home_team_dict['Reserve_C_PTS'] = 10.0 ** (-9)    
    home_team_dict['Reserve_C_ORB_per'] = 10.0 ** (-9)
    home_team_dict['Reserve_C_DRB_per'] = 10.0 ** (-9)
    home_team_dict['Reserve_C_TRB_per'] = 10.0 ** (-9)
    home_team_dict['Reserve_C_AST_per'] = 10.0 ** (-9)
    home_team_dict['Reserve_C_STL_per'] = 10.0 ** (-9)
    home_team_dict['Reserve_C_BLK_per'] = 10.0 ** (-9)
    home_team_dict['Reserve_C_USG_per'] = 10.0 ** (-9)

    # reserves
    for i in range(len(tbl_rows)):
        row = tbl_rows[i]
        cells = row.find_all('td')
        player_link = row.find('a', href=True)['href']
        player_bbr_id = re.search('(?<=/)[a-z0-9]+(?=\.html)', player_link).group()
        player_pos = get_player_pos(player_bbr_id)
        home_team_dict['Reserve_'+player_pos+'_MP'] += format_to_float(cells[1].text)
        home_team_dict['Reserve_'+player_pos+'_FG'] += format_to_float(cells[2].text)
        home_team_dict['Reserve_'+player_pos+'_FGA'] += format_to_float(cells[3].text)
        home_team_dict['Reserve_'+player_pos+'_3P'] += format_to_float(cells[5].text)
        home_team_dict['Reserve_'+player_pos+'_3PA'] += format_to_float(cells[6].text)
        home_team_dict['Reserve_'+player_pos+'_FT'] += format_to_float(cells[8].text)
        home_team_dict['Reserve_'+player_pos+'_FTA'] += format_to_float(cells[9].text)
        home_team_dict['Reserve_'+player_pos+'_ORB'] += format_to_float(cells[11].text)
        home_team_dict['Reserve_'+player_pos+'_DRB'] += format_to_float(cells[12].text)
        home_team_dict['Reserve_'+player_pos+'_TRB'] += format_to_float(cells[13].text)
        home_team_dict['Reserve_'+player_pos+'_AST'] += format_to_float(cells[14].text)
        home_team_dict['Reserve_'+player_pos+'_STL'] += format_to_float(cells[15].text)
        home_team_dict['Reserve_'+player_pos+'_BLK'] += format_to_float(cells[16].text)
        home_team_dict['Reserve_'+player_pos+'_TOV'] += format_to_float(cells[17].text)
        home_team_dict['Reserve_'+player_pos+'_PF'] += format_to_float(cells[18].text)
        home_team_dict['Reserve_'+player_pos+'_PTS'] += format_to_float(cells[19].text)

    # -------------------------------------------
    # advanced stats for starting players
    # -------------------------------------------
    div_id = 'div_'+home_team+'_advanced'
    table = soup_data.find('div', {'id':div_id}).find('tbody')
    tbl_rows = [r for r in table.find_all('tr')]
    '''
Starters    MP  TS% eFG%    ORB%    DRB%    TRB%    AST%    STL%    BLK%    TOV%    USG%    ORtg    DRtg
Anderson Varejao    37:22   .541    .429    39.5    26.2    31.8    36.0    0.0 4.4 10.7    11.0    157 90
Kyrie Irving    34:34   .653    .625    0.0 15.4    9.0 20.1    0.0 2.4 15.3    33.5    122 97
Alonzo Gee  33:53   .222    .222    7.3 2.6 4.6 8.5 3.2 0.0 25.0    15.6    58  99
Tristan Thompson    31:31   .615    .625    11.7    19.7    16.4    26.8    1.7 0.0 17.0    16.5    125 92
Dion Waiters    28:14   .539    .500    0.0 6.3 3.7 0.0 5.8 0.0 16.0    29.3    102 92
    '''
    # starters
    for i in range(5):
        row = tbl_rows[i]
        cells = row.find_all('td')
        player_link = row.find('a', href=True)['href']
        player_bbr_id = re.search('(?<=/)[a-z0-9]+(?=\.html)', player_link).group()
        player_pos = get_player_pos(player_bbr_id)
        home_team_dict['Starting_'+player_pos+'_ORB_per'] += format_to_float(cells[4].text)
        home_team_dict['Starting_'+player_pos+'_DRB_per'] += format_to_float(cells[5].text)
        home_team_dict['Starting_'+player_pos+'_TRB_per'] += format_to_float(cells[6].text)
        home_team_dict['Starting_'+player_pos+'_AST_per'] += format_to_float(cells[7].text)
        home_team_dict['Starting_'+player_pos+'_STL_per'] += format_to_float(cells[8].text)
        home_team_dict['Starting_'+player_pos+'_BLK_per'] += format_to_float(cells[9].text)
        home_team_dict['Starting_'+player_pos+'_USG_per'] += format_to_float(cells[11].text)

    # -------------------------------------------
    # advanced stats for reserved players
    # -------------------------------------------
    div_id = 'div_'+home_team+'_advanced'
    table = soup_data.find('div', {'id':div_id}).find('tbody')
    tbl_rows = [r for r in table.find_all('tr')][6:]
    '''
Reserves    MP  TS% eFG%    ORB%    DRB%    TRB%    AST%    STL%    BLK%    TOV%    USG%    ORtg    DRtg
C.J. Miles  17:42   .200    .200    0.0 20.1    11.7    8.1 0.0 0.0 37.5    20.0    37  96
Daniel Gibson   16:11   .740    .800    7.6 11.0    9.6 10.9    0.0 5.1 0.0 18.4    164 99
Tyler Zeller    14:53   .512    .500    0.0 11.9    6.9 0.0 3.7 5.6 0.0 14.5    120 90
Donald Sloan    13:26   .400    .400    0.0 0.0 0.0 12.4    0.0 0.0 28.6    23.0    70  108
Luke Walton 12:14   .500    .500    0.0 7.3 4.2 0.0 0.0 0.0 50.0    14.4    47  104
Team Totals 240 .530    .500    46.2    66.7    58.1    61.1    8.0 8.5 18.4    100.0   106.9   95.5
    '''
    # reserved players
    for i in range(len(tbl_rows)):
        row = tbl_rows[i]
        cells = row.find_all('td')
        player_link = row.find('a', href=True)['href']
        player_bbr_id = re.search('(?<=/)[a-z0-9]+(?=\.html)', player_link).group()
        player_pos = get_player_pos(player_bbr_id)
        home_team_dict['Reserve_'+player_pos+'_ORB_per'] += format_to_float(cells[4].text)
        home_team_dict['Reserve_'+player_pos+'_DRB_per'] += format_to_float(cells[5].text)
        home_team_dict['Reserve_'+player_pos+'_TRB_per'] += format_to_float(cells[6].text)
        home_team_dict['Reserve_'+player_pos+'_AST_per'] += format_to_float(cells[7].text)
        home_team_dict['Reserve_'+player_pos+'_STL_per'] += format_to_float(cells[8].text)
        home_team_dict['Reserve_'+player_pos+'_BLK_per'] += format_to_float(cells[9].text)
        home_team_dict['Reserve_'+player_pos+'_USG_per'] += format_to_float(cells[11].text)


    # -------------------------------------------
    # team total
    # -------------------------------------------
    div_id = 'div_'+home_team+'_advanced'
    table = soup_data.find('div', {'id':div_id}).find('tfoot')
    home_team_dict['team_ORtg'] = format_to_float([r.text for r in table.find_all('td')][12])
    home_team_dict['team_DRtg'] = format_to_float([r.text for r in table.find_all('td')][13])

        
    # -----------------------
    # calculate starters stats
    # -----------------------
    home_team_dict['starters_FG'] = 10.0 ** (-9) 
    home_team_dict['starters_FGA'] = 10.0 ** (-9)    
    home_team_dict['starters_3P'] = 10.0 ** (-9) 
    home_team_dict['starters_3PA'] = 10.0 ** (-9)    
    home_team_dict['starters_FT'] = 10.0 ** (-9) 
    home_team_dict['starters_FTA'] = 10.0 ** (-9)    
    home_team_dict['starters_ORB'] = 10.0 ** (-9)    
    home_team_dict['starters_DRB'] = 10.0 ** (-9)    
    home_team_dict['starters_TRB'] = 10.0 ** (-9)    
    home_team_dict['starters_AST'] = 10.0 ** (-9)    
    home_team_dict['starters_STL'] = 10.0 ** (-9)    
    home_team_dict['starters_BLK'] = 10.0 ** (-9)    
    home_team_dict['starters_TOV'] = 10.0 ** (-9)    
    home_team_dict['starters_PF'] = 10.0 ** (-9) 
    home_team_dict['starters_PTS'] = 10.0 ** (-9)    
    home_team_dict['starters_ORB_per'] = 10.0 ** (-9)
    home_team_dict['starters_DRB_per'] = 10.0 ** (-9)
    home_team_dict['starters_TRB_per'] = 10.0 ** (-9)
    home_team_dict['starters_AST_per'] = 10.0 ** (-9)
    home_team_dict['starters_STL_per'] = 10.0 ** (-9)
    home_team_dict['starters_BLK_per'] = 10.0 ** (-9)
    home_team_dict['starters_USG_per'] = 10.0 ** (-9)

    for pos in {'G', 'F', 'C'}:
        home_team_dict['starters_FG'] += home_team_dict['Starting_'+pos+'_FG']
        home_team_dict['starters_FGA'] += home_team_dict['Starting_'+pos+'_FGA']
        home_team_dict['starters_3P'] += home_team_dict['Starting_'+pos+'_3P']
        home_team_dict['starters_3PA'] += home_team_dict['Starting_'+pos+'_3PA']
        home_team_dict['starters_FT'] += home_team_dict['Starting_'+pos+'_FT']
        home_team_dict['starters_FTA'] += home_team_dict['Starting_'+pos+'_FTA']
        home_team_dict['starters_ORB'] += home_team_dict['Starting_'+pos+'_ORB']
        home_team_dict['starters_DRB'] += home_team_dict['Starting_'+pos+'_DRB']
        home_team_dict['starters_TRB'] += home_team_dict['Starting_'+pos+'_TRB']
        home_team_dict['starters_AST'] += home_team_dict['Starting_'+pos+'_AST']
        home_team_dict['starters_STL'] += home_team_dict['Starting_'+pos+'_STL']
        home_team_dict['starters_BLK'] += home_team_dict['Starting_'+pos+'_BLK']
        home_team_dict['starters_TOV'] += home_team_dict['Starting_'+pos+'_TOV']
        home_team_dict['starters_PF'] += home_team_dict['Starting_'+pos+'_PF']
        home_team_dict['starters_PTS'] += home_team_dict['Starting_'+pos+'_PTS']
        home_team_dict['starters_ORB_per'] += home_team_dict['Starting_'+pos+'_ORB_per']
        home_team_dict['starters_DRB_per'] += home_team_dict['Starting_'+pos+'_DRB_per']
        home_team_dict['starters_TRB_per'] += home_team_dict['Starting_'+pos+'_TRB_per']
        home_team_dict['starters_AST_per'] += home_team_dict['Starting_'+pos+'_AST_per']
        home_team_dict['starters_STL_per'] += home_team_dict['Starting_'+pos+'_STL_per']
        home_team_dict['starters_BLK_per'] += home_team_dict['Starting_'+pos+'_BLK_per']
        home_team_dict['starters_USG_per'] += home_team_dict['Starting_'+pos+'_USG_per']

    # -----------------------
    # calculate reserves stats
    # -----------------------
    home_team_dict['reserves_FG'] = 10.0 ** (-9) 
    home_team_dict['reserves_FGA'] = 10.0 ** (-9)    
    home_team_dict['reserves_3P'] = 10.0 ** (-9) 
    home_team_dict['reserves_3PA'] = 10.0 ** (-9)    
    home_team_dict['reserves_FT'] = 10.0 ** (-9) 
    home_team_dict['reserves_FTA'] = 10.0 ** (-9)    
    home_team_dict['reserves_ORB'] = 10.0 ** (-9)    
    home_team_dict['reserves_DRB'] = 10.0 ** (-9)    
    home_team_dict['reserves_TRB'] = 10.0 ** (-9)    
    home_team_dict['reserves_AST'] = 10.0 ** (-9)    
    home_team_dict['reserves_STL'] = 10.0 ** (-9)    
    home_team_dict['reserves_BLK'] = 10.0 ** (-9)    
    home_team_dict['reserves_TOV'] = 10.0 ** (-9)    
    home_team_dict['reserves_PF'] = 10.0 ** (-9) 
    home_team_dict['reserves_PTS'] = 10.0 ** (-9)    
    home_team_dict['reserves_ORB_per'] = 10.0 ** (-9)
    home_team_dict['reserves_DRB_per'] = 10.0 ** (-9)
    home_team_dict['reserves_TRB_per'] = 10.0 ** (-9)
    home_team_dict['reserves_AST_per'] = 10.0 ** (-9)
    home_team_dict['reserves_STL_per'] = 10.0 ** (-9)
    home_team_dict['reserves_BLK_per'] = 10.0 ** (-9)
    home_team_dict['reserves_USG_per'] = 10.0 ** (-9)

    for pos in {'G', 'F', 'C'}:
        home_team_dict['reserves_FG'] += home_team_dict['Reserve_'+pos+'_FG']
        home_team_dict['reserves_FGA'] += home_team_dict['Reserve_'+pos+'_FGA']
        home_team_dict['reserves_3P'] += home_team_dict['Reserve_'+pos+'_3P']
        home_team_dict['reserves_3PA'] += home_team_dict['Reserve_'+pos+'_3PA']
        home_team_dict['reserves_FT'] += home_team_dict['Reserve_'+pos+'_FT']
        home_team_dict['reserves_FTA'] += home_team_dict['Reserve_'+pos+'_FTA']
        home_team_dict['reserves_ORB'] += home_team_dict['Reserve_'+pos+'_ORB']
        home_team_dict['reserves_DRB'] += home_team_dict['Reserve_'+pos+'_DRB']
        home_team_dict['reserves_TRB'] += home_team_dict['Reserve_'+pos+'_TRB']
        home_team_dict['reserves_AST'] += home_team_dict['Reserve_'+pos+'_AST']
        home_team_dict['reserves_STL'] += home_team_dict['Reserve_'+pos+'_STL']
        home_team_dict['reserves_BLK'] += home_team_dict['Reserve_'+pos+'_BLK']
        home_team_dict['reserves_TOV'] += home_team_dict['Reserve_'+pos+'_TOV']
        home_team_dict['reserves_PF'] += home_team_dict['Reserve_'+pos+'_PF']
        home_team_dict['reserves_PTS'] += home_team_dict['Reserve_'+pos+'_PTS']
        home_team_dict['reserves_ORB_per'] += home_team_dict['Reserve_'+pos+'_ORB_per']
        home_team_dict['reserves_DRB_per'] += home_team_dict['Reserve_'+pos+'_DRB_per']
        home_team_dict['reserves_TRB_per'] += home_team_dict['Reserve_'+pos+'_TRB_per']
        home_team_dict['reserves_AST_per'] += home_team_dict['Reserve_'+pos+'_AST_per']
        home_team_dict['reserves_STL_per'] += home_team_dict['Reserve_'+pos+'_STL_per']
        home_team_dict['reserves_BLK_per'] += home_team_dict['Reserve_'+pos+'_BLK_per']
        home_team_dict['reserves_USG_per'] += home_team_dict['Reserve_'+pos+'_USG_per']
        
    # -----------------------
    # calculate team stats
    # -----------------------
    home_team_dict['team_FG'] = 10.0 ** (-9) 
    home_team_dict['team_FGA'] = 10.0 ** (-9)    
    home_team_dict['team_3P'] = 10.0 ** (-9) 
    home_team_dict['team_3PA'] = 10.0 ** (-9)    
    home_team_dict['team_FT'] = 10.0 ** (-9) 
    home_team_dict['team_FTA'] = 10.0 ** (-9)    
    home_team_dict['team_ORB'] = 10.0 ** (-9)    
    home_team_dict['team_DRB'] = 10.0 ** (-9)    
    home_team_dict['team_TRB'] = 10.0 ** (-9)    
    home_team_dict['team_AST'] = 10.0 ** (-9)    
    home_team_dict['team_STL'] = 10.0 ** (-9)    
    home_team_dict['team_BLK'] = 10.0 ** (-9)    
    home_team_dict['team_TOV'] = 10.0 ** (-9)    
    home_team_dict['team_PF'] = 10.0 ** (-9) 
    home_team_dict['team_PTS'] = 10.0 ** (-9)    
    home_team_dict['team_ORB_per'] = 10.0 ** (-9)
    home_team_dict['team_DRB_per'] = 10.0 ** (-9)
    home_team_dict['team_TRB_per'] = 10.0 ** (-9)
    home_team_dict['team_AST_per'] = 10.0 ** (-9)
    home_team_dict['team_STL_per'] = 10.0 ** (-9)
    home_team_dict['team_BLK_per'] = 10.0 ** (-9)
    home_team_dict['team_USG_per'] = 10.0 ** (-9)

    for pos in {'G', 'F', 'C'}:
        home_team_dict['team_FG'] += home_team_dict['Starting_'+pos+'_FG']
        home_team_dict['team_FG'] += home_team_dict['Reserve_'+pos+'_FG']
        home_team_dict['team_FGA'] += home_team_dict['Starting_'+pos+'_FGA']
        home_team_dict['team_FGA'] += home_team_dict['Reserve_'+pos+'_FGA']
        home_team_dict['team_3P'] += home_team_dict['Starting_'+pos+'_3P']
        home_team_dict['team_3P'] += home_team_dict['Reserve_'+pos+'_3P']
        home_team_dict['team_3PA'] += home_team_dict['Starting_'+pos+'_3PA']
        home_team_dict['team_3PA'] += home_team_dict['Reserve_'+pos+'_3PA']
        home_team_dict['team_FT'] += home_team_dict['Starting_'+pos+'_FT']
        home_team_dict['team_FT'] += home_team_dict['Reserve_'+pos+'_FT']
        home_team_dict['team_FTA'] += home_team_dict['Starting_'+pos+'_FTA']
        home_team_dict['team_FTA'] += home_team_dict['Reserve_'+pos+'_FTA']
        home_team_dict['team_ORB'] += home_team_dict['Starting_'+pos+'_ORB']
        home_team_dict['team_ORB'] += home_team_dict['Reserve_'+pos+'_ORB']
        home_team_dict['team_DRB'] += home_team_dict['Starting_'+pos+'_DRB']
        home_team_dict['team_DRB'] += home_team_dict['Reserve_'+pos+'_DRB']
        home_team_dict['team_TRB'] += home_team_dict['Starting_'+pos+'_TRB']
        home_team_dict['team_TRB'] += home_team_dict['Reserve_'+pos+'_TRB']
        home_team_dict['team_AST'] += home_team_dict['Starting_'+pos+'_AST']
        home_team_dict['team_AST'] += home_team_dict['Reserve_'+pos+'_AST']
        home_team_dict['team_STL'] += home_team_dict['Starting_'+pos+'_STL']
        home_team_dict['team_STL'] += home_team_dict['Reserve_'+pos+'_STL']
        home_team_dict['team_BLK'] += home_team_dict['Starting_'+pos+'_BLK']
        home_team_dict['team_BLK'] += home_team_dict['Reserve_'+pos+'_BLK']
        home_team_dict['team_TOV'] += home_team_dict['Starting_'+pos+'_TOV']
        home_team_dict['team_TOV'] += home_team_dict['Reserve_'+pos+'_TOV']
        home_team_dict['team_PF'] += home_team_dict['Starting_'+pos+'_PF']
        home_team_dict['team_PF'] += home_team_dict['Reserve_'+pos+'_PF']
        home_team_dict['team_PTS'] += home_team_dict['Starting_'+pos+'_PTS']
        home_team_dict['team_PTS'] += home_team_dict['Reserve_'+pos+'_PTS']
        home_team_dict['team_ORB_per'] += home_team_dict['Starting_'+pos+'_ORB_per']
        home_team_dict['team_ORB_per'] += home_team_dict['Reserve_'+pos+'_ORB_per']
        home_team_dict['team_DRB_per'] += home_team_dict['Starting_'+pos+'_DRB_per']
        home_team_dict['team_DRB_per'] += home_team_dict['Reserve_'+pos+'_DRB_per']
        home_team_dict['team_TRB_per'] += home_team_dict['Starting_'+pos+'_TRB_per']
        home_team_dict['team_TRB_per'] += home_team_dict['Reserve_'+pos+'_TRB_per']
        home_team_dict['team_AST_per'] += home_team_dict['Starting_'+pos+'_AST_per']
        home_team_dict['team_AST_per'] += home_team_dict['Reserve_'+pos+'_AST_per']
        home_team_dict['team_STL_per'] += home_team_dict['Starting_'+pos+'_STL_per']
        home_team_dict['team_STL_per'] += home_team_dict['Reserve_'+pos+'_STL_per']
        home_team_dict['team_BLK_per'] += home_team_dict['Starting_'+pos+'_BLK_per']
        home_team_dict['team_BLK_per'] += home_team_dict['Reserve_'+pos+'_BLK_per']
        home_team_dict['team_USG_per'] += home_team_dict['Starting_'+pos+'_USG_per']
        home_team_dict['team_USG_per'] += home_team_dict['Reserve_'+pos+'_USG_per']

    # ----------------------------------------------
    # calculate percentages
    # ----------------------------------------------
    for pos in {'G', 'F', 'C'}:
        home_team_dict['Starting_'+pos+'_FG_per'] = home_team_dict['Starting_'+pos+'_FG'] / home_team_dict['Starting_'+pos+'_FGA']
        home_team_dict['Starting_'+pos+'_3P_per'] = home_team_dict['Starting_'+pos+'_3P'] / home_team_dict['Starting_'+pos+'_3PA']
        home_team_dict['Starting_'+pos+'_FT_per'] = home_team_dict['Starting_'+pos+'_FT'] / home_team_dict['Starting_'+pos+'_FTA']
        home_team_dict['Reserve_'+pos+'_FG_per'] = home_team_dict['Reserve_'+pos+'_FG'] / home_team_dict['Reserve_'+pos+'_FGA']
        home_team_dict['Reserve_'+pos+'_3P_per'] = home_team_dict['Reserve_'+pos+'_3P'] / home_team_dict['Reserve_'+pos+'_3PA']
        home_team_dict['Reserve_'+pos+'_FT_per'] = home_team_dict['Reserve_'+pos+'_FT'] / home_team_dict['Reserve_'+pos+'_FTA']

    home_team_dict['starters_FG_per'] = home_team_dict['starters_FG'] / home_team_dict['starters_FGA']
    home_team_dict['starters_3P_per'] = home_team_dict['starters_3P'] / home_team_dict['starters_3PA']
    home_team_dict['starters_FT_per'] = home_team_dict['starters_FT'] / home_team_dict['starters_FTA']

    home_team_dict['reserves_FG_per'] = home_team_dict['reserves_FG'] / home_team_dict['reserves_FGA']
    home_team_dict['reserves_3P_per'] = home_team_dict['reserves_3P'] / home_team_dict['reserves_3PA']
    home_team_dict['reserves_FT_per'] = home_team_dict['reserves_FT'] / home_team_dict['reserves_FTA']

    home_team_dict['team_FG_per'] = home_team_dict['team_FG'] / home_team_dict['team_FGA']
    home_team_dict['team_3P_per'] = home_team_dict['team_3P'] / home_team_dict['team_3PA']
    home_team_dict['team_FT_per'] = home_team_dict['team_FT'] / home_team_dict['team_FTA']

    # ====================================
    # putting the data into the dataframe
    # ====================================
    home_team_score = home_team_dict['team_PTS']
    away_team_score = away_team_dict['team_PTS']
    
    if home_team_score > away_team_score:
        home_team_dict['result'] = 1
        away_team_dict['result'] = 0
    elif home_team_score < away_team_score:
        home_team_dict['result'] = 0
        away_team_dict['result'] = 1
    else:
        print "error, the team's scores do not a strict inequality"


    team1 = {k+'_home':home_team_dict[k] for k in home_team_dict}
    team2 = {k+'_away':away_team_dict[k] for k in away_team_dict}

    game_stat_line = dict(team1.items() + team2.items())
    df = df.append(pd.Series(game_stat_line), ignore_index=True)    

# putting data into the psql database
table_name = 'df_game_simulations'
cnx.reset()
cnx_exe('DROP TABLE if EXISTS %s' %table_name)
pdpsql.write_frame(df, table_name, cnx)



