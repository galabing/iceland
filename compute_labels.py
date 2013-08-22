#!/usr/local/bin/python3

""" Computes labels, which are the excess return over the next n months.
    This script is similar to compute_features.py, where the purpose is to
    do a batch computation.  The downstream training script will probably
    pick a subset of the labels generated.
"""

import argparse
import logging
import utils
from os import path

MONTHS = '1,2,3,6,9,12,15,18,21,24'
PRICE_BONUS = 0.01

# Computes the yyyy-mm string that is delta months after the current yyyy-mm
# string.
def compute_date(current_date, delta):
  y, m = current_date.split('-')
  y, m = int(y), int(m)
  yd = int(delta / 12)
  md = delta % 12
  y += yd
  m += md
  if m > 12:
    y += 1
    m -= 12
  return '%04d-%02d' % (y, m)

def compute_labels(stock_samples, market_samples, months, output_path):
  lines = []
  for date_from in sorted(stock_samples.keys(), reverse=True):
    assert date_from in market_samples
    items = []
    for m in months:
      date_to = compute_date(date_from, m)
      if date_to not in stock_samples:
        continue
      assert date_to in market_samples
      v = utils.compute_excess(stock_samples[date_from][0],
                               stock_samples[date_to][0],
                               market_samples[date_from][0],
                               market_samples[date_to][0],
                               PRICE_BONUS)
      items.append('%d:%.4f' % (m, v))
    if len(items) == 0:
      lines.append(date_from)
    else:
      lines.append('%s %s' % (date_from, ' '.join(items)))

  with open(output_path, 'w') as fp:
    for line in lines:
      print(line, file=fp)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--sample_dir', required=True)
  parser.add_argument('--market_sample_path', required=True)
  parser.add_argument('--output_dir', required=True)
  parser.add_argument('--months', default=MONTHS)
  parser.add_argument('--overwrite', action='store_true')
  parser.add_argument('--verbose', action='store_true')
  args = parser.parse_args()

  utils.setup_logging(args.verbose)

  market_samples = utils.read_samples(args.market_sample_path)
  months = [int(m) for m in args.months.split(',')]

  # Tickers are listed one per line.
  with open(args.ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()
  logging.info('Processing %d tickers' % len(tickers))

  for i in range(len(tickers)):
    ticker = tickers[i]
    assert ticker.find('^') == -1  # ^GSPC should not be in tickers.
    logging.info('%d/%d: %s' % (i+1, len(tickers), ticker))
    stock_sample_path = '%s/%s.csv' % (args.sample_dir, ticker)
    if not path.isfile(stock_sample_path):
      logging.warning('Input file does not exist: %s' % stock_sample_path)
      continue
    # The output format is no longer csv.  Use txt instead.
    output_path = '%s/%s.txt' % (args.output_dir, ticker)
    if path.isfile(output_path) and not args.overwrite:
      logging.warning('Output file exists: %s, skipping' % output_path)
      continue
    stock_samples = utils.read_samples(stock_sample_path)
    compute_labels(stock_samples, market_samples, months, output_path)

if __name__ == '__main__':
  main()

