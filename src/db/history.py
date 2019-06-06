import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, register_adapter, AsIs
import strategy.environ
import os 
import datetime
import pandas as pd
import numpy

class History():

	dbname ="dat1co0qkecvuj"
	user = "kenxmeuwltvdre"
	password = "ffd50671d51cb82f338f3a6c1d003e3ce7e921c675f9e0c248f526ff2e60750d"
	host="ec2-23-21-148-223.compute-1.amazonaws.com"
	port="5432"
	dir_path = os.path.dirname(os.path.realpath(__file__))

	def __init__(self):
		_environ = strategy.environ.Environ()
		self.dbname = _environ.get('dbname') if _environ.get('dbname') else self.dbname
		self.user = _environ.get('user') if _environ.get('user') else self.user
		self.password = _environ.get('password') if _environ.get('password') else self.password
		self.host = _environ.get('host') if _environ.get('host') else self.host
		self.port = _environ.get('port') if _environ.get('port') else self.port

	def get_conn(self):
		conn = psycopg2.connect("host=" + self.host + " port=" + self.port + " dbname=" + self.dbname + " user=" + self.user + " password=" + self.password)
		conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

		return conn

	def exec_query(self, query, args = None, is_get_res = False):
		conn = self.get_conn()

		cur = conn.cursor()
		
		cur.execute(query, args)

		res = None

		if is_get_res:
			res = cur.fetchall()
		
		conn.commit()
		cur.close()
		conn.close()

		return res

	def exec_query_by_panda(self, query, index_col):
		conn = self.get_conn()

		cur = conn.cursor()

		res = pd.read_sql(sql=query, con=conn, index_col=index_col )

		conn.commit()
		cur.close()
		conn.close()

		return res

	def get(self):

		return self.exec_query("SELECT * FROM history;", None, True)

	def get_all_by_panda(self):
		conn = self.get_conn()

		cur = conn.cursor()

		rows = self.exec_query_by_panda("SELECT * FROM history;", 'id')

		cur.close()
		conn.close()

		return rows

	def get_all_by_csv(self):
		df = self.get_all_by_panda()

		return df.to_csv(sep=",", line_terminator='\n', encoding='utf-8')

	def insert(self, trade_id, price, price_target, state, instrument, units, unrealized_pl, event_open_id, trend_1, trend_2, judge_1, judge_2, rule_1, rule_2, rule_3, rule_4, memo=''):
		create_time = datetime.datetime.now() 
		
		sql_file = open(self.dir_path + '/query/insert.sql','r')
		args =(
			trade_id,
			create_time,
			price,
			price_target,
			state,
			instrument,
			units,
			unrealized_pl,
			event_open_id,
			trend_1,
			trend_2,
			judge_1,
			judge_2,
			rule_1,
			rule_2,
			rule_3,
			rule_4,
			memo
		)
		self.exec_query( sql_file.read(), args)


	def delete(self, id):
		create_time = datetime.datetime.now() 
		
		query = 'DELETE FROM history where id = %s'

		self.exec_query( query, (id,))

	def update(self, trade_id, price_close, pl, event_close_id, state):

		update_time = datetime.datetime.now() 
		
		sql_file = open(self.dir_path + '/query/update.sql','r')
		self.exec_query(sql_file.read(),(update_time, price_close, pl, event_close_id, state, trade_id))

	def create(self):

		sql_file = open(self.dir_path + '/query/create.sql','r')
		self.exec_query(sql_file.read())

	def drop(self):

		self.exec_query( 'DROP TABLE IF EXISTS history')

def main():
	history = History()
	# history.drop()
	history.create()
	trade_id = 1
	price = 100.20
	price_target = 100.30
	state = 'state 1'
	instrument = 'USD_JPY'
	units = 10000
	unrealized_pl = 10000
	event_open_id = 1
	trend_1 = 10 
	trend_2 = 20 
	judge_1 = True 
	judge_2 = False
	memo = 'test'
	rule_1 = True
	rule_2 = True
	rule_3 = True
	rule_4 = True

	history.insert(
		trade_id,
		price,
		price_target,
		state,
		instrument,
		units,
		unrealized_pl,
		event_open_id,
		trend_1,
		trend_2,
		judge_1,
		judge_2,
		rule_1,
		rule_2,
		rule_3,
		rule_4,
		memo
	)

	pl = 20000
	price_close = 100.40
	event_close_id = 1
	history.update(trade_id, price_close, pl, event_close_id, state)

	print(history.get_all_by_panda())

	history.delete(event_close_id)

	
if __name__ == "__main__":
	main()






