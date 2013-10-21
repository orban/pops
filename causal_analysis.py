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
mongo_box_score = db_bbref['box_score'] #collection box_score
