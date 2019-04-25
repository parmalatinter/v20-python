#!/usr/bin/env python

import subprocess
import line.line

def get_account_detail():
	command = 'v20-account-details'
	res = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True)
	res.wait()

	print(command)
	out, err = res.communicate()
	return command + ' ' + out.decode('utf-8')
	

def main():

	_line = line.line.Line()
	res = get_account_detail()
	_line.send('Now details #', res )

if __name__ == "__main__":
    main()
