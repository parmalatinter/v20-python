#!/usr/bin/env python

import pandas as pd
import pandas.tseries.offsets as offsets
import numpy as np
import datetime
from io import StringIO
import line.line
import os
import file.file_utility
import strategy.environ
import market.condition

class Calendar(object):

    folder = '1-QJOYv1pJuLN9-SXoDpZoZAtMDlfymWe'
    calendar_csv = None
    filename = 'calendar.csv'
    hours = 0

    def __init__(self):
        _environ = strategy.environ.Environ()
        os.environ['TZ'] = 'America/New_York'
        self.folder = _environ.get('sub_drive_id') if _environ.get('sub_drive_id') else self.folder
        self.hours = (float(_environ.get('hours')) if _environ.get('hours') else 3) / 2
        self.calendar_csv = file.file_utility.File_utility(self.filename, self.folder)       

    def get_drive_id(self):
        return self.folder

    def dataGet(self):

        url = 'https://www.yjfx.jp/gaikaex/mark/calendar/' #みんかぶFXの経済指標URLを取得
        dfs = pd.read_html(url) #テーブルのオブジェクトを生成
        return dfs

    def format(self, dfs):
        now = datetime.datetime.now()
        dfs1 = dfs[0] #.dropna(subset = [4]) #4番にNaNが入っている行はバグなので、削除
        dfs1.columns = ["day", "time", "country", "name","important","predict","result","beforte"] #列名を手動で追加。
        dfs1 = dfs1[(dfs1['country'] == '日本') | (dfs1['country'] == '米国')]
        dfs1 = dfs1[dfs1['important'].str.contains('★★★')]
        dfs1 = dfs1[~dfs1["time"].str.contains('--')]
        dfs1 = dfs1.replace(np.nan, '', regex=True)
        dfs1 = dfs1.replace('\(月\)', '', regex=True)
        dfs1 = dfs1.replace('\(火\)', '', regex=True)
        dfs1 = dfs1.replace('\(水\)', '', regex=True)
        dfs1 = dfs1.replace('\(木\)', '', regex=True)
        dfs1 = dfs1.replace('\(金\)', '', regex=True)
        dfs1 = dfs1.replace('\(土\)', '', regex=True)
        dfs1 = dfs1.replace('\(日\)', '', regex=True)
        f_brackets1 = lambda x:  x[0:2] if int(x[0:2]) < 24 else str(int(x[0:2]) - 24)
        dfs1['hour'] = dfs1['time'].map(f_brackets1)
        f_brackets2 = lambda x:  x[0:2]
        dfs1['base_hour'] = dfs1['time'].map(f_brackets2)
        f_brackets3 = lambda x:  x[3:5]
        dfs1['minutes'] = dfs1['time'].map(f_brackets3)
        dfs1['us_date'] = str(now.year) +  '/' + dfs1['day'] + ' ' + dfs1['hour'] + ':' + dfs1['minutes']
        dfs1['base_us_datetime'] = pd.to_datetime(dfs1['us_date'])
        f_brackets4 = lambda x: x['base_us_datetime'] + datetime.timedelta(days=+1) if x['hour'] != x['base_hour'] else x['base_us_datetime']
        dfs1['us_datetime'] = dfs1.apply(f_brackets4, axis=1)
        f_brackets5 = lambda x: x['us_datetime'] + datetime.timedelta(hours=-13)
        dfs1['us_datetime'] = dfs1.apply(f_brackets5, axis=1)
        f_brackets6 = lambda x: x['us_datetime'] + datetime.timedelta(hours=-self.hours)
        f_brackets7 = lambda x: x['us_datetime'] + datetime.timedelta(hours=+self.hours)
        dfs1['from_us_datetime'] = dfs1.apply(f_brackets6, axis=1)
        dfs1['to_us_datetime'] = dfs1.apply(f_brackets7, axis=1)

        dfs1 = dfs1.drop("hour", axis=1)
        dfs1 = dfs1.drop("minutes", axis=1)
        dfs1 = dfs1.drop("base_hour", axis=1)
        dfs1 = dfs1.drop("us_date", axis=1)
        dfs1 = dfs1.drop("base_us_datetime", axis=1)

        return dfs1

    def set_to_drive(self, dfs):
        s = StringIO()
        dfs.to_csv(s)
        text = s.getvalue()
        self.calendar_csv.set_contents(text)
        self.calendar_csv.export_drive()
        return text

    def get_df(self):
        calendar_csv_string = self.calendar_csv.get_string()
        df = pd.read_csv(calendar_csv_string, sep=',', engine='python', skipinitialspace=True)
        return df

    def test_log(self, title, now, from_us_datetime, to_us_datetime):
        log = 'log trade {} now : {} {} - {}'.format(title, now.strftime('%Y-%m-%d %H:%M:%S'), from_us_datetime.strftime('%Y-%m-%d %H:%M:%S'), to_us_datetime.strftime('%Y-%m-%d %H:%M:%S'))
        print(log)

    def in_danger_time(self, df):
        df = df[df['important'].str.contains('★★★')]
        now = pd.Timestamp.now()
        print(now.strftime('%Y-%m-%d %H:%M:%S'))
        now = now + offsets.Hour(-13)
        print(now.strftime('%Y-%m-%d %H:%M:%S'))
        # 計算式
        # 答え < 0 or  0 > 0 - self.hours　危険時間帯
        # from 5:00 to 8:00 now 7:00
        # 5:00 - 7:00 -2
        # 7:00 - 8:00 -1

        # from 5:00 to 8:00 now 11:00
        # 5:00 - 11:00 -5
        # 11:00 - 8:00 3

        # from 5:00 to 8:00 now 4:00
        # 5:00 - 4:00 1
        # 4:00 - 8:00 -4

        for index, row in df.iterrows():
            from_us_datetime = pd.to_datetime(row['from_us_datetime'], format='%Y-%m-%d %H:%M:%S')
            to_us_datetime = pd.to_datetime(row['to_us_datetime'], format='%Y-%m-%d %H:%M:%S')
            from_us_datetime_hours = int(round((from_us_datetime - now).total_seconds() / 60 / 60 ))
            to_us_datetime_hours = int(round((now - to_us_datetime).total_seconds() / 60 / 60))
            
            self.test_log(row['name'], now, from_us_datetime, to_us_datetime)
            if from_us_datetime_hours > 0-self.hours and from_us_datetime_hours < 0 and to_us_datetime_hours > 0-self.hours and to_us_datetime_hours < 0:
                log = 'stop trade {} {} - {}'.format(row['name'], from_us_datetime.strftime('%Y-%m-%d %H:%M:%S'), to_us_datetime.strftime('%Y-%m-%d %H:%M:%S'))
                print(log)
                return True
        _market = market.condition.Market()
        # # 日経開始時間
        from_us_datetime = pd.to_datetime(str(now.year) +  '-' + str(now.month) + '-' + str(now.day) + ' 19:00:00', format='%Y-%m-%d %H:%M:%S')
        to_us_datetime = pd.to_datetime(str(now.year) +  '-' + str(now.month) + '-' + str(now.day) + ' 21:00:00', format='%Y-%m-%d %H:%M:%S')
        from_us_datetime_hours = int(round((from_us_datetime - now).total_seconds() / 60 / 60 ))
        to_us_datetime_hours = int(round((now - to_us_datetime).total_seconds() / 60 / 60))
        
        self.test_log('日経開始時間', now, from_us_datetime, to_us_datetime)
        if from_us_datetime_hours > 0-self.hours and from_us_datetime_hours < 0 and to_us_datetime_hours > 0-self.hours and to_us_datetime_hours < 0:
            log = 'stop trade {} now : {} {} - {}'.format('日経開始時間', now.strftime('%Y-%m-%d %H:%M:%S'), from_us_datetime.strftime('%Y-%m-%d %H:%M:%S'), to_us_datetime.strftime('%Y-%m-%d %H:%M:%S'))
            print(log)
            return True

        # # ダウ開始時間
        utc_time = _market.get_utc_time()
        if _market.get_is_summer(utc_time):
            from_us_datetime = pd.to_datetime(str(now.year) +  '-' + str(now.month) + '-' + str(now.day) + ' 08:30:00', format='%Y-%m-%d %H:%M:%S')
            to_us_datetime = pd.to_datetime(str(now.year) +  '-' + str(now.month) + '-' + str(now.day) + ' 10:30:00', format='%Y-%m-%d %H:%M:%S')
        else:
            from_us_datetime = pd.to_datetime(str(now.year) +  '-' + str(now.month) + '-' + str(now.day) + ' 09:30:00', format='%Y-%m-%d %H:%M:%S')
            to_us_datetime = pd.to_datetime(str(now.year) +  '-' + str(now.month) + '-' + str(now.day) + ' 11:30:00', format='%Y-%m-%d %H:%M:%S')

        from_us_datetime_hours = int(round((from_us_datetime - now).total_seconds() / 60 / 60 ))
        to_us_datetime_hours = int(round((now - to_us_datetime).total_seconds() / 60 / 60))
        
        self.test_log('ダウ開始時間', now, from_us_datetime, to_us_datetime)
        if from_us_datetime_hours > 0-self.hours and from_us_datetime_hours < 0 and to_us_datetime_hours > 0-self.hours and to_us_datetime_hours < 0:
            log = 'stop trade {} now : {} {} - {}'.format('ダウ開始時間', now.strftime('%Y-%m-%d %H:%M:%S'), from_us_datetime.strftime('%Y-%m-%d %H:%M:%S'), to_us_datetime.strftime('%Y-%m-%d %H:%M:%S'))
            print(log)
            return True
            
        return False

    def delete_all_by_filename(self):
        self.calendar_csv.delete_all_by_filename()

def main():

    calendar = Calendar()
    dfs = calendar.dataGet()
    df = calendar.format(dfs)
    calendar.delete_all_by_filename()
    text = calendar.set_to_drive(df)
    _line = line.line.Line()
    _line.send("calendar",text)
    # print(calendar.in_danger_time(df))

def test():
    calendar = Calendar()
    dfs = calendar.dataGet()
    df = calendar.format(dfs)

if __name__ == "__main__":
    main()