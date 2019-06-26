import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, register_adapter, AsIs
import strategy.environ
import os
import datetime
import pandas as pd
import numpy
import math

import account.details
import strategy.environ
import file.file_utility


class System():

    dbname = "dat1co0qkecvuj"
    user = "kenxmeuwltvdre"
    password = "ffd50671d51cb82f338f3a6c1d003e3ce7e921c675f9e0c248f526ff2e60750d"
    host = "ec2-23-21-148-223.compute-1.amazonaws.com"
    port = "5432"
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filename ='system.csv'

    def __init__(self):
        _environ = strategy.environ.Environ()
        self.dbname = _environ.get('dbname') if _environ.get(
            'dbname') else self.dbname
        self.user = _environ.get('user') if _environ.get('user') else self.user
        self.password = _environ.get('password') if _environ.get(
            'password') else self.password
        self.host = _environ.get('host') if _environ.get('host') else self.host
        self.port = _environ.get('port') if _environ.get('port') else self.port

    def get_conn(self):
        conn = psycopg2.connect("host=" + self.host + " port=" + self.port + " dbname=" +
                                self.dbname + " user=" + self.user + " password=" + self.password)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        return conn

    def exec_query(self, query, args=None, is_get_res=False):
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

        res = pd.read_sql(sql=query, con=conn, index_col=index_col)

        conn.commit()
        cur.close()
        conn.close()

        return res

    def get(self):

        return self.exec_query("SELECT * FROM system ORDER BY update_time;", None, True)

    def get_last_pl_percent(self):

        rows = self.exec_query(
            "SELECT pl_percent FROM system ORDER BY id DESC LIMIT 1;", None, True)

        if rows[0]:
            return rows[0][0]
        else:
            return 1

    def get_by_panda(self, id):
        conn = self.get_conn()

        cur = conn.cursor()

        args = dict(id=id)
        query = 'SELECT * FROM system where id = %(id)s;' % args
        rows = self.exec_query_by_panda(query, 'id')

        cur.close()
        conn.close()

        return rows.tail(1)

    def get_all_by_panda(self):
        conn = self.get_conn()

        cur = conn.cursor()

        rows = self.exec_query_by_panda(
            "SELECT * FROM system ORDER BY update_time;", 'id')

        cur.close()
        conn.close()

        return rows

    def get_all_by_csv(self):
        df = self.get_all_by_panda()

        return df.to_csv(sep=",", line_terminator='\n', encoding='utf-8')

    def insert(self, balance, pl, pl_percent, win_count, lose_count, trade_count, create_time):
        create_time = datetime.datetime.now()

        sql_file = open(self.dir_path + '/query/system/insert.sql', 'r')
        args = (
            balance,
            pl,
            pl_percent,
            win_count,
            lose_count,
            trade_count,
            create_time
        )
        self.exec_query(sql_file.read(), args)

    def delete(self, id):

        query = 'DELETE FROM system where id = %s'

        self.exec_query(query, (id,))

    def update(self, balance, pl, unrealized_pl, pl_percent, win_count, lose_count, trade_count):

        update_time = datetime.datetime.now()

        sql_file = open(self.dir_path + '/query/system/update.sql', 'r')

        self.exec_query(sql_file.read(), (update_time, balance, pl,
                                          unrealized_pl, pl_percent, win_count, lose_count, trade_count))

    def update_profit(self, pl, unrealized_pl):

        update_time = datetime.datetime.now()

        sql_file = open(self.dir_path + '/query/system/update_profit.sql', 'r')

        self.exec_query(sql_file.read(), (update_time, pl, unrealized_pl))

    def create(self):

        sql_file = open(self.dir_path + '/query/system/create.sql', 'r')
        self.exec_query(sql_file.read())

    def drop(self):

        self.exec_query('DROP TABLE IF EXISTS system')

    def export_drive(self):
        _environ = strategy.environ.Environ()
        drive_id = '1-QJOYv1pJuLN9-SXoDpZoZAtMDlfymWe'
        csv_string = self.get_all_by_csv()
        csv = file.file_utility.File_utility(self.filename, drive_id)
        csv.set_contents(csv_string)
        csv.export_drive()

    def delete_all_csv(self):
        for file1 in self.file_list:
            if file1['title'] == self.filename:
                file1.Delete()
                print('deleted: %s, id: %s' % (file1['title'], file1['id']))
        self.reset_file_list()

def main():
    system = System()
    # print(system.get_last_pl_percent())
    details = account.details.Details()
    details_dict = details.get_account()
    # system.drop()
    system.create()
    balance = math.floor(details_dict['Balance'])
    pl = math.floor(details_dict['Profit/Loss'])
    unrealized_pl = math.floor(details_dict['Unrealized Profit/Loss'])
    pl_percent = round(((pl / balance) + 1), 2)
    win_count = 0
    lose_count = 0
    trade_count = 0
    create_time = datetime.datetime.now()

    system.insert(
        balance,
        pl,
        pl_percent,
        win_count,
        lose_count,
        trade_count,
        create_time
    )

    system.update(balance, pl, unrealized_pl, pl_percent,
                  win_count, lose_count, trade_count)
    system.delete_all_csv()
    system.export_drive()


if __name__ == "__main__":
    main()
