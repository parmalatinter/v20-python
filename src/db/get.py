import psycopg2
import strategy.environ

class DB():

	dbname =""
	user = ""
	password = ""
	url = ""

	def __init__(self):
		_environ = strategy.environ.Environ()
		self.dbname = _environ.get('dbname') if _environ.get('dbname') else "test"
		self.user = int(_environ.get('user')) if _environ.get('user') else "postgres"
		self.password = int(_environ.get('password')) if _environ.get('password') else "postgres"
		self.url = int(_environ.get('DATABASE_URL')) if _environ.get('DATABASE_URL') else ""

	def get(self):
		if self.url:
			conn = psycopg2.connect(self.url, sslmode='require')
		else:
			conn = psycopg2.connect("dbname=test user=postgres password=postgres")

		cur = conn.cursor()

		cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'test'")
		exists = cur.fetchone()
		if not exists:
		    cur.execute('CREATE DATABASE test')

		cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
		cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)",(100, "abc'def"))
		cur.execute("SELECT * FROM test;")
		cur.fetchone()
		conn.commit()
		cur.close()
		conn.close()

	
def main():
	db = DB()
	print(db.get())

if __name__ == "__main__":
	main()






