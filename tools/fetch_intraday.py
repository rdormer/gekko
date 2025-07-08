from datetime import datetime, timedelta
from polygon import RESTClient
from time import sleep
from os import getenv
import argparse
import csv

def fetch_for_date(ticker, target_date, dirname=None):
    dstring = datetime.strftime(target_date, "%Y-%m-%d")
    fname = "{0}-{1}.csv".format(ticker, dstring)

    if dirname != None:
        fname = dirname + '/' + fname

    with open(fname, 'w', newline='') as csvfile:
        ohlcwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

        for a in client.list_aggs(ticker, 1, "minute", dstring, dstring):
            current_time = datetime.fromtimestamp(a.timestamp / 1000)
            if (current_time.hour < 16 and current_time.hour > 9) or (current_time.hour == 9 and current_time.minute >= 30):
                current = []
                current.append(int(a.timestamp / 1000))
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
opts.add_argument('-d', '--date', help="The single date to fetch data for (YYY-MM-DD)")
opts.add_argument('-t', '--ticker', help="The ticker to fetch data for")
args = opts.parse_args()

client = RESTClient(getenv("POLYGON_KEY"))

if args.start_date and args.end_date:
    current = datetime.strptime(args.start_date, '%Y-%m-%d')
    done = datetime.strptime(args.end_date, '%Y-%m-%d')

    while current <= done:
        sleep(13)
        fetch_for_date(args.ticker, current, args.output_dir)
        current += timedelta(days=1)
else:
    current = datetime.strptime(args.date, '%Y-%m-%d')
    fetch_for_date(args.ticker, current, args.output_dir)
