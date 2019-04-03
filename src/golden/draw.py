#!/usr/bin/env python

import argparse
import common.config
import common.args
from datetime import datetime
import pandas as pd
import numpy as np
 
# ローソク足描写
import matplotlib.pyplot as plt
from mpl_finance import candlestick2_ohlc, volume_overlay as mpf

import os 


def main():

    dir_path = os.path.dirname(os.path.realpath(__file__))
    print(dir_path)
    # データの読み込み
    os.chdir(dir_path + "/datas")
    df = pd.read_csv("usd_10min_api.csv")

    # 不要なカラムを削除
    del df['Unnamed: 0']
    del df['volume']

    # カラム名を変更 ,time,close,open,high,low,volume
    df.columns = ['t', 'c', 'o', 'h', 'l']
    df.head()

    # 終値を10〜30分シフトさせる
    df['c1'] = df['c'].shift(1)
    df['c2'] = df['c'].shift(2)
    df['c3'] = df['c'].shift(3)

    # 始値（open）を10〜30分ずらす
    df['o1'] = df['o'].shift(1)
    df['o2'] = df['o'].shift(2)
    df['o3'] = df['o'].shift(3)

    # カラムの並び替えと削除
    df = df[[
        't', 'c', 'c1', 'c2', 'c3', 
        'o', 'o1', 'o2', 'o3','h', 'l'
    ]]
     
    df.head()

    df['mean'] = df['c'].rolling(window=20).mean()
    df['std'] = df['c'].rolling(window=20).std()
    df['upper'] = df['mean'] + (df['std'] * 2)
    df['lower'] = df['mean'] - (df['std'] * 2)
    df['sma_5'] = np.round(df['c'].rolling(window=5).mean(), 2)
    df['sma_15'] = np.round(df['c'].rolling(window=15).mean(), 2)
    df['diff'] = df['sma_5'] - df['sma_15']

    # ルールその1 C3 < lower
    df['rule_1'] = 1
    df.loc[(df['c3'] < df['lower']),'rule_1']=0

    # ルールその2
    df['rule_2'] = -1
    df.loc[(df['o'] - df['c'] < 0) & (df['o1'] - df['c1'] < 0) & (df['o2'] - df['c2'] < 0),'rule_2']=0

    # ゴールデンクロスを検出
    asign = np.sign(df['diff'])
     
    sz = asign == 0
    while sz.any():
        asign[sz] = np.roll(asign, 1)[sz]
        sz = asign == 0
     
    signchange = ((np.roll(asign, 1) - asign) == -2).astype(int)
    df['golden'] = signchange

    # デッドクロスを検出
    signchange = ((np.roll(asign, 1) - asign) == 2).astype(int)

    # デッドクロスの出現箇所を「-1」としてデータフレームへコピー
    df['dead'] = signchange
    df['dead'][df['dead'] == 1] = -1

    # 最初の19行を削除してインデックスをリセット
    df = df[19:]
    df = df.reset_index(drop=True)
    df.head()

    print(df)

    # # ルール1とルール2が該当するレコードを探す
    # df[(df['rule_1'] == 1.0) & (df['rule_2'] == 1.0)][0:5]

    # ローソク足表示
    ax = plt.subplot(2, 2, 1)
    candle_temp = df[16073:16402]
    candle_temp = candle_temp.reset_index()
    candlestick2_ohlc(
        ax, candle_temp["o"], candle_temp["h"], candle_temp["l"],
        candle_temp["c"], width=0.9, colorup="r", colordown="b"
    )
     
    ax.plot(candle_temp['mean'])
    ax.plot(candle_temp['upper'])
    ax.plot(candle_temp['lower'])
    ax.plot(candle_temp['upper'])
    ax.plot(candle_temp['lower'])
    ax.plot(candle_temp['sma_5'])
    ax.plot(candle_temp['sma_15'])


    ax = plt.subplot(2, 2, 2)
    ax.plot(candle_temp['rule_1'])
    ax.plot(candle_temp['rule_2'])

    ax = plt.subplot(2, 2, 3)
    ax.plot(candle_temp['golden'])
    ax.plot(candle_temp['dead'])



    plt.savefig('my_figure.png')
    plt.show()



if __name__ == "__main__":
    main()
