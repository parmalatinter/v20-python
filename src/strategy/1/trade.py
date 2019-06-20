#!/usr/bin/env python

import subprocess
import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
from pytz import timezone
from io import StringIO
import time
import copy
import math

import market.condition
import golden.draw
import line.line
import drive.drive
import file.file_utility
import strategy.environ
import strategy.account
import trend.get
import db.history
import db.system
import instrument.candles as inst
import transaction.transactions
import order.market
import order.take_profit
import order.stop_loss
import trade.close
import trade.get_by_trade_ids


class Trade():

    history = db.history.History()
    _system = db.system.System()
    market = order.market.Market()
    _take_profit = order.take_profit.Take_profit()
    _stop_loss = order.stop_loss.Stop_loss()
    _close = trade.close.Close()

    _line = line.line.Line()
    instrument = "USD_JPY"
    units = 10
    limit_units_count = 2
    hours = 3
    trend_usd = trend.get.Trend().get()
    last_df = pd.DataFrame(columns=[])
    caculate_df = pd.DataFrame(columns=[])
    caculate_df_all = pd.DataFrame(columns=[])
    resistande_info = {}

    rule_1 = False
    rule_2 = False
    rule_3 = False
    rule_4 = False
    rule_5 = False
    rule_6 = False
    is_golden = False
    is_dead = False

    upper = 0
    lower = 0
    mean = 0
    late = 0


    def __init__(self, _environ):
        os.environ['TZ'] = 'America/New_York'
        self.instrument = _environ.get('instrument') if _environ.get(
            'instrument') else self.instrument
        units = int(_environ.get('units')) if _environ.get(
            'units') else self.units
        self.units = math.floor(units * self._system.get_last_pl_percent())
        self.hours = int(_environ.get('hours')) if _environ.get(
            'hours') else self.hours

    def get_df(self, csv_string):
        return pd.read_csv(csv_string, sep=',', engine='python', skipinitialspace=True)

    def get_df_by_string(self, csv_string):
        if csv_string:
            return pd.read_csv(pd.compat.StringIO(csv_string), sep=',', engine='python', skipinitialspace=True)
        else:
            return pd.DataFrame(columns=[])

    def get_account_details(self):
        account = strategy.account.Account()
        details = account.get_account_detail()
        return details

    def get_caculate_df(self, df_candles):
        if self.caculate_df.empty:
            draw = golden.draw.Draw()
            self.caculate_df_all = draw.caculate(df_candles)
            self.caculate_df = self.caculate_df_all.tail(1)
            self.resistande_info = draw.candle_supres()

        return self.caculate_df

    def get_caculate_df_all(self, df_candles):
        if self.caculate_df_all.empty:
            self.get_caculate_df(df_candles)

        return self.caculate_df_all

    def get_info(self, candles_df):
        df = candles_df.tail(1)
        return {'time': df['time'][df.index[0]], 'close': df['close'][df.index[0]]}

    def get_histoy_csv(self):
        return self.history.get_all_by_csv()

    def take_profit(self, trade_id, profit_rate, takeProfitOrderID, client_order_comment, event_close_id):

        profit_rate = str(profit_rate)
        if takeProfitOrderID:
            self._take_profit.exec({'tradeID': str(trade_id), 'price': profit_rate,
                                    'replace_order_id': takeProfitOrderID, 'client_order_comment': client_order_comment})
        else:
            self._take_profit.exec({'tradeID': str(
                trade_id), 'price': profit_rate, 'client_order_comment': client_order_comment})
        response = self._take_profit.get_response()
        if response.status == 201:
            self._line.send('fix order take profit #', profit_rate +
                            ' event:' + str(event_close_id) + ' ' + client_order_comment)
        else:
            errors = self._take_profit.get_errors()
            self._line.send('fix order take profit faild #', str(
                errors['errorCode']) + ':' + errors['errorMessage'] + ' event:' + str(event_close_id))

    def stop_loss(self, trade_id, stop_rate, stopLossOrderID, client_order_comment, event_close_id):

        stop_rate = str(stop_rate)

        if stopLossOrderID:
            self._stop_loss.exec({'tradeID': str(trade_id),  'price': stop_rate,
                                  'replace_order_id': stopLossOrderID, 'client_order_comment': client_order_comment})
        else:
            self._stop_loss.exec({'tradeID': str(
                trade_id),  'price': stop_rate, 'client_order_comment': client_order_comment})

        response = self._stop_loss.get_response()

        if response.status == 201:
            self._line.send('fix order stop loss #', stop_rate + ' event:' +
                            str(event_close_id) + ' ' + client_order_comment)
        else:
            errors = self._stop_loss.get_errors()
            self._line.send('fix order stop loss faild #', str(
                errors['errorCode']) + ':' + errors['errorMessage'] + ' event:' + str(event_close_id))

    def order(self, instrument, units, profit_rate, stop_rate, event_open_id, client_order_comment):
        self.market.exec({'instrument': instrument, 'units': units})
        response = self.market.get_response()

        stop_rate = str(stop_rate)
        profit_rate = str(profit_rate)

        if response.status == 201:
            transaction = self.market.get_transaction()
            tradeID = str(self.market.get_trade_id())

            self._take_profit.exec({'tradeID':  tradeID, 'price': profit_rate})
            response1 = self._take_profit.get_response()
            if response1.status == 201:
                self._line.send('order profit #' + tradeID,
                                str(profit_rate) + ' ' + str(event_open_id))
            elif response2.status == 400:
                errors = self._take_profit.get_errors()
                self._line.send('order profit bad request #', str(
                    errors['errorCode']) + ':' + errors['errorMessage'] + ' trade_id:' + tradeID) 
            else:
                errors = self._take_profit.get_errors()
                self._line.send('order profit faild #', str(
                    errors['errorCode']) + ':' + errors['errorMessage'] + ' trade_id:' + tradeID)

            self._stop_loss.exec({'tradeID':  tradeID, 'price': stop_rate})
            response2 = self._stop_loss.get_response()
            if response2.status == 201:
                self._line.send('order stop #' + tradeID,
                                str(stop_rate) + ' ' + str(event_open_id))
            elif response2.status == 400:
                errors = self._stop_loss.get_errors()
                self._line.send('order stop bad request #', str(
                    errors['errorCode']) + ':' + errors['errorMessage'] + ' trade_id:' + tradeID) 
                # Stop lossが通らないほど逆行した場合は逆にポジションを張る
                self.market_close(tradeID, 'ALL', 100)
                self.market.exec({'instrument': instrument, 'units': 0 - units})
                _tradeID = str(self.market.get_trade_id())
                trade_history = {
                    'late': round(self.late, 2),
                    'target_price': 0,
                    'units':0 - units,
                    'event_open_id':100
                }
                self.insert_histoy(trade_history, _tradeID)
            else:
                errors = self._stop_loss.get_errors()
                self._line.send('order stop faild #', str(
                    errors['errorCode']) + ':' + errors['errorMessage'] + ' trade_id:' + tradeID)
            return tradeID

        errors = self.market.get_errors()
        self._line.send('order faild #', errors['errorMessage'])
        return None

    def market_close(self, trade_id, units, event_close_id):
        self._close.exec(trade_id, units)
        response = self._close.get_response()

        if response.status == 201 or response.reason == 'OK':
            self._line.send('expire close  #', str(
                trade_id) + ' event:' + str(event_close_id))
        else:
            self._line.send('expire close  faild #', str(
                trade_id) + ' event:' + str(event_close_id) + ' ' + response.reason)

    def close(self, orders_info, caculate_df, now_dt, last_rate):

        now_dt = datetime.strptime(
            now_dt.replace('T', ' '), '%Y-%m-%d %H:%M:%S')

        for trade_id, row in orders_info.items():


            _price = round(float(row['price']), 2)
            _client_order_comment = ''

            unix = row['openTime'].split(".")[0]
            try:
                time = datetime.fromtimestamp(int(unix), pytz.timezone(
                    "America/New_York")).strftime('%Y-%m-%d %H:%M:%S')
            except:
                time = row['openTime'].split(".")[0]

            trade_dt = datetime.strptime(
                time.replace('T', ' '), '%Y-%m-%d %H:%M:%S')

            delta = now_dt - trade_dt

            takeProfitOrderID = str(row['takeProfitOrderID']) if row['takeProfitOrderID'] else ''
            stopLossOrderID = str(row['stopLossOrderID']) if row['stopLossOrderID'] else ''
            # trailingStopLossOrderID = str(row['trailingStopLossOrderID']) if row['trailingStopLossOrderID'] else ''

            delta_total_minuts = delta.total_seconds()/60
            delta_total_hours = delta_total_minuts/60
            event_close_id = 0

            last_rate = round(last_rate, 2)

            # 3時間経過後 現在値でcloseする
            if delta_total_hours >= self.hours:
                self.market_close(trade_id, 'ALL', 99)

                self.history.update(int(trade_id), 99, 'close 120min')
                continue

            history_df = self.history.get_by_panda(trade_id)

            if history_df.empty:
                # 万が一	hitstoryが存在しない場合は追加する
                trade_history = {
                    'late': _price,
                    'target_price': 0,
                    'units':  row['initialUnits'],
                    'event_open_id': 0,
                    'is_golden': self.is_golden,
                    'is_dead': self.is_dead,
                    'rule_1': self.rule_1,
                    'rule_2': self.rule_2,
                    'rule_3': self.rule_3,
                    'rule_4': self.rule_4,
                    'rule_5': self.rule_5,
                    'rule_6': self.rule_6
                }
                self.insert_histoy(trade_history, trade_id)
                continue

            self.upper = caculate_df['upper'][caculate_df.index[0]]
            self.lower = caculate_df['lower'][caculate_df.index[0]]

            event_close_id = history_df['event_close_id'][history_df.index[0]
                                                          ] if history_df['event_close_id'][history_df.index[0]] else 0

            # 30分 ~ close処理無しの場合
            condition_1 = delta_total_minuts > 30 and event_close_id == 0
            if condition_1:
                state = 'fix order 30min'
                if row['currentUnits'] > 0:
                    profit_rate = _price + 0.05
                    event_close_id = 1
                else:
                    profit_rate = _price - 0.05
                    event_close_id = 2

                _client_order_comment = state + \
                    ' profit reduce ' + str(event_close_id)

                self.take_profit(
                    trade_id, profit_rate, takeProfitOrderID, _client_order_comment, event_close_id)
                self.history.update(int(trade_id), event_close_id, state)
                continue

            # 90分 ~ でclose処理(id:1,2)の場合
            condition_2 = delta_total_minuts >= 90 and event_close_id <= 2
            # 120分 ~ で以前利益があったの場合
            condition_3 = delta_total_minuts >= 120 and event_close_id == 3 and event_close_id == 4
            # 90分 ~ 利益なしの場合
            condition_4 = delta_total_minuts >= 90 and row['unrealizedPL'] < 0
            if condition_2 or condition_3:

                event_close_id = 99
                state = ''
                profit_rate = 0

                # 勝ちの場合
                if row['unrealizedPL'] > 0:
                    if delta_total_minuts > 90:
                        state = 'profit close 120min'
                    else:
                        state = 'profit close 90min'

                    stop_rate = _price

                    # buyの場合 現在価格プラス0.1でcloseする
                    if row['currentUnits'] > 0:

                        if float(self.upper) > float(self.last_rate):
                            profit_rate = float(self.upper)
                        else:
                            profit_rate = float(last_rate) + 0.01

                        event_close_id = 3
                        _client_order_comment = (
                            state + ' win ' + str(event_close_id))

                    # sellの場合 現在価格マイナス0.1でcloseする
                    else:

                        if float(self.lower) < float(last_rate):
                            profit_rate = float(self.lower)
                        else:
                            profit_rate = float(last_rate) - 0.01

                        event_close_id = 4
                        _client_order_comment = (
                            state + ' win ' + str(event_close_id))

                # 負けの場合
                else:

                    if delta_total_minuts > 90:
                        state = 'lose close 120min'
                    else:
                        state = 'lose close 90min'

                    # buyの場合 発注価格でcloseする
                    if row['currentUnits'] > 0:
                        stop_rate = last_rate - 0.5
                        profit_rate = _price + 0.01

                        event_close_id = 5
                        _client_order_comment = (
                            state + ' lose ' + str(event_close_id))

                    # sellの場合 発注価格でcloseする
                    else:
                        stop_rate = last_rate + 0.5
                        profit_rate = _price - 0.01

                        event_close_id = 6
                        _client_order_comment = (
                            state + ' lose ' + str(event_close_id))

                self.take_profit(trade_id, round(
                    profit_rate, 2), takeProfitOrderID, _client_order_comment, event_close_id)
                self.stop_loss(trade_id, round(
                    stop_rate, 2), stopLossOrderID, _client_order_comment, event_close_id)

                self.history.update(int(trade_id), event_close_id, state)
            if condition_4:
                state = 'lose proift 90min'
                # 90分 ~ で利益ない場合　とりあえず発注価格でcloseする
                event_close_id = 7

                self.take_profit(trade_id, _price, takeProfitOrderID, _client_order_comment, event_close_id)
                self.history.update(int(trade_id), event_close_id, state)                                 

    def analyze_trade(self, df_candles, long_units, short_units):

        self.last_df = self.get_caculate_df(df_candles)
        self.late = self.last_df['c'][self.last_df.index[0]]
        self.is_golden = self.last_df['golden'][self.last_df.index[0]]
        self.is_dead = self.last_df['dead'][self.last_df.index[0]]
        self.upper = self.last_df['upper'][self.last_df.index[0]]
        self.lower = self.last_df['lower'][self.last_df.index[0]]
        self.mean = self.last_df['mean'][self.last_df.index[0]]
        self.long_units = long_units
        self.short_units = short_units
        # ルールその1 C3 < lower
        self.rule_1 = self.last_df['rule_1'][self.last_df.index[0]] == 1
        # ルールその2　3つ陽線
        self.rule_2 = self.last_df['rule_2'][self.last_df.index[0]] == 1
        # ルールその3 C3 > upper
        self.rule_3 = self.last_df['rule_3'][self.last_df.index[0]] == 1
        # ルールその4 3つ陰線
        self.rule_4 = self.last_df['rule_4'][self.last_df.index[0]] == 1
        # ルールその5 ボリバン上限突破
        self.rule_5 = self.last_df['rule_5'][self.last_df.index[0]] == 1
        # ルールその6 ボリバン下限限突破
        self.rule_6 = self.last_df['rule_6'][self.last_df.index[0]] == 1

        _units = 0
        _event_open_id = 0
        _message = ''
        _target_price = 0
        _stop_rate = 0

        # ゴールデンクロスの場合
        if self.is_golden:
            self.is_golden = True
            # trendが5以上の場合
            if self.trend_usd['res'] > 15:
                _message = ("buy order 1 #", round(self.late, 2))
                _units = self.units
                _event_open_id = 1
                _target_price = self.late + 0.1

            # trendが-5以下の場合
            elif self.trend_usd['res'] < -15:
                _message = ("sell order 2 #", round(self.late, 2))
                _units = 0 - self.units
                _event_open_id = 2
                _target_price = self.late - 0.1
            # その他の場合
            else:
                _message = ("buy order 3 #", round(self.late, 2))
                _units = self.units
                _event_open_id = 3
                _target_price = self.late + 0.05
        # ゴールデンクロスではない場合
        else:
            self.is_golden = False

        # 新規オーダーする場合
        self.new_trade(
             message=_message,
             units=_units,
             event_open_id=_event_open_id,
             target_price=_target_price
         )

        _event_open_id = 0

        # デッドクロスの場合
        if self.is_dead:
            self.is_dead = True
            # trendが-5以下の場合
            if self.trend_usd['res'] < -15:
                _message = ("sell order 4 #", round(self.late, 2))
                _units = 0 - self.units
                _event_open_id = 4
                _target_price = self.late - 0.1

            # trendが5以上の場合
            elif self.trend_usd['res'] > 15:
                _message = ("buy order 5 #", round(self.late, 2))
                _units = self.units
                _event_open_id = 5
                _target_price = self.late + 0.1
            # その他の場合
            else:
                _message = ("sell order 6 #", round(self.late, 2))
                _units = 0 - self.units
                _event_open_id = 6
                _target_price = self.late - 0.05
        # デッドクロスではない場合
        else:
            self.is_dead = False

        # 新規オーダーする場合
        self.new_trade(
             message=_message,
             units=_units,
             event_open_id=_event_open_id,
             target_price=_target_price
         )
        _event_open_id = 0
        # ルールその1 C3 < lower　且つ　 ルールその2　3つ陽線
        if self.rule_1 and self.rule_2:
            _message = ("buy chance order 7 #", round(self.late, 2))
            _units = self.units
            _event_open_id = 7
            _target_price = self.late + 0.1

        # ルールその3 C3 > upper　且つ　 ルールその4　3つ陰線
        elif self.rule_3 and self.rule_4:
            _message = ("sell chance order 8 #", round(self.late, 2))
            _units = 0 - self.units
            _event_open_id = 8
            _target_price = self.late - 0.1

        # ルールその5 ボリバン上限突破　且つ　 trendが-20以下の場合
        elif self.rule_5 and self.trend_usd['res'] < -20:
            _message = ("sell chance order 9 #", round(self.late, 2))
            _units = self.units
            _event_open_id = 9
            _target_price = self.late + 0.1
            # _stop_rate = mean

        # ルールその6 ボリバン下限突破　且つ　 trendが20以上の場合
        elif self.rule_6 and self.trend_usd['res'] > 20:
            _message = ("buy chance order 10 #", round(self.late, 2))
            _units = 0 - self.units
            _event_open_id = 10
            _target_price = self.late - 0.1
            # _stop_rate = mean

        # 新規オーダーする場合
        self.new_trade(
             message=_message,
             units=_units,
             event_open_id=_event_open_id,
             target_price=_target_price,
             stop_rate=_stop_rate
         )
        _event_open_id = 0
        # 判定基準がなく停滞中
        if not (self.rule_1 or self.rule_2 or self.rule_3 or self.rule_4) and 15 > self.trend_usd['res'] and self.trend_usd['res'] > -15 :
            # 抵抗ライン上限突破
            if self.resistande_info['resistance_high'] < self.late:
                _message = ("sell chance order 11 #", round(self.late, 2))
                _units = 0- self.units
                _event_open_id = 11
                _target_price = self.mean

            # 抵抗ライン下限突破
            elif self.resistande_info['resistance_low'] > self.late:
                _message = ("buy chance order 12 #", round(self.late, 2))
                _units = self.units
                _event_open_id = 12
                _target_price = self.mean

        # 新規オーダーする場合
        self.new_trade(
             message=_message,
             units=_units,
             event_open_id=_event_open_id,
             target_price=_target_price,
         )

    def new_trade(self,  message, units, event_open_id, target_price, stop_rate=0):
        # 新規オーダーする場合
        if event_open_id > 0:
            if units > 0:
                if (self.long_units / units) > (self.limit_units_count):
                    return
                if stop_rate == 0:
                    stop_rate = round(self.mean - ((self.mean - self.lower) / 2) , 2)
            else:
                if (self.short_units / units) < (0 - self.limit_units_count):
                    return
                if stop_rate == 0:
                    stop_rate = round(self.mean + ((self.upper - self.mean) / 2), 2)

            target_price = round(target_price, 2)
            trade_id = self.order(self.instrument, units, target_price, stop_rate, event_open_id, message)
            trade_history = {
                'late': round(self.late, 2),
                'target_price': round(target_price, 2),
                'units':units,
                'event_open_id':event_open_id
            }
            self.insert_histoy(trade_history, trade_id)
            self._line.send(event_open_id, message)

    def insert_histoy(self, trade_history, trade_id):
        self.history.insert(
            trade_id=int(trade_id),
            price=float(trade_history['late']),
            price_target=float(trade_history['target_price']),
            state='open',
            instrument=self.instrument,
            units=trade_history['units'],
            unrealized_pl=0,
            event_open_id=trade_history['event_open_id'],
            trend_1=round(self.trend_usd['v1_usd'], 2),
            trend_2=round(self.trend_usd['v2_usd'], 2),
            trend_3=round(self.trend_usd['v1_jpy'], 2),
            trend_4=round(self.trend_usd['v2_jpy'], 2),
            trend_cal=round(self.trend_usd['res'], 2),
            judge_1=self.is_golden,
            judge_2=self.is_dead,
            rule_1=bool(self.rule_1),
            rule_2=bool(self.rule_2),
            rule_3=bool(self.rule_3),
            rule_4=bool(self.rule_4),
            rule_5=bool(self.rule_5),
            rule_6=bool(self.rule_6),
            memo=''
        )

    def system_update(self, positions_infos):
        self._system.update_profit(
            positions_infos['pl'], positions_infos['unrealizedPL'])
        self._system.export_drive()

    def history_fix(self):
        ids = self.history.get_trade_ids_by_not_update_pl_by_panda()
        get_by_trade_ids = trade.get_by_trade_ids.Get_by_trade_ids()
        rows = get_by_trade_ids.get(ids)

        for trade_id, row in rows.items():
            self.history.fix_update(int(
                trade_id), row['createTime'], row['filledTime'], row['price'], row['realizedPL'], row['type'])


def main():

    condition = market.condition.Market()
    if condition.get_is_opening() == False:
        exit()

    _environ = strategy.environ.Environ()
    reduce_time = float(_environ.get('reduce_time')
                        ) if _environ.get('reduce_time') else 5
    drive_id = _environ.get('drive_id') if _environ.get(
        'drive_id') else '1A3k4a4u4nxskD-hApxQG-kNhlM35clSa'

    googleDrive = drive.drive.Drive(drive_id)
    googleDrive.delete_all()
    time.sleep(5)

    trade = Trade(_environ)

    candles = inst.Candles()
    candles_csv_string = candles.get('USD_JPY', 'M10')
    candles_df = trade.get_df_by_string(candles_csv_string)

    transactions = transaction.transactions.Transactions()
    transactions.get()
    trades_infos = transactions.get_trades()
    positions_infos = transactions.get_positions()
    long_units = transactions.get_short_pos_units()
    short_units = transactions.get_short_pos_units()

    if condition.get_is_eneble_new_order(reduce_time) and not _environ.get('is_stop'):
        trade.analyze_trade(candles_df, long_units, short_units)

    caculate_df = trade.get_caculate_df(candles_df)
    caculate_df_all = trade.get_caculate_df_all(candles_df)

    if trades_infos:
        info = trade.get_info(candles_df)

        if info['time']:
            trade.close(trades_infos, caculate_df, info['time'], info['close'])

    trade.system_update(positions_infos)

    details = trade.get_account_details()
    details_csv = file.file_utility.File_utility('details.csv', drive_id)
    details_csv.set_contents(details)
    details_csv.export_drive()

    # if transactions_csv_string:
    # 	transactions_csv = file.file_utility.File_utility( 'transactions.csv', drive_id)
    # 	transactions_csv.set_contents(transactions_csv_string)
    # 	transactions_csv.export_drive()

    candles_csv = file.file_utility.File_utility('candles.csv', drive_id)
    candles_csv.set_contents(caculate_df_all.to_csv())
    candles_csv.export_drive()

    trade.history_fix()

    histoy_csv_string = trade.get_histoy_csv()
    histoy_csv = file.file_utility.File_utility('history.csv', drive_id)
    histoy_csv.set_contents(histoy_csv_string)
    histoy_csv.export_drive()


if __name__ == "__main__":

    try:
        main()
    except:
        _line = line.line.Line()
        _line.send('Error', sys.exc_info())
