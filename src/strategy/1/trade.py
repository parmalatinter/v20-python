#!/usr/bin/env python

import subprocess
import os 
import sys
from pathlib import Path
import market.condition
import golden.draw

def main():
	
	condition = market.condition.Market()
	if condition.get_is_opening():
		print('true')
		command = 'v20-transaction-get-all'
		print(command)
		res = subprocess.Popen(command, shell=True)
		res.wait()
		print(res)

		command = 'v20-instrument-data-tables'
		print(command)
		res = subprocess.Popen(command, shell=True)
		res.wait()
		print(res)

		dir_path =Path(__file__).parent.parent.parent / "instrument"
		draw = golden.draw.Draw()
		draw.chdir(dir_path)
		draw.set_file_name('data.csv')
		df = draw.caculate()
		candle_temp = draw.caculate_candle(df)
		draw.plot(df, candle_temp)
	else:
		print('false')

if __name__ == "__main__":
    main()
