#!/usr/bin/env python

import argparse
import common.config
from .args import OrderArguments
from v20.order import MarketOrderRequest
from .view import print_order_create_response_transactions
import v20.transaction

class Market():

    args = None
    response = None
    transaction = None
    parser = argparse.ArgumentParser()
    common.config.add_argument(parser)
    errorCode = '' 
    errorMessage = ''
    trade_id = 0

    def exec_by_cmd(self):

        """
        Create a Market Order in an Account based on the provided command-line
        arguments.
        """



        #
        # Add the command line arguments required for a Market Order
        #
        marketOrderArgs = OrderArguments(self.parser)
        marketOrderArgs.add_instrument()
        marketOrderArgs.add_units()
        marketOrderArgs.add_time_in_force(["FOK", "IOC"])
        marketOrderArgs.add_price_bound()
        marketOrderArgs.add_position_fill()
        marketOrderArgs.add_take_profit_on_fill()
        marketOrderArgs.add_stop_loss_on_fill()
        marketOrderArgs.add_trailing_stop_loss_on_fill()
        marketOrderArgs.add_client_order_extensions()
        marketOrderArgs.add_client_trade_extensions()

        self.args = self.parser.parse_args()
        #
        # Extract the Market order parameters from the parsed arguments
        #
        marketOrderArgs.parse_arguments(self.args)

        self.exec(marketOrderArgs.parsed_args)

    def exec(self, arguments):
 

        self.args = self.parser.parse_args()
        #
        # Create the api context based on the contents of the
        # v20 config file
        #
        api = self.args.config.create_context()
        #
        # Submit the request to create the Market Order
        #

        if 'take_profit_price' in arguments:
            kwargs = {'price': arguments['take_profit_price']}
            arguments['takeProfitOnFill'] = v20.transaction.TakeProfitDetails(**kwargs)
        if 'stop_loss_price' in arguments:
            kwargs = {'price': arguments['stop_loss_price']}
            arguments['stopLossOnFill'] = v20.transaction.StopLossDetails(**kwargs)

        kwargs = {}
        if 'client_order_id' in arguments:
            kwargs["id"] = arguments['client_order_id']
        if 'client_order_tag' in arguments:
            kwargs["tag"] = arguments['client_order_id']
        if 'client_order_comment' in arguments:
            kwargs["comment"] = arguments['client_order_id']
        if kwargs:
            arguments['clientExtensions'] = v20.transaction.ClientExtensions(**kwargs)

        kwargs = {}
        if 'client_trade_id' in arguments:
            kwargs["id"] = arguments['client_trade_id']
        if 'client_trade_tag' in arguments:
            kwargs["tag"] = arguments['client_trade_id']
        if 'client_trade_comment' in arguments:
            kwargs["comment"] = arguments['client_trade_id']
        if kwargs:
            arguments['tradeClientExtensions'] = v20.transaction.ClientExtensions(**kwargs)

        response = api.order.market(
            self.args.config.active_account,
            **arguments
        )

        self.response = response

        if self.response.status == 201 and self.response.reason == "Created":
            self.trade_id = self.response.get("lastTransactionID", None)
        else:
            self.errorMessage = response.get("errorMessage", None)

    def get_response(self):
        return self.response

    def get_trade_id(self):
        return self.trade_id

    def get_errors(self):
        return {
            'errorCode' : self.errorCode,
            'errorMessage' : self.errorMessage
        }

    def print_response(self):
        if self.response:
            print("Response: {} ({})".format(self.response.status, self.response.reason))
            print("")

            print_order_create_response_transactions(self.response)
            
# def main():
#     market = Market()
#     market.exec({'instrument': 'USD_JPY', 'units':1, 'take-profit-price' : 120, 'client-order-comment' : 'test'})
#     response = market.get_response()
#     print(response.__dict__)

def main():
    market = Market()
    market.exec_by_cmd()
    market.print_response()

if __name__ == "__main__":
    main()
