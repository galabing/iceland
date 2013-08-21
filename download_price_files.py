#!/usr/local/bin/python3

""" Downloads csv files of historical stock price from yahoo.com.
"""

import argparse
import logging
from os import environ, path, remove, system
from time import tzset

WGET = '/usr/local/bin/wget'

def download(ticker, output_path):
  url = ('http://ichart.finance.yahoo.com/table.csv?s=%s'
         % ticker.replace('.', '-'))
  cmd = '%s -q "%s" -O %s' % (WGET, url, output_path)
  if system(cmd) != 0:
    logging.warning('Download failed for %s: %s' % (ticker, url))
    if path.isfile(output_path):
      remove(output_path)
    return False
  return True

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--output_dir', required=True)
  parser.add_argument('--overwrite', action='store_true')
  parser.add_argument('--verbose', action='store_true')
  args = parser.parse_args()

  environ['TZ'] = 'US/Pacific'
  tzset()

  level = logging.INFO
  if args.verbose:
    level = logging.DEBUG
  logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s',
                      level=level)

  # Tickers are listed one per line.
  with open(args.ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()
  logging.info('Processing %d tickers' % len(tickers))

  sl, fl = [], []  # Lists of tickers succeeded/failed to download.
  for i in range(len(tickers)):
    ticker = tickers[i]
    logging.info('%d/%d: %s' % (i+1, len(tickers), ticker))

    output_path = '%s/%s.csv' % (args.output_dir, ticker.replace('^', '_'))
    dl = False
    if path.isfile(output_path):
      action = 'skipping'
      if args.overwrite:
        remove(output_path)
        action = 'overwriting'
        dl = True
      logging.warning('Output file exists: %s, %s' % (output_path, action))
    else: dl = True

    if dl:
      ok = download(ticker, output_path)
      if ok: sl.append(ticker)
      else: fl.append(ticker)
  logging.info('Downloaded %d tickers, failed %d tickers'
               % (len(sl), len(fl)))
  logging.info('Downloaded tickers: %s' % sl)
  logging.info('Failed tickers: %s' % fl)

if __name__ == '__main__':
  main()

