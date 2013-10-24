#!/usr/bin/env python
import os, sys, time, re, json, pdb
import datetime
# -----------------------------------------
import numpy as np
import pandas as pd
from pandas.io import sql
import scipy as sp
import requests
from requests_oauthlib import OAuth1Session
from pymongo import MongoClient
from bson.objectid import ObjectId
from bs4 import BeautifulSoup as Soup
# ------------------------------------------
import psycopg2

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
	print sql.read_frame("SELECT VERSION()",cnx)
except:
	print sys.exc_info()[0]
cnx_exe("""
DROP TABLE if EXISTS abc;
CREATE TABLE abc AS
SELECT VERSION();
""")

# ------------------
# helper functions
# ------------------
def format_home(txt):
	if txt == '@':
		return 0
	return 1
def format_streak(txt):
	if re.search('W', txt):
		result = int(re.search('[0-9]+', txt).group())
	elif re.search('L', txt):
		result = -int(re.search('[0-9]+', txt).group())
	else:
		result = 0
	return result
def format_ot(txt):
	if txt:
		return txt
	else:
		return "-"

# ------------------------
# getting team results
# ------------------------
def get_team_results(team_name,season):
	# basic http request setup
	user_agent_info = '''Jin Huang (huangjinf@gmail.com)\n
	Please let me know if there is any rate limit information.
	I am not colelcting data for any commercial use.
	'''
	headers = {'user_agent': user_agent_info}
	base_url = "http://www.basketball-reference.com/teams/"
	url = base_url+team_name+'/'+season+'_games.html'
	print url
	data = requests.get(test_url, headers=headers)
	soup_data = Soup(data.text)
	table_body = soup_data.find(id='div_teams_games').find('tbody')

	table_name = "result_"+team_name+"_"+season
	# --------
	cnx.reset()
	cnx_exe("""
	DROP TABLE if EXISTS %(table)s;
	""" % {'table': table_name})
	cnx_exe("""
	CREATE TABLE %(table)s (g SMALLINT PRIMARY KEY,  
						date DATE NOT NULL,
						home SMALLINT NOT NULL,
						opp VARCHAR(25) NOT NULL,
						result CHAR(1) NOT NULL,
						ot VARCHAR(5) NOT NULL,
						score_t SMALLINT NOT NULL,
						score_o SMALLINT NOT NULL,
						w SMALLINT NOT NULL,
						l SMALLINT NOT NULL,
						streak SMALLINT NOT NULL);
	""" % {'table': table_name})
	# --------
	for row in table_body.find_all('tr'):
		if not(re.search('Box Score', row.text)):
			continue
		_row = {i: x.text for i,x in enumerate(row.find_all('td'))}
		g = int(_row[0])
		date = pd.to_datetime(_row[1]).date().isoformat()
		home = format_home(_row[2])
		opp = _row[4]
		result = _row[5]
		ot = format_ot(_row[6])
		score_t = int(_row[7])
		score_o = int(_row[8])
		w = int(_row[9])
		l = int(_row[10])
		streak = format_streak(_row[11])
		cnx_exe("""
		INSERT INTO %s (g, date, home, opp, result, ot, score_t, score_o, w, l, streak) 
		VALUES           (%s, '%s', %s,  '%s',  '%s',   '%s','%s',    %s,    %s, %s, %s); 
		""" % (table_name, g, date, home, opp, result, ot, score_t, score_o, w, l, streak))
	cnx.commit()
	print team_name, season
	print 'done'
	print '----'
	
# -------------------------------------
# importing the list of name team names
# -------------------------------------
df_team_names = pd.read_csv('bbref_team_names.txt')

for _team in df_team_names['tag']:
	get_team_results(_team, '2013')

