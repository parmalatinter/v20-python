from time import gmtime, strftime
import subprocess
import os 
from datetime import datetime, timedelta
from pytz import timezone

def main():
	now = datetime.now(timezone('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M:%S')
	before_date= datetime.today() + timedelta(hours=-2)
	before = before_date.strftime('%Y-%m-%d %H:%M:%S')
	args = dict(instrument='USD_JPY', before=before, now=now)
	command = ' v20-instrument-candles %(instrument)s --from-time="%(before)s" --to-time="%(now)s" --alignment-timezone=Japan' % args
	res = subprocess.Popen(command, shell=True)

if __name__ == "__main__":
    main()
