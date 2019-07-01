import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, register_adapter, AsIs
import strategy.environ
import os
import datetime
import pandas as pd
import numpy

import line.line
import common.trace_log

class History():

    dbname = "dat1co0qkecvuj"
    user = "kenxmeuwltvdre"
    password = "ffd50671d51cb82f338f3a6c1d003e3ce7e921c675f9e0c248f526ff2e60750d"
    host = "ec2-23-21-148-223.compute-1.amazonaws.com"
    port = "5432"
    dir_path = os.path.dirname(os.path.realpath(__file__))
    trace_log = common.trace_log.Trace_log()
    logger = trace_log.get()

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

        res = None

        try:
            cur.execute(query, args)
            conn.commit()
            if is_get_res:
                res = cur.fetchall()
        except Exception as e:
            print(e)
            print(query)
            text = query + ', '
            for arg in args:
                text = text + str(type(arg)) + ','
                print(type(arg))
            _line = line.line.Line()
            _line.send(str(e), text)
            self.logger.debug(str(e) + ':' + text)

        cur.close()
        conn.close()

        return res

    def exec_query_by_panda(self, query, index_col):
        conn = self.get_conn()

        cur = conn.cursor()

        res = None

        try:
            res = pd.read_sql(sql=query, con=conn, index_col=index_col)
            conn.commit()
        except Exception as e:
            print(e)
            self.logger.debug(e)

        cur.close()
        conn.close()

        return res

    def get(self):

        return self.exec_query("SELECT * FROM history ORDER BY trade_id;", None, True)

    def get_trade_ids_by_not_update_pl_by_panda(self):

        conn = self.get_conn()

        cur = conn.cursor()

        query = "SELECT trade_id FROM history where price_close = 0.0 OR pl IS NULL OR memo IS NULL OR update_time IS NULL;"
        rows = self.exec_query_by_panda(query, 'trade_id')

        cur.close()
        conn.close()

        return rows.index.values

    def get_by_panda(self, trade_id):
        conn = self.get_conn()

        cur = conn.cursor()

        args = dict(trade_id=trade_id)
        query = 'SELECT * FROM history where trade_id = %(trade_id)s;' % args
        rows = self.exec_query_by_panda(query, 'id')

        cur.close()
        conn.close()

        return rows.tail(1)

    def get_all_by_panda(self):
        conn = self.get_conn()

        cur = conn.cursor()

        sql_file = open(self.dir_path + '/query/history/select_all.sql', 'r')

        rows = self.exec_query_by_panda(sql_file.read(), 'trade_id')

        cur.close()
        conn.close()

        return rows

    def get_by_query(self, query, key):
        conn = self.get_conn()

        cur = conn.cursor()

        rows = self.exec_query_by_panda(query, key)

        cur.close()
        conn.close()

        return rows

    def get_all_by_csv(self):
        df = self.get_all_by_panda()

        return df.to_csv(sep=",", line_terminator='\n', encoding='utf-8')

    def insert(self, trade_id, price, price_target, state, instrument, units, unrealized_pl, event_open_id, trend_1, trend_2, trend_3, trend_4, trend_cal, judge_1, judge_2, rule_1, rule_2, rule_3, rule_4, rule_5, rule_6, resistance_high, resistance_low, memo=''):
        create_time = datetime.datetime.now()

        args = dict(trade_id=trade_id,
                price=price,
                price_target=price_target,
                state=state,
                instrument=instrument,
                units=units,
                unrealized_pl=unrealized_pl,
                event_open_id=event_open_id,
                trend_1=trend_1,
                trend_2=trend_1,
                trend_3=trend_1,
                trend_4=trend_1,
                trend_cal=trend_1,
                judge_1=judge_1,
                judge_2=judge_2,
                rule_1=rule_1,
                rule_2=rule_2,
                rule_3=rule_3,
                rule_4=rule_4,
                rule_5=rule_5,
                rule_6=rule_6,
                resistance_high=resistance_high,
                resistance_low=resistance_low,
                create_time=create_time
            )
        sql_file = open(self.dir_path + '/query/history/insert.sql', 'r')
        self.exec_query(sql_file.read() % args)

    def delete(self, trade_id):

        query = 'DELETE FROM history where trade_id = %s'

        self.exec_query(query, (trade_id,))

    def update(self, trade_id, event_close_id, state):

        update_time = datetime.datetime.now()

        sql_file = open(self.dir_path + '/query/history/update.sql', 'r')
        self.exec_query(sql_file.read(), (update_time, event_close_id, state, trade_id))

    def fix_update(self, trade_id, filledTime, price_close, pl, memo=''):

        sql_file = open(self.dir_path + '/query/history/fix_update.sql', 'r')
        self.exec_query(sql_file.read(), (filledTime, price_close, pl, memo, trade_id))

    def create(self):
        sql_file = open(self.dir_path + '/query/history/create.sql', 'r')
        self.exec_query(sql_file.read())

    def add_column(self, column_name_type):
        self.exec_query(
            'ALTER TABLE history ADD COLUMN IF NOT EXISTS ' + column_name_type)

    def get_todays_win_count(self):
        res = self.get_by_query("SELECT count(*) AS count FROM history WHERE pl > 0 AND create_time > now() - interval '1 day'", 'count')
        return int(res.index[0])


    def get_todays_lose_count(self):
        res = self.get_by_query("SELECT count(*) AS count FROM history WHERE pl < 0 AND create_time > now() - interval '1 day'", 'count')
        return int(res.index[0])

    def drop(self):

        self.exec_query('DROP TABLE IF EXISTS history')


def main():
    history = History()
    # print(history.get_by_query("SELECT memo , event_open_id, count(state), sum(pl) FROM history GROUP BY memo, event_open_id ORDER BY memo, count", 'memo'))
    # print(history.get_by_query("SELECT event_open_id, count(state), sum(pl) AS sum FROM history GROUP BY event_open_id ORDER BY sum DESC", 'event_open_id'))
    # print(history.get_todays_win_count())
    # print(history.get_todays_lose_count())
    

    # history.add_column("resistance_high numeric")
    # history.add_column("resistance_low numeric")
    # history.add_column("trend_cal numeric")
    # history.add_column("rule_5 boolean")
    # history.add_column("rule_6 boolean")
    # history.drop()

    # history.create()
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
    trend_3 = 30
    trend_4 = 40
    trend_5 = 50
    trend_6 = 60
    trend_cal = 100
    judge_1 = True
    judge_2 = False
    # memo = 'test'
    rule_1 = True
    rule_2 = True
    rule_3 = True
    rule_4 = True
    rule_5 = True
    rule_6 = True
    resistance_high = 100
    resistance_low = 100

    history.insert(
        trade_id, price, price_target, state, instrument, units, unrealized_pl, event_open_id, trend_1, trend_2, trend_3, trend_4, trend_cal, judge_1, judge_2, rule_1, rule_2, rule_3, rule_4, rule_5, rule_6, resistance_high, resistance_low
    )

    # pl = 20000
    # price_close = 100.40
    # event_close_id = 1
    # history.update(trade_id, price_close, pl, event_close_id, state)

    # # print(history.get_all_by_panda())
    df = history.get_by_panda(1)
    print(df['trade_id'][df.index[0]])

    history.delete(1)


if __name__ == "__main__":
    main()
