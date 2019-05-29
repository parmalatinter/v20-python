import requests
import pandas as pd
import json


class Trend():

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

def main():
	trend = Trend()
	trend.get()

if __name__ == "__main__":
	main()
