#!/usr/bin/env python

import argparse
import common.config
from .args import OrderArguments, add_replace_order_id_argument
from .view import print_order_create_response_transactions
import v20.transaction

class Trailing_stop_loss():

    Response = type('Response', (object,), {'status' : 0})
    response = Response()
    errorCode = '' 
    errorMessage = ''

    def create_response(self, code):
        self.response.status = code

    def exec(self, arguments):

        #
        # Create the api context based on the contents of the
        # v20 config file
        #

        parser = argparse.ArgumentParser()

        #
        # Add the command line argument to parse to the v20 config
        #
        common.config.add_argument(parser)

        args = parser.parse_args()

        api = args.config.create_context()

        if not 'trade_id' in arguments:
            self.errorMessage = 'nothing trade_id'
            self.response = self.create_response(400)
            return

        if not 'distance' in arguments:
            self.errorMessage = 'nothing distance'
            self.response = self.create_response(400)
            return

        kwargs = {}
        if 'client_order_id' in arguments:
            kwargs["id"] = arguments['client_order_id']
        if 'client_order_tag' in arguments:
            kwargs["tag"] = arguments['client_order_tag']
        if 'client_order_comment' in arguments:
            kwargs["comment"] = arguments['client_order_comment']
        if kwargs:
            arguments['clientExtensions'] = v20.transaction.ClientExtensions(**kwargs)

        kwargs = {}
        if 'client_trade_id' in arguments:
            kwargs["id"] = arguments['client_trade_id']
        if 'client_trade_tag' in arguments:
            kwargs["tag"] = arguments['client_trade_tag']
        if 'client_trade_comment' in arguments:
            kwargs["comment"] = arguments['client_trade_comment']
        if kwargs:
            arguments['tradeClientExtensions'] = v20.transaction.ClientExtensions(**kwargs)

        if 'replace_order_id' in arguments:
            #
            # Submit the request to cancel and replace a Trailing Stop Loss Order
            #
            self.response = api.order.trailing_stop_loss_replace(
                args.config.active_account,
                arguments['replace_order_id'],
                **arguments
            )
        else:
            #
            # Submit the request to create a Trailing Stop Loss Order
            #
            self.response = api.order.trailing_stop_loss(
                args.config.active_account,
                **arguments
            )

        if not self.response.status == 201:
            self.errorMessage = self.response.get("errorMessage", None)

    def get_response(self):
        return self.response

    def get_errors(self):
        return {
            'errorCode' : self.errorCode,
            'errorMessage' : self.errorMessage
        }
def main():
    trailing_stop_loss = Trailing_stop_loss()
    trailing_stop_loss.exec({
        'trade_id': '1',
        'distance': '1',
        'replace_order_id' : '1',
        'client_trade_tag' : '999',
        'client_trade_comment' :'test',
        'client_order_tag' : '999',
        'client_order_comment' :'test'
    })
    # Trailing_stop_loss.exec({'tradeID': 1713, 'profit_rate':110, 'client-order-comment' : 'test'})
    response = trailing_stop_loss.get_response()
    # transaction = trailing_stop_loss.get_tansaction()
    print(trailing_stop_loss.get_errors())

if __name__ == "__main__":
    main()
