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

    orders = {}
    position = {}
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

        file_name = 'transaction.csv'

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
        orders = {}
        position = {}
        for pos in getattr(res, "positions", []):
            self.position = pos

        orders = {}
        for order in getattr(res, "orders", []):
            self.orders[order.id] = order

        texts = ''
        for trade in getattr(res, "trades", []):
            response2 = api.transaction.get(account_id, trade.id)
            transaction = response2.get("transaction", 200)
            self.trades[trade.id] = {}
            self.trades[trade.id]['trade'] = trade

            # print(transaction.price)
            self.trades[trade.id]['transaction'] = transaction

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

    def get_info(self):
        return {
            'orders' : self.orders,
            'position' : self.position,
            'trades' : self.trades,
        }

def main():
    transactions = Transactions()
    print(transactions.get())
    # print(transactions.get_info())

if __name__ == "__main__":
    main()
