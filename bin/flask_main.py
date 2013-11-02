#!/usr/bin/env python
#-*- coding: utf-8 -*-
# native
import os, sys, time, re, json, pdb
import datetime, random, pickle, subprocess
# third parties
import requests
import numpy as np
from flask import Flask, request, Response
from flask import render_template
# # analyses
# import causal_analysis

# =============
# loading data
# =============
# empty for now

# ======
# app
# ======
app = Flask(__name__)

@app.route('/')
def home():
    with open('./static/index.html') as f:
        html = f.read()
    return html   

@app.route('/index2')
def testing():
    with open('./static/index2.html') as f:
        html = f.read()
    #return render_template('index2.html')        
    return html    

@app.route("/analyze_hist", methods=['POST'])
def analyze_hist():
    if request.method == 'POST':
        #   receiving the post
        #------------------------
        feature_list = json.loads(request.form['data'])
        features_txt = unicode(','.join(feature_list))

        #   processing
        #------------------
        hist_analysis = {'feature_list': feature_list}
        execfile("analyze_history.py", hist_analysis)
        d3_graph_json = hist_analysis['d3_graph_json']

        #  returning back to the client
        #----------------------------------
        _data = {
            'input'  : request.form,
            'output' : d3_graph_json
        }
        _json = json.dumps(_data)
        return Response(_json, status=200, mimetype='application/json')
    else:
        return "Error: are you posting?"

# testing route
@app.route("/msg", methods = ['GET', 'POST', 'PATCH', 'PUT', 'DELETE'])
def msg():
    return 'NOTHING'

# show an error message for all other routes.
@app.route("/<name>")
def not_valid(name):
    return "/" + name + ' is not a valid route.'


# ================
# running the app
# ===============
if __name__ == '__main__':
    app.debug = True    
    app.run(host='0.0.0.0', port=5100)


    
