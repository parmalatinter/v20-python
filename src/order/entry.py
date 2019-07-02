#!/usr/bin/env python

import argparse
import common.config
from .args import OrderArguments, add_replace_order_id_argument
from .view import print_order_create_response_transactions

class Entry():

    args = None
    response = None
    transaction = None
    parser = argparse.ArgumentParser()
    common.config.add_argument(parser)
    errorCode = '' 
    errorMessage = ''
    trade_id = ''
    
    def exec_by_cmd(self):
        """
        Create or replace an OANDA Entry Order in an Account based on the provided
        command-line arguments.
        """

        #
        # Add the command line argument to parse to the v20 config
        #
        common.config.add_argument(self.parser)

        #
        # Add the argument to support replacing an existing argument
        #
        
        # add_replace_order_id_argument(parser)

        #
        # Add the command line arguments required for an Entry Order
        #
        orderArgs = OrderArguments(parser)
        orderArgs.add_instrument()
        orderArgs.add_units()
        orderArgs.add_price()
        orderArgs.add_price_bound()
        orderArgs.add_time_in_force(["GTD", "GFD", "GTC"])
        orderArgs.add_position_fill()
        orderArgs.add_take_profit_on_fill()
        orderArgs.add_stop_loss_on_fill()
        orderArgs.add_trailing_stop_loss_on_fill()
        orderArgs.add_client_order_extensions()
        orderArgs.add_client_trade_extensions()

        self.args = self.parser.parse_args()
        #
        # Extract the Market order parameters from the parsed arguments
        #
        orderArgs.parse_arguments(self.args)

        self.exec(marketOrderArgs.parsed_args)

    def exec(self, arguments):

        self.args = self.parser.parse_args()

        #
        # Create the api context based on the contents of the
        # v20 config file
        #
        api = self.args.config.create_context()

        #
        # Extract the Entry Order parameters from the parsed arguments
        #
        orderArgs = OrderArguments(self.parser)

        orderArgs.parse_arguments(self.args)

        try:
            if self.args.replace_order_id is not None:
                arguments['replace_order_id'] = self.args.replace_order_id
        except:
            arguments

        if 'replace_order_id' in arguments:
            #
            # Submit the request to cancel and replace an Entry Order
            #
            response = api.order.market_if_touched_replace(
                self.args.config.active_account,
                arguments['replace_order_id'],
                **arguments
            )
        else:
            #
            # Submit the request to create an Entry Order
            #
            response = api.order.market_if_touched(
                self.args.config.active_account,
                **arguments
            )

        self.response = response

        if self.response.status == 201 and self.response.reason == "Created":
            self.trade_id = self.response.get("lastTransactionID", None)
            
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

def main():
    entry = Entry()
    entry.exec({'instrument': 'USD_JPY', 'units':1, 'price' : 120})
    response = entry.get_response()
    print(response.__dict__)

# def Entry():
#     entry = Entry()
#     entry.exec_by_cmd()
#     entry.print_response()

if __name__ == "__main__":
    main()
