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

import common.trace_log
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
import instrument.candle as inst_one
import transaction.transactions
import transaction.get_by_transaction_ids
import order.market
import order.entry
import order.take_profit
import order.stop_loss
import order.trailing_stop_loss
import trade.close
import order.cancel
import trade.get_by_trade_ids
import account.details
import pricing.get


class Trade():

    _history = None
    _system = None
    _market = None
    _entry = None
    _cancel = None
    _take_profit = None
    _stop_loss = None
    _trailing_stop_loss = None
    _close = None
    _logger = None
    _line = None
    _candle = None
    _trend = None
    _pricing = None
    instrument = "USD_JPY"
    units = 10
    limit_units_count = 2

    trend_usd = {}
    last_df = pd.DataFrame(columns=[])
    candles_df = pd.DataFrame(columns=[])
    caculate_df = pd.DataFrame(columns=[])
    caculate_df_all = pd.DataFrame(columns=[])
    orders_info = None
    new_orders_info = None
    resistande_info = {'resistance_high' : 0, 'resistance_low' : 0}
    now_dt = None

    rule_1 = False
    rule_2 = False
    rule_3 = False
    rule_4 = False
    rule_5 = False
    rule_6 = False
    is_golden = False
    is_dead = False
    is_long_and_short_trade = False
    is_new_trade = False

    upper = 0
    lower = 0
    upper_high = 0
    lower_low = 0
    mean = 0
    late = 0
    min_spred = 0.008
    spred = 0
    last_rate = 0
    long_units = 0
    short_units = 0
    regular_profit_pips = 0.14
    entry_pips = 0.04
    min_profit_pips = 0.05
    normal_pips_range = 15
    normal_trend_range = 15
    close_limit_minutes_1 = 60
    close_limit_minutes_2 = 90
    close_limit_minutes_3 = 135
    close_limit_hours = 6
    close_order_limit_minutes = 90

    first_event_close_ids = [1.1, 1.2, 1.3, 2.1, 2.2, 2.3]
    win_event_close_ids = [1.1, 1.2, 2.1, 2.2, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3]

    def __init__(self, _environ):
        self._line = line.line.Line()
        self._history = db.history.History()
        self._system = db.system.System()
        self._market = order.market.Market()
        self._entry = order.entry.Entry()
        self._cancel = order.cancel.Cancel()
        self._take_profit = order.take_profit.Take_profit()
        self._stop_loss = order.stop_loss.Stop_loss()
        self._trailing_stop_loss = order.trailing_stop_loss.Trailing_stop_loss()
        self._close = trade.close.Close()
        self._candle = inst_one.Candle()
        self._pricing = pricing.get.Pricing()

        self._trend = trend.get.Trend()
        trace_log = common.trace_log.Trace_log()
        self._logger = trace_log.get()

        os.environ['TZ'] = 'America/New_York'
        self.instrument = _environ.get('instrument') if _environ.get('instrument') else self.instrument
        units = int(_environ.get('units')) if _environ.get('units') else self.units
        self.units = math.floor(units * self._system.get_last_pl_percent())
        self.close_limit_hours = int(_environ.get('close_limit_hours')) if _environ.get(
            'close_limit_hours') else self.close_limit_hours
        self.close_limit_minutes_1 = int(_environ.get('close_limit_minutes_1')) if _environ.get(
            'close_limit_minutes_1') else self.close_limit_minutes_1
        self.close_limit_minutes_2 = int(_environ.get('close_limit_minutes_2')) if _environ.get(
            'close_limit_minutes_2') else self.close_limit_minutes_2
        self.close_limit_minutes_3 = int(_environ.get('close_limit_minutes_3')) if _environ.get(
            'close_limit_minutes_3') else self.close_limit_minutes_3
        self.normal_pips_range = int(_environ.get('normal_pips_range')) if _environ.get(
            'normal_pips_range') else self.normal_pips_range
        self.normal_trend_range = int(_environ.get('normal_trend_range')) if _environ.get(
            'normal_trend_range') else self.normal_trend_range
        self.regular_profit_pips = float(_environ.get('regular_profit_pips')) if _environ.get('regular_profit_pips') else self.regular_profit_pips
        self.min_profit_pips =  float(_environ.get('min_profit_pips')) if _environ.get('min_profit_pips') else self.min_profit_pips
        self.entry_pips =  float(_environ.get('entry_pips')) if _environ.get('entry_pips') else self.entry_pips
        self.min_spred =  float(_environ.get('min_spred')) if _environ.get('min_spred') else self.min_spred

    def set_property(self, candles_df, long_units, short_units, orders_info, new_orders_info):
        self.candles_df = candles_df
        self.long_units = long_units
        self.short_units = short_units
        self.is_long_and_short_trade = self.long_units > 0 and self.short_units > 0
        self.trend_usd = self._trend.get()
        self.orders_info = orders_info
        self.new_orders_info = new_orders_info
        self.last_df = self.get_caculate_df(self.candles_df)
        self.is_golden = True if self.last_df['golden'][self.last_df.index[0]] else False
        self.is_dead = True if self.last_df['dead'][self.last_df.index[0]] else False
        self.upper = float(self.last_df['upper'][self.last_df.index[0]])
        self.lower = float(self.last_df['lower'][self.last_df.index[0]])
        self.mean = float(self.last_df['mean'][self.last_df.index[0]])
        self.upper_high = float(self.last_df['upper_high'][self.last_df.index[0]])
        self.lower_low = float(self.last_df['lower_low'][self.last_df.index[0]])

        # ルールその1 C3 < lower
        self.rule_1 = True if self.last_df['rule_1'][self.last_df.index[0]] == 1 else False
        # ルールその2 3つ陽線
        self.rule_2 = True if self.last_df['rule_2'][self.last_df.index[0]] == 1 else False
        # ルールその3 C3 > upper
        self.rule_3 = True if self.last_df['rule_3'][self.last_df.index[0]] == 1 else False
        # ルールその4 3つ陰線
        self.rule_4 = True if self.last_df['rule_4'][self.last_df.index[0]] == 1 else False
        # ルールその5 連続二回ボリバン上限突破
        self.rule_5 = True if self.last_df['rule_5'][self.last_df.index[0]] == 1 else False
        # ルールその6 連続二回ボリバン下限限突破
        self.rule_6 = True if self.last_df['rule_6'][self.last_df.index[0]] == 1 else False
        # ルールその7 判定基準外
        self.rule_7 = True if self.rule_1 or self.rule_2 or self.rule_3 or self.rule_4 else False

        self.update_last_rate()

    def update_last_rate(self):
        price = self._pricing.get(self.instrument)
        self.spred = price['spred']
        self.last_rate = price['price']
        self.now_dt = price['time']

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

    def get_histoy_csv(self):
        return self._history.get_all_by_csv()

    def send_draw(self):
        if self.is_new_trade:
            draw = golden.draw.Draw()
            draw.plot(self.caculate_df_all, 50)

    def take_profit(self, trade_id, profit_rate, takeProfitOrderID, client_order_comment, event_close_id):

        profit_rate = str(profit_rate)
        
        if takeProfitOrderID:
            self._take_profit.exec({
                'tradeID': str(trade_id),
                'price': profit_rate,
                'replace_order_id': takeProfitOrderID,
                'client_trade_tag' : str(event_close_id),
                'client_trade_comment' :client_order_comment,
                'client_order_tag' : str(event_close_id),
                'client_order_comment' :client_order_comment
            })
        else:
            self._take_profit.exec({
                'tradeID': str(trade_id),
                'price': profit_rate,
                'client_trade_tag' : str(event_close_id),
                'client_trade_comment' :client_order_comment,
                'client_order_tag' : str(event_close_id),
                'client_order_comment' :client_order_comment
            })

        response = self._take_profit.get_response()

        message = 'event_close_id: {}, now_rate : {}, trade_id : {}, profit_rate : {}, take_profit_order_id : {}, comment : {}, now : {}'.format(
            str(event_close_id),
            str(self.last_rate),
            str(trade_id),
            str(profit_rate),
            str(takeProfitOrderID),
            client_order_comment,
            self.now_dt.strftime('%Y-%m-%d %H:%M:%S')
        )

        if response.status == 201:
            self._line.send('fix order profit', message)
            return True
        else:
            errors = self._take_profit.get_errors()
            self._line.send('fix order profit failed ' + str(errors['errorCode']) + ' ' + errors['errorMessage'], message)
            return False


    def stop_loss(self, trade_id, stop_rate, stopLossOrderID, trailingStopLossOrderID, client_order_comment, event_close_id, is_trailing=False, distance=0):

        stop_rate = str(stop_rate)

        stop_obj = self._trailing_stop_loss if is_trailing and distance > 0 else self._stop_loss

        if stopLossOrderID:
            stop_obj.exec({
                'tradeID': str(trade_id),
                'price': stop_rate,
                'replace_order_id': stopLossOrderID,
                'client_trade_tag' : str(event_close_id),
                'client_trade_comment' :client_order_comment,
                'client_order_tag' : str(event_close_id),
                'client_order_comment' :client_order_comment,
                'distance' : str(distance)
            })
        else:
            stop_obj.exec({
                'tradeID': str(trade_id),
                'replace_order_id': trailingStopLossOrderID,
                'client_trade_tag' : str(event_close_id),
                'client_trade_comment' :client_order_comment,
                'client_order_tag' : str(event_close_id),
                'client_order_comment' :client_order_comment,
                'distance' : str(distance)
            })

        response = stop_obj.get_response()

        message = 'event_close_id: {}, now_rate : {}, trade_id : {}, stop_rate : {}, stop_loss_order_id : {}, comment : {}, now : {}'.format(
            str(event_close_id),
            str(self.last_rate),
            str(trade_id),
            str(stop_rate),
            str(stopLossOrderID),
            client_order_comment,
            self.now_dt.strftime('%Y-%m-%d %H:%M:%S')
        )

        if response.status == 201:
            self._line.send('fix order stop loss', message)
            return True
        else:
            errors = stop_obj.get_errors()
            self._line.send('fix order stop failed ' + str(errors['errorCode']) + ' ' + errors['errorMessage'], message)
            return False

    def order(self, units, profit_rate, stop_rate, event_open_id, client_order_comment):
        target_rate = self.last_rate - self.entry_pips if units > 0 else self.last_rate + self.entry_pips
        target_rate = round(target_rate,3)
        profit_rate = round(profit_rate,3)
        stop_rate = round(stop_rate,3)

        target_rate = str(target_rate)
        stop_rate = str(stop_rate)
        profit_rate = str(profit_rate)

        self._entry.exec({
            'instrument': self.instrument,
            'units': units,
            'price' : target_rate,
            'take_profit_price' : profit_rate ,
            'stop_loss_price' : stop_rate,
            'client_trade_tag' : str(event_open_id),
            'client_trade_comment' :client_order_comment,
            'client_order_tag' : str(event_open_id),
            'client_order_comment' : client_order_comment,
            'trailing_stop_loss_distance' : str(self.min_profit_pips)
        })
        response = self._entry.get_response()

        transaction_id = self._entry.get_transaction_id()
        message = 'event_open_id: {}, units : {}, target_rate : {}, profit_rate : {}, stop_rate : {}, now_rate : {}, transaction_id : {}, distance: {}, now : {}'.format(
            str(event_open_id),
            str(units),
            str(target_rate),
            str(profit_rate) ,
            str(stop_rate),
            str(self.last_rate),
            str(transaction_id),
            str(self.min_profit_pips),
            self.now_dt.strftime('%Y-%m-%d %H:%M:%S')
        )

        if response.status == 201:
            self._line.send('new order', message)
        else:
            errors = self._entry.get_errors()
            self._line.send('new order failed ' + str(errors['errorCode']) + ' ' + errors['errorMessage'], message)
        
        return int(transaction_id)

    def order_market(self, units, profit_rate, stop_rate, event_open_id, client_order_comment):
        profit_rate = round(profit_rate,3)
        stop_rate = round(stop_rate,3)

        stop_rate = str(stop_rate)
        profit_rate = str(profit_rate)

        self._market.exec({
            'instrument': self.instrument, 
            'units': units, 
            'take_profit_price' : profit_rate , 
            'stop_loss_price' : stop_rate,
            'client_trade_tag' : str(event_open_id),
            'client_trade_comment' :client_order_comment,
            'client_order_tag' : str(event_open_id),
            'client_order_comment' :client_order_comment
        })
        response = self._market.get_response()

        tradeID = self._market.get_trade_id()
        message = 'event_open_id: {}, units : {}, profit_rate : {}, stop_rate : {}, now_rate : {}, trade_id : {}, now : {}'.format(
            str(event_open_id),
            str(units),
            str(profit_rate) ,
            str(stop_rate),
            str(self.last_rate),
            str(tradeID),
            self.now_dt.strftime('%Y-%m-%d %H:%M:%S')
        )

        if response.status == 201:
            self._line.send('new market order', message)
        else:
            errors = self._market.get_errors()
            self._line.send('new market order failed ' + str(errors['errorCode']) + ' ' + errors['errorMessage'], message)
        
        return int(tradeID)

    def market_close(self, trade_id, units, event_close_id):
        self._close.exec(trade_id, units)
        response = self._close.get_response()

        message = 'event_close_id: {}, units : {}, now_rate : {}, trade_id : {}, now : {}'.format(
            str(event_close_id),
            str(units),
            str(self.last_rate),
            str(trade_id),
            self.now_dt.strftime('%Y-%m-%d %H:%M:%S')
        )

        if response.status == 201 or response.reason == 'OK':
            self._line.send('expire close', message)
        else:
            self._line.send('expire close failed ' + response.reason, message)

    def to_date(self, time_str):
        unix = time_str.split(".")[0]
        return datetime.fromtimestamp(int(unix))

    def close(self):
        if not self.now_dt:
            return

        for trade_id, row in self.orders_info.items():

            self.update_last_rate()

            _price = round(float(row['price']), 3)
            _client_order_comment = ''
            unix = row['openTime'].split(".")[0]
            trade_dt = None
            try:
                trade_dt = datetime.strptime(unix.replace('T', ' '), '%Y-%m-%d %H:%M:%S')
            except:
                trade_dt = self.to_date(unix)

            delta = self.now_dt - trade_dt

            takeProfitOrderID = str(row['takeProfitOrderID']) if row['takeProfitOrderID'] else ''
            stopLossOrderID = str(row['stopLossOrderID']) if row['stopLossOrderID'] else ''
            trailingStopLossOrderID = str(row['trailingStopLossOrderID']) if row['trailingStopLossOrderID'] else ''

            delta_total_minuts = delta.total_seconds()/60
            delta_total_hours = delta_total_minuts/60
            event_close_id = 0

            # 3時間経過後 現在値でcloseする
            if delta_total_hours >= self.close_limit_hours:
                self.market_close(trade_id, 'ALL', 99)
                continue

            history_df = self._history.get_by_panda(trade_id)

            if history_df.empty:
                self._line.send('history_df.empty', 'info')
                continue
            event_close_id = float(history_df['event_close_id'][history_df.index[0]]) if history_df['event_close_id'][history_df.index[0]] else 0
            # 利益がunitsの0.15倍ある場合は決済
            if row['unrealizedPL'] / self.units  > 0.15:
                _client_order_comment = 'profit max close'
                self.stop_loss(trade_id, 0, stopLossOrderID, trailingStopLossOrderID, _client_order_comment, event_close_id, True, 0.05)
                continue

            pips = 0
            # close_limit_minutes_1分 ~ close処理無しの場合 
            # close_limit_minutes_2分 ~ close処理無し 両建ての場合 
            condition_1 = delta_total_minuts > self.close_limit_minutes_1 and event_close_id <= 0 and not self.is_long_and_short_trade
            condition_2 = delta_total_minuts > self.close_limit_minutes_2 and event_close_id <= 0 and self.is_long_and_short_trade
            if condition_1 or condition_2:
                if delta_total_minuts >= self.close_limit_minutes_1:
                    state = 'fix order {} min'.format(str(self.close_limit_minutes_1))
                else:
                    state = 'fix order {} min'.format(str(self.close_limit_minutes_2))

                 # buyの場合 
                if row['currentUnits'] > 0:
                    
                    pips = self.last_rate - _price
                    # 利益0.1以上
                    if pips > self.regular_profit_pips:
                        event_close_id = 11
                        _client_order_comment = state + ' profit imidiete ' + str(event_close_id)
                        self.stop_loss(trade_id, 0, stopLossOrderID, trailingStopLossOrderID, _client_order_comment, event_close_id, True, 0.05)
                        continue
                    # 利益0.5以上
                    elif pips > 0.05:
                        event_close_id = 12
                        profit_rate = self.last_rate + 0.03
                    # それ以外
                    else:
                        event_close_id = 13
                        # spred分の損を回収
                        profit_rate = _price + 0.02
                # sellの場合 
                else:
                    pips = _price - self.last_rate
                    # 利益0.1以上
                    if pips > self.regular_profit_pips:
                        event_close_id = 21
                        _client_order_comment = state + ' profit imidiete ' + str(event_close_id)
                        self.stop_loss(trade_id, 0, stopLossOrderID, trailingStopLossOrderID, _client_order_comment, event_close_id, True, 0.05)
                        continue
                    # 利益0.5以上
                    elif pips > 0.1:
                        event_close_id = 22
                        profit_rate = self.last_rate - 0.03
                    # それ以外
                    else:
                        event_close_id = 23
                        # spred分の損を回収
                        profit_rate = _price - 0.02

                _client_order_comment = state + ' profit reduce ' + str(event_close_id)

                self.take_profit(trade_id, round(profit_rate, 3), takeProfitOrderID, _client_order_comment, event_close_id)
                continue

            # 90分 ~ でclose処理(id:1,2)の場合
            condition_3 = delta_total_minuts >= self.close_limit_minutes_2 and event_close_id in self.first_event_close_ids
            # 120分 ~ で以前利益があったの場合
            condition_4 = delta_total_minuts >= self.close_limit_minutes_3 and event_close_id in self.win_event_close_ids
            # 90分 ~ 利益なしの場合
            condition_5 = delta_total_minuts >= self.close_limit_minutes_2 and row['unrealizedPL'] < 0
            if condition_3 or condition_4:

                event_close_id = 99
                state = ''
                profit_rate = 0

                if delta_total_minuts >= self.close_limit_minutes_2:
                    state = 'fix order {} min'.format(str(self.close_limit_minutes_2))
                else:
                    state = 'fix order {} min'.format(str(self.close_limit_minutes_3))

                # 勝ちの場合
                if row['unrealizedPL'] > 0:

                    stop_rate = _price
                    
                    # buyの場合 現在価格プラス0.1でcloseする
                    if row['currentUnits'] > 0:
                        
                        _client_order_comment = state + ' win 3'
                        # regular_profit_pips以上利益の場合closeする
                        if self.last_rate - _price > self.regular_profit_pips:
                            event_close_id = 31
                            profit_rate = self.last_rate + 0.02
                        # ボリバン上限突破
                        elif self.upper_high < self.last_rate:
                            event_close_id = 32
                            self.market_close(trade_id, 'ALL', event_close_id)
                            continue
                        # それ以外
                        else:
                            event_close_id = 33
                            profit_rate = self.last_rate + 0.03

                        if not stopLossOrderID or not trailingStopLossOrderID:
                            distance = round(stop_rate-self.last_rate, 3)
                            self.stop_loss(trade_id, 0, stopLossOrderID, trailingStopLossOrderID, _client_order_comment, event_close_id, True, distance)

                    # sellの場合 現在価格マイナス0.1でcloseする
                    else:
                        _client_order_comment = state + ' win 4'
                        # regular_profit_pips以上利益の場合closeする
                        if _price - self.last_rate > self.regular_profit_pips:
                            event_close_id = 41
                            profit_rate = self.last_rate - 0.02
                        # ボリバン下限突破
                        elif self.lower_low > self.last_rate:
                            event_close_id = 42
                            self.market_close(trade_id, 'ALL', event_close_id)
                            continue
                        # それ以外
                        else:
                            event_close_id = 43
                            profit_rate = self.last_rate - 0.03

                        if not stopLossOrderID or not trailingStopLossOrderID:
                            distance = round(self.last_rate - stop_rate, 3)
                            self.stop_loss(trade_id, 0, stopLossOrderID, trailingStopLossOrderID, _client_order_comment, event_close_id, True, distance)

                # 負けの場合
                else:

                    # buyの場合 発注価格+0.03でcloseする
                    if row['currentUnits'] > 0:
                        stop_rate = self.last_rate - 0.5
                        profit_rate = _price + 0.03

                        event_close_id = 50
                        _client_order_comment = state + ' lose ' + str(event_close_id)

                    # sellの場合 発注価格-0.03でcloseする
                    else:
                        stop_rate = self.last_rate + 0.5
                        profit_rate = _price - 0.03

                        event_close_id = 60
                        _client_order_comment = state + ' lose ' + str(event_close_id)

                if not stopLossOrderID or not trailingStopLossOrderID:
                    self.stop_loss(trade_id, round(stop_rate, 3), stopLossOrderID, _client_order_comment, event_close_id)

                self.take_profit(trade_id, round(profit_rate, 3), takeProfitOrderID, _client_order_comment, event_close_id)

            if condition_5:
                if delta_total_minuts >= self.close_limit_minutes_2:
                    state = 'lose proift 0 order {} min'.format(str(self.close_limit_minutes_2))
                else:
                    state = 'lose proift 0 order {} min'.format(str(self.close_limit_minutes_3))

                _client_order_comment = state + ' lose ' + str(event_close_id)

                # 90分 ~ で利益ない場合 とりあえず発注価格でcloseする
                event_close_id = 70

                # buyの場合 発注価格+0.01でcloseする
                if row['currentUnits'] > 0:
                    profit_rate = _price + 0.01
                # buyの場合 発注価格-0.01でcloseする
                else:
                    profit_rate = _price - 0.01

                self.take_profit(trade_id, round(profit_rate, 3), takeProfitOrderID, _client_order_comment, event_close_id)                                 

        for order_id, row in self.new_orders_info.items():

            delta = self.now_dt - row['time']
            delta_total_minuts = delta.total_seconds()/60

            if delta_total_minuts >= self.close_order_limit_minutes or self.min_spred < self.spred:
                self._cancel.exec({'order_id': order_id})
                response = self._cancel.get_response()
                message = '# {}, now : {}'.format(order_id, self.now_dt.strftime('%Y-%m-%d %H:%M:%S'))

                if response.status == 201:
                    self._line.send('order cancel s', message)
                else:
                    errors = self._cancel.get_errors()
                    self._line.send('order cancel ' + str(response.status) + ' ' + errors['errorMessage'], message)


    def analyze_trade(self):

        _units = 0
        _event_open_id = 0
        _message = ''
        _target_price = 0
        _stop_rate = 0

        self.update_last_rate()

        if self.min_spred < self.spred:
            return

        print('start trade')

        # ゴールデンクロスの場合
        if self.is_golden:
            self._line.send('is_golden', str(self.last_rate))
            # trendがnormal_trend_range以上の場合
            if self.trend_usd['res'] > self.normal_trend_range:
                _message = 'buy golden order trend > normal_trend_range 1 # {}'.format(str(self.last_rate))
                _units = self.units
                _event_open_id = 11
                _target_price = self.last_rate + 0.1
                _stop_rate = self.last_rate - 0.1

            # trendが-normal_trend_range以下の場合
            elif self.trend_usd['res'] < 0-self.normal_trend_range:
                _message = 'buy golden order trend < -normal_trend_range 2  # {}'.format(str(self.last_rate))
                _units = self.units
                _event_open_id = 12
                _target_price = self.last_rate + 0.1
                _stop_rate = self.last_rate - 0.1
            # その他の場合
            else:
                _message = 'buy golden order trend other 3 # {}'.format(str(self.last_rate))
                _units = self.units
                _event_open_id = 13
                _target_price = self.last_rate + self.entry_pips
                _stop_rate = self.last_rate - self.regular_profit_pips

                self.new_trade(
                     message=_message,
                     units=_units,
                     event_open_id=_event_open_id,
                     target_price=_target_price,
                     stop_rate=_stop_rate,
                     is_market=False
                 )

                _units = 0 - _units
                _target_price = self.last_rate - self.entry_pips
                _stop_rate = self.last_rate + self.regular_profit_pips

        # 新規オーダーする場合
        self.new_trade(
             message=_message,
             units=_units,
             event_open_id=_event_open_id,
             target_price=_target_price,
             stop_rate=_stop_rate,
             is_market=False
         )

        _event_open_id = 0

        # デッドクロスの場合
        if self.is_dead:
            self._line.send('is_dead', str(self.last_rate))
            # trendが-normal_trend_range以下の場合
            if self.trend_usd['res'] < 0 - self.normal_trend_range:
                _message = 'sell dead order trend < -normal_trend_range 4 # {}'.format(str(self.last_rate))
                _units = 0 - self.units
                _event_open_id = 21
                _target_price = self.last_rate - 0.1
                _stop_rate = self.last_rate + 0.1

            # trendがnormal_trend_range以上の場合
            elif self.trend_usd['res'] > self.normal_trend_range:
                _message = 'sell dead order trend > normal_trend_range 5 # {}'.format(str(self.last_rate))
                _units = 0 - self.units
                _event_open_id = 22
                _target_price = self.last_rate - 0.1
                _stop_rate = self.last_rate + 0.1
            # その他の場合
            else:
                _message = 'sell dead order other 6 # {}'.format(str(self.last_rate))
                _units = self.units
                _event_open_id = 23
                _target_price = self.last_rate - self.entry_pips
                _stop_rate = self.last_rate + self.regular_profit_pips

                self.new_trade(
                     message=_message,
                     units= 0 - _units,
                     event_open_id=_event_open_id,
                     target_price=_target_price,
                     stop_rate=_stop_rate,
                     is_market=False
                 )

                _target_price = self.last_rate + self.entry_pips
                _stop_rate = self.last_rate - self.regular_profit_pips

        # 新規オーダーする場合
        self.new_trade(
             message=_message,
             units=_units,
             event_open_id=_event_open_id,
             target_price=_target_price,
             stop_rate=_stop_rate,
             is_market=False
         )
        _event_open_id = 0
        # ルールその1 C3 < lower 且つ  ルールその2 3つ陽線
        if self.rule_1 and self.rule_2:
            _message = 'buy chance order 7 # {}'.format(str(self.last_rate))
            _units = self.units
            _event_open_id = 31
            _target_price = self.last_rate + self.regular_profit_pips

        # ルールその3 C3 > upper 且つ  ルールその4 3つ陰線
        elif self.rule_3 and self.rule_4:
            _message = 'sell chance order 8 # {}'.format(str(self.last_rate))
            _units = 0 - (self.units)
            _event_open_id = 32
            _target_price = self.last_rate - self.regular_profit_pips

        # ルールその5 連続二回ボリバン上限突破
        elif self.rule_5:
            _message = 'buy chance order 9 # {}'.format(str(self.last_rate))
            _units = self.units
            _event_open_id = 33
            _target_price = self.last_rate + self.entry_pips
            _stop_rate = self.last_rate - self.regular_profit_pips

            self.new_trade(
                 message=_message,
                 units=_units,
                 event_open_id=_event_open_id,
                 target_price=_target_price,
                 stop_rate=_stop_rate,
                 is_market=False
             )

            _units = 0 - _units
            _target_price = self.last_rate - self.entry_pips
            _stop_rate = self.last_rate + self.regular_profit_pips

        # ルールその6 連続二回ボリバン下限突破
        elif self.rule_6:
            _message = 'sell chance order 10 # {}'.format(str(self.last_rate))
            _units = self.units
            _event_open_id = 41
            _target_price = self.last_rate - self.entry_pips
            _stop_rate = self.last_rate + self.regular_profit_pips

            self.new_trade(
                 message=_message,
                 units= 0 - _units,
                 event_open_id=_event_open_id,
                 target_price=_target_price,
                 stop_rate=_stop_rate,
                 is_market=False
             )

            _target_price = self.last_rate + self.entry_pips
            _stop_rate = self.last_rate - self.regular_profit_pips

        # 新規オーダーする場合
        self.new_trade(
             message=_message,
             units=_units,
             event_open_id=_event_open_id,
             target_price=_target_price,
             stop_rate=_stop_rate,
             is_market=False
         )
        _event_open_id = 0
        # 判定基準がなく停滞中
        if not self.rule_7 and self.normal_trend_range > self.trend_usd['res'] and self.trend_usd['res'] > 0 - self.normal_trend_range :
            # 抵抗ライン上限突破
            if self.resistande_info['resistance_high'] == 0:
                return
            elif self.resistande_info['resistance_high'] < self.last_rate:
                _message = 'resistance break chance order 11 # {}'.format(str(self.last_rate))
                _units = 0 - self.units
                _event_open_id = 51
                _target_price = self.last_rate - (self.entry_pips/2)
                _stop_rate = self.last_rate + self.regular_profit_pips

                self.new_trade(
                     message=_message,
                     units=_units,
                     event_open_id=_event_open_id,
                     target_price=_target_price,
                     stop_rate=_stop_rate,
                     is_market=False
                 )

                _units = self.units
                _target_price = self.last_rate + (self.entry_pips/2)
                _stop_rate = self.last_rate - self.regular_profit_pips

                self.new_trade(
                     message=_message,
                     units=_units,
                     event_open_id=_event_open_id,
                     target_price=_target_price,
                     stop_rate=_stop_rate,
                     is_market=False
                 )

            # 抵抗ライン下限突破
            if self.resistande_info['resistance_low'] == 0:
                return
            elif self.resistande_info['resistance_low'] > self.last_rate:
                _message = 'resistance break chance order 12 # {}'.format(str(self.last_rate))
                _units = self.units
                _event_open_id = 61
                _target_price = self.last_rate - (self.entry_pips/2)
                _stop_rate = self.last_rate + self.regular_profit_pips

                self.new_trade(
                     message=_message,
                     units=_units,
                     event_open_id=_event_open_id,
                     target_price=_target_price,
                     stop_rate=_stop_rate,
                     is_market=False
                 )

                _units = 0 - self.units
                _target_price = self.last_rate + (self.entry_pips/2)
                _stop_rate = self.last_rate - self.regular_profit_pips

                self.new_trade(
                     message=_message,
                     units=_units,
                     event_open_id=_event_open_id,
                     target_price=_target_price,
                     stop_rate=_stop_rate,
                     is_market=False
                )

    def new_trade(self,  message, units, event_open_id, target_price, stop_rate=0, is_market=False):
        # 新規オーダーする場合
        if event_open_id > 0:

            if units > 0:
                if self.long_units > 0:
                    if (self.long_units / units) >= self.limit_units_count:
                        return
                if stop_rate == 0:
                    stop_rate = self.mean - ((self.mean - self.lower) / 2)
                # stopが浅いので変更
                if self.last_rate - stop_rate < self.regular_profit_pips:
                    stop_rate = self.lower
                if self.last_rate - stop_rate < self.regular_profit_pips:
                    stop_rate = self.last_rate - 0.14
                # targetが浅いので変更
                if target_price - self.last_rate < self.regular_profit_pips:
                    target_price = self.last_rate + 0.14
            else:
                if self.short_units > 0:
                    if (self.short_units / units) >= self.limit_units_count:
                        return
                if stop_rate == 0:
                    stop_rate = self.mean + ((self.upper - self.mean) / 2)
                    # stopが浅いので変更
                if stop_rate - self.last_rate < self.regular_profit_pips:
                    stop_rate = self.upper
                if stop_rate - self.last_rate  < self.regular_profit_pips:
                    stop_rate = self.last_rate + 0.14
                # targetが浅いので変更
                if self.last_rate - target_price < self.regular_profit_pips:
                    target_price = self.last_rate - 0.14

            trade_id = 0
            transaction_id = 0
            if is_market:
                trade_id = self.order_market(
                    units=units,
                    profit_rate=round(target_price, 3),
                    stop_rate=round(stop_rate, 3),
                    event_open_id=event_open_id,
                    client_order_comment=message
                )
            else:
                transaction_id = self.order(
                    units=units,
                    profit_rate=round(target_price, 3),
                    stop_rate=round(stop_rate, 3),
                    event_open_id=event_open_id,
                    client_order_comment=message
                )

            self.is_new_trade = True

            if trade_id <= 0 and transaction_id <= 0 :
                return

            trade_history = {
                'rate': self.last_rate,
                'target_price': round(target_price, 3),
                'units':units,
                'event_open_id':event_open_id
            }
            self._line.send(event_open_id, message)

    def system_update(self, positions_infos):
        win_count = self._history.get_todays_win_count()
        lose_count = self._history.get_todays_lose_count()
        self._system.update_profit(
            positions_infos['pl'], positions_infos['unrealizedPL'], win_count, lose_count)
        self._system.delete_all_by_filename()
        self._system.export_drive()

    def history_update(self):
        history_obj = {
            'state' : 'open',
            'instrument' : self.instrument,
            'unrealized_pl' : 0,
            'event_open_id' : 0,
            'trend_1' : round(self.trend_usd['v1_usd'], 3),
            'trend_2' : round(self.trend_usd['v2_usd'], 3),
            'trend_3' : round(self.trend_usd['v1_jpy'], 3),
            'trend_4' : round(self.trend_usd['v2_jpy'], 3),
            'trend_cal' : round(self.trend_usd['res'], 3),
            'judge_1' : self.is_golden,
            'judge_2' : self.is_dead,
            'rule_1' : self.rule_1,
            'rule_2' : self.rule_2,
            'rule_3' : self.rule_3,
            'rule_4' : self.rule_4,
            'rule_5' : self.rule_5,
            'rule_6' : self.rule_6,
            'resistance_high' : round(self.resistande_info['resistance_high'], 3),
            'resistance_low' : round(self.resistande_info['resistance_low'], 3),
            'transaction_id' : 0
         }
 
        details = account.details.Details()
        details_dict = details.get_account()

        get_by_transaction_ids = transaction.get_by_transaction_ids.Get_by_transaction_ids(history_obj)
        transaction_id = int(details_dict['Last Transaction ID'])
        from_transaction_id = 1
        if transaction_id < 50:
            from_transaction_id = 1
        else:
            from_transaction_id = transaction_id - 50
        get_by_transaction_ids.main(from_transaction_id, transaction_id)

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

    transactions = transaction.transactions.Transactions()
    transactions.get()
    orders_info = transactions.get_trades()
    new_orders_info = transactions.get_new_orders()
    positions_infos = transactions.get_positions()
    long_units = transactions.get_short_pos_units()
    short_units = transactions.get_short_pos_units()

    trade = Trade(_environ)

    candles = inst.Candles()
    candles_csv_string = candles.get('USD_JPY', 'M10')
    candles_df = trade.get_df_by_string(candles_csv_string)

    trade.set_property(candles_df=candles_df, long_units=long_units, short_units=short_units, orders_info=orders_info, new_orders_info=new_orders_info)
    
    print(_environ.get('is_stop'))
    if condition.get_is_eneble_new_order(reduce_time) and _environ.get('is_stop') == '0':
        trade.analyze_trade()
        trade.send_draw()

    trade.close()

    trade.system_update(positions_infos)

    trade.history_update()

    details = trade.get_account_details()
    details_csv = file.file_utility.File_utility('details.csv', drive_id)
    details_csv.set_contents(details)
    details_csv.export_drive()

    caculate_df_all = trade.get_caculate_df_all(candles_df)
    candles_csv = file.file_utility.File_utility('candles.csv', drive_id)
    candles_csv.set_contents(caculate_df_all.to_csv())
    candles_csv.export_drive()

    histoy_csv_string = trade.get_histoy_csv()
    histoy_csv = file.file_utility.File_utility('history.csv', drive_id)
    histoy_csv.set_contents(histoy_csv_string)
    histoy_csv.export_drive()

def test():

    _environ = strategy.environ.Environ()
    transactions = transaction.transactions.Transactions()
    transactions.get()
    orders_info = transactions.get_trades()
    new_orders_info = transactions.get_new_orders()
    # positions_infos = transactions.get_positions()
    long_units = transactions.get_short_pos_units()
    short_units = transactions.get_short_pos_units()

    trade = Trade(_environ)

    candles = inst.Candles()
    candles_csv_string = candles.get('USD_JPY', 'M10')
    candles_df = trade.get_df_by_string(candles_csv_string)

    trade.set_property(candles_df=candles_df, long_units=long_units, short_units=short_units, orders_info=orders_info, new_orders_info=new_orders_info)

    # trade.order(1, 110, 108, 999, 'test')

    trade.history_update()

    condition = market.condition.Market()
    print(condition.get_is_opening())
    print(condition.get_is_eneble_new_order(5))

if __name__ == "__main__":

    try:
        # test()
        main()
    except:
        _line = line.line.Line()
        _line.send('Error', sys.exc_info())
