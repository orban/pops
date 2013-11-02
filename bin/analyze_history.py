#!/usr/bin/env python
import os, sys, time, re, json, pdb, random, datetime, subprocess
# -----------------------------------
import numpy as np
import pandas as pd
import pandas.io.sql as psql
from scipy import stats
# from bson.objectid import ObjectId
# from pymongo import MongoClient
import psycopg2
# -----------------------------------
import utils.pandas_psql as pdpsql

# R interface
import rpy2.robjects as robjects
import rpy2.rinterface as RI
import warnings
warnings.filterwarnings('ignore')
R = robjects.r
RI.initr()

# ----------------------------------------
# connecting to the PostgreSQL database
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
    
cnx.reset()
df_games_complete = psql.read_frame('SELECT * FROM df_games_2013;', cnx)

try:
    feature_list
except:
    try:
        # if called as a subprocess
        feature_list = sys.argv[1].split(',')        
    except:
        # for testing only
        feature_list = [u'TEAM_FG', u'TEAM_FGA', u'TEAM_3P', u'TEAM_3PA', u'TEAM_FT', 
                        u'TEAM_FTA', u'TEAM_ORB', u'TEAM_DRB', u'TEAM_TRB', u'TEAM_AST', 
                        u'TEAM_STL', u'TEAM_BLK', u'TEAM_TOV', u'TEAM_PF', u'TEAM_PTS']

        
# ======================
# Data Frame Preparation
# ======================
feature_list = [x.lower() for x in feature_list]
if not('result' in feature_list):
    feature_list.append('result')

df_games = df_games_complete[feature_list].applymap(float)
df_games['result'] = df_games['result'].apply(int)

feature_names = df_games[list(set(df_games.columns) - {'result'})].columns.values
data_X = df_games[list(set(df_games.columns) - {'result'})].values
data_y = df_games['result'].values

df_CI = df_games[feature_list]
df_CI['result'] = df_games['result']

# ===================
# Causal Inference
# ===================

# passing data into R
df_CI.to_csv('./app_data/df_CI_R.csv', header=True, index=False)

with open('analyze_history.r', 'rb') as f:
    r_script = f.read()
        
# run R
R(r_script)
d3_graph_json = json.loads(R('tmptJSON')[0])

# ====================================
# processing the data for D3
# ====================================
        
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

with open('./static/data/hist_cr.json', 'wb') as f:
    json.dump(d3_graph_json,f)

    
# --------------
# testing
# --------------
if __name__ == '__main__':
    pass
