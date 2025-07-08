from datetime import datetime, timedelta
from polygon import RESTClient
from time import sleep
from os import getenv
import argparse
import csv

DATE_FORMAT = "%Y-%m-%d"

def fetch_for_date(ticker, start_date, end_date, dirname=None):
    sstring = datetime.strftime(start_date, DATE_FORMAT)
    dstring = datetime.strftime(end_date, DATE_FORMAT)
    fname = "{0}-{1}-{2}.csv".format(ticker, sstring, dstring)

    if dirname != None:
        fname = dirname + '/' + fname

    with open(fname, 'w', newline='') as csvfile:
        ohlcwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

        for a in client.list_aggs(ticker, 1, "day", sstring, dstring):

            current = []
            current_time = datetime.fromtimestamp(a.timestamp / 1000)
            current.append(datetime.strftime(current_time, DATE_FORMAT))
            current.append(a.open)
            current.append(a.high)
            current.append(a.low)
            current.append(a.close)
            current.append(a.volume)

            ohlcwriter.writerow(current)

opts = argparse.ArgumentParser(
    prog='datatest',
    description='blah',
)

opts.add_argument('-sd', '--start-date', help="The starting date to fetch range data for")
opts.add_argument('-ed', '--end-date', help="The ending date to fetch range data for")
opts.add_argument('-od', '--output-dir', help="The directory to write range data to")
opts.add_argument('-t', '--ticker', help="The ticker to fetch data for")
args = opts.parse_args()

client = RESTClient(getenv("POLYGON_KEY"))

if args.start_date and args.end_date:
    current = datetime.strptime(args.start_date, '%Y-%m-%d')
    done = datetime.strptime(args.end_date, '%Y-%m-%d')
    fetch_for_date(args.ticker, current, done, args.output_dir)
