#!/usr/bin/env python

import argparse
import common.config
import common.args
import time
import db.history
import account.details

class Get_by_transaction_ids(object):

    history_obj = {}

    def __init__(self, history_obj):
        self.history_obj = history_obj

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

        new_rows = {}
        update_rows = {}
        history = db.history.History()

        for transaction in response.get("transactions", 200):
            
            if hasattr(transaction, 'tradeOpened'):
                if transaction.tradeOpened:
                    new_rows[transaction.id] = {
                        'reason' : transaction.reason,
                        'price' : transaction.tradeOpened.price,
                        'units' : transaction.tradeOpened.units,
                        'tradeID' : transaction.tradeOpened.tradeID,
                        'event_open_id' : 0,
                        'memo' : ''
                    }
                    if hasattr(transaction.tradeOpened, 'clientExtensions'):
                        if hasattr(transaction.tradeOpened.clientExtensions, 'tag'):
                            new_rows[transaction.id]['event_open_id'] = int(transaction.tradeOpened.clientExtensions.tag)
                        if hasattr(transaction.tradeOpened.clientExtensions, 'comment'):
                            new_rows[transaction.id]['memo'] = transaction.tradeOpened.clientExtensions.comment
            if hasattr(transaction, 'tradesClosed'):
                if transaction.tradesClosed:
                    for closed in transaction.tradesClosed:
                        if hasattr(closed, 'realizedPL'):
                            update_rows[transaction.id] = {
                                'reason' : transaction.reason,
                                'price' : closed.price,
                                'realizedPL' : closed.realizedPL,
                                'tradeID' : closed.tradeID,
                                'event_close_id' : '',
                                'memo' : ''
                            }
                            if hasattr(closed, 'clientExtensions'):
                                if hasattr(closed.clientExtensions, 'tag'):
                                    new_rows[transaction.id]['event_close_id'] = int(closed.clientExtensions.tag)
                                if hasattr(closed.clientExtensions, 'comment'):
                                    new_rows[transaction.id]['memo'] = closed.clientExtensions.comment

        for transaction_id, row in new_rows.items():
            history.insert(
                trade_id=int(row['tradeID']),
                price=row['price'],
                price_target=0,
                state='open',
                instrument=self.history_obj['instrument'],
                units=row['units'],
                unrealized_pl=0,
                event_open_id=row['event_open_id'],
                trend_1=self.history_obj['trend_1'],
                trend_2=self.history_obj['trend_2'],
                trend_3=self.history_obj['trend_3'],
                trend_4=self.history_obj['trend_4'],
                trend_cal=self.history_obj['trend_cal'],
                judge_1=self.history_obj['judge_1'],
                judge_2=self.history_obj['judge_2'],
                rule_1=self.history_obj['rule_1'],
                rule_2=self.history_obj['rule_2'],
                rule_3=self.history_obj['rule_3'],
                rule_4=self.history_obj['rule_4'],
                rule_5=self.history_obj['rule_5'],
                rule_6=self.history_obj['rule_6'],
                resistance_high=self.history_obj['resistance_high'],
                resistance_low=self.history_obj['resistance_low'],
                transaction_id=0,
                memo=row['memo']
            )

        for transaction_id, row in update_rows.items():
            history.fix_update(int(row['tradeID']), row['price'], row['realizedPL'], row['event_close_id'], row['reason'])

def main():
    details = account.details.Details()
    details_dict = details.get_account()
    get_by_transaction_ids = Get_by_transaction_ids()
    transaction_id = int(details_dict['Last Transaction ID'])
    get_by_transaction_ids.main(transaction_id - 50, transaction_id)


if __name__ == "__main__":
    main()
