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

def dataGet():

    url = 'https://www.yjfx.jp/gaikaex/mark/calendar/' #みんかぶFXの経済指標URLを取得
    dfs = pd.read_html(url) #テーブルのオブジェクトを生成
    return dfs

def format(dfs):
    now = datetime.datetime.now()
    dfs1 = dfs[0] #.dropna(subset = [4]) #4番にNaNが入っている行はバグなので、削除
    # dfs2 = dfs1.drop(2,axis =1) #2番目の列を削除。axis = 1は列を削除するオプション
    dfs1 = dfs1.replace(np.nan, '', regex=True)
    dfs1 = dfs1.replace('\(月\)', '', regex=True)
    dfs1 = dfs1.replace('\(火\)', '', regex=True)
    dfs1 = dfs1.replace('\(水\)', '', regex=True)
    dfs1 = dfs1.replace('\(木\)', '', regex=True)
    dfs1 = dfs1.replace('\(金\)', '', regex=True)
    dfs1 = dfs1.replace('\(土\)', '', regex=True)
    dfs1 = dfs1.replace('\(日\)', '', regex=True)
    dfs1.columns = ["day", "time", "country", "name","important","predict","result","beforte"] #列名を手動で追加。
    dfs1 = dfs1[(dfs1['country'] == '日本') | (dfs1['country'] == '米国')]
    dfs1 = dfs1[dfs1['important'].str.contains('★★★')]
    dfs1 = dfs1[~dfs1["time"].str.contains('--')]

    dfs1['us_date'] = str(now.year) +  '/' + dfs1['day'] + ' ' + dfs1['time'] + ':00-0900'

    return dfs1

def set_to_drive(filemame, dfs):
    s = StringIO()
    dfs.to_csv(s)
    googleDrive = drive.drive.Drive('1-QJOYv1pJuLN9-SXoDpZoZAtMDlfymWe')
    googleDrive.delete_all()
    text = s.getvalue()
    googleDrive.upload(filemame, text)
    return text


def main():

    dfs = dataGet()
    df = format(dfs)
    
    text = set_to_drive('calendar.csv', df)
    _line = line.line.Line()
    _line.send("calendar",text)

    print(df)


if __name__ == "__main__":
    main()
