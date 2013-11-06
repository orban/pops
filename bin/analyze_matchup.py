#!/usr/bin/env python
import os, sys, time, re, json, pdb, random, datetime, subprocess
from sys import modules
# third parties
import numpy as np
import pandas as pd
import pandas.io.sql as psql
from scipy import stats
import psycopg2
# R interface
import rpy2.robjects as robjects
import rpy2.rinterface as RI
import warnings
warnings.filterwarnings('ignore')
R = robjects.r
RI.initr()
# personal utilities
import utils.pandas_psql as pdpsql


# ----------------------------------------
# setting up the computation environment
# ----------------------------------------
try:
    # local postgresql database
    cnx = psycopg2.connect(host='localhost', database='popsfundamental', 
                           user='jhuang') 

    # # remote database
    # cnx = psycopg2.connect(host='54.200.190.191', database='pops',
    #                        # password='not_shown_here',                       
    #                        user='pops')
    
    cur = cnx.cursor()
    cnx_exe = cur.execute
except:
    print sys.exc_info()[0]

pdb.set_trace()

import simulation_box as sb
import feature_selection as fs	

# deleting existing modules for testing
try:
	del modules['simulation_box']
	import simulation_box as sb
except:
	import simulation_box as sb
try:
	del modules['feature_selection']
	import feature_selection as fs	
except:
	import feature_selection as fs		

# ------------------------------------------------------    

try:
    match_up_input
except:
	match_up_input = {'home': 'LAC',
					  'away': 'LAL'}
	
# read in the historical games
feature_list = [u'fg',
				u'fga',
				u'two',
				u'two_a',
				u'three',
				u'three_a',
				u'ft',
				u'fta',
				u'pts',
				u'ast',
				u'tov',
				u'stl',
				u'blk',
				u'orb',
				u'drb',
				u'trb',
				u'pf']

# # ------------------------------------------------------------ 
# # making fake data
# obs = simulation_box.make_stat_line(match_up_input)

# df_teams = pd.read_csv('app_data/bbref_team_names_2014.txt')
# column_name = obs.keys()
# df_game = pd.DataFrame(columns = column_name)

# for i in range(1000):
#   _obs = simulation_box.make_stat_line(match_up_input)
#   df_game = df_game.append(pd.Series(_obs),
#                            ignore_index = True)
# # ------------------------------------------------------------ 

feature_list = [k+'_home' for k in feature_list]

df_game_1999_2013_for_simulation = df_game.copy() ####
df_game_1999_2013 = df_game.copy() ####
df_game_1999_2013['result'] = [random.random() for x in range(1000)]

df_simulator 

# ======================
# Data Frame Preparation
# ======================
game_list = sb.simulating_game(sb.make_stat_line(match_up_input), 
								 df_game_1999_2013_for_simulation)
df_match_up = df_game_1999_2013.iloc[game_list,:][feature_list]
df_match_up['result'] = df_game_1999_2013.iloc[game_list,:]['result']

data_X = df_match_up[feature_list].values
data_y = df_match_up['result'].values

# ===================
# Feature Selections
# ===================

top_features = fs.top_features(data_X, data_y, feature_list, num_feature=10)
top_features.append('result')
df_CI = df_match_up[top_features].applymap(float)

# ===================
# Causal Inference
# ===================

# passing data into R
df_CI.to_csv('./app_data/df_matchup_CI_R.csv', header=True, index=False)

with open('analyze_match_up.r', 'rb') as f:
    r_script = f.read()
        
# run R
R(r_script)
d3_graph_json = json.loads(R('tmptJSON')[0])

# ------------------------------
# processing the data for D3
# ------------------------------
# identifying the incoming edges
for i, record in enumerate(d3_graph_json['vertices']):
    if record['friends'] != '':
        out_going_list = [int(x) for x in record['friends'].split(',')]
    else:
        out_going_list = []
    d3_graph_json['vertices'][i]['out_going'] = out_going_list
    
out_going_dict = {v['node']:v['out_going'] for v in d3_graph_json['vertices']}

# identifying the outgoing edges
incoming_dict = {node['node']:[] for node in d3_graph_json['vertices']}
for node in incoming_dict:
    for out_edge in d3_graph_json['vertices'][node]['out_going']:
        incoming_dict[out_edge].append(node)

for i in incoming_dict:
    d3_graph_json['vertices'][i]['in_coming'] = incoming_dict[i]

# classifying nodes
node_classification_dict = {i:'' for i in incoming_dict}
for node in node_classification_dict:
    if len(out_going_dict[node]) == 0:
        node_classification_dict[node] = 'terminal'
    elif len(incoming_dict[node]) == 0:
        node_classification_dict[node] = 'causal'
    else:
        node_classification_dict[node] = 'internal'        
        
for i in incoming_dict:
    d3_graph_json['vertices'][i]['incoming'] = incoming_dict[i]
    d3_graph_json['vertices'][i]['type'] = node_classification_dict[i]

# set the 'TEAM_ORTG' and 'TEAM_DRTG'     
# to be terminal nodes
d3_graph_json['vertices'][-1]['type'] = 'terminal'
d3_graph_json['vertices'][-2]['type'] = 'terminal'

# edge distances
long_dist = 500
short_dist = long_dist / 2.0
for i, edge in enumerate(d3_graph_json['edges']):
    source = edge['source']
    target = edge['target']
    source_type = node_classification_dict[source]
    target_type = node_classification_dict[target]
    if (source_type == 'causal') and (target_type == 'terminal'):
        d3_graph_json['edges'][i]['dist'] = long_dist
    else:
        d3_graph_json['edges'][i]['dist'] = short_dist    

with open('./static/data/match_up_cr.json', 'wb') as f:
    json.dump(d3_graph_json,f)

# --------------
# testing
# --------------
if __name__ == '__main__':
    pass
