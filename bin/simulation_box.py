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


def team_stat_line(team, home=True):
    
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
    
    stat_list = [u'fg', u'fga',
                 u'three', u'three_a',
                 u'ft', u'fta',
                 u'pts', u'ast', u'tov', u'stl', u'blk',
                 u'orb', u'drb', u'trb', u'pf']

    if home:
        suffix = '_home'
        stat_list_modified = [x+suffix for x in stat_list]
        stat_line = dict.fromkeys(stat_list_modified, 0)
    else:
        suffix = '_away'
        stat_list_modified = [x+suffix for x in stat_list]
        stat_line = dict.fromkeys(stat_list_modified, 0)
    
    for i in range(roster.shape[0]):
        player_id = roster['id'][i]

        query = "SELECT * FROM df_players WHERE player_id='%s';" % player_id
        player_stat_line = psql.read_frame(query, cnx)

        try:
            df_team_stats = df_team_stats.append(player_stat_line.iloc[0,:],
                                                 ignore_index=True)
        except:
            # # a very small number of role players does not have
            # # records in the database
            # print '-'*20
            # print team
            # print player_id + '--does not have proper stats in record.'
            # print '-'*20            
            pass

    for pos in ['G', 'F', 'C']:
        # multiplying factor by postion    
        pos_factor = 1 if (pos =='C') else 2 
        
        _mp = df_team_stats[df_team_stats['pos']==pos]['mp']    
        _df = df_team_stats[df_team_stats['pos']==pos][stat_list]
        total_mp = sum(_mp)
        
        for _stat in _df.columns:
            # weighing by minutes
            stat_line[_stat+'_'+pos+suffix] = sum(_df[_stat] / total_mp) * 48 * pos_factor
            stat_line[_stat+suffix] += sum(_df[_stat] / total_mp) * 48 * pos_factor

    return stat_line

# # testing
# stat_line_home = team_stat_line('LAC', home=True)
# stat_line_away = team_stat_line('LAL', home=False)
# obs = dict(stat_line_home.items() + stat_line_away.items())
# pdb.set_trace()

def make_stat_line(game_dict):
    '''
    An example of the argument:
    
        {'home': 'LAC',
        'away': 'LAL'}

    Output should be a dictionary that has 120 keys:
[u'ast_C_away',
 u'ast_C_home',
 u'ast_F_away',
 u'ast_F_home',
 u'ast_G_away',
 u'ast_G_home',
 u'ast_away',
 u'ast_home',
 u'blk_C_away',
 u'blk_C_home',
 u'blk_F_away',
 u'blk_F_home',
 u'blk_G_away',
 u'blk_G_home',
 u'blk_away',
 u'blk_home',
 u'drb_C_away',
 u'drb_C_home',
 u'drb_F_away',
 u'drb_F_home',
 u'drb_G_away',
 u'drb_G_home',
 u'drb_away',
 u'drb_home',
 u'fg_C_away',
 u'fg_C_home',
 u'fg_F_away',
 u'fg_F_home',
 u'fg_G_away',
 u'fg_G_home',
 u'fg_away',
 u'fg_home',
 u'fga_C_away',
 u'fga_C_home',
 u'fga_F_away',
 u'fga_F_home',
 u'fga_G_away',
 u'fga_G_home',
 u'fga_away',
 u'fga_home',
 u'ft_C_away',
 u'ft_C_home',
 u'ft_F_away',
 u'ft_F_home',
 u'ft_G_away',
 u'ft_G_home',
 u'ft_away',
 u'ft_home',
 u'fta_C_away',
 u'fta_C_home',
 u'fta_F_away',
 u'fta_F_home',
 u'fta_G_away',
 u'fta_G_home',
 u'fta_away',
 u'fta_home',
 u'orb_C_away',
 u'orb_C_home',
 u'orb_F_away',
 u'orb_F_home',
 u'orb_G_away',
 u'orb_G_home',
 u'orb_away',
 u'orb_home',
 u'pf_C_away',
 u'pf_C_home',
 u'pf_F_away',
 u'pf_F_home',
 u'pf_G_away',
 u'pf_G_home',
 u'pf_away',
 u'pf_home',
 u'pts_C_away',
 u'pts_C_home',
 u'pts_F_away',
 u'pts_F_home',
 u'pts_G_away',
 u'pts_G_home',
 u'pts_away',
 u'pts_home',
 u'stl_C_away',
 u'stl_C_home',
 u'stl_F_away',
 u'stl_F_home',
 u'stl_G_away',
 u'stl_G_home',
 u'stl_away',
 u'stl_home',
 u'three_C_away',
 u'three_C_home',
 u'three_F_away',
 u'three_F_home',
 u'three_G_away',
 u'three_G_home',
 u'three_a_C_away',
 u'three_a_C_home',
 u'three_a_F_away',
 u'three_a_F_home',
 u'three_a_G_away',
 u'three_a_G_home',
 u'three_a_away',
 u'three_a_home',
 u'three_away',
 u'three_home',
 u'tov_C_away',
 u'tov_C_home',
 u'tov_F_away',
 u'tov_F_home',
 u'tov_G_away',
 u'tov_G_home',
 u'tov_away',
 u'tov_home',
 u'trb_C_away',
 u'trb_C_home',
 u'trb_F_away',
 u'trb_F_home',
 u'trb_G_away',
 u'trb_G_home',
 u'trb_away',
 u'trb_home']
    '''
    stat_line_home = team_stat_line(game_dict['home'], home=True)
    stat_line_away = team_stat_line(game_dict['away'], home=False)
    _obs = dict(stat_line_home.items() + stat_line_away.items())
    
    return _obs

# # testing
# print make_stat_line({'home': 'BOS','away': 'NOP'})
# print make_stat_line({'home': 'HOU','away': 'MIA'})
# pdb.set_trace()

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

def simulating_games(obs):
    '''
    Input is an observation, see the output of make_stat_line.

    Output is a data frame whose columns are:
    # =====================
    # the columns from obs
    # =====================
     stat_list = [u'fg', u'fga',
                 u'three', u'three_a',
                 u'ft', u'fta',
                 u'pts', u'ast', u'tov', u'stl', u'blk',
                 u'orb', u'drb', u'trb', u'pf']

 which are permutated by [G,F,C] and [home, away]

 And there are those who are in:
 'app_data/simulated_game_features.json' 
    
    Each row is a record of an simulated game.
    '''
    RETAINED_PER = 0.05
    query = "SELECT * FROM df_simulator"
    df_simulator = psql.read_frame(query, cnx)

    text_fields = ['result_home', 'result_away',
                   'team_home', 'team_away',
                   'game_id_home', 'game_id_away',
                   'opp_home', 'opp_away']

    for _f in text_fields:
        del df_simulator[_f]

    df_simulator = df_simulator.applymap(float)

    stat_list = [u'fg', u'fga',
                 u'three', u'three_a',
                 u'ft', u'fta',
                 u'pts', u'ast', u'tov', u'stl', u'blk',
                 u'orb', u'drb', u'trb', u'pf']
    
    stat_list2 = [u'fg', u'fga',
                   u'3p', u'3pa',
                   u'ft', u'fta',
                   u'pts', u'ast', u'tov', u'stl', u'blk',
                   u'orb', u'drb', u'trb', u'pf']
    # _home 
    # _pos_home
    # total  15 * (3+1) * 2

    # create a place holder for the simulator data frame
    df_simulator_extra = df_simulator.ix[:, ['team_pts_home','team_pts_away']]
    counter = 0 
    
    for where in ['home','away']:
        for i in range(len(stat_list)):
            _stat = stat_list[i]
            _stat2 = stat_list2[i]
            _key = _stat + '_' + where
            _foreign_key = 'team_' + _stat2 + '_' + where

            df_simulator_extra[_key] = df_simulator[_foreign_key]
            
            # counter += 1
            # print counter,' | ', _key, ' | ', _foreign_key
              
        for pos in ['G', 'F', 'C']:
            for i in range(len(stat_list)):
                _stat = stat_list[i]
                _stat2 = stat_list2[i]
                
                _key = _stat + '_' + pos + '_' + where
                _f_key1 = 'starters_' + _stat2 + '_' + where
                _f_key2 = 'reserves_' + _stat2 + '_' + where                

                df_simulator_extra[_key] = df_simulator[_f_key1] + df_simulator[_f_key2]
                # counter += 1
                # print counter, ' | ', _key, ' | ', _f_key1, ' | ', _f_key2

    # these two fields were place holders
    del  df_simulator_extra['team_pts_home']
    del  df_simulator_extra['team_pts_away']    

    # we use the usual R square distance
    # to measure similarity of the current stat line
    # to historical games
    scaler = preprocessing.StandardScaler().fit(df_simulator_extra.values)
    arr_game = scaler.transform(df_simulator_extra.values)
    arr_obs = scaler.transform(obs.values())
    
    _rank = R2_dist(arr_game, arr_obs)
    _range = np.arange(0,len(_rank)).reshape(_rank.shape)
    df_rank = pd.DataFrame(np.hstack((_rank,_range)), 
                           columns=['rank', 'id'])
    df_rank = df_rank.sort('rank')


    cut_off = int(np.floor(df_simulator_extra.shape[0] * RETAINED_PER))
    _chosen_list = map(int, df_rank['id'][0:cut_off].tolist())

    # making the data frame for output

    with open('app_data/simulated_game_features.json', 'rb') as f:
        _features = json.loads(f.read())['features']
    _features = [s.lower() for s in _features]
    _features = [x+'_home' for x in _features] + [x+'_away' for x in _features]

    df_left = df_simulator.ix[_chosen_list, _features]
    df_right = df_simulator_extra.iloc[_chosen_list, :]
    df = df_left.join(df_right)

    return df

#   test
# -----------
if __name__ == '__main__':
    matchup_input = {'home': 'LAC',
                      'away': 'LAL'}
    obs = make_stat_line(matchup_input)
    # ------
    df = simulating_games(obs)
    
