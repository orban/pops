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
# connecting to databases
# ------------------------------------------
# PostgreSQL
cnx = psycopg2.connect(host='localhost', database='popsfundamental', 
                       user='jhuang')
cur = cnx.cursor()
cnx_exe = cur.execute
cnx.reset()
# MongoDb
client = MongoClient('localhost', 27017)
client = MongoClient('mongodb://localhost:27017/')
db_bbref = client['bbref'] #database bbref
box_score_1999_to_2013 = db_bbref['box_score_1999_2013'] #collection box_score

# -------------------------------------------------------------
# acquiring the documents from basketball-reference.com
# -------------------------------------------------------------
df_links = psql.read_frame('SELECT link FROM games_id_links_1999_to_2013;', cnx)
counter = 0
for i in range(len(df_links)):
    link = df_links.iloc[i,:]['link']
    url = 'http://www.basketball-reference.com' + link
    
    # http request
    time.sleep(.5)
    data = requests.get(url)
    page_content = data.content
    doc = {'link': link, 'html': page_content}
    print '---------------'
    counter += 1
    print counter
    print doc['link']
    print '----------------'
    box_score_1999_to_2013.find_and_modify(query={'link': link},
                                           update=doc, upsert=True)
