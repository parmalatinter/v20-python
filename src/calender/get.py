#!/usr/bin/env python

import urllib.request as request
import json
import sys
import pandas as pd

def dataGet():

    # URIスキーム
    url = 'https://kanemochifx.com/binary_api'

    # 読み込むオブジェクトの作成
    readObj = request.urlopen(url)

    # webAPIからのJSONを取得
    response = readObj.read()

    return response

# webAPIから取得したデータをJSONに変換する
def jsonConversion(jsonStr):

    # webAPIから取得したJSONデータをpythonで使える形に変換する
    return json.loads(jsonStr)

def get_data_flame(jsonStr):
	return pd.read_json(jsonStr)

def main():

    resStr = dataGet()
    res = jsonConversion(resStr)
    df = get_data_flame(resStr)
    del df['indicator_d']
    del df['indicator_m']
    del df['information_source']
    del df['indicator_y']
    del df['indicator_y_m_d_time']
    
    df.columns = ['weight', 'name', 'date']
    df.head()

    print(df)


if __name__ == "__main__":
    main()
