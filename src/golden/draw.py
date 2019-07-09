#!/usr/bin/env python

import argparse
import common.config
import common.args
from datetime import datetime
import pandas as pd
import numpy as np
import math

import strategy.environ 
import file.file_utility
import line.line

# ローソク足描写
import matplotlib.pyplot as plt
from mpl_finance import candlestick2_ohlc, volume_overlay as mpf

import os
import io

class Draw(object):

    file_name = 'data.csv'
    df = pd.DataFrame(columns=[])

    def supres(self, low, high, n=28, min_touches=2, stat_likeness_percent=1.5, bounce_percent=5):

        df = pd.concat([high, low], keys = ['high', 'low'], axis=1)
        df['sup'] = pd.Series(np.zeros(len(low)))
        df['res'] = pd.Series(np.zeros(len(low)))
        df['sup_break'] = pd.Series(np.zeros(len(low)))
        df['sup_break'] = 0
        df['res_break'] = pd.Series(np.zeros(len(high)))
        df['res_break'] = 0

        for x in range((n-1)+n, len(df)):
            tempdf = df[x-n:x+1].copy()
            sup = None
            res = None
            maxima = tempdf.high.max()
            minima = tempdf.low.min()
            move_range = maxima - minima
            move_allowance = move_range * (stat_likeness_percent / 100)
            bounce_distance = move_range * (bounce_percent / 100)
            touchdown = 0
            awaiting_bounce = False
            for y in range(0, len(tempdf)):
                if abs(maxima - tempdf.high.iloc[y]) < move_allowance and not awaiting_bounce:
                    touchdown = touchdown + 1
                    awaiting_bounce = True
                elif abs(maxima - tempdf.high.iloc[y]) > bounce_distance:
                    awaiting_bounce = False
            if touchdown >= min_touches:
                res = maxima

            touchdown = 0
            awaiting_bounce = False
            for y in range(0, len(tempdf)):
                if abs(tempdf.low.iloc[y] - minima) < move_allowance and not awaiting_bounce:
                    touchdown = touchdown + 1
                    awaiting_bounce = True
                elif abs(tempdf.low.iloc[y] - minima) > bounce_distance:
                    awaiting_bounce = False
            if touchdown >= min_touches:
                sup = minima
            if sup:
                df['sup'].iloc[x] = sup
            if res:
                df['res'].iloc[x] = res
        res_break_indices = list(df[(np.isnan(df['res']) & ~np.isnan(df.shift(1)['res'])) & (df['high'] > df.shift(1)['res'])].index)
        for index in res_break_indices:
            df['res_break'].at[index] = 1
        sup_break_indices = list(df[(np.isnan(df['sup']) & ~np.isnan(df.shift(1)['sup'])) & (df['low'] < df.shift(1)['sup'])].index)
        for index in sup_break_indices:
            df['sup_break'].at[index] = 1
        ret_df = pd.concat([df['sup'], df['res'], df['sup_break'], df['res_break']], keys = ['sup', 'res', 'sup_break', 'res_break'], axis=1)
        return ret_df

    def candle_supres(self):

        n=30
        mint=2
        slp=3.5
        bp=2
        df=self.df

        levels = self.supres(df['l'],
                    df['h'],
                    n=n,
                    min_touches=mint,
                    stat_likeness_percent=slp,
                    bounce_percent=bp)

        fig = plt.figure(figsize=(18, 9))
        ax = plt.subplot(1, 1, 1)

        result = {}
        count = 0
        res_sum = 0
        for sup in levels['sup']:
            if sup != np.nan and sup > 0:
                res_sum = res_sum + sup 
                count = count+1
        if count == 0 or res_sum == 0:
            result['resistance_low'] = 0
        else:
            result['resistance_low'] = res_sum / count
        count = 0
        res_sum = 0
        for res in levels['res']:
            if res != np.nan and res > 0:
                res_sum = res_sum + res 
                count = count+1
        if count == 0 or res_sum == 0:
            result['resistance_high'] = 0
        else:
            result['resistance_high'] = res_sum / count

        return result

    def set_file_name(self, name):
        self.file_name = name

    def chdir(self, path):
        os.chdir(path)

    def caculate(self, _df):
        pd.options.mode.chained_assignment = None
        df = _df.copy()

        # 不要なカラムを削除
        del df['index']
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

        # 平均
        df['mean'] = df['c'].rolling(window=14).mean()
        # 標準偏差
        df['std'] = df['c'].rolling(window=14).std()

        # 1σ
        # df['upper'] = df['mean'] + (df['std'] * 1)
        # df['lower'] = df['mean'] - (df['std'] * 1)
        # 2σ
        df['upper'] = df['mean'] + (df['std'] * 2)
        df['lower'] = df['mean'] - (df['std'] * 2)
        # 3σ
        df['upper_high'] = df['mean'] + (df['std'] * 2)
        df['lower_low'] = df['mean'] - (df['std'] * 2)

        # 期間5単純移動平均
        df['sma_2'] = np.round(df['c'].rolling(window=2).mean(), 2)
        # 期間14単純移動平均
        df['sma_14'] = np.round(df['c'].rolling(window=14).mean(), 2)
        df['diff1'] = df['mean'] - df['l']
        df['diff2'] = df['mean'] - df['h']

        # ルールその1 C3 < lower
        df['rule_1'] = 0
        df.loc[(df['c3'] < df['lower']),'rule_1']=1

        # ルールその2　3つ陽線
        df['rule_2'] = 0
        df.loc[(df['o'] - df['c'] < 0) & (df['o1'] - df['c1'] < 0) & (df['o2'] - df['c2'] < 0),'rule_2']=1


        # ルールその3 C3 > upper
        df['rule_3'] = 0
        df.loc[(df['o3'] > df['upper']),'rule_3']=1

        # ルールその4 3つ陰線
        df['rule_4'] = 0
        df.loc[(df['o'] - df['c'] > 0) & (df['o1'] - df['c1'] > 0) & (df['o2'] - df['c2'] > 0),'rule_4']=1

        # ルールその5 h > upper
        df['rule_5'] = 0
        df.loc[(df['h'] > df['upper_high']),'rule_5']=1

        # ルールその6 l > lower
        df['rule_6'] = 0
        df.loc[(df['l'] < df['lower_low']),'rule_6']=1

        # ゴールデンクロスを検出
        asign1 = np.sign(df['diff1'])
        asign2 = np.sign(df['diff2'])
         
        sz = asign1 == 0
        while sz.any():
            asign1[sz] = np.roll(asign1, 1)[sz]
            sz = asign1 == 0
        sz = asign2 == 0
        while sz.any():
            asign2[sz] = np.roll(asign2, 1)[sz]
            sz = asign2 == 0

        df['golden'] = ((np.roll(asign1, 1) - asign1) == -2).astype(int)

        # デッドクロスを検出
        df['dead'] = ((np.roll(asign2, 1) - asign2) == 2).astype(int)

        # ranges = slice(df['l'],170,None)
 
        # 10分間でポジションを決済
        # df['g_returns'] = df['c'] - df['c'].shift(5)
        # df['d_returns'] = df['c'].shift(5) - df['c']
        # df['g_profit'] = df['g_returns'] * df['golden']
        # df['d_profit'] = df['d_returns'] * df['dead']

        # 最初の19行を削除してインデックスをリセット
        df = df[19:]
        df = df.reset_index(drop=True)
        df.head()


        # # ルール1とルール2が該当するレコードを探す
        # df[(df['rule_1'] == 1.0) & (df['rule_2'] == 1.0)][0:5]

        self.df = df
        return df



    def caculate_candle(self, df):
        ax = plt.subplot(2, 1, 1)
        candle_temp = df.tail(30)
        candle_temp = candle_temp.reset_index()
        candlestick2_ohlc(
            ax, candle_temp["o"], candle_temp["h"], candle_temp["l"],
            candle_temp["c"], width=0.9, colorup="r", colordown="b"
        )
        return candle_temp

    def plot(self, candle_temp, from_index):

        _line = line.line.Line()
        format = "png"
        candle_temp = candle_temp[from_index:].copy()
        # # ローソク足表示
        ax = plt.subplot(2, 1, 1)
        ax.plot(candle_temp['mean'])
        ax.plot(candle_temp['upper_high'])
        ax.plot(candle_temp['lower_low'])
        ax.plot(candle_temp['sma_2'])
        ax.plot(candle_temp['sma_14'])
        ax.plot(candle_temp['h'])
        ax.plot(candle_temp['l'])

        ax = plt.subplot(2, 1, 2, title='golden dead')
        ax.plot(candle_temp['golden'])
        ax.plot(candle_temp['dead'])

        # plt.savefig('draw1.png')
        
        sio = io.BytesIO()
        plt.savefig(sio, format=format)
        _line.send('image', 'golden dead', sio.getvalue())
        # plt.show()

        ax = plt.subplot(2, 1, 1)
        ax.plot(candle_temp['mean'])
        ax.plot(candle_temp['upper_high'])
        ax.plot(candle_temp['lower_low'])
        ax.plot(candle_temp['sma_2'])
        ax.plot(candle_temp['sma_14'])
        ax.plot(candle_temp['h'])
        ax.plot(candle_temp['l'])

        ax = plt.subplot(2, 1, 2, title='rule_1 Close before 3 < lower, rule_2 3 positive')
        ax.plot(candle_temp['rule_1'])
        ax.plot(candle_temp['rule_2'])

        # plt.savefig('draw2.png')
        sio = io.BytesIO()
        plt.savefig(sio, format=format)
        _line.send('image', 'rule_1 Close before 3 < lower, rule_2 3 positive', sio.getvalue())
        # plt.show()

        ax = plt.subplot(2, 1, 1)
        ax.plot(candle_temp['mean'])
        ax.plot(candle_temp['upper_high'])
        ax.plot(candle_temp['lower_low'])
        ax.plot(candle_temp['sma_2'])
        ax.plot(candle_temp['sma_14'])
        ax.plot(candle_temp['h'])
        ax.plot(candle_temp['l'])

        ax = plt.subplot(2, 1, 2, title='rule_3 C3 > upper, rule_4 3 negative')
        ax.plot(candle_temp['rule_3'])
        ax.plot(candle_temp['rule_4'])

        # plt.savefig('draw3.png')
        sio = io.BytesIO()
        plt.savefig(sio, format=format)
        _line.send('image', 'rule_3 C3 > upper, rule_4 3 negative', sio.getvalue())
        # plt.show()

        ax = plt.subplot(2, 1, 1)
        ax.plot(candle_temp['mean'])
        ax.plot(candle_temp['upper_high'])
        ax.plot(candle_temp['lower_low'])
        ax.plot(candle_temp['sma_2'])
        ax.plot(candle_temp['sma_14'])
        ax.plot(candle_temp['h'])
        ax.plot(candle_temp['l'])

        ax = plt.subplot(2, 1, 2, title='rule_5 h > upper, rule_6, l > lower')
        ax.plot(candle_temp['rule_5'])
        ax.plot(candle_temp['rule_6'])

        # plt.savefig('draw4.png')
        sio = io.BytesIO()
        plt.savefig(sio, format=format)
        _line.send('image', 'rule_5 h > upper, rule_6, l > lower', sio.getvalue())
        # plt.show()


    def get_df_by_string(self, csv_string):
        if csv_string:
            return pd.read_csv(pd.compat.StringIO(csv_string), sep=',', engine='python', skipinitialspace=True)
        else:
            return pd.DataFrame(columns=[])

def main():

    environ = strategy.environ.Environ()
    drive_id = environ.get('drive_id') if environ.get('drive_id') else '1K8dkTbwHXcAv60u5O6BELrqT50gheNkC'
    candles_csv = file.file_utility.File_utility('candles.csv', drive_id)
    candles_csv_string = candles_csv.get_string().getvalue()

    draw = Draw()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    draw.chdir(dir_path + "/datas")
    candles_df = draw.get_df_by_string(candles_csv_string)
    draw.plot(candles_df, 50)
    print(candles_df)

    # print(draw.candle_supres())

if __name__ == "__main__":
    main()



