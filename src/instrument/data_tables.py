from time import gmtime, strftime
import subprocess
import os 
from datetime import datetime, timedelta
from pytz import timezone

def main():
	print(datetime.now(timezone('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M:%S'))
	now = datetime.now(timezone('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M:%S')
	before_date= datetime.today() + timedelta(hours=-1)
	before = before_date.strftime('%Y-%m-%d %H:%M:%S')   # => 1日前

	# now2 = gmtime() + timedelta(days=1) 
	# YYYY-MM-DD HH:MM:SS
	# print(now)

	dir_path = os.path.dirname(os.path.realpath(__file__))
	# print(dir_path)
	# データの読み込み
	os.chdir(dir_path)
	args = dict(instrument='USD_JPY', before=before, now=now)
	command = ' v20-instrument-candles %(instrument)s --from-time="%(before)s" --to-time="%(now)s" --alignment-timezone=Japan' % args
	print(command)
	res = subprocess.Popen(command, shell=True)
	print(res)

if __name__ == "__main__":
    main()
