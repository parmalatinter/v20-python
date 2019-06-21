#!/usr/bin/env python

import argparse
import common.config
import common.view
import db.history


class Get_by_trade_ids(object):

    def to_date(self, time_str):
        unix = time_str.split(".")[0]
        return datetime.fromtimestamp(int(unix))

    def get(self, trade_ids):
        """
        Get details of a specific Trade or all open Trades in an Account
        """

        parser = argparse.ArgumentParser()

        #
        # Add the command line argument to parse to the v20 config
        #
        common.config.add_argument(parser)

        args = parser.parse_args()

        account_id = args.config.active_account

        #
        # Create the api context based on the contents of the
        # v20 config file
        #
        api = args.config.create_context()

        res = {}
        for trade_id in trade_ids:

            response = api.trade.get(account_id, trade_id)
            try:
                orderFillTransaction = response.get("orderFillTransaction", 200)
            except:
                print('info not found trade id ' + str(trade_id))
                continue

            print(response.__dict__)
            res[trade_id]['filledTime'] = orderFillTransaction.time.replace('T', ' ')
            res[trade_id]['realizedPL'] = orderFillTransaction.pl
            res[trade_id]['price'] = orderFillTransaction.price
            res[trade_id]['type'] = orderFillTransaction.type


        return res

def main():
        history = db.history.History()
        ids = history.get_trade_ids_by_not_update_pl_by_panda()
        get_by_trade_ids = Get_by_trade_ids()
        rows = get_by_trade_ids.get(ids)

        print(rows)

        for trade_id, row in rows.items():
            history.fix_update(int(trade_id), row['filledTime'], row['price'], row['realizedPL'], row['type'])

if __name__ == "__main__":
    main()
