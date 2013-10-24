'''###!/usr/bin/env python
### -*- coding: utf-8 -*-
'''
# native
import os, sys, time, re, json, pdb
import datetime, random, pickle
# third parties
import requests
import numpy as np
from flask import Flask, request, Response
from flask import render_template

# =============
# loading data
# =============

# =============
# app
# =============
app = Flask(__name__)

@app.route('/')
def home():
    with open('./static/index.html') as f:
        html = f.read()
    #return render_template('index.html')        
    return html    


# testing route
@app.route("/msg", methods = ['GET', 'POST', 'PATCH', 'PUT', 'DELETE'])
def msg():
    return 'NOTHING'

# show an error message for all other routes.
@app.route("/<name>")
def not_valid(name):
    return "/" + name + ' is not a valid route.'

# ========
# testing
# ========


# ================
# running the app
# ===============
if __name__ == '__main__':
    app.debug = True    
    app.run(host='0.0.0.0')


    
