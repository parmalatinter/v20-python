#!/usr/bin/env python

import subprocess
import os 
import sys
from pathlib import Path
import market.condition
import golden.draw
import line.line

import pandas as pd
import numpy as np

from datetime import datetime
from pytz import timezone

from io import StringIO

import drive.drive
import time

def init():
	os.environ['TZ'] = 'America/New_York'
	googleDrive = drive.drive.Drive('1A3k4a4u4nxskD-hApxQG-kNhlM35clSa')
	googleDrive.delete_all()
	time.sleep(5)

def get_csv(filename):
	googleDrive = drive.drive.Drive('1A3k4a4u4nxskD-hApxQG-kNhlM35clSa')
	res = googleDrive.get_content_by_filename(filename)
	if res: 	
		return StringIO(res.GetContentString())
	return ''

def order(instrument, units, _line):
	args = dict(instrument=instrument, units=units)
	command = ' v20-order-market %(instrument)s %(units)s' % args
	print(command)
	res = subprocess.Popen(command, shell=True)
	res.wait()

	print(command)
	_line.send('order #', command )

def close(filename, hours, now_dt, _line):
	csv = get_csv(filename)

	df = pd.read_csv(csv, sep=',', engine='python', skipinitialspace=True)

	for index, row in df.iterrows():
		now_dt = datetime.strptime(now_dt, '%Y-%m-%dT%H:%M:%S')
		trade_dt = datetime.strptime(row.time, '%Y-%m-%dT%H:%M:%S')
		delta = now_dt - trade_dt
		
		delta_total_minuts = delta.total_seconds()/60
		delta_total_hours = delta_total_minuts/60

		if delta_total_hours >= hours:
			args = dict(tradeid=row.id, units='ALL')
			command = ' v20-trade-close %(tradeid)s --units="%(units)s"' % args
			res = subprocess.Popen(command, shell=True)
			res.wait()
			_line.send('order #', command )

def main():
	init()
	instrument = 'USD_JPY'
	units = 1
	hours = 5

	print(instrument)
	
	_line = line.line.Line()
	condition = market.condition.Market()
	if condition.get_is_opening() == False:
		exit()

	command = 'v20-transaction-get-all'
	print(command)
	res = subprocess.Popen(command, shell=True)
	res.wait()
	print(res)

	command = 'v20-instrument-data-tables'
	print(command)
	res = subprocess.Popen(command, shell=True)
	res.wait()
	print(res)

	time.sleep(5)


	filename = 'candles.csv'
	csv = get_csv(filename)
	draw = golden.draw.Draw()
	df = draw.caculate(csv)
	# candle_temp = draw.caculate_candle(df)
	last_df = df.tail(1)
	late = str(last_df['c'][last_df.index[0]])
	if last_df['golden'][last_df.index[0]]:
		order(instrument, 1, _line)
		print('golden order')
	elif last_df['dead'][last_df.index[0]]:
		order(instrument, -1, _line)
		print('dead order')
	if last_df['rule_1'][last_df.index[0]] == 0 and last_df['rule_2'][last_df.index[0]] == 0:
		print('chance order')
		_line.send("chance order #",str(late))
		
	filename = 'transaction.csv'
	now_dt = last_df['t'][last_df.index[0]]
	close(filename, hours, now_dt, _line)

if __name__ == "__main__":
    main()
