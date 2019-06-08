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
import instrument.candles as inst
import transaction.transactions

import time
import copy


class Trade():

	is_ordered = False
	history = db.history.History()
	_line = line.line.Line()
	instrument =  "USD_JPY"
	units = 10
	hours = 3
	trend_usd = trend.get.Trend().get()

	def __init__(self, _environ):
		os.environ['TZ'] = 'America/New_York'
		self.is_ordered = False
		self.instrument = _environ.get('instrument') if _environ.get('instrument')
		self.units = int(_environ.get('units')) if _environ.get('units') 
		self.hours = int(_environ.get('hours')) if _environ.get('hours')

	def get_df(self, csv_string):
		return pd.read_csv(csv_string, sep=',', engine='python', skipinitialspace=True)

	def get_df_by_string(self, csv_string):
		return pd.read_csv(pd.compat.StringIO(csv_string), sep=',', engine='python', skipinitialspace=True)

	def order(self, instrument, units, price):
		args = dict(instrument=instrument, units=units, price=price)
		command = ' v20-order-market %(instrument)s %(units)s --take-profit-price=%(price)s' % args
		res = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True)
		res.wait()
		out, err = res.communicate()
		self._line.send('order #', command + ' ' + out.decode('utf-8') )
		self.is_ordered = True

	def close(self, df, now_dt, last_rate):

		now_dt = datetime.strptime(now_dt.replace('T', ' '), '%Y-%m-%d %H:%M:%S')

		for index, row in df.iterrows():

			trade_dt = datetime.strptime(row.time.replace('T', ' '), '%Y-%m-%d %H:%M:%S')
			delta = now_dt - trade_dt

			delta_total_minuts = delta.total_seconds()/60
			delta_total_hours = delta_total_minuts/60

			if delta_total_hours >= self.hours:
				args = dict(tradeid=row.id, units='ALL')
				command = ' v20-trade-close %(tradeid)s --units="%(units)s"' % args
				res = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True)
				res.wait()
				out, err = res.communicate()
				self.is_ordered = True
				self.history.update(int(row.id), last_rate,  float(row.unrealizedPL), 99, 'CLOSED')
				self._line.send('order #', command + ' ' + out.decode('utf-8') )

	def get_account_details(self):
		account = strategy.account.Account()
		details = account.get_account_detail()
		return details

	def golden_trade(self, df_candles):
		draw = golden.draw.Draw()
		df = draw.caculate(df_candles)
		last_df = df.tail(1)
		late = last_df['c'][last_df.index[0]]
		
		is_golden = last_df['golden'][last_df.index[0]]
		is_dead = last_df['dead'][last_df.index[0]]
		_units = 0
		_event_open_id = 0
		_message = ''
		_target_price = 0
		rule_1 = last_df['rule_1'][last_df.index[0]] == 0
		rule_2 = last_df['rule_2'][last_df.index[0]] == 0
		rule_3 = last_df['rule_3'][last_df.index[0]] == 0
		rule_4 = last_df['rule_4'][last_df.index[0]] == 0

		if is_golden:
			is_golden = True
			if self.trend_usd['res'] > 5:
				_message = ("buy order 1 #",str(late))
				_units = self.units
				_event_open_id = 1
				_target_price = late + 0.1
				
			elif self.trend_usd['res'] < -5:
				_message = ("sell order 2 #",str(late))
				_units = 0 - self.units
				_event_open_id = 2
				_target_price = late - 0.1

			else:
				_message = ("buy order 3 #",str(late))
				_units = self.units
				_event_open_id = 3
				_target_price = late + 0.05
		else:
			is_golden = False

		if is_dead:
			is_dead = True
			if self.trend_usd['res'] < -5:
				_message = ("sell order 1 #",str(late))
				_units = 0 - self.units
				_event_open_id = 4
				_target_price = late - 0.1

			elif self.trend_usd['res'] > 5:
				_message = ("buy order 2 #",str(late))
				_units = self.units
				_event_open_id = 5
				_target_price = late + 0.1
				
			else:
				_message = ("sell order 3 #",str(late))
				_units = 0 - self.units
				_event_open_id = 6
				_target_price = late - 0.05
		else:
			is_dead = False

		if rule_1 and rule_2:
			_message = ("buy chance order #",str(late))
			_units = self.units * 2
			_event_open_id = 7
			_target_price = late + 0.1

		elif rule_3 and rule_4:
			_message = ("sell chance order #",str(late))
			_units = 0 - (self.units * 2)
			_event_open_id = 8
			_target_price = late - 0.1
		
		if _event_open_id > 0:
			self.is_ordered = True
			_target_price =  round(_target_price, 2)
			self.order(self.instrument, _units,_target_price)
			self._line.send(_event_open_id, _message)

			return {
				'late': round(late, 2),
				'target_price' : round(_target_price, 2),
				'units': _units,
				'event_open_id' : _event_open_id,
				'is_golden': is_golden,
				'is_dead' :is_dead,
				'rule_1' :bool(rule_1),
				'rule_2' :bool(rule_2),
				'rule_3' :bool(rule_3),
				'rule_4' :bool(rule_4)
			}

		return None
	
	def get_info(self, df):
		last_df = df.tail(1)
		return {'time' : last_df['time'][last_df.index[0]], 'close' : last_df['close'][last_df.index[0]]}

	def insert_histoy(self, trade_history, trade_id):
		self.history.insert(
			int(trade_id),
			float(trade_history['late']),
			float(trade_history['target_price']),
			'OPEN',
			self.instrument,
			trade_history['units'],
			0,
			trade_history['event_open_id'],
			round(self.trend_usd['v1'], 2),
			round(self.trend_usd['v2'], 2),
			trade_history['is_golden'],
			trade_history['is_dead'],
			trade_history['rule_1'],
			trade_history['rule_2'],
			trade_history['rule_3'],
			trade_history['rule_4'],
			round(self.trend_usd['res'], 2),
		)

	def get_histoy_csv(self):
		return self.history.get_all_by_csv()
	
def main():

	
	condition = market.condition.Market()
	if condition.get_is_opening() == False:
		exit()

	_environ = strategy.environ.Environ()
	reduce_time = float(_environ.get('reduce_time')) if _environ.get('reduce_time') else 5
	drive_id = _environ.get('drive_id') if _environ.get('drive_id') else '1A3k4a4u4nxskD-hApxQG-kNhlM35clSa'
	now_dt = None

	googleDrive = drive.drive.Drive(drive_id)
	googleDrive.delete_all()
	time.sleep(5)

	trade = Trade(_environ)
	
	candles = inst.Candles()
	candles_csv_string= candles.get('USD_JPY', 'M10')
	candles_df= trade.get_df_by_string(candles_csv_string)

	trade_history = None
	if condition.get_is_eneble_new_order(reduce_time):
		trade_history = trade.golden_trade(candles_df)

	transactions = transaction.transactions.Transactions()
	transactions_csv_string = transactions.get()
	transaction_df= trade.get_df_by_string(transactions_csv_string)

	if not transaction_df.empty:
		info = trade.get_info(candles_df)
		if info['time']:
			trade.close(transaction_df, hours, info['time'], info['close'])

		if trade_history:
			last_df = transaction_df.tail(1)
			trade.insert_histoy(trade_history,last_df['id'][last_df.index[0]])

	details = trade.get_account_details()
	details_csv = file.file_utility.File_utility('details.csv', drive_id)
	details_csv.set_contents(details)
	details_csv.export_drive()

	transactions_csv = file.file_utility.File_utility( 'transactions.csv', drive_id)
	transactions_csv.set_contents(transactions_csv_string)
	transactions_csv.export_drive()

	candles_csv = file.file_utility.File_utility( 'candles.csv', drive_id)
	candles_csv.set_contents(candles_csv_string)
	candles_csv.export_drive()

	histoy_csv_string = trade.get_histoy_csv()
	histoy_csv = file.file_utility.File_utility( 'history.csv', drive_id)
	histoy_csv.set_contents(histoy_csv_string)
	histoy_csv.export_drive()


if __name__ == "__main__":
	main()
