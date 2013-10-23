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
from scipy import stats

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

# --------
# MongoDB
# --------
client = MongoClient('localhost', 27017)
client = MongoClient('mongodb://localhost:27017/')
db_bbref = client['bbref'] #database bbref
mongo_box_score = db_bbref['box_score'] #collection box_score

# ======================
# Data Frame Preparation
# ======================
df_games_complete = psql.read_frame('SELECT * FROM df_games_2013;', cnx)
all_columns = set(df_games_complete.columns)

# removing some features in the dataset
ignored_features = {'team', 'opp', 'game_id', 
                    'team_plub_minus',
                    'starters_plub_minus',
                    'reserves_plub_minus',
                    'starting_f_plub_minus',
                    'starting_g_plub_minus',
                    'starting_c_plub_minus',
                    'reserve_g_plub_minus',
                    'reserve_f_plub_minus',
                    'reserve_c_plub_minus'}
advanced_stats = {'efg_per', 'tov_per', 'orb_per', 'ft_fga', 'ortg'}
scoring_stats = {x for x in df_games_complete.columns.values if re.search('scoring', x)}

team_features = {x for x in df_games_complete.columns.values if re.search('team', x)}
ignored_features = ignored_features | team_features | advanced_stats | scoring_stats

remaining_features = list(set(df_games_complete.columns) - ignored_features)
df_games = df_games_complete[remaining_features].applymap(float)
df_games['result'] = df_games['result'].apply(int)

feature_names = df_games[list(set(df_games.columns) - {'result'})].columns.values
data_X = df_games[list(set(df_games.columns) - {'result'})].values
data_y = df_games['result'].values

# ===================
# Feature Selections
# ===================

# # by SVM
# from sklearn.feature_selection import SelectKBest
# from sklearn import svm
# from sklearn.cross_validation import StratifiedKFold
# from sklearn.feature_selection import RFECV
# from scipy import stats

# svc = svm.SVC(C=1, kernel='linear')
# rfecv = RFECV(estimator=svc, step=1) #cv=StratifiedKFold(y, 2), scoring='accuracy')
# rfecv.fit(data_X, data_y)

# dict_feature_to_rank_svm = {f:r for f,r in zip(feature_names, rfecv.ranking_)}
# dict_rank_to_feature_svm = {r:f for f,r in zip(feature_names, rfecv.ranking_)}

# print '---------------'
# print 'feature selection results using SVM'
# print dict_rank_to_feature
# print '---------------'

# by Pearson correlation

def pearson_rank(data_X, data_y):
    n_features = data_X.shape[1]
    df = pd.DataFrame(columns=['features', 'p_value'])
    for i in range(n_features):
        x = data_X[:,i]
        p_value = stats.pearsonr(x,data_y)[1]
        _row = pd.Series([i, p_value], index=['features', 'p_value'])
        _row.name = i
        df = df.append(_row)
    df = df.sort('p_value', ascending=1)
    df['rank'] = np.arange(n_features) + 1
    df = df.sort('features', ascending=1)
    return df['rank'].values
# # testing the function
# print pearson_rank(data_X, data_y)

ranks = pearson_rank(data_X, data_y)
dict_feature_to_rank_pearson = {f:r for f,r in zip(feature_names, ranks)}
dict_rank_to_feature_pearson = {r:f for f,r in zip(feature_names, ranks)}

NUM_SELECTED_FEATURES = 10
top_features = list({dict_rank_to_feature_pearson[i] 
                for i in np.arange(NUM_SELECTED_FEATURES)+1})
dict_top_features = {i+1:x for i,x in enumerate(top_features)}
dict_top_features[NUM_SELECTED_FEATURES+1] = 'result'
df_CI = df_games[top_features]
df_CI['result'] = df_games['result']

# ===================
# Causal Inference
# ===================
import rpy2.robjects as robjects
R = robjects.r
import warnings
warnings.filterwarnings('ignore')

# passing data into R
df_CI.to_csv('df_CI_R.csv', header=True, index=False)
R('''
require("pcalg");

# getting the data
df_CI <- read.csv("df_CI_R.csv");

# fitting the causal analysis algorithm
suffStat <- list(C = cor(df_CI), n = nrow(df_CI));
pc.fit <- pc(suffStat, indepTest = gaussCItest, p = ncol(df_CI), alpha = 0.01)
plot(pc.fit, main='')

''')
print dict_top_features

# ==========================
# testing
# ==========================
with open('features.json', "wb") as f:
    json.dump({i:x for i,x in enumerate(df_games_complete.columns)},f)

