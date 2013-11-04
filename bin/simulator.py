#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os, sys, time, re, json, pdb, pickle
import datetime, random
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

# -----------------------------------
import utils.pandas_psql as pdpsql

# =======================================
# INPUTS
# =======================================
team = 'LAC'
opp = 'LAL'

# # ------------------------------------------
# # connecting to the PostgreSQL database
# # ------------------------------------------
try:
    # cnx = psycopg2.connect(host='localhost', database='popsfundamental', 
    #                        user='jhuang')

    # remote database
    cnx = psycopg2.connect(host='54.200.190.191', database='pops',
                           # password='not_shown_here',                       
                           user='pops')    
    cur = cnx.cursor()
    cnx_exe = cur.execute
except:
    print sys.exc_info()[0]
cnx.reset()


# # ------------------------------------------
# # MongoDB
# # ------------------------------------------
# client = MongoClient('localhost', 27017)
# client = MongoClient('mongodb://localhost:27017/')
# db_bbref = client['bbref'] # database bbref
# mongo_rosters = db_bbref['team_roster']

# ========================================================================
# step 1:
# building the stats for both teams

# step 2:
# find the past games that were similar to these stat lines

# =========================================================================


# ----------------
# STEP 1
# ----------------
def team_stat_line(team, opp=False):
    
    # team roster dict
    with open('app_data/team_roster_dict.pkl', 'rb') as f:
        team_roster_dict = pickle.load(f)
    
    # building stat lines for the team
    roster = team_roster_dict[team]
    df_team_stats = pd.DataFrame(columns = [u'ft',
                                            u'three', 
                                            u'tov', 
                                            u'pos', 
                                            u'two_a', 
                                            u'fg', 
                                            u'player_id', 
                                            u'three_a', 
                                            u'drb', 
                                            u'ast', 
                                            u'two_per', 
                                            u'pf', 
                                            u'pts', 
                                            u'fga', 
                                            u'two', 
                                            u'stl', 
                                            u'trb', 
                                            u'fta', 
                                            u'link', 
                                            u'blk', 
                                            u'handle', 
                                            u'name', 
                                            u'three_per', 
                                            u'fg_per', 
                                            u'ft_per', 
                                            u'mp', 
                                            u'orb'])
    
    stat_list = [u'fg', u'fga', u'two', u'two_a',
                 u'three', u'three_a',
                 u'ft', u'fta',
                 u'pts', u'ast', u'tov', u'stl', u'blk',
                 u'orb', u'drb', u'trb', u'pf']

    if opp:
        suffix = '_opp'
        stat_list_modified = [x+suffix for x in stat_list]
        stat_line = dict.fromkeys(stat_list_modified, 0)
    else:
        suffix = ''
        stat_line = dict.fromkeys(stat_list, 0)

    for i in range(roster.shape[0]):
        player_id = roster['id'][i]

        # this line has some issues
		# ####
        query = "SELECT * FROM players_bbref WHERE player_bbr_id='%s';" % player_id
		# ######
        player_stat_line = psql.read_frame(query, cnx)

        try:
            df_team_stats = df_team_stats.append(player_stat_line.iloc[0,:],
                                                 ignore_index=True)
        except:
            pass
            # print '-'*20
            # print team
            # print player_id + '--does not have proper stats in record.'
            # print '-'*20            

    for pos in ['G', 'F', 'C']:
        # multiplying factor by postion    
        pos_factor = 1 if (pos =='C') else 2 
        
        _mp = df_team_stats[df_team_stats['pos']==pos]['mp']    
        _df = df_team_stats[df_team_stats['pos']==pos][stat_list]
        total_mp = sum(_mp)
        
        for _stat in _df.columns:
            # weighing by minutes
            stat_line[pos+'_'+_stat+suffix] = sum(_df[_stat] / total_mp) * 48 * pos_factor
            stat_line[_stat+suffix] += sum(_df[_stat] / total_mp) * 48 * pos_factor

    pdb.set_trace()
    return stat_line

# # testing
# print team_stat_line('LAC')
# print team_stat_line('LAL')

# ----------------
# STEP 2
# ----------------

PERCENTAGE_RETAINED = 0.1

stat_line = team_stat_line(team)
stat_line_opp = team_stat_line(opp, opp=True)
obs = dict(stat_line.items() + stat_line_opp.items())

# # ------------------------------------------------------------
# # a fake df_game for testing
# df_teams = pd.read_csv('app_data/bbref_team_names_2014.txt')
# column_name = an_obs.keys()
# df_game = pd.DataFrame(columns = column_name)
                                  
# for team in df_teams['tag']:
#     stat_line = team_stat_line(team)
#     stat_line_opp = team_stat_line(df_teams['tag'][random.randint(0,29)],
#                                    opp=True)
#     _obs = dict(stat_line.items() + stat_line_opp.items())
#     df_game = df_game.append(pd.Series(_obs), 
#                              ignore_index=True)
# # ------------------------------------------------------------ 

# game_id_dict = {x:i for i,x in enumerate(df_teams['tag'])}
# id_game_dict = {i:x for i,x in enumerate(df_teams['tag'])}

# from sklearn import preprocessing
# from sklearn.metrics.pairwise import euclidean_distances as R2_dist

# scaler = preprocessing.StandardScaler().fit(df_game.values)

# arr_game = scaler.transform(df_game.values)
# arr_obs = scaler.transform(obs.values())

# _rank = R2_dist(arr_game, arr_obs)
# _range = np.arange(0,len(_rank)).reshape(_rank.shape)
# df_rank = pd.DataFrame(np.hstack((_rank,_range)), 
#                        columns=['rank', 'id'])
# df_rank = df_rank.sort('rank')

# _chosen_list = df_rank['id'][0:5]
# id_game_dict[_chosen_list]


# generating games
