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
# import utils.pandas_psql as pdpsql

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
    # # local postgresql database
    # cnx = psycopg2.connect(host='localhost', database='popsfundamental', 
    #                        user='jhuang') 

    # # remote database
    cnx = psycopg2.connect(host='54.200.190.191', database='pops',
                           # password='not_shown_here',                       
                           user='pops')
    
    cur = cnx.cursor()
    cnx_exe = cur.execute
except:
    print sys.exc_info()[0]
    
cnx.reset()
df_2014 = psql.read_frame('SELECT * FROM games_id_links_2014;', cnx)

# make a json file for the upcoming schedule
_json = {}
gp = df_2014.groupby('date')

for item in gp.groups:
    key = item.strftime("%m/%d/%Y")

    _list = []
    for i in gp.groups[item]:
        _line = df_2014.iloc[i, :]
        game = _line['visitor'] + ' @ ' + _line['home']
        _list.append(game)
    _json[key] = _list

with open('../bin/app_data/2014_schedule.json', 'wb') as f:
	json.dump(_json,f)

    
    
