#!/bin/env python
# coding: utf-8

import os
import pandas as pd
import datetime
from flask import Flask, render_template, redirect
from flask_httpauth import HTTPBasicAuth

import file.file_utility
import strategy.environ
import calender.get
import pricing.get
import subprocess

app = Flask(__name__)
auth = HTTPBasicAuth()

users = {
    "xxx": "yyy",
}

app.debug = True
os.environ['TZ'] = 'America/New_York'
environ = strategy.environ.Environ()

@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None

@app.route('/')
@auth.login_required
def index():
    return render_template('index.html')


@app.route('/hello/<name>')
@auth.login_required
def hello(name='candles'):
    drive_id = environ.get('drive_id') if environ.get('drive_id') else '1A3k4a4u4nxskD-hApxQG-kNhlM35clSa'
    now = pd.Timestamp.now()
    _pricing = pricing.get.Pricing()
    instrument = _environ.get('instrument') if _environ.get('instrument') else "USD_JPY"
    price = _pricing.get(instrument)
    last_rate = price['price']
    if name == 'calendar' or name == 'system':
        _calender = calender.get.Calendar()
        drive_id =_calender.get_drive_id()

    candles_csv = file.file_utility.File_utility(name + '.csv', drive_id)
    candles_csv_string = candles_csv.get_string()

    if not candles_csv_string:
        return u'Now Uploading...'

    contents = candles_csv_string.getvalue()
    candles_csv_string.close()
    if name == '':
        name = u'ななしさん'
    return render_template('hello.html', name=name, contents=contents, now=now, last_rate=last_rate)

@app.route('/line/<name>')
@auth.login_required
def line(name=''):
    if name == 'send':
        res = subprocess.Popen('v20-golden-draw', stdout=subprocess.PIPE, stderr=None, shell=True)
        res.wait()
        out, err = res.communicate()
    return redirect('/', code=200)



@app.route('/debug')
@auth.login_required
def debug():
    return render_template('notemplate.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(port=port)