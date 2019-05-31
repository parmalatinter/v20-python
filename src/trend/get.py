import requests
import pandas as pd
import json
import math
import instrument.data_tables

class Trend():

	# def __init__(self):
	# 	instrument.data_tables.Data_tables('EURUSD_H1.csv', 'EUR_USD', 24, "H1").set()
	# 	instrument.data_tables.Data_tables('USDJPY_H1.csv', 'USD_JPY', 24, "H1").set()
	# 	instrument.data_tables.Data_tables('USDCHF_H1.csv', 'USD_CHF', 24, "H1").set()
	# 	instrument.data_tables.Data_tables('GBPUSD_H1.csv', 'GBP_USD', 24, "H1").set()
	# 	instrument.data_tables.Data_tables('AUDUSD_H1.csv', 'AUD_USD', 24, "H1").set()
	# 	instrument.data_tables.Data_tables('USDCAD_H1.csv', 'USD_CAD', 24, "H1").set()
	# 	instrument.data_tables.Data_tables('NZDUSD_H1.csv', 'NZD_USD', 24, "H1").set()
	# 	instrument.data_tables.Data_tables('EURJPY_H1.csv', 'EUR_JPY', 24, "H1").set()
	# 	instrument.data_tables.Data_tables('CHFJPY_H1.csv', 'CHF_JPY', 24, "H1").set()
	# 	instrument.data_tables.Data_tables('GBPJPY_H1.csv', 'GBP_JPY', 24, "H1").set()
	# 	instrument.data_tables.Data_tables('AUDJPY_H1.csv', 'AUD_JPY', 24, "H1").set()
	# 	instrument.data_tables.Data_tables('CADJPY_H1.csv', 'CAD_JPY', 24, "H1").set()
	# 	instrument.data_tables.Data_tables('NZDJPY_H1.csv', 'NZD_JPY', 24, "H1").set()
	
	def get(self):
		# https://currency-strength.com/
		res = requests.get("https://currency-strength.com/php/chart1d.json")

		j = res.json()

		df = pd.DataFrame(j[0]).tail(1)
		usd = df['values'][df.index[0]][1]

		df = pd.DataFrame(j[2]).tail(1)
		jpy = df['values'][df.index[0]][1] 
		
		print(usd - jpy)
		return (usd - jpy)

	# 変化率
	def getVal(v1, v2):

		if v2 == 0:
			return

		return math.log(v1/v2)*10000


	def getValM(v1, v2, v3, v4):

		v1 = v1 * v3
		v2 = v2 * v4
		if v2 == 0:
			return

		return math.log(v1/v2)*10000


	def getValD(v1, v2, v3, v4):

		if v3 == 0 or v4 == 0:
			return


		v1 = v1 / v3
		v2 = v2 / v4
		if v2 == 0:
			return

		return math.log(v1/v2)*10000

def main():
	trend = Trend()
	trend.get()
	# v1は起点の価格、v2は現在時刻の価格
	# EURUSD = trend.getVal(v1['EURUSD'],v2['EURUSD']);
	# USDJPY = trend.getVal(v1['USDJPY'],v2['USDJPY']);
	# USDCHF = trend.getVal(v1['USDCHF'],v2['USDCHF']);
	# GBPUSD = trend.getVal(v1['GBPUSD'],v2['GBPUSD']);
	# AUDUSD = trend.getVal(v1['AUDUSD'],v2['AUDUSD']);
	# USDCAD = trend.getVal(v1['USDCAD'],v2['USDCAD']);
	# NZDUSD = trend.getVal(v1['NZDUSD'],v2['NZDUSD']);
	# EURJPY = trend.getValM(v1['EURUSD'],v2['EURUSD'],v1['USDJPY'],v2['USDJPY']);
	# EURCHF = trend.getValM(v1['EURUSD'],v2['EURUSD'],v1['USDCHF'],v2['USDCHF']);
	# EURGBP = trend.getValD(v1['EURUSD'],v2['EURUSD'],v1['GBPUSD'],v2['GBPUSD']);
	# CHFJPY = trend.getValD(v1['USDJPY'],v2['USDJPY'],v1['USDCHF'],v2['USDCHF']);
	# GBPCHF = trend.getValM(v1['GBPUSD'],v2['GBPUSD'],v1['USDCHF'],v2['USDCHF']);
	# GBPJPY = trend.getValM(v1['GBPUSD'],v2['GBPUSD'],v1['USDJPY'],v2['USDJPY']);
	# AUDCHF = trend.getValM(v1['AUDUSD'],v2['AUDUSD'],v1['USDCHF'],v2['USDCHF']);
	# AUDJPY = trend.getValM(v1['AUDUSD'],v2['AUDUSD'],v1['USDJPY'],v2['USDJPY']);
	# CADJPY = trend.getValD(v1['USDJPY'],v2['USDJPY'],v1['USDCAD'],v2['USDCAD']);
	# NZDJPY = trend.getValM(v1['NZDUSD'],v2['NZDUSD'],v1['USDJPY'],v2['USDJPY']);

	# # 各通貨の値の計算
	# Pairs = 7;
	# USD = (-EURUSD+USDJPY+USDCHF-GBPUSD-AUDUSD+USDCAD-NZDUSD)/Pairs;
	# JPY = (-EURJPY-USDJPY-CHFJPY-GBPJPY-AUDJPY-CADJPY-NZDJPY)/Pairs;
if __name__ == "__main__":
	main()






