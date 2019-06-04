import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import strategy.environ

class DB():

	dbname ="dat1co0qkecvuj"
	user = "kenxmeuwltvdre"
	password = "ffd50671d51cb82f338f3a6c1d003e3ce7e921c675f9e0c248f526ff2e60750d"
	host="ec2-23-21-148-223.compute-1.amazonaws.com"
	port="5432"

	def __init__(self):
		_environ = strategy.environ.Environ()
		self.dbname = _environ.get('dbname') if _environ.get('dbname') else self.dbname
		self.user = _environ.get('user') if _environ.get('user') else self.user
		self.password = _environ.get('password') if _environ.get('password') else self.password
		self.host = _environ.get('host') if _environ.get('host') else self.host
		self.port = _environ.get('port') if _environ.get('port') else self.port


	def get(self):
		conn = psycopg2.connect("dbname=test user=postgres password=postgres")
		conn = psycopg2.connect("host=" + self.host + " port=" + self.port + " dbname=" + self.dbname + " user=" + self.user + " password=" + self.password)

		conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

		cur = conn.cursor()

		cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'test'")
		exists = cur.fetchone()
		if not exists:
		    cur.execute('CREATE DATABASE test')

		cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
		cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)",(100, "abc'def"))
		cur.execute("SELECT * FROM test;")
		cur.execute('DROP DATABASE IF EXISTS test')
		cur.fetchone()
		conn.commit()
		cur.close()
		conn.close()

	
def main():
	db = DB()
	print(db.get())

if __name__ == "__main__":
	main()






