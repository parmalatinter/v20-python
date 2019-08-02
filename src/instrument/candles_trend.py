#!/usr/bin/env python

import argparse
import common.config
import common.args
from instrument.view import CandlePrinter
from datetime import datetime, timedelta
import os 
from pytz import timezone


class Candles_trend():

    def get(self):
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
            before_date= datetime.today() + timedelta(hours=-66)

        kwargs = {}
        kwargs["granularity"] = "H6"
        kwargs["fromTime"] = api.datetime_to_str(before_date)

        #
        # Fetch the candles
        #
        response_list = [
            {'key':'EUR_USD', 'value' : None},
            {'key':'USD_JPY', 'value' : None},
            {'key':'USD_CHF', 'value' : None},
            {'key':'GBP_USD', 'value' : None},
            {'key':'AUD_USD', 'value' : None},
            {'key':'USD_CAD', 'value' : None},
            {'key':'NZD_USD', 'value' : None},
            {'key':'EUR_JPY', 'value' : None},
            {'key':'CHF_JPY', 'value' : None},
            {'key':'GBP_JPY', 'value' : None},
            {'key':'AUD_JPY', 'value' : None},
            {'key':'CAD_JPY', 'value' : None},
            {'key':'NZD_JPY', 'value' : None},
            {'key':'GBP_AUD', 'value' : None},
            {'key':'GBP_CAD', 'value' : None},
            {'key':'GBP_NZD', 'value' : None}
        ]

        printer = CandlePrinter()
        file_name = 'trend.csv'

        res = '{},{},{},{},{},{},{},{}\n'.format("instrument", "index", "time", "close", "open", "high", "low", "volume")
        for response in response_list:
            response['value'] = api.instrument.candles(response['key'], **kwargs)
            count = 0 
            if response['value'].status != 200:
                print(response['value'])
                print(response['value'].body)
                return

            for candle in response['value'].get("candles", 200):
                text = printer.get_format_csv(candle,file_name,count)
                res=res+response['key'] + ',' + text
                count=count+1

        return res

def main():
    candles_trend = Candles_trend()
    print(candles_trend.get())

if __name__ == "__main__":
    main()
