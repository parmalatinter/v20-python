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


import time

class Trade():

	is_ordered = False
	drive_id = ''

	def init(self, drive_id):
		self.is_ordered = False
		self.drive_id = drive_id
		os.environ['TZ'] = 'America/New_York'
		googleDrive = drive.drive.Drive(self.drive_id)
		googleDrive.delete_all()
		time.sleep(5)

	def order(self, instrument, units, price, _line):
		price = round(price, 2)
		args = dict(instrument=instrument, units=units, price=price)
		command = ' v20-order-market %(instrument)s %(units)s --take-profit-price=%(price)s' % args
		print(command)
		res = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True)
		res.wait()

		print(command)
		out, err = res.communicate()
		_line.send('order #', command + ' ' + out.decode('utf-8') )
		self.is_ordered = True

	def close(self, transaction_csv_string, hours, now_dt, _line):

		df = pd.read_csv(transaction_csv_string, sep=',', engine='python', skipinitialspace=True)

		now_dt = datetime.strptime(now_dt, '%Y-%m-%dT%H:%M:%S')

		for index, row in df.iterrows():

			trade_dt = datetime.strptime(row.time, '%Y-%m-%dT%H:%M:%S')
			delta = now_dt - trade_dt

			delta_total_minuts = delta.total_seconds()/60
			delta_total_hours = delta_total_minuts/60

			if delta_total_hours >= hours:
				args = dict(tradeid=row.id, units='ALL')
				command = ' v20-trade-close %(tradeid)s --units="%(units)s"' % args
				res = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True)
				res.wait()
				out, err = res.communicate()
				_line.send('order #', command + ' ' + out.decode('utf-8') )
				self.is_ordered = True

	def get_account_details(self):
		account = strategy.account.Account()
		details = account.get_account_detail()
		return details

	def exec_command(self, command):
		res = subprocess.Popen(command, shell=True)
		res.wait()
		print(res)
		time.sleep(5)

	def golden_tragde(self, instrument, units, candles_csv_string, _line):
		draw = golden.draw.Draw()
		df = draw.caculate(candles_csv_string)
		last_df = df.tail(1)
		late = last_df['c'][last_df.index[0]]
		if last_df['golden'][last_df.index[0]]:
			self.order(instrument, units, late + 0.1, _line)
			print('golden order')
		elif last_df['dead'][last_df.index[0]]:
			self.order(instrument, (0 - units), late - 0.1, _line)
			print('dead order')
		if last_df['rule_1'][last_df.index[0]] == 0 and last_df['rule_2'][last_df.index[0]] == 0:
			print('chance order')
			self.order(instrument, (units * 2), late + 0.1, _line)
			_line.send("chance order #",str(late))

		return last_df['t'][last_df.index[0]]
	
	def get_now_dt(self, candles_csv_string):
		df = pd.read_csv(candles_csv_string, sep=',', engine='python', skipinitialspace=True)
		return df['t'][df.index[0]]
	
def main():

	_environ = strategy.environ.Environ()

	instrument = _environ.get('instrument') if _environ.get('instrument') else "USD_JPY"
	units = _environ.get('units') if _environ.get('units') else 10
	hours = _environ.get('hours') if _environ.get('hours') else 3
	reduce_time = _environ.get('reduce_time') if _environ.get('reduce_time') else 5
	drive_id = _environ.get('drive_id') if _environ.get('drive_id') else '1A3k4a4u4nxskD-hApxQG-kNhlM35clSa'
	now_dt = None

	trade = Trade()
	trade.init(drive_id)

	_line = line.line.Line()
	condition = market.condition.Market()
	if condition.get_is_opening() == False:
		exit()

	trade.exec_command('v20-transaction-get-all')
	trade.exec_command('v20-instrument-data-tables')

	time.sleep(5)
	
	filename = 'candles.csv'
	candles_csv = file.file_utility.File_utility(filename, drive_id)
	candles_csv_string = candles_csv.get_string()
		
	if condition.get_is_eneble_new_order(reduce_time):
		trade.golden_tragde(instrument, units, candles_csv_string, _line)
	
	now_dt = trade.get_now_dt(candles_csv_string)
	
	filename = 'transaction.csv'
	transaction_csv = file.file_utility.File_utility(filename, drive_id)
	transaction_csv_string = transaction_csv.get_string()

	if transaction_csv_string and now_dt:
		trade.close(transaction_csv_string, hours, now_dt, _line)

	filename = 'details.csv'
	details = trade.get_account_details()
	details_csv = file.file_utility.File_utility(filename, drive_id)
	details_csv.set_contents(details)
	details_csv.export_drive()

if __name__ == "__main__":
	main()
