import requests
import pandas as pd
import json
import math
import instrument.data_tables
import instrument.candles_trend
import numpy as np

class Trend():
	instrument_1 = ''
	instrument_2 = ''
	v1_instrument_1_name = ''
	v2_instrument_1_name = ''
	v1_instrument_2_name = ''
	v2_instrument_2_name = ''

	def __init__(self, instrument_1='USD', instrument_2='JPY'):
		self.instrument_1 = instrument_1
		self.instrument_2 = instrument_2
		self.v1_instrument_1_name = 'v1_{}'.format(instrument_1)
		self.v2_instrument_1_name = 'v2_{}'.format(instrument_1)
		self.v1_instrument_2_name = 'v1_{}'.format(instrument_2)
		self.v2_instrument_2_name = 'v2_{}'.format(instrument_2)

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
			{'NZD_JPY' : {'val' : None, 'res' : None}},
			{'GBP_AUD' : {'val' : None, 'res' : None}},
			{'GBP_CAD' : {'val' : None, 'res' : None}},
			{'GBP_NZD' : {'val' : None, 'res' : None}},
		]

		df = pd.read_csv(pd.compat.StringIO(csv), sep=',', engine='python', skipinitialspace=True)

		for response in response_list:
			for property in list(response.keys()):
				dfs1 = df[(df['instrument'] == property)]
				index = dfs1.shape[0] -1
				# v1は起点の価格、v2は現在時刻の価格
				response[property]['val'] = {'start': dfs1['close'].values[0], 'v1': dfs1['close'].values[index], 'v2': dfs1['close'].values[index-1]}

		# v1は起点の価格、vlは現在時刻の価格
		# # 各通貨の値の計算
		Pairs = 7;
		val_list = ['v1', 'v2']
		res = {'v1' : None, 'v2' : None}
		for val in val_list:
			EURUSD = self.getVal(response_list[0]['EUR_USD']['val']['start'],response_list[0]['EUR_USD']['val'][val]);
			USDJPY = self.getVal(response_list[1]['USD_JPY']['val']['start'],response_list[1]['USD_JPY']['val'][val]);
			USDCHF = self.getVal(response_list[2]['USD_CHF']['val']['start'],response_list[2]['USD_CHF']['val'][val]);
			GBPUSD = self.getVal(response_list[3]['GBP_USD']['val']['start'],response_list[3]['GBP_USD']['val'][val]);
			AUDUSD = self.getVal(response_list[4]['AUD_USD']['val']['start'],response_list[4]['AUD_USD']['val'][val]);
			USDCAD = self.getVal(response_list[5]['USD_CAD']['val']['start'],response_list[5]['USD_CAD']['val'][val]);
			NZDUSD = self.getVal(response_list[6]['NZD_USD']['val']['start'],response_list[6]['NZD_USD']['val'][val]);
			EURJPY = self.getValM(response_list[0]['EUR_USD']['val']['start'],response_list[0]['EUR_USD']['val'][val],response_list[1]['USD_JPY']['val']['start'],response_list[1]['USD_JPY']['val'][val]);
			EURCHF = self.getValM(response_list[0]['EUR_USD']['val']['start'],response_list[0]['EUR_USD']['val'][val],response_list[2]['USD_CHF']['val']['start'],response_list[2]['USD_CHF']['val'][val]);
			EURGBP = self.getValD(response_list[0]['EUR_USD']['val']['start'],response_list[0]['EUR_USD']['val'][val],response_list[3]['GBP_USD']['val']['start'],response_list[3]['GBP_USD']['val'][val]);
			CHFJPY = self.getValD(response_list[1]['USD_JPY']['val']['start'],response_list[1]['USD_JPY']['val'][val],response_list[2]['USD_CHF']['val']['start'],response_list[2]['USD_CHF']['val'][val]);
			GBPCHF = self.getValM(response_list[3]['GBP_USD']['val']['start'],response_list[3]['GBP_USD']['val'][val],response_list[2]['USD_CHF']['val']['start'],response_list[2]['USD_CHF']['val'][val]);
			GBPJPY = self.getValM(response_list[3]['GBP_USD']['val']['start'],response_list[3]['GBP_USD']['val'][val],response_list[1]['USD_JPY']['val']['start'],response_list[1]['USD_JPY']['val'][val]);
			AUDCHF = self.getValM(response_list[4]['AUD_USD']['val']['start'],response_list[4]['AUD_USD']['val'][val],response_list[2]['USD_CHF']['val']['start'],response_list[2]['USD_CHF']['val'][val]);
			AUDJPY = self.getValM(response_list[4]['AUD_USD']['val']['start'],response_list[4]['AUD_USD']['val'][val],response_list[1]['USD_JPY']['val']['start'],response_list[1]['USD_JPY']['val'][val]);
			CADJPY = self.getValD(response_list[1]['USD_JPY']['val']['start'],response_list[1]['USD_JPY']['val'][val],response_list[5]['USD_CAD']['val']['start'],response_list[5]['USD_CAD']['val'][val]);
			NZDJPY = self.getValM(response_list[6]['NZD_USD']['val']['start'],response_list[6]['NZD_USD']['val'][val],response_list[1]['USD_JPY']['val']['start'],response_list[1]['USD_JPY']['val'][val]);

			val_1 = 0
			val_2 = 0
			if self.instrument_1 =='USD' and self.instrument_2 =='JPY':
				val_1 = (-EURUSD+USDJPY+USDCHF-GBPUSD-AUDUSD+USDCAD-NZDUSD)/Pairs;
				val_2 = (-EURJPY-USDJPY-CHFJPY-GBPJPY-AUDJPY-CADJPY-NZDJPY)/Pairs;

			if self.instrument_1 =='GBP' and self.instrument_2 =='USD':
				GBPAUD = self.getValD(response_list[3]['GBP_USD']['val']['start'],response_list[3]['GBP_USD']['val'][val],response_list[4]['AUD_USD']['val']['start'],response_list[4]['AUD_USD']['val'][val]);
				GBPCAD = self.getValD(response_list[3]['GBP_USD']['val']['start'],response_list[3]['GBP_USD']['val'][val],response_list[5]['USD_CAD']['val']['start'],response_list[5]['USD_CAD']['val'][val]);
				GBPNZD = self.getValD(response_list[3]['GBP_USD']['val']['start'],response_list[3]['GBP_USD']['val'][val],response_list[6]['NZD_USD']['val']['start'],response_list[6]['NZD_USD']['val'][val]);
				
				val_1 = (-EURGBP+GBPUSD+GBPCHF+GBPJPY+GBPAUD+GBPCAD+GBPNZD)/Pairs;
				val_2 = (-EURUSD+USDJPY+USDCHF-GBPUSD-AUDUSD+USDCAD-NZDUSD)/Pairs;

			res[val+'_' + self.instrument_1] = float(val_1)
			res[val+'_' + self.instrument_2] = float(val_2)

		return {
			'res' : ((res[self.v1_instrument_1_name] + res[self.v2_instrument_1_name]) - (res[self.v1_instrument_2_name] + res[self.v2_instrument_1_name])) /2 ,
			self.v1_instrument_1_name : res[self.v1_instrument_1_name],
			self.v2_instrument_1_name : res[self.v2_instrument_1_name],
			self.v1_instrument_2_name : res[self.v1_instrument_2_name],
			self.v2_instrument_2_name : res[self.v2_instrument_2_name]
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
	print(trend.get())


	# # 各通貨の値の計算
	# Pairs = 7;
	# USD = (-EURUSD+USDJPY+USDCHF-GBPUSD-AUDUSD+USDCAD-NZDUSD)/Pairs;
	# JPY = (-EURJPY-USDJPY-CHFJPY-GBPJPY-AUDJPY-CADJPY-NZDJPY)/Pairs;
if __name__ == "__main__":
	main()






