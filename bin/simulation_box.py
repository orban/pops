#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os, sys, time, re, json, pdb, pickle
import datetime, random
# -----------------------------------------
import numpy as np
import pandas as pd
import pandas.io.sql as psql
import scipy as sp
from sklearn import preprocessing
from sklearn.metrics.pairwise import euclidean_distances as R2_dist
import requests
from requests_oauthlib import OAuth1Session
from pymongo import MongoClient
from bson.objectid import ObjectId
from bs4 import BeautifulSoup as Soup
import psycopg2

def make_stat_line(game_dict):
    '''
    An example of the argument:
    
        {'home': 'LAC',
        'away': 'LAL'}

    Output should be a dictionary that has 136 keys:
        {u'ast': 0,
        u'ast_C_away': 0,
        u'ast_C_home': 0,
        u'ast_F_away': 0,
        u'ast_F_home': 0,
        u'ast_G_away': 0,
        u'ast_G_home': 0,
        u'ast_away': 0,
        u'ast_home': 0,
        u'blk': 0,
        u'blk_C_away': 0,
        u'blk_C_home': 0,
        u'blk_F_away': 0,
        u'blk_F_home': 0,
        u'blk_G_away': 0,
        u'blk_G_home': 0,
        u'blk_away': 0,
        u'blk_home': 0,
        u'drb': 0,
        u'drb_C_away': 0,
        u'drb_C_home': 0,
        u'drb_F_away': 0,
        u'drb_F_home': 0,
        u'drb_G_away': 0,
        u'drb_G_home': 0,
        u'drb_away': 0,
        u'drb_home': 0,
        u'fg': 0,
        u'fg_C_away': 0,
        u'fg_C_home': 0,
        u'fg_F_away': 0,
        u'fg_F_home': 0,
        u'fg_G_away': 0,
        u'fg_G_home': 0,
        u'fg_away': 0,
        u'fg_home': 0,
        u'fga': 0,
        u'fga_C_away': 0,
        u'fga_C_home': 0,
        u'fga_F_away': 0,
        u'fga_F_home': 0,
        u'fga_G_away': 0,
        u'fga_G_home': 0,
        u'fga_away': 0,
        u'fga_home': 0,
        u'ft': 0,
        u'ft_C_away': 0,
        u'ft_C_home': 0,
        u'ft_F_away': 0,
        u'ft_F_home': 0,
        u'ft_G_away': 0,
        u'ft_G_home': 0,
        u'ft_away': 0,
        u'ft_home': 0,
        u'fta': 0,
        u'fta_C_away': 0,
        u'fta_C_home': 0,
        u'fta_F_away': 0,
        u'fta_F_home': 0,
        u'fta_G_away': 0,
        u'fta_G_home': 0,
        u'fta_away': 0,
        u'fta_home': 0,
        u'orb': 0,
        u'orb_C_away': 0,
        u'orb_C_home': 0,
        u'orb_F_away': 0,
        u'orb_F_home': 0,
        u'orb_G_away': 0,
        u'orb_G_home': 0,
        u'orb_away': 0,
        u'orb_home': 0,
        u'pf': 0,
        u'pf_C_away': 0,
        u'pf_C_home': 0,
        u'pf_F_away': 0,
        u'pf_F_home': 0,
        u'pf_G_away': 0,
        u'pf_G_home': 0,
        u'pf_away': 0,
        u'pf_home': 0,
        u'pts': 0,
        u'pts_C_away': 0,
        u'pts_C_home': 0,
        u'pts_F_away': 0,
        u'pts_F_home': 0,
        u'pts_G_away': 0,
        u'pts_G_home': 0,
        u'pts_away': 0,
        u'pts_home': 0,
        u'stl': 0,
        u'stl_C_away': 0,
        u'stl_C_home': 0,
        u'stl_F_away': 0,
        u'stl_F_home': 0,
        u'stl_G_away': 0,
        u'stl_G_home': 0,
        u'stl_away': 0,
        u'stl_home': 0,
        u'three': 0,
        u'three_C_away': 0,
        u'three_C_home': 0,
        u'three_F_away': 0,
        u'three_F_home': 0,
        u'three_G_away': 0,
        u'three_G_home': 0,
        u'three_a': 0,
        u'three_a_C_away': 0,
        u'three_a_C_home': 0,
        u'three_a_F_away': 0,
        u'three_a_F_home': 0,
        u'three_a_G_away': 0,
        u'three_a_G_home': 0,
        u'three_a_away': 0,
        u'three_a_home': 0,
        u'three_away': 0,
        u'three_home': 0,
        u'tov': 0,
        u'tov_C_away': 0,
        u'tov_C_home': 0,
        u'tov_F_away': 0,
        u'tov_F_home': 0,
        u'tov_G_away': 0,
        u'tov_G_home': 0,
        u'tov_away': 0,
        u'tov_home': 0,
        u'trb': 0,
        u'trb_C_away': 0,
        u'trb_C_home': 0,
        u'trb_F_away': 0,
        u'trb_F_home': 0,
        u'trb_G_away': 0,
        u'trb_G_home': 0,
        u'trb_away': 0,
        u'trb_home': 0,
        u'two': 0,
        u'two_C_away': 0,
        u'two_C_home': 0,
        u'two_F_away': 0,
        u'two_F_home': 0,
        u'two_G_away': 0,
        u'two_G_home': 0,
        u'two_a': 0,
        u'two_a_C_away': 0,
        u'two_a_C_home': 0,
        u'two_a_F_away': 0,
        u'two_a_F_home': 0,
        u'two_a_G_away': 0,
        u'two_a_G_home': 0,
        u'two_a_away': 0,
        u'two_a_home': 0,
        u'two_away': 0,
        u'two_home': 0}    
    '''

    # team roster dict
    with open('app_data/team_roster_dict.pkl', 'rb') as f:
        team_roster_dict = pickle.load(f)

    var_list = [u'fg', u'fga', u'two', u'two_a',
                 u'three', u'three_a',
                 u'ft', u'fta',
                 u'pts', u'ast', u'tov', u'stl', u'blk',
                 u'orb', u'drb', u'trb', u'pf']
    stat_list = []

    for where in ['home', 'away']:
        [stat_list.append(k+'_'+where) for k in var_list]       
        for pos in ['G', 'F', 'C']:
            [stat_list.append(k+'_'+pos+'_'+where) for k in var_list]
        
    stat_line = dict.fromkeys(stat_list, 0)

    ############
    # simple randomized mockup
    stat_line = {k:np.random.normal(0,1) for k in stat_line}
    ############

    return stat_line

# # ------------------------------------------------------------ 
# # # making a fake dataset
# obs = make_stat_line(match_up_input)

# df_teams = pd.read_csv('app_data/bbref_team_names_2014.txt')
# column_name = obs.keys()
# df_game = pd.DataFrame(columns = column_name)

# for i in range(1000):
#   _obs = make_stat_line(match_up_input)
#   df_game = df_game.append(pd.Series(_obs),
#                            ignore_index = True)
# # ------------------------------------------------------------ 

def simulating_game(obs, df_game):
    '''
    Input is a stat line, see the output of make_stat_line

    Output is a data frame that use that stat_line keys as columns.
    Each row is a record of a game.
    '''
    RETAINED_PER = 0.01
    
    scaler = preprocessing.StandardScaler().fit(df_game.values)
    arr_game = scaler.transform(df_game.values)
    arr_obs = scaler.transform(obs.values())
    
    _rank = R2_dist(arr_game, arr_obs)
    _range = np.arange(0,len(_rank)).reshape(_rank.shape)
    df_rank = pd.DataFrame(np.hstack((_rank,_range)), 
                           columns=['rank', 'id'])
    df_rank = df_rank.sort('rank')


    cut_off = int(np.floor(df_game.shape[0] * RETAINED_PER))
    _chosen_list = map(int, df_rank['id'][0:cut_off].tolist())
    df = df_game.iloc[_chosen_list,:]

    return _chosen_list


#   test
# -----------
if __name__ == '__main__':
	match_up_input = {'home': 'LAC',
					  'away': 'LAL'}
	
	df_simulated_game = simulating_game(make_stat_line(match_up_input), 
										df_game)


