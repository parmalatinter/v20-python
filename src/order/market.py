#!/usr/bin/env python

import argparse
import common.config
from .args import OrderArguments
from v20.order import MarketOrderRequest
from .view import print_order_create_response_transactions

class Market():

    args = None
    response = None

    def exec_by_cmd(self):

        """
        Create a Market Order in an Account based on the provided command-line
        arguments.
        """

        parser = argparse.ArgumentParser()

        #
        # Add the command line argument to parse to the v20 config
        #
        common.config.add_argument(parser)

        #
        # Add the command line arguments required for a Market Order
        #
        marketOrderArgs = OrderArguments(parser)
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
        self.args = parser.parse_args()

        print(self.args)

        #
        # Extract the Market order parameters from the parsed arguments
        #
        marketOrderArgs.parse_arguments(self.args)

        self.exec(marketOrderArgs)

    def exec(self, arguments):
 

        #
        # Create the api context based on the contents of the
        # v20 config file
        #
        api = self.args.config.create_context()


        #
        # Submit the request to create the Market Order
        #
        response = api.order.market(
            self.args.config.active_account,
            **arguments.parsed_args
        )

        self.response = response

    def get_response(self):
        return self.response

    def print_response(self):
        if self.response:
            print("Response: {} ({})".format(self.response.status, self.response.reason))
            print("")

            print_order_create_response_transactions(self.response)

def main():
    market = Market()
    market.exec_by_cmd()
    market.print_response()

if __name__ == "__main__":
    main()
