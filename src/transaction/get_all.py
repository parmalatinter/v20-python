#!/usr/bin/env python

import argparse
import common.config
import common.args
import time
from datetime import datetime, timedelta
import os
import drive.drive
import pytz

def export_drive(file_name, text ):

    googleDrive = drive.drive.Drive('1A3k4a4u4nxskD-hApxQG-kNhlM35clSa')
    googleDrive.upload(file_name, text )

def main():
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

    trades = {}

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

    for trade in getattr(response1.get("account", 200), "trades", []):
        response2 = api.transaction.get(account_id, trade.id)
        transaction = response2.get("transaction", 200)
        trades[trade.id] = {}
        trades[trade.id]['trade'] = trade

        # print(transaction.price)
        trades[trade.id]['transaction'] = transaction
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

        res = res + text

    export_drive(file_name, res)
    
if __name__ == "__main__":
    main()
