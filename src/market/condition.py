#!/usr/bin/env python

import datetime
import calender.get
import strategy.environ

class Market(object):
	is_stop = True

	def __init__(self):
		environ = strategy.environ.Environ()
		self.is_stop = environ.get('is_stop') if environ.get('is_stop') else self.is_stop

	def get_utc_time(self):
		return datetime.datetime.utcnow() + datetime.timedelta(hours=9)

	# 【米国サマータイム（夏時間）】2007年より3月第2日曜日～11月第1日曜日
	# 取引時間：（日本時間）月曜午前7時～土曜午前6時
	# 【米国標準時間（冬時間）】2007年より11月第1日曜日～3月第2日曜日
	# 取引時間：（日本時間）月曜午前7時～土曜午前7時
	def get_is_summer(self, jstTime):
		day = jstTime.day
		res = False

		#1週間前の日付が同月かどうか調べる -> 1日より前か後かで判別
		#dayが1日以降(同月)なら出現回数+1してdayに1週間前の日付を代入(-7する)、1日より前(前の月の日付)なら処理終了
		weeks = 0
		while day > 0:
			weeks += 1
			day -= 7

		if jstTime.month > 3 and jstTime.month < 11:
			is_summer = True
		elif jstTime.month < 3:
			is_summer = False
		elif jstTime.month > 11:
			is_summer = False
		elif jstTime.month == 11 and weeks > 1:
			is_summer = True
		elif jstTime.month == 3 and weeks < 2:
			is_summer = False
		return is_summer


	# CLOSE 米国東部標準時間時(冬時間時 NYクローズは朝7時00分）
	# 		米国東部夏時間時(NYクローズは朝6時00分）
	def get_close(self, is_summer):
		if is_summer:
			return 6
		else:
			return 7

	def judge_is_opening(self, jstTime, close):
			# 元旦
		if jstTime.month == 1 and jstTime.day == 1:
			res = False
		# クリスマス
		elif jstTime.month == 12 and jstTime.day == 25:
			res = False
		# 火曜日～金曜日
		elif jstTime.weekday() >= 1 and jstTime.weekday() <= 4 :
			res = True
		# 月曜日
		# OPEN 朝7時00分
		elif jstTime.weekday() == 0 and jstTime.hour <= 7 :
			res = False
		# 土曜日
		# CLOSE 米国東部標準時間時(冬時間時 NYクローズは朝7時00分）
		# 		米国東部夏時間時(NYクローズは朝6時00分）
		elif jstTime.weekday() >= 5 and jstTime.hour > close :
			res = False
		# 日曜日
		elif jstTime.weekday() >= 6:
			res = False
		else:
			res = True
		return res

	def get_is_opening(self):
		jstTime = self.get_utc_time()
		is_summer = self.get_is_summer(jstTime)
		close = self.get_close(is_summer)
		is_opening = self.judge_is_opening(jstTime, close) 
		return is_opening

	def get_is_eneble_new_order(self, reduce_time = 0):
		jstTime = self.get_utc_time()
		is_summer = self.get_is_summer(jstTime)
		close = self.get_close(is_summer)
		is_eneble = self.judge_is_opening(jstTime, close - reduce_time) 
		if not is_eneble:
			return False
		elif not self.is_stop:
			return False

		_calender = calender.get.Calendar()
		df = _calender.get_df()
		if _calender.in_danger_time(df):
			return False
		return True

def main():
	#日本時間での現在の日付データ取得
	#念のためUTCの時間を取得してから時差分を足してる
	market = Market()
	if market.get_is_opening():
		print('true')
	else:
		print('false')
	if market.get_is_eneble_new_order():
		print('true')
	else:
		print('false')
		
if __name__ == "__main__":
	 main()
