#!/usr/bin/env python

import argparse
import common.config
import common.args
import time
import db.history
import account.details

class Get_by_transaction_ids(object):

    def main(self, fromid, toid):

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

        response = api.transaction.range(
            account_id,
            fromID=fromid,
            toID=toid,
            type=None
        )

        rows = {}
        history = db.history.History()
        for transaction in response.get("transactions", 200):
            if hasattr(transaction, 'pl'):
                if transaction.pl:
                    rows[transaction.id] = {
                        'time' : transaction.time.split(".")[0].replace('T', ' '),
                        'reason' :  transaction.reason
                    }
                    for closed in transaction.tradesClosed:
                        if hasattr(closed, 'realizedPL'):
                            rows[transaction.id]['price'] = closed.price
                            rows[transaction.id]['realizedPL'] = closed.realizedPL
                            rows[transaction.id]['tradeID'] = closed.tradeID

        for transaction_id, row in rows.items():
            history.fix_update(int(row['tradeID']), row['price'], row['realizedPL'], row['reason'])

def main():
    details = account.details.Details()
    details_dict = details.get_account()
    get_by_transaction_ids = Get_by_transaction_ids()
    transaction_id = int(details_dict['Last Transaction ID'])
    get_by_transaction_ids.main(transaction_id - 100, transaction_id)


if __name__ == "__main__":
    main()
