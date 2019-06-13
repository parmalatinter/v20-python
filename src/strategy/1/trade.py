#!/usr/bin/env python

import subprocess
import os 
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
from pytz import timezone
from io import StringIO
import time
import copy

import market.condition
import golden.draw
import line.line
import drive.drive
import file.file_utility
import strategy.environ
import strategy.account
import trend.get
import db.history
import instrument.candles as inst
import transaction.transactions
import order.market
import order.take_profit


class Trade():

	is_ordered = False
	history = db.history.History()
	market = order.market.Market()
	take_profit = order.take_profit.Take_profit()

	_line = line.line.Line()
	instrument =  "USD_JPY"
	units = 10
	hours = 3
	trend_usd = trend.get.Trend().get()
	caculate_df = pd.DataFrame(columns=[])


	def __init__(self, _environ):
		os.environ['TZ'] = 'America/New_York'
		self.is_ordered = False
		self.instrument = _environ.get('instrument') if _environ.get('instrument') else self.instrument
		self.units = int(_environ.get('units')) if _environ.get('units') else self.units
		self.hours = int(_environ.get('hours')) if _environ.get('hours') else self.hours

	def get_is_orderd(self):
		return self.is_ordered

	def get_df(self, csv_string):
		return pd.read_csv(csv_string, sep=',', engine='python', skipinitialspace=True)

	def get_df_by_string(self, csv_string):
		if csv_string:
			return pd.read_csv(pd.compat.StringIO(csv_string), sep=',', engine='python', skipinitialspace=True)
		else:
			return pd.DataFrame(columns=[])

	def order(self, instrument, units, price, event_open_id):
		client_order_comment = ' market order'
		args = {'instrument': instrument, 'units':units, 'take-profit-price' : price, 'client-order-comment' : client_order_comment}
		self.market.exec(args)
		response = self.market.get_response()
		if response.status == 200:
			tansaction = self.market.get_tansaction()
			self._line.send('order #' + str(tansaction.id), str(price) + ' ' + str(event_open_id) )
			self.is_ordered = True
			return tansaction
		else:
			self._line.send('order faild #', command + ' ' + out.decode('utf-8') )
			return None

	def close(self, orders_info, caculate_df, now_dt, last_rate):

		now_dt = datetime.strptime(now_dt.replace('T', ' '), '%Y-%m-%d %H:%M:%S')

		for trade_id, row in orders_info.items():


			unix = row['openTime'].split(".")[0]

			try:
				time = datetime.fromtimestamp(int(unix), pytz.timezone("America/New_York")).strftime('%Y-%m-%d %H:%M:%S')
			except:
				time = row['openTime'].split(".")[0]

			trade_dt = datetime.strptime(time.replace('T', ' '), '%Y-%m-%d %H:%M:%S')

			delta = now_dt - trade_dt

			takeProfitOrderID = str(row['takeProfitOrderID']) if row['takeProfitOrderID'] else ''
			stopLossOrderID = str(row['stopLossOrderID']) if row['stopLossOrderID'] else ''
			trailingStopLossOrderID = str(row['trailingStopLossOrderID']) if row['trailingStopLossOrderID'] else ''

			delta_total_minuts = delta.total_seconds()/60
			delta_total_hours = delta_total_minuts/60

			last_rate = round(last_rate,2)

			# 3時間経過後 現在地でcloseする
			if delta_total_hours >= self.hours:
				args = dict(tradeid=trade_id, units='ALL')
				command = ' v20-trade-close %(tradeid)s --units=%(units)s' % args
				res = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True)
				res.wait()
				out, err = res.communicate()
				self.is_ordered = True
				self.history.update(int(trade_id), last_rate,  float(row['unrealizedPL']), 99, 'CLOSED')
				self._line.send('order #', command + ' ' + out.decode('utf-8') )
				continue
			
			history_df =self.history.get_by_panda(trade_id)

			if history_df.empty:
				continue

			upper = caculate_df['upper'][caculate_df.index[0]]
			lower = caculate_df['lower'][caculate_df.index[0]]

			event_close_id = history_df['event_close_id'][history_df.index[0]] if history_df['event_close_id'][history_df.index[0]] else 0
			
			# 30分 ~ close処理無しの場合
			condition_1 = delta_total_minuts > 30 and event_close_id == 0
			if condition_1:
				state = 'fix order 30min'
				if row['currentUnits'] > 0:
					rate = row['price'] - 0.05
					event_close_id = 1
				else:
					rate = row['price'] + 0.05
					event_close_id = 2

				
				args = dict(tradeid=trade_id, rate=rate, client_order_comment=state + ' profit reduce ' + str(event_close_id), replace_order_id=str(takeProfitOrderID) )
				command1 = ' v20-order-take-profit %(tradeid)s "%(rate)s" --client-order-comment="%(client_order_comment)s"  --replace-order-id="%(takeProfitOrderID)s"' % args
				res = subprocess.Popen(command1, stdout=subprocess.PIPE, stderr=None, shell=True)
				res.wait()
				out, err = res.communicate()
				self._line.send('order #', command1 + ' ' + out.decode('utf-8') )

				self.history.update(int(trade_id), last_rate,  float(row['unrealizedPL']), event_close_id, state)
				continue

			condition_2 = delta_total_minuts >= 90 and event_close_id >= 2
			condition_3 = delta_total_minuts >= 120 and event_close_id <= 4

			# 90分 ~ でclose処理(id:1,2)無しの場合 or 120分 ~ で以前利益があったの場合
			if condition_2 or condition_3:

				args = dict()
				command1 = ''
				args = dict(tradeid=trade_id)
				event_close_id = 99
				rate = round(row['price'],2)
				state = ''

				# 勝ちの場合
				if row['unrealizedPL'] > 0:
					if delta_total_minuts > 90:
						state = 'profit close 120min'
					else:
						state = 'profit close 90min'

					# buyの場合 現在価格プラス0.1でcloseする
					if row['currentUnits'] > 0:

						if float(upper) > float(last_rate):
							profit_rate = float(upper)
						else:
							profit_rate = float(last_rate) + 0.01

						event_close_id = 3
						args = dict(tradeid=trade_id, profit_rate=profit_rate, stop_rate=rate, client_order_comment=(state + ' win ' + event_close_id), profit_id=takeProfitOrderID, stop_id=stopLossOrderID) 

					# sellの場合 現在価格マイナス0.1でcloseする
					else:

						if float(lower) < float(last_rate):
							profit_rate = float(lower)
						else:
							profit_rate = float(last_rate) - 0.01

						event_close_id = 4
						args = dict(tradeid=trade_id, profit_rate=profit_rate, stop_rate=rate, client_order_comment=(state + ' win ' + event_close_id), profit_id=takeProfitOrderID, stop_id=stopLossOrderID) 

				# 負けの場合
				else:
					if delta_total_minuts > 90:
						state = 'lose close 120min'
					else:
						state = 'lose close 90min'

					# buyの場合 発注価格でcloseする
					if row['currentUnits'] > 0:
						stop_rate = float(last_rate) - 0.5

						event_close_id = 5
						args = dict(tradeid=trade_id, profit_rate=rate, stop_rate=stop_rate, client_order_comment=(state + ' lose ' + event_close_id), profit_id=takeProfitOrderID, stop_id=stopLossOrderID) 
						# v20-order-take-profit 1 116 --client-order-comment="test"
					# sellの場合 発注価格でcloseする
					else:
						stop_rate = float(last_rate) + 0.5

						event_close_id = 6
						args = dict(tradeid=trade_id, profit_rate=rate, stop_rate=stop_rate, client_order_comment=(state + ' lose ' + event_close_id), profit_id=takeProfitOrderID, stop_id=stopLossOrderID) 

				command2 = ' v20-order-stop-loss %(tradeid)s %(stop_rate)s --client-order-comment="%(client_order_comment)s" --replace-order-id="%(stop_id)s"' % args

				args = {'tradeid': tradeid1, 'profit_rate':profit_rate, 'replace_order_id' : profit_id, 'client-order-comment' : client_order_comment}
				self.take_profit.exec(args)
				response = self.take_profit.get_response()
				if response.status == 200:
					self._line.send('fix order take profit #', str(profit_rate) + ' ' +str(profit_id) + ' ' + client_order_comment )
					self.is_ordered = True
				else:
					self._line.send('fix order take profit faild #', str(profit_rate) + ' ' +str(profit_id) + ' ' + client_order_comment )
				
				res = subprocess.Popen(command2, stdout=subprocess.PIPE, stderr=None, shell=True)
				res.wait()
				out, err = res.communicate()
				self._line.send('order #', command2 + ' ' + out.decode('utf-8') )

				self.history.update(int(trade_id), last_rate,  float(row['unrealizedPL']), event_close_id, state)


	def get_account_details(self):
		account = strategy.account.Account()
		details = account.get_account_detail()
		return details

	def get_caculate_df(self, df_candles):
		if self.caculate_df.empty:
			draw = golden.draw.Draw()
			df = draw.caculate(df_candles)
			self.caculate_df = df.tail(1)

		return self.caculate_df

	def golden_trade(self, df_candles):
		last_df = self.get_caculate_df(df_candles)
		late = last_df['c'][last_df.index[0]]
		
		is_golden = last_df['golden'][last_df.index[0]]
		is_dead = last_df['dead'][last_df.index[0]]
		_units = 0
		_event_open_id = 0
		_message = ''
		_target_price = 0
		# ルールその1 C3 < lower
		rule_1 = last_df['rule_1'][last_df.index[0]] == 0
		# ルールその2　3つ陽線
		rule_2 = last_df['rule_2'][last_df.index[0]] == 0
		# ルールその3 C3 > upper
		rule_3 = last_df['rule_3'][last_df.index[0]] == 0
		# ルールその4 3つ陰線
		rule_4 = last_df['rule_4'][last_df.index[0]] == 0

		# ゴールデンクロスの場合
		if is_golden:
			is_golden = True
			# trendが5以上の場合
			if self.trend_usd['res'] > 5:
				_message = ("buy order 1 #",str(late))
				_units = self.units
				_event_open_id = 1
				_target_price = late + 0.1
			
			# trendが-5以下の場合
			elif self.trend_usd['res'] < -5:
				_message = ("sell order 2 #",str(late))
				_units = 0 - self.units
				_event_open_id = 2
				_target_price = late - 0.1
			# その他の場合
			else:
				_message = ("buy order 3 #",str(late))
				_units = self.units
				_event_open_id = 3
				_target_price = late + 0.05
		# ゴールデンクロスではない場合
		else:
			is_golden = False

		# デッドクロスの場合
		if is_dead:
			is_dead = True
			# trendが-5以下の場合
			if self.trend_usd['res'] < -5:
				_message = ("sell order 1 #",str(late))
				_units = 0 - self.units
				_event_open_id = 4
				_target_price = late - 0.1

			# trendが5以上の場合
			elif self.trend_usd['res'] > 5:
				_message = ("buy order 2 #",str(late))
				_units = self.units
				_event_open_id = 5
				_target_price = late + 0.1
			# その他の場合
			else:
				_message = ("sell order 3 #",str(late))
				_units = 0 - self.units
				_event_open_id = 6
				_target_price = late - 0.05
		# デッドクロスではない場合
		else:
			is_dead = False

		# ルールその1 C3 < lower　且つ　 ルールその2　3つ陽線
		if rule_1 and rule_2:
			_message = ("buy chance order #",str(late))
			_units = self.units * 2
			_event_open_id = 7
			_target_price = late + 0.1

		# ルールその3 C3 > upper　且つ　 ルールその4　3つ陰線
		if rule_3 and rule_4:
			_message = ("sell chance order #",str(late))
			_units = 0 - (self.units * 2)
			_event_open_id = 8
			_target_price = late - 0.1
		
		# 新規オーダーした場合
		if _event_open_id > 0:
			self.is_ordered = True
			_target_price =  round(_target_price, 2)
			transaction = self.order(self.instrument, _units,_target_price, _event_open_id)
			self._line.send(_event_open_id, _message)

			if not transaction:
				return

			trade_history = {
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
			trade.insert_histoy(trade_history,transaction.id)
	
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
			round(self.trend_usd['v1_usd'], 2),
			round(self.trend_usd['v2_usd'], 2),
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

	googleDrive = drive.drive.Drive(drive_id)
	googleDrive.delete_all()
	time.sleep(5)

	trade = Trade(_environ)
	
	candles = inst.Candles()
	candles_csv_string= candles.get('USD_JPY', 'M10')
	candles_df= trade.get_df_by_string(candles_csv_string)

	trade_history = None
	if condition.get_is_eneble_new_order(reduce_time) and not _environ.get('is_stop'):
		trade.golden_trade(candles_df)

	transactions = transaction.transactions.Transactions()
	transactions_csv_string = transactions.get()

	orders_info = transactions.get_orders()
	transaction_df= trade.get_df_by_string(transactions_csv_string)

	caculate_df = trade.get_caculate_df(candles_df) 
	if orders_info:
		info = trade.get_info(candles_df)

		if info['time']:
			trade.close(orders_info, caculate_df, info['time'], info['close'])
			transactions.get()
			orders_info = transactions.get_orders()

	details = trade.get_account_details()
	details_csv = file.file_utility.File_utility('details.csv', drive_id)
	details_csv.set_contents(details)
	details_csv.export_drive()

	# if transactions_csv_string: 
	# 	transactions_csv = file.file_utility.File_utility( 'transactions.csv', drive_id)
	# 	transactions_csv.set_contents(transactions_csv_string)
	# 	transactions_csv.export_drive()

	candles_csv = file.file_utility.File_utility( 'candles.csv', drive_id)
	candles_csv.set_contents(caculate_df.to_csv())
	candles_csv.export_drive()

	histoy_csv_string = trade.get_histoy_csv()
	histoy_csv = file.file_utility.File_utility( 'history.csv', drive_id)
	histoy_csv.set_contents(histoy_csv_string)
	histoy_csv.export_drive()


if __name__ == "__main__":

	try:
	    main()
	except:
		import traceback
		_line = line.line.Line()
		_line.send('Error', traceback.print_exc() )

	
