#!/usr/bin/env python

import argparse
import common.config
import common.args
from .view import price_to_string
import time
from datetime import datetime

class Pricing(object):

    price = None 
    def get(self, instrument):

        """
        Get the prices for a list of Instruments for the active Account.
        Repeatedly poll for newer prices if requested.
        """

        parser = argparse.ArgumentParser()

        common.config.add_argument(parser)

        parser.add_argument(
            '--instrument', "-i",
            type=common.args.instrument,
            required=False,
            action="append",
            help="Instrument to get prices for"
        )

        parser.add_argument(
            '--poll', "-p",
            action="store_true",
            default=False,
            help="Flag used to poll repeatedly for price updates"
        )

        parser.add_argument(
            '--poll-interval',
            type=float,
            default=2,
            help="The interval between polls. Only relevant polling is enabled"
        )

        args = parser.parse_args()

        account_id = args.config.active_account
        
        api = args.config.create_context()

        latest_price_time = None 

        price= None

        def poll(latest_price_time):
            """
            Fetch and display all prices since than the latest price time

            Args:
                latest_price_time: The time of the newest Price that has been seen

            Returns:
                The updated latest price time
            """

            response = api.pricing.get(
                account_id,
                instruments=instrument,
                since=latest_price_time,
                includeUnitsAvailable=False
            )



            #
            # Print out all prices newer than the lastest time 
            # seen in a price
            #
            for _price in response.get("prices", 200):
                if latest_price_time is None or _price.time > latest_price_time:
                    self.price = _price
            #
            # Stash and return the current latest price time
            #
            for _price in response.get("prices", 200):
                if latest_price_time is None or _price.time > latest_price_time:
                    latest_price_time = _price.time
        
            return latest_price_time

        #
        # Fetch the current snapshot of prices
        #
        latest_price_time = poll(latest_price_time)

        #
        # Poll for of prices
        #
        while args.poll:
            time.sleep(args.poll_interval)
            poll(latest_price_time)

        spred = round(self.price.asks[0].price - self.price.bids[0].price,3)
        price = round((self.price.asks[0].price + self.price.bids[0].price)/2,3)
        unix = self.price.time.split(".")[0]
        try:
            time = datetime.strptime(unix.replace('T', ' '), '%Y-%m-%d %H:%M:%S')
        except:
            time = datetime.fromtimestamp(int(unix))
        return {'time' : time, 'price' : price, 'bids' : self.price.bids[0].price, 'asks' : self.price.asks[0].price, 'spred' : spred}


    def main():
        """
        Get the prices for a list of Instruments for the active Account.
        Repeatedly poll for newer prices if requested.
        """

        parser = argparse.ArgumentParser()

        common.config.add_argument(parser)

        parser.add_argument(
            '--instrument', "-i",
            type=common.args.instrument,
            required=True,
            action="append",
            help="Instrument to get prices for"
        )

        parser.add_argument(
            '--poll', "-p",
            action="store_true",
            default=False,
            help="Flag used to poll repeatedly for price updates"
        )

        parser.add_argument(
            '--poll-interval',
            type=float,
            default=2,
            help="The interval between polls. Only relevant polling is enabled"
        )

        args = parser.parse_args()

        account_id = args.config.active_account
        
        api = args.config.create_context()

        latest_price_time = None 

        def poll(latest_price_time):
            """
            Fetch and display all prices since than the latest price time

            Args:
                latest_price_time: The time of the newest Price that has been seen

            Returns:
                The updated latest price time
            """

            response = api.pricing.get(
                account_id,
                instruments=",".join(args.instrument),
                since=latest_price_time,
                includeUnitsAvailable=False
            )

            #
            # Print out all prices newer than the lastest time 
            # seen in a price
            #
            for price in response.get("prices", 200):
                if latest_price_time is None or price.time > latest_price_time:
                    print(price_to_string(price))

            #
            # Stash and return the current latest price time
            #
            for price in response.get("prices", 200):
                if latest_price_time is None or price.time > latest_price_time:
                    latest_price_time = price.time
        
            return latest_price_time

        #
        # Fetch the current snapshot of prices
        #
        latest_price_time = poll(latest_price_time)

        #
        # Poll for of prices
        #
        while args.poll:
            time.sleep(args.poll_interval)
            latest_price_time = poll(latest_price_time)


def main():
    pricing = Pricing()
    print(pricing.get('USD_JPY'))

if __name__ == "__main__":
    main()
