#!/usr/bin/env python

import argparse
import common.config
import common.view
from order.view import print_order_create_response_transactions

class Close():

    args = None
    response = None

    parser = argparse.ArgumentParser()

    #
    # Add the command line argument to parse to the v20 config
    #
    common.config.add_argument(parser)

    def exec_by_cmd(self):

        self.parser.add_argument(
            "tradeid",
            help=(
                "The ID of the Trade to close. If prepended "
                "with an '@', this will be interpreted as a client Trade ID"
            )
        )

        self.parser.add_argument(
            "--units",
            default="ALL",
            help=(
                "The amount of the Trade to close. Either the string 'ALL' "
                "indicating a full Trade close, or the number of units of the "
                "Trade to close. This number must always be positive and may "
                "not exceed the magnitude of the Trade's open units"
            )
        )

        self.args = self.parser.parse_args()

        self.exec(self.args.tradeid, self.args.units)

    def exec(self, tradeid, units):

        self.args = self.parser.parse_args()

        account_id = self.args.config.active_account

        #
        # Create the api context based on the contents of the
        # v20 config file
        #
        api = self.args.config.create_context()

        self.response = api.trade.close(
            account_id,
            tradeid,
            units=units
        )

    def get_response(self):
        return self.response

    def print_response(self):
        print(
            "Response: {} ({})\n".format(
                self.response.status,
                self.response.reason
            )
        )

        print_order_create_response_transactions(self.response)

# def main():
    # close = Close()
    # close.exec(1,1)
    # response = close.get_response()
    # print(response)

def main():
    close = Close()
    close.exec_by_cmd()
    close.print_response()

if __name__ == "__main__":
    main()
