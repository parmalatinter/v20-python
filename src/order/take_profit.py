#!/usr/bin/env python

import argparse
import common.config
from .args import OrderArguments, add_replace_order_id_argument
from .view import print_order_create_response_transactions
import v20.transaction

class Take_profit():

    args = None
    response = None
    errorCode = '' 
    errorMessage = ''
    # transaction = None
    parser = argparse.ArgumentParser()
    common.config.add_argument(parser)

    def exec_by_cmd(self):

        #
        # Add the argument to support replacing an existing argument
        #
        add_replace_order_id_argument(self.parser)

        #
        # Add the command line arguments required for a Limit Order
        #
        orderArgs = OrderArguments(self.parser)
        orderArgs.add_trade_id()
        orderArgs.add_price()
        orderArgs.add_time_in_force(["GTD", "GFD", "GTC"])
        orderArgs.add_client_order_extensions()

        self.args = self.parser.parse_args()

        #
        # Extract the Limit Order parameters from the parsed arguments
        #
        orderArgs.parse_arguments(self.args)

        self.exec(orderArgs.parsed_args)

    def exec(self, arguments):

        self.args = self.parser.parse_args()

        #
        # Create the api context based on the contents of the
        # v20 config file
        #
        api = self.args.config.create_context()


        orderArgs = OrderArguments(self.parser)

        orderArgs.parse_arguments(self.args)



        try:
            if self.args.replace_order_id is not None:
                arguments['replace_order_id'] = self.args.replace_order_id
        except:
            arguments

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
            # Submit the request to cancel and replace a Take Profit Order
            #
            
            response = api.order.take_profit_replace(
                self.args.config.active_account,
                arguments['replace_order_id'],
                **arguments
            )
            
        else:
            #
            # Submit the request to create a Take Profit Order
            #
            response = api.order.take_profit(
                self.args.config.active_account,
                **arguments
            )


        

        self.response = response
        #  (contains 'orderCancelRejectTransaction', 'relatedTransactionIDs', 'lastTransactionID', 'errorCode', 'errorMessage')
        if not self.response.status == 201:
            # self.errorCode = response.get("errorCode", None)
            self.errorMessage = response.get("errorMessage", None)
        
        # self.transaction = response.get("orderFillTransaction", None)

    def get_response(self):
        return self.response

    def get_errors(self):
        return {
            'errorCode' : self.response.status,
            'errorMessage' : self.errorMessage
        }

    # def get_tansaction(self):
    #     return self.transaction

    def print_response(self):
        print("Response: {} ({})".format(self.response.status, self.response.reason))
        print("")

        print_order_create_response_transactions(self.response)

# def main():
#     take_profit = Take_profit()
#     take_profit.exec({'tradeID': '1719', 'price':110, 'client-order-comment' : 'test'})
#     response = take_profit.get_response()
#     # transaction = take_profit.get_tansaction()
#     print(take_profit.get_errors())

def main():
    take_profit = Take_profit()
    take_profit.exec_by_cmd()
    take_profit.print_response()

if __name__ == "__main__":
    main()
