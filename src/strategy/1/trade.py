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
import file.file_utility
import strategy.environ
import strategy.account
import trend.get
import db.history

import time
import copy


class Trade():

	is_ordered = False
	drive_id = ''
	history = db.history.History()

	def init(self, drive_id):
		self.is_ordered = False
		self.drive_id = drive_id
		os.environ['TZ'] = 'America/New_York'
		googleDrive = drive.drive.Drive(self.drive_id)
		googleDrive.delete_all()
		time.sleep(5)

	def get_df(self, csv_string):
		return pd.read_csv(csv_string, sep=',', engine='python', skipinitialspace=True)

	def order(self, instrument, units, price, _line):
		args = dict(instrument=instrument, units=units, price=price)
		command = ' v20-order-market %(instrument)s %(units)s --take-profit-price=%(price)s' % args
		res = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True)
		res.wait()
		out, err = res.communicate()
		_line.send('order #', command + ' ' + out.decode('utf-8') )
		self.is_ordered = True

	def close(self, instrument, df, hours, now_dt, last_rate, _line):

		now_dt = datetime.strptime(now_dt.replace('T', ' '), '%Y-%m-%d %H:%M:%S')

		for index, row in df.iterrows():

			trade_dt = datetime.strptime(row.time.replace('T', ' '), '%Y-%m-%d %H:%M:%S')
			delta = now_dt - trade_dt

			delta_total_minuts = delta.total_seconds()/60
			delta_total_hours = delta_total_minuts/60

			if delta_total_hours >= hours:
				args = dict(tradeid=row.id, units='ALL')
				command = ' v20-trade-close %(tradeid)s --units="%(units)s"' % args
				res = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True)
				res.wait()
				out, err = res.communicate()
				self.is_ordered = True
				self.history.update(int(row.id), last_rate,  float(row.unrealizedPL), 99)
				_line.send('order #', command + ' ' + out.decode('utf-8') )

	def get_account_details(self):
		account = strategy.account.Account()
		details = account.get_account_detail()
		return details

	def exec_command(self, command):
		res = subprocess.Popen(command, shell=True)
		res.wait()
		time.sleep(5)

	def golden_trade(self, instrument, units, candles_csv_string, _line):
		draw = golden.draw.Draw()
		df = draw.caculate(candles_csv_string)
		last_df = df.tail(1)
		late = last_df['c'][last_df.index[0]]
		trend_usd = trend.get.Trend().get()
		is_golden = last_df['golden'][last_df.index[0]]
		is_dead = last_df['dead'][last_df.index[0]]
		_units = 0
		_event_open_id = 0
		_message = ''
		_target_price = 0
		if is_golden:
			if trend_usd > 5:
				_message = ("buy order 1 #",str(late))
				_units = units
				_event_open_id = 1
				_target_price = late + 0.1
				
			elif trend_usd < -5:
				_message = ("sell order 2 #",str(late))
				_units = 0 - units
				_event_open_id = 2
				_target_price = late - 0.1

			else:
				_message = ("buy order 3 #",str(late))
				_units = units
				_event_open_id = 3
				_target_price = late + 0.05

		elif is_dead:
			if trend_usd < -5:
				_message = ("sell order 1 #",str(late))
				_units = 0 - units
				_event_open_id = 4
				_target_price = late - 0.1

			elif trend_usd > 5:
				_message = ("buy order 2 #",str(late))
				_units = units
				_event_open_id = 5
				_target_price = late + 0.1
				
			else:
				_message = ("sell order 3 #",str(late))
				_units = 0 - units
				_event_open_id = 6
				_target_price = late - 0.05

		if last_df['rule_1'][last_df.index[0]] == 0 and last_df['rule_2'][last_df.index[0]] == 0:
			_message = ("buy chance order #",str(late))
			_units = units * 2
			_event_open_id = 7
			_target_price = late + 0.1

		elif last_df['rule_3'][last_df.index[0]] == 0 and last_df['rule_4'][last_df.index[0]] == 0:
			_message = ("sell chance order #",str(late))
			_units = 0 - (units * 2)
			_event_open_id = 8
			_target_price = late - 0.1
		
		if _event_open_id > 0:
			self.is_ordered = True
			_target_price =  round(_target_price, 2)
			self.order(instrument, _units,_target_price, _line)
			_line.send(_event_open_id, _message)
			return {
				'late': late,
				'target_price' : _target_price,
				'instrument': instrument,
				'units': _units,
				'event_open_id' : _event_open_id,
				'trend' : trend_usd,
				'is_golden': is_golden,
				'is_dead' :is_dead
			}

		return None
	
	def get_info(self, df):
		last_df = df.tail(1)
		return {'time' : last_df['time'][last_df.index[0]], 'close' : last_df['close'][last_df.index[0]]}

	def insert_histoy(self, trade_history, trade_id):
		self.history.insert(
			int(trade_id),
			float(trade_history.late),
			'target:' + str(trade_history.target_price),
			trade_history.instrument,
			trade_history.units,
			0,
			trade_history.event_open_id,
			trade_history.trend,
			trade_history.is_golden,
			trade_history.is_dead
		)

	
def main():

	_environ = strategy.environ.Environ()

	instrument = _environ.get('instrument') if _environ.get('instrument') else "USD_JPY"
	units = int(_environ.get('units')) if _environ.get('units') else 10
	hours = int(_environ.get('hours')) if _environ.get('hours') else 3
	reduce_time = float(_environ.get('reduce_time')) if _environ.get('reduce_time') else 5
	drive_id = _environ.get('drive_id') if _environ.get('drive_id') else '1A3k4a4u4nxskD-hApxQG-kNhlM35clSa'
	now_dt = None

	trade = Trade()
	trade.init(drive_id)

	_line = line.line.Line()
	condition = market.condition.Market()
	if condition.get_is_opening() == False:
		exit()

	trade.exec_command('v20-instrument-data-tables')
	
	filename = 'candles.csv'
	candles_csv = file.file_utility.File_utility(filename, drive_id)
	candles_csv_string = candles_csv.get_string()
	candles_csv_string2 = copy.copy(candles_csv_string)
	candles_df= trade.get_df(candles_csv_string)
		
	trade_history = None
	if condition.get_is_eneble_new_order(reduce_time):
		trade_history = trade.golden_trade(instrument, units, candles_csv_string2, _line)
		
	info = trade.get_info(candles_df)

	trade.exec_command('v20-transaction-get-all')

	filename = 'transaction.csv'
	transaction_csv = file.file_utility.File_utility(filename, drive_id)
	transaction_csv_string = transaction_csv.get_string()
	transaction_df= trade.get_df(transaction_csv_string)

	if not transaction_df.empty:
		if info['time']:
			trade.close(instrument, transaction_df, hours, info['time'], info['close'], _line)

		if trade_history:
			trade.insert_histoy(trade_history,transaction_df['id'][transaction_df.index[0]])

	filename = 'details.csv'
	details = trade.get_account_details()
	details_csv = file.file_utility.File_utility(filename, drive_id)
	details_csv.set_contents(details)
	details_csv.export_drive()

if __name__ == "__main__":
	main()
