#!/usr/bin/env python

import argparse
import common.config
import common.args
from datetime import datetime, timedelta
import os 
from pytz import timezone
import strategy.environ

class Candle():

    candles = None
    last_candle = None
    time = None

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
        before_date= datetime.today() + timedelta(hours=-9.1)

        weekday = before_date.weekday()

        kwargs = {}
        kwargs["granularity"] =granularity
        kwargs["fromTime"] = api.datetime_to_str(before_date)

        response = api.instrument.candles(instrument, **kwargs)
        count = 0 
        if response.status != 200:
            print(response)
            print(response.body)
            return

        self.candles = response.get("candles", 200)
        self.last_candle = self.candles[-1]
        unix = self.last_candle.time.split(".")[0]
        try:
            self.time = datetime.strptime(unix.replace('T', ' '), '%Y-%m-%d %H:%M:%S')
        except:
            self.time = datetime.fromtimestamp(int(unix))

        return self.last_candle

    def get_last_rate(self):
        return float(self.last_candle.mid.c)

    def get_last_date(self):
        return self.time

def main():
    candle = Candle()
    environ = strategy.environ.Environ()
    instrument = environ.get('instrument') if environ.get('instrument') else 'USD_JPY'
    candle.get(instrument, 'M10')
    print(candle.get_last_rate())
    print(candle.get_last_date())

if __name__ == "__main__":
    main()
