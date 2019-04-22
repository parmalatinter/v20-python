#!/usr/bin/env python

from datetime import datetime
import os 


class CandlePrinter(object):
    def __init__(self):
        self.width = {
            'index' : 6,
            'time' : 19,
            'type' : 4,
            'price' : 8,
            'volume' : 6,
            'none' : 0,
        }
        # setattr(self.width, "time", 19)
        self.time_width = 19

    def print_header(self):
        print("{:<{width[time]}} {:<{width[type]}} {:<{width[price]}} {:<{width[price]}} {:<{width[price]}} {:<{width[price]}} {:<{width[volume]}}".format(
            "Time",
            "Type",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            width=self.width
        ))

        print("{} {} {} {} {} {} {}".format(
            "=" * self.width['time'],
            "=" * self.width['type'],
            "=" * self.width['price'],
            "=" * self.width['price'],
            "=" * self.width['price'],
            "=" * self.width['price'],
            "=" * self.width['volume']
        ))

    def print_csv_header(self, file):
        # time,close,open,high,low,volume

        text = '{},{},{},{},{},{},{}\n'.format("index", "time", "close", "open", "high", "low", "volume")

        with open(file, mode='a') as f:
            f.writelines(text)
        
    def print_candle(self, candle):
        try:
            time = str(
                datetime.strptime(
                    candle.time,
                    "%Y-%m-%dT%H:%M:%S.000000000Z"
                )
            )
        except:
            time = candle.time.split(".")[0]

        volume = candle.volume

        for price in ["mid", "bid", "ask"]:
            c = getattr(candle, price, None)

            if c is None:
                continue

            print("{:>{width[time]}} {:>{width[type]}} {:>{width[price]}} {:>{width[price]}} {:>{width[price]}} {:>{width[price]}} {:>{width[volume]}}".format(
                time,
                price,
                c.o,
                c.h,
                c.l,
                c.c,
                volume,
                width=self.width
            ))

            volume = ""
            time = ""

    def export_csv(self, candle, file, index):

            unix = candle.time.split(".")[0]
            try:
                time = datetime.fromtimestamp(int(unix)).strftime('%Y-%m-%d %H:%M:%S')
            except:
                time = candle.time.split(".")[0]

            volume = candle.volume

            for price in ["mid", "bid", "ask"]:
                c = getattr(candle, price, None)

                if c is None:
                    continue
                # ,time,close,open,high,low,volume
                
                text = '{},{},{},{},{},{},{}\n'.format(index, time, c.c, c.o, c.h, c.l, volume)

                with open('/tmp/' + file, mode='a') as f:
                    f.writelines(text)


                volume = ""
                time = ""

