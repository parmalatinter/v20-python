#!/usr/bin/env python

import subprocess
import market.condition

def main():
	
	condition = market.condition.Market()
	if condition.get_is_opening():
		print('true')
		command = 'v20-transaction-get-all'
		print(command)
		res = subprocess.Popen(command, shell=True)
		print(res)
		

		command = 'v20-instrument-data-tables'
		print(command)
		res = subprocess.Popen(command, shell=True)
		print(res)
		
		# command = 'v20-golden-draw'
		# print(command)
		# res = subprocess.Popen(command, shell=True)
		# print(res
	else:
		print('false')

if __name__ == "__main__":
    main()
