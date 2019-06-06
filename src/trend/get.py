import requests
import pandas as pd
import json
import math
import instrument.data_tables
import instrument.candles_trend
import numpy as np

class Trend():
	
	def get(self):
		# https://currency-strength.com/

		candles_trend = instrument.candles_trend.Candles_trend()

		csv = candles_trend.get()

		response_list = [
			{'EUR_USD' : {'val' : None, 'res' : None}},
			{'USD_JPY' : {'val' : None, 'res' : None}},
			{'USD_CHF' : {'val' : None, 'res' : None}},
			{'GBP_USD' : {'val' : None, 'res' : None}},
			{'AUD_USD' : {'val' : None, 'res' : None}},
			{'USD_CAD' : {'val' : None, 'res' : None}},
			{'NZD_USD' : {'val' : None, 'res' : None}},
			{'EUR_JPY' : {'val' : None, 'res' : None}},
			{'CHF_JPY' : {'val' : None, 'res' : None}},
			{'GBP_JPY' : {'val' : None, 'res' : None}},
			{'AUD_JPY' : {'val' : None, 'res' : None}},
			{'CAD_JPY' : {'val' : None, 'res' : None}},
			{'NZD_JPY' : {'val' : None, 'res' : None}}
		]

		df = pd.read_csv(pd.compat.StringIO(csv), sep=',', engine='python', skipinitialspace=True)

		for response in response_list:

			for property in list(response.keys()):
				dfs1 = df[(df['instrument'] == property)]
				index = dfs1.shape[0] -1

				# v1は起点の価格、v2は現在時刻の価格
				response[property]['val'] = {'v1': dfs1['close'].values[0], 'v2': dfs1['close'].values[index-1], 'vl': dfs1['close'].values[index]}

		# v1は起点の価格、vlは現在時刻の価格
		# # 各通貨の値の計算
		Pairs = 7;
		val_list = ['v1', 'v2']
		res = {'v1' : None, 'v2' : None}
		for val in val_list:
			EURUSD = self.getVal(response_list[0]['EUR_USD']['val'][val],response_list[0]['EUR_USD']['val']['vl']);
			USDJPY = self.getVal(response_list[1]['USD_JPY']['val'][val],response_list[1]['USD_JPY']['val']['vl']);
			USDCHF = self.getVal(response_list[2]['USD_CHF']['val'][val],response_list[2]['USD_CHF']['val']['vl']);
			GBPUSD = self.getVal(response_list[3]['GBP_USD']['val'][val],response_list[3]['GBP_USD']['val']['vl']);
			AUDUSD = self.getVal(response_list[4]['AUD_USD']['val'][val],response_list[4]['AUD_USD']['val']['vl']);
			USDCAD = self.getVal(response_list[5]['USD_CAD']['val'][val],response_list[5]['USD_CAD']['val']['vl']);
			NZDUSD = self.getVal(response_list[6]['NZD_USD']['val'][val],response_list[6]['NZD_USD']['val']['vl']);
			EURJPY = self.getValM(response_list[0]['EUR_USD']['val'][val],response_list[0]['EUR_USD']['val']['vl'],response_list[1]['USD_JPY']['val'][val],response_list[1]['USD_JPY']['val']['vl']);
			EURCHF = self.getValM(response_list[0]['EUR_USD']['val'][val],response_list[0]['EUR_USD']['val']['vl'],response_list[2]['USD_CHF']['val'][val],response_list[2]['USD_CHF']['val']['vl']);
			EURGBP = self.getValD(response_list[0]['EUR_USD']['val'][val],response_list[0]['EUR_USD']['val']['vl'],response_list[3]['GBP_USD']['val'][val],response_list[3]['GBP_USD']['val']['vl']);
			CHFJPY = self.getValD(response_list[1]['USD_JPY']['val'][val],response_list[1]['USD_JPY']['val']['vl'],response_list[2]['USD_CHF']['val'][val],response_list[2]['USD_CHF']['val']['vl']);
			GBPCHF = self.getValM(response_list[3]['GBP_USD']['val'][val],response_list[3]['GBP_USD']['val']['vl'],response_list[2]['USD_CHF']['val'][val],response_list[2]['USD_CHF']['val']['vl']);
			GBPJPY = self.getValM(response_list[3]['GBP_USD']['val'][val],response_list[3]['GBP_USD']['val']['vl'],response_list[1]['USD_JPY']['val'][val],response_list[1]['USD_JPY']['val']['vl']);
			AUDCHF = self.getValM(response_list[4]['AUD_USD']['val'][val],response_list[4]['AUD_USD']['val']['vl'],response_list[2]['USD_CHF']['val'][val],response_list[2]['USD_CHF']['val']['vl']);
			AUDJPY = self.getValM(response_list[4]['AUD_USD']['val'][val],response_list[4]['AUD_USD']['val']['vl'],response_list[1]['USD_JPY']['val'][val],response_list[1]['USD_JPY']['val']['vl']);
			CADJPY = self.getValD(response_list[1]['USD_JPY']['val'][val],response_list[1]['USD_JPY']['val']['vl'],response_list[5]['USD_CAD']['val'][val],response_list[5]['USD_CAD']['val']['vl']);
			NZDJPY = self.getValM(response_list[6]['NZD_USD']['val'][val],response_list[6]['NZD_USD']['val']['vl'],response_list[1]['USD_JPY']['val'][val],response_list[1]['USD_JPY']['val']['vl']);

			USD = (-EURUSD+USDJPY+USDCHF-GBPUSD-AUDUSD+USDCAD-NZDUSD)/Pairs;
			JPY = (-EURJPY-USDJPY-CHFJPY-GBPJPY-AUDJPY-CADJPY-NZDJPY)/Pairs;
			res[val] = USD - JPY

		return {
			'res' : (res['v1'] + res['v2']) /2,
			'v1' : res['v1'],
			'v2' : res['v2']
		}

	# 変化率
	def getVal(self, v1, v2):

		if v2 == 0:
			return

		return math.log(v1/v2)*10000


	def getValM(self, v1, v2, v3, v4):

		v1 = v1 * v3
		v2 = v2 * v4
		if v2 == 0:
			return

		return math.log(v1/v2)*10000


	def getValD(self, v1, v2, v3, v4):

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
	print(trend.get())


	# # 各通貨の値の計算
	# Pairs = 7;
	# USD = (-EURUSD+USDJPY+USDCHF-GBPUSD-AUDUSD+USDCAD-NZDUSD)/Pairs;
	# JPY = (-EURJPY-USDJPY-CHFJPY-GBPJPY-AUDJPY-CADJPY-NZDJPY)/Pairs;
if __name__ == "__main__":
	main()






