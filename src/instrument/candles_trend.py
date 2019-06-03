#!/usr/bin/env python

import argparse
import common.config
import common.args
from instrument.view import CandlePrinter
from datetime import datetime, timedelta
import os 
from pytz import timezone


def main():
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

    parser.add_argument(
        "--mid", 
        action='store_true',
        help="Get midpoint-based candles"
    )

    parser.add_argument(
        "--bid", 
        action='store_true',
        help="Get bid-based candles"
    )

    parser.add_argument(
        "--ask", 
        action='store_true',
        help="Get ask-based candles"
    )

    parser.add_argument(
        "--smooth", 
        action='store_true',
        help="'Smooth' the candles"
    )

    parser.set_defaults(mid=False, bid=False, ask=False)

    parser.add_argument(
        "--count",
        default=None,
        help="The number of candles to fetch"
    )

    date_format = "%Y-%m-%d %H:%M:%S"

    parser.add_argument(
        "--from-time",
        default=None,
        type=common.args.date_time(),
        help="The start date for the candles to be fetched. Format is 'YYYY-MM-DD HH:MM:SS'"
    )

    parser.add_argument(
        "--to-time",
        default=None,
        type=common.args.date_time(),
        help="The end date for the candles to be fetched. Format is 'YYYY-MM-DD HH:MM:SS'"
    )

    parser.add_argument(
        "--alignment-timezone",
        default=None,
        help="The timezone to used for aligning daily candles"
    )

    parser.add_argument(
        "--file_name",
        default=None,
        help="file_name'"
    )

    args = parser.parse_args()

    account_id = args.config.active_account

    #
    # The v20 config object creates the v20.Context for us based on the
    # contents of the config file.
    #
    api = args.config.create_context()

    os.environ['TZ'] = 'America/New_York'
    before_date= datetime.today() + timedelta(hours=-24)
    before = before_date.strftime('%Y-%m-%d %H:%M:%S')

    weekday = before_date.weekday()
    if(weekday > 5):
        diff = weekday - 3
        before_date= datetime.today() + timedelta(hours=(-24*diff))

    kwargs = {}

    kwargs["granularity"] = "H12"
    kwargs["fromTime"] = api.datetime_to_str(before_date)

    if args.smooth is not None:
        kwargs["smooth"] = args.smooth

    if args.count is not None:
        kwargs["count"] = args.count

    if args.to_time is not None:
        kwargs["toTime"] = api.datetime_to_str(args.to_time)

    if args.alignment_timezone is not None:
        kwargs["alignmentTimezone"] = args.alignment_timezone

    price = "mid"

    if args.mid:
        kwargs["price"] = "M" + kwargs.get("price", "")
        price = "mid"

    if args.bid:
        kwargs["price"] = "B" + kwargs.get("price", "")
        price = "bid"

    if args.ask:
        kwargs["price"] = "A" + kwargs.get("price", "")
        price = "ask"

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
        {'key':'NZD_JPY', 'value' : None}
    ]

    printer = CandlePrinter()
    file_name = 'trend.csv'
    if args.file_name is not None:
       file_name = args.file_name

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

    printer.export_drive(file_name, res)
    

if __name__ == "__main__":
    main()
