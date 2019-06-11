#!/usr/bin/env python

import pandas as pd
import numpy as np
import datetime
from io import StringIO
import line.line
import os
import file.file_utility
import strategy.environ

class Calendar(object):

    folder = '1-QJOYv1pJuLN9-SXoDpZoZAtMDlfymWe'
    calendar_csv = None
    filename = 'calendar.csv'
    hours = 0

    def __init__(self):
        _environ = strategy.environ.Environ()
        os.environ['TZ'] = 'America/New_York'
        self.calendar_csv = file.file_utility.File_utility(self.filename, self.folder)
        self.hours = (float(_environ.get('hours')) if _environ.get('hours') else 3) / 2

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

    def in_danger_time(self, df):
        df = df[df['important'].str.contains('★★★')]
        now = pd.Timestamp.now()
        
        for index, row in df.iterrows():
            from_us_datetime = pd.to_datetime(row['from_us_datetime'], format='%Y-%m-%d %H:%M:%S')
            to_us_datetime = pd.to_datetime(row['to_us_datetime'], format='%Y-%m-%d %H:%M:%S')
            from_us_datetime_hours = int(round((from_us_datetime - now).total_seconds() / 60 / 60 ))
            to_us_datetime_hours = int(round((now - to_us_datetime).total_seconds() / 60 / 60))
            
            if from_us_datetime_hours < self.hours and  from_us_datetime_hours > 0:
                return True
            if to_us_datetime_hours > -self.hours and  to_us_datetime_hours < 0:
                return True
        return False

    def delete_drive(self):
        self.calendar_csv.delete_drive()
            

def main():

    calendar = Calendar()
    calendar.delete_drive()
    dfs = calendar.dataGet()
    df = calendar.format(dfs)
    text = calendar.set_to_drive(df)
    _line = line.line.Line()
    _line.send("calendar",text)
    # print(calendar.in_danger_time(df))

if __name__ == "__main__":
    main()
