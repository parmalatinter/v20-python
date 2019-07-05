#!/usr/bin/env python

import argparse
import common.config
import common.view
from common.input import get_yn
from .view import print_orders

class Cancel():

    ars = None
    response = None
    errorCode = '' 
    errorMessage = ''
    # transaction = None
    parser = argparse.ArgumentParser()
    common.config.add_argument(parser)

    def exec_by_cmd(self):
        """
        Cancel one or more Pending Orders in an Account
        """

        self.parser.add_argument(
            "--order-id", "-o",
            help=(
                "The ID of the Order to cancel. If prepended "
                "with an '@', this will be interpreted as a client Order ID"
            )
        )

        self.parser.add_argument(
            "--all", "-a",
            action="store_true",
            default=False,
            help="Flag to cancel all Orders in the Account"
        )


        #
        # Add the command line argument to parse to the v20 config
        # 

        self.exec(self.args)

    def exec(self, arguments):

        self.args = self.parser.parse_args()

        account_id = self.args.config.active_account
        #
        # Create the api context based on the contents of the
        # v20 config file
        #
        api = self.args.config.create_context()

        if 'all' in arguments:
            #
            # Get the list of all pending Orders

            #
            self.response = api.order.list_pending(account_id)

            orders = self.response.get("orders", 200)

            if len(orders) == 0:
                print("Account {} has no pending Orders to cancel".format(
                    account_id
                ))
                return

            print_orders(orders)

            if not get_yn("Cancel all Orders?"):
                return

            #
            # Loop through the pending Orders and cancel each one
            #
            for order in orders:
                self.response = api.order.cancel(account_id, order.id)

                orderCancelTransaction = response.get("orderCancelTransaction", 200)

                print(orderCancelTransaction.title())

        elif 'order_id' in arguments:


            #
            # Submit the request to create the Market Order
            #
            self.response = api.order.cancel(
                account_id,
                arguments['order_id']
            )

            if self.response.status == 200 :
                self.errorMessage = "Order Cancel"
       
            elif not self.response.status == 201 :
                self.errorMessage = self.response.get("errorMessage", None)
 
    def get_response(self):
        return self.response

    def print_response(self):
        print("Response: {} ({})".format(self.response.status, self.response.reason))

        print("")

        common.view.print_response_entity(
            self.response, 200, "Order Cancel", "orderCancelTransaction"
        )

        common.view.print_response_entity(
            self.response, 404, "Order Cancel Reject", "orderCancelRejectTransaction"
        )

    def get_errors(self):
        return {
            'errorCode' : self.errorCode,
            'errorMessage' : self.errorMessage
        }

def main():
    cancel = Cancel()
    cancel.exec({'order_id': '1'})
    response = cancel.get_response()
    print(response)
    print(cancel.get_errors())

# def main():
    # cancel = Cancel()
    # cancel.exec_by_cmd()
    # cancel.print_response()

if __name__ == "__main__":
    main()
