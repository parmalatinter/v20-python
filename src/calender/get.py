#!/usr/bin/env python

import urllib.request as request
import json
import sys
import pandas as pd
import numpy as np
import datetime
import drive.drive
from io import StringIO
import line.line
import re

class Calendar(object):

    folder = '1-QJOYv1pJuLN9-SXoDpZoZAtMDlfymWe'

    def __init__(self):
        os.environ['TZ'] = 'America/New_York'

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
        f_brackets6 = lambda x: x['us_datetime'] + datetime.timedelta(hours=-1)
        f_brackets7 = lambda x: x['us_datetime'] + datetime.timedelta(hours=+1)
        dfs1['from_us_datetime'] = dfs1.apply(f_brackets6, axis=1)
        dfs1['to_us_datetime'] = dfs1.apply(f_brackets7, axis=1)

        dfs1 = dfs1.drop("hour", axis=1)
        dfs1 = dfs1.drop("minutes", axis=1)
        dfs1 = dfs1.drop("base_hour", axis=1)
        dfs1 = dfs1.drop("us_date", axis=1)
        dfs1 = dfs1.drop("base_us_datetime", axis=1)

        return dfs1

    def set_to_drive(self, filemame, dfs):
        s = StringIO()
        dfs.to_csv(s)
        googleDrive = drive.drive.Drive(self.folder)
        googleDrive.delete_all()
        text = s.getvalue()
        googleDrive.upload(filemame, text)
        return text


def main():

    calendar = Calendar()
    dfs = calendar.dataGet()
    df = calendar.format(dfs)
    text = calendar.set_to_drive('calendar.csv', df)
    print(text)
    _line = line.line.Line()
    _line.send("calendar",text)

if __name__ == "__main__":
    main()
