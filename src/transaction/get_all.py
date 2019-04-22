#!/usr/bin/env python

import argparse
import common.config
import common.args
import time
from datetime import datetime, timedelta
import os 


def main():
    """
    Poll Transactions for the active Account
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    parser = argparse.ArgumentParser()

    common.config.add_argument(parser)

    args = parser.parse_args()

    api = args.config.create_context()

    account_id = args.config.active_account

    response1 = api.account.get(account_id)

    trades = {}

    file = 'data.csv'
    try:
        os.remove(file)
    except OSError:
        pass

    text = '{},{},{},{},{},{},{}\n'.format(
        'id',
        'time',
        'price',
        'state',
        'instrument',
        'currentUnits',
        'unrealizedPL'
    )
    with open(file, mode='a') as f:
        f.writelines(text)

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
            time = datetime.fromtimestamp(int(unix)).strftime('%Y-%m-%d %H:%M:%S')
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

        os.makedirs('/tmp/transaction/', exist_ok=True)
        with open('/tmp/transaction/' + file, mode='a') as f:
            f.writelines(text)
            print(text)

    
if __name__ == "__main__":
    main()
