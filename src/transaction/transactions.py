#!/usr/bin/env python

import argparse
import common.config
import common.args
import time
from datetime import datetime, timedelta
import os
import drive.drive
import pytz

class Transactions(object):

    new_orders = {}
    orders = {}
    positions = {'pl': 0, 'unrealizedPL': 0}
    long_pos = {'units': 0}
    short_pos = {'units': 0}
    trades = {}

    def get(self):
        """
        Poll Transactions for the active Account
        """

        os.environ['TZ'] = 'America/New_York'
        parser = argparse.ArgumentParser()

        common.config.add_argument(parser)

        args = parser.parse_args()

        api = args.config.create_context()

        account_id = args.config.active_account

        response1 = api.account.get(account_id)

        res = '{},{},{},{},{},{},{}\n'.format(
            'id',
            'time',
            'price',
            'state',
            'instrument',
            'currentUnits',
            'unrealizedPL'
        )

        res = response1.get("account", 200)

        for pos in getattr(res, "positions", []):
            self.positions = pos.__dict__
            self.long_pos = self.positions['long'].__dict__
            self.short_pos = self.positions['short'].__dict__

        for order in getattr(res, "orders", []):
            self.orders[order.id] = order.__dict__
            if self.orders[order.id]['type'] == 'MARKET_IF_TOUCHED':
                self.new_orders[order.id] = self.orders[order.id]
                # ,time,close,open,high,low,volume
                unix = self.new_orders[order.id]['createTime'].split(".")[0]
                try:
                    time = datetime.strptime(unix.replace('T', ' '), '%Y-%m-%d %H:%M:%S')
                except:
                    time = unix.split(".")[0]

                self.new_orders[order.id]['time'] = time
            
        texts = ''
        for trade in getattr(res, "trades", []):
            response2 = api.transaction.get(account_id, trade.id)
            transaction = response2.get("transaction", 200)
            self.trades[trade.id] = {}
            self.trades[trade.id] = trade.__dict__
            self.trades[trade.id]['takeProfitOrder'] = None
            self.trades[trade.id]['stopLossOrder'] = None
            self.trades[trade.id]['trailingStopLossOrder'] = None
            if trade.takeProfitOrderID:
                self.trades[trade.id]['takeProfitOrder'] = self.orders[trade.takeProfitOrderID]
            if trade.stopLossOrderID:
                self.trades[trade.id]['stopLossOrder'] = self.orders[trade.stopLossOrderID]
            if trade.trailingStopLossOrderID:
                self.trades[trade.id]['trailingStopLossOrder'] = self.orders[trade.trailingStopLossOrderID]

            # print(transaction.price)
            self.trades[trade.id]['transaction'] = transaction.__dict__

            # ,time,close,open,high,low,volume
            unix = transaction.time.split(".")[0]
            try:
                time = datetime.fromtimestamp(int(unix), pytz.timezone("America/New_York")).strftime('%Y-%m-%d %H:%M:%S')
            except:
                time = transaction.time.split(".")[0]

            text = '{},{},{},{},{},{},{}\n'.format(
                transaction.id,
                time,
                trade.price,
                trade.state,
                trade.instrument,
                trade.currentUnits,
                trade.unrealizedPL
            )

            texts = texts + text

        return texts

    def get_trades(self):
        return self.trades

    def get_orders(self):
        return self.orders

    def get_new_orders(self):
        return self.new_orders

    def get_positions(self):
        return self.positions

    def get_long_pos_units(self):
        return int(self.long_pos['units'])

    def get_short_pos_units(self):
        return int(self.short_pos['units'])

def main():
    transactions = Transactions()
    transactions.get()
    res = transactions.get_new_orders()
    print(res)

if __name__ == "__main__":
    main()
