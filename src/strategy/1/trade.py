#!/usr/bin/env python

import subprocess
import os 
import sys
from pathlib import Path
import market.condition
import golden.draw

import pandas as pd
import numpy as np

from datetime import datetime
from pytz import timezone

def order(units):
	args = dict(instrument=instrument, units=units)
	command = ' v20-trade-close %(instrument)s %(units)s --instrument="%(units)s"' % args
	print(command)
	res = subprocess.Popen(command, shell=True)
	print(command)

def close(file_path):
	dir_path = Path(__file__).parent.parent.parent / "transaction"
	os.chdir(dir_path)
	df = pd.read_csv(file_path, sep=',', engine='python', skipinitialspace=True)
	now_str = datetime.now(timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S')

	for index, row in df.iterrows():
		now_dt = datetime.strptime(now_str, '%Y-%m-%d %H:%M:%S')
		trade_dt = datetime.strptime(row.time, '%Y-%m-%dT%H:%M:%S')
		delta = now_dt - trade_dt
		print(delta)
		
		past_hours = delta.total_seconds()/60
		if past_hours >= 50:
			print("close id #" + str(row.id))

			args = dict(tradeid=row.id, units='ALL')
			command = ' v20-trade-close %(tradeid)s --units="%(units)s"' % args
			print(command)
			res = subprocess.Popen(command, shell=True)
			print(res)

def main():
	instrument = 'USD_JPY'
	units = 1
	
	condition = market.condition.Market()
	if condition.get_is_opening():
		file_path = 'data.csv'

		print('true')
		command = 'v20-transaction-get-all'
		print(command)
		res = subprocess.Popen(command, shell=True)
		res.wait()
		print(res)

		close(file_path)

		command = 'v20-instrument-data-tables'
		print(command)
		res = subprocess.Popen(command, shell=True)
		res.wait()
		print(res)

		dir_path = Path(__file__).parent.parent.parent / "instrument"
		
		draw = golden.draw.Draw()
		draw.chdir(dir_path)
		draw.set_file_name(file_path)
		df = draw.caculate()
		candle_temp = draw.caculate_candle(df)
		last_df = df.tail(1)
		if last_df['golden'][last_df.index[0]]:
			order(1)
			print('golden order')
		elif last_df['dead'][last_df.index[0]]:
			order(-1)
			print('dead order')
		draw.plot(df, candle_temp)
	else:
		print('false')

if __name__ == "__main__":
    main()
