#!/bin/env python
# coding: utf-8

import os
import sys
import pandas as pd
import datetime
from flask import Flask, render_template
import file.file_utility
import strategy.environ
import calender.get

app = Flask(__name__)
app.debug = True
os.environ['TZ'] = 'America/New_York'
environ = strategy.environ.Environ()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/hello/<name>')
def hello(name='candles'):
	template_path = os.path.dirname(app.instance_path) + '/src/app/templates/'
	drive_id = environ.get('drive_id') if environ.get('drive_id') else '1A3k4a4u4nxskD-hApxQG-kNhlM35clSa'
	now1 = pd.Timestamp.now()
	now2 = datetime.datetime.now() 

	if name == 'calendar':
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
	return render_template('hello.html', name=name, contents=contents, now1=now1, now2=now2)


@app.route('/debug')
def debug():
    return render_template('notemplate.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(port=port)