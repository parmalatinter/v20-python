#!/usr/bin/env python

import argparse
import common.config
import common.args
from instrument.view import CandlePrinter
from datetime import datetime, timedelta
import os 
from pytz import timezone


class Candle():

    candles = None
    last_candle = None

    def get(self, instrument, granularity='M1'):
        """
        Create an API context, and use it to fetch candles for an instrument.

        The configuration for the context is parsed from the config file provided
        as an argumentV
        """

        parser = argparse.ArgumentParser()

        #
        # The config object is initialized by the argument parser, and contains
        # the REST APID host, port, accountID, etc.
        #
        common.config.add_argument(parser)

        args = parser.parse_args()

        account_id = args.config.active_account

        #
        # The v20 config object creates the v20.Context for us based on the
        # contents of the config file.
        #
        api = args.config.create_context()

        os.environ['TZ'] = 'America/New_York'
        before_date= datetime.today() + timedelta(hours=-24)

        weekday = before_date.weekday()

        if(weekday > 5):
            before_date= datetime.today() + timedelta(hours=-84)

        kwargs = {}
        kwargs["granularity"] =granularity
        kwargs["fromTime"] = api.datetime_to_str(before_date)

        printer = CandlePrinter()
        file_name = 'candles.csv'

        res = '{},{},{},{},{},{},{}\n'.format("index", "time", "close", "open", "high", "low", "volume")

        response = api.instrument.candles(instrument, **kwargs)
        count = 0 
        if response.status != 200:
            print(response)
            print(response.body)
            return

        self.candles = response.get("candles", 200)
        self.last_candle = self.candles[0]
        print(self.candles.__dict__)

        return self.last_candle

    def get_last_rate(self):
        return float(self.last_candle.mid.c)

def main():
    candle = Candle()
    candle.get('USD_JPY', 'M10')
    print(candle.get_last_rate())

if __name__ == "__main__":
    main()
