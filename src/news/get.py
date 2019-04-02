#!/usr/bin/env python

import urllib.request as request
import json
import sys
import pandas as pd
import feedparser

def dataGet():

    # Zai FXのデータ取得
    response = feedparser.parse('http://zai.diamond.jp/list/feed/rssfxnews')

    return response


def get_data_flame(obj):
    # データフレーム形式へ変換
    return pd.DataFrame(obj['entries'])

def main():

    response = dataGet()
    df = get_data_flame(response)
    df = df[['published', 'summary']]

    print(df.head())


if __name__ == "__main__":
    main()
