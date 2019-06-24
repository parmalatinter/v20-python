#!/usr/bin/env python

import argparse
import common.config
import common.args
from instrument.view import CandlePrinter
from datetime import datetime, timedelta
import os 
from pytz import timezone


class Candles():

    def get(self, instrument, granularity='M10'):
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

        for candle in response.get("candles", 200):
            text = printer.get_format_csv(candle,file_name,count)
            res=res + text
            count=count+1

        return res

def main():
    candles = Candles()
    print(candles.get('USD_JPY', 'M10'))

if __name__ == "__main__":
    main()


# import argparse
# import common.config
# import common.args
# from instrument.view import CandlePrinter
# from datetime import datetime
# import os


# def main():
#     """
#     Create an API context, and use it to fetch candles for an instrument.

#     The configuration for the context is parsed from the config file provided
#     as an argumentV
#     """

#     parser = argparse.ArgumentParser()

#     #
#     # The config object is initialized by the argument parser, and contains
#     # the REST APID host, port, accountID, etc.
#     #
#     common.config.add_argument(parser)

#     parser.add_argument(
#         "instrument",
#         type=common.args.instrument,
#         help="The instrument to get candles for"
#     )

#     parser.add_argument(
#         "--mid", 
#         action='store_true',
#         help="Get midpoint-based candles"
#     )

#     parser.add_argument(
#         "--bid", 
#         action='store_true',
#         help="Get bid-based candles"
#     )

#     parser.add_argument(
#         "--ask", 
#         action='store_true',
#         help="Get ask-based candles"
#     )

#     parser.add_argument(
#         "--smooth", 
#         action='store_true',
#         help="'Smooth' the candles"
#     )

#     parser.set_defaults(mid=False, bid=False, ask=False)

#     parser.add_argument(
#         "--granularity",
#         default=None,
#         help="The candles granularity to fetch"
#     )

#     parser.add_argument(
#         "--count",
#         default=None,
#         help="The number of candles to fetch"
#     )

#     date_format = "%Y-%m-%d %H:%M:%S"

#     parser.add_argument(
#         "--from-time",
#         default=None,
#         type=common.args.date_time(),
#         help="The start date for the candles to be fetched. Format is 'YYYY-MM-DD HH:MM:SS'"
#     )

#     parser.add_argument(
#         "--to-time",
#         default=None,
#         type=common.args.date_time(),
#         help="The end date for the candles to be fetched. Format is 'YYYY-MM-DD HH:MM:SS'"
#     )

#     parser.add_argument(
#         "--alignment-timezone",
#         default=None,
#         help="The timezone to used for aligning daily candles"
#     )

#     parser.add_argument(
#         "--file_name",
#         default=None,
#         help="file_name'"
#     )

#     args = parser.parse_args()

#     account_id = args.config.active_account

#     #
#     # The v20 config object creates the v20.Context for us based on the
#     # contents of the config file.
#     #
#     api = args.config.create_context()

#     kwargs = {}

#     if args.granularity is not None:
#         kwargs["granularity"] = args.granularity

#     if args.smooth is not None:
#         kwargs["smooth"] = args.smooth

#     if args.count is not None:
#         kwargs["count"] = args.count

#     if args.from_time is not None:
#         kwargs["fromTime"] = api.datetime_to_str(args.from_time)

#     if args.to_time is not None:
#         kwargs["toTime"] = api.datetime_to_str(args.to_time)

#     if args.alignment_timezone is not None:
#         kwargs["alignmentTimezone"] = args.alignment_timezone

#     price = "mid"

#     if args.mid:
#         kwargs["price"] = "M" + kwargs.get("price", "")
#         price = "mid"

#     if args.bid:
#         kwargs["price"] = "B" + kwargs.get("price", "")
#         price = "bid"

#     if args.ask:
#         kwargs["price"] = "A" + kwargs.get("price", "")
#         price = "ask"

#     #
#     # Fetch the candles
#     #
#     response = api.instrument.candles(args.instrument, **kwargs)

#     if response.status != 200:
#         print(response)
#         print(response.body)
#         return

#     printer = CandlePrinter()

#     file_name = 'candles.csv'
#     if args.file_name is not None:
#        file_name = args.file_name

#     count = 0 
#     res = printer.get_header_format_csv()
#     for candle in response.get("candles", 200):
#         text = printer.get_format_csv(candle,file_name,count)
#         res=res+text
#         count=count+1

#     printer.export_drive(file_name, res)

# if __name__ == "__main__":
#     main()
