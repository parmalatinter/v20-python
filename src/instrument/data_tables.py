from time import gmtime, strftime
import subprocess
import os 
from datetime import datetime, timedelta
from pytz import timezone

class Data_tables():

	file_name=None
	instrument=None
	before_hours=None
	granularity=None

	def __init__(self, file_name, instrument, before_hours, granularity):
		self.file_name = file_name
		self.instrument = instrument
		self.before_hours = before_hours
		self.granularity = granularity

	def set(self):
		os.environ['TZ'] = 'America/New_York'
		before_date= datetime.today() + timedelta(hours=(0-self.before_hours))
		before = before_date.strftime('%Y-%m-%d %H:%M:%S')

		dir_path = os.path.dirname(os.path.realpath(__file__))
		os.chdir(dir_path)
		args = dict(instrument=self.instrument, before=before, file_name=self.file_name, granularity =self.granularity)
		command = ' v20-instrument-candles %(instrument)s --from-time="%(before)s" --granularity="%(granularity)s" --file_name="%(file_name)s"' % args
		res = subprocess.Popen(command, shell=True)

def main():
	data_tables = Data_tables('candles.csv', 'USD_JPY', 24, "M10")
	data_tables.set()

if __name__ == "__main__":
    main()
