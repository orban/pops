import os, sys, time, re, json, pdb
import datetime, random
import pickle
# -----------------------------------------
import requests
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from bs4 import BeautifulSoup as Soup
from flask import Flask, request, Response
from flask import render_template

# =================================
# Testing the trained model
# =================================
with open('pkl/trained_vectorizer.pkl', 'rb') as f:
    vectorizer_trained = pickle.load(f)
with open('pkl/trained_classifier.pkl', 'rb') as f:
    clf_trained = pickle.load(f)
with open('pkl/dict_id_to_name.pkl', 'rb') as f:
    dict_id_to_name = pickle.load(f)

_url = 'http://www.newyorker.com/reporting/2013/10/21/131021fa_fact_max'
response = requests.get(_url)
_doc = [Soup(response.text).find('body').text]
x = vectorizer_trained.transform(_doc).toarray()

print '----------------------'
print 'testing...'
print dict_id_to_name[clf_trained.predict(x)[0]]
print '---------------------'

app = Flask(__name__)

@app.route('/')
def home():
    print 'I am home'
    return render_template('index.html')

@app.route("/msg", methods = ['GET', 'POST', 'PATCH', 'PUT', 'DELETE'])
def msg():
    print 'We are hitting the /msg resource.'
    return 'NOTHING'

# ===========================
# The classification resource
# ===========================
@app.route("/clf", methods=['POST'])
def clf():
    if request.method == 'POST':
        url = request.form['url']
        print '+++++'
        print 'The url that is requested to be classified is'
        print url
        print '+++++'
        response = requests.get(url)

        # in case the http request does not
        # go through
        requests_counter = 0
        while not(response.ok) and requests_counter < 5:
            response = requests.get(url)
            requests_counter += 1
        if not(response.ok):
            return 'The url does not return a document'
        
        _doc = [Soup(response.text).find('body').text]
        x = vectorizer_trained.transform(_doc).toarray()
        classification = dict_id_to_name[clf_trained.predict(x)[0]]
        print '-----------------------------------------'
        print 'the classification is: ', classification
        print '-----------------------------------------'
        
        # returned data
        data = {
            'input'  : request.form,
            'output' : classification
            }
        js = json.dumps(data)
        return Response(js, status=200, mimetype='application/json')
    else:
        return "The classifier needs an url."

# show an error message for all other routes.
@app.route("/<name>")
def not_valid(name):
    return "/"+name+' is not a valid route.'

#app.debug = True
app.run(host='0.0.0.0')

# url="http://www.newyorker.com/reporting/2013/10/21/131021fa_fact_max"
# curl --data url=$url http://127.0.0.1:5000/clf; printf "\n"
# curl --data 'url=http://www.newyorker.com/reporting/2013/10/21/131021fa_fact_max' 54.200.190.191:5000/clf


