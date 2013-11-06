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

# ------------------------------------------
# setting up the computation environment
# -------------------------------------------

# the postgres database connection is made
# global to avoid confusion when we
# switch location
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

#  inputs    
try:
    matchup_input
except:
	matchup_input = {'home': 'LAC',
					  'away': 'LAL'}
print '--analyzing matchup --: ', matchup_input	

try:
    where
except:
    where = 'home'

# generating the data set
obs = sb.make_stat_line(matchup_input, cnx)
df_simulator = sb.simulating_games(obs, cnx)

if where == 'home':
    _result = df_simulator['team_pts_home'] > df_simulator['team_pts_away']
    df_simulator['result'] = _result.apply(lambda x: 1 if x else 0)
elif where == 'away':
    _result = df_simulator['team_pts_home'] < df_simulator['team_pts_away']
    df_simulator['result'] = _result.apply(lambda x: 1 if x else 0)
else:
    print "The where variable is not set properly"
    raise

# - Features to be analyzed
# - See the columns of df_simulator for
#   what is available
FEATURE_LIST = [x+'_'+where for x in 
                ['fg', 'fga',
                 'three', 'three_a',
                 'ft', 'fta',
                 'pts', 'ast', 'tov', 'stl', 'blk',
                 'orb', 'drb', 'trb', 'pf',
                 'team_ortg', 'team_drtg']]

# ======================
# Data Frame Preparation
# ======================

data_X = df_simulator[FEATURE_LIST].values
data_y = df_simulator['result'].values

# ===================
# Feature Selections
# ===================

_num = 7 if where == 'home' else 5

top_features = fs.top_features(data_X, data_y, FEATURE_LIST, num_feature=_num)
top_features.append('result')
df_CI = df_simulator[top_features].applymap(float)


# ===================
# Causal Inference
# ===================

# passing data into R
df_CI.to_csv('./app_data/df_matchup_CI_R.csv', header=True, index=False)

with open('analyze_matchup.r', 'rb') as f:
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

# with open('./static/data/matchup_cr.json', 'wb') as f:
#     json.dump(d3_graph_json,f)

# --------------
# testing
# --------------
if __name__ == '__main__':
    pass
