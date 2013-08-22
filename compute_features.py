#!/usr/local/bin/python3

""" Computes features:
    - past x months' excess return
    - past y months' excess volume
    Price gains/losses are calculated with a bonus of 0.01 and capped at 100%.
    Volume gains/losses are calculated with a bonus of 1 and capped at 100%.
    Notice that without capping a gain can go infinite while a loss cannot go
    below -100%.

    x and y are arrays from the flag, eg:
    --er_months=1,2,3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48
    --ev_months=1,2,3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48

    This script is intended for batch feature computation without knowing
    which of them will eventually be used. Thus er_months and ev_months should
    be specified as dense as necessary.  The downstream training/testing phases
    will probably sample a few columns as actual features.

    The output will not be a matrix, because early dates may not have x months
    of history, so the features will be keyed by er<x> and ev<y>, and different
    dates may have different numbers of features.  For example:
    2013-08 er1:0.1 ev1:-0.1 er2:0.2 ev2:-0.2
    2013-07 er1:0.1 ev1:-0.1
    Notice that 2013-07 only has one month worth of data (ie, 2013-06 is likely
    the last entry in the sample file).
"""

import argparse
import logging
import utils
from os import path

ER_MONTHS = '1,2,3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48'
EV_MONTHS = '1,2,3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48'
PRICE_BONUS = 0.01
VOLUME_BONUS = 1.0
MIN_CAP = -1.0
MAX_CAP = 1.0

def read_samples(file_path):
  with open(file_path, 'r') as fp:
    lines = fp.read().splitlines()
  d = dict()
  for line in lines:
    dt, vo, pr = line.split(' ')
    vo, pr = float(vo), float(pr)
    d[dt] = (pr, vo)  # The order is switched as we will output er before ev.
  return d

def compute_excess(stock_from, stock_to, market_from, market_to,
                   bonus, min_cap=MIN_CAP, max_cap=MAX_CAP):
  assert stock_from >= 0
  assert stock_to >= 0
  assert market_from >= 0
  assert market_to >= 0
  assert bonus > 0  # bonus must be positive to prevent divide-by-zero errors.
  stock_r = (stock_to - stock_from) / (stock_from + bonus)
  market_r = (market_to - market_from) / (market_from + bonus)
  excess = stock_r - market_r
  if excess > max_cap: return max_cap
  if excess < min_cap: return min_cap
  return excess

# Computes the yyyy-mm string that is delta months before the current yyyy-mm
# string.
def compute_date(current_date, delta):
  y, m = current_date.split('-')
  y, m = int(y), int(m)
  yd = int(delta / 12)
  md = delta % 12
  y -= yd
  m -= md
  if m < 1:
    y -= 1
    m += 12
  return '%04d-%02d' % (y, m)

def compute_features(stock_samples, market_samples, er_months, ev_months,
                     output_path):
  lines = []
  for date_to in sorted(stock_samples.keys(), reverse=True):
    assert date_to in market_samples
    items = []
    for m in er_months:
      date_from = compute_date(date_to, m)
      if date_from not in stock_samples:
        continue
      assert date_from in market_samples
      v = compute_excess(stock_samples[date_from][0],
                         stock_samples[date_to][0],
                         market_samples[date_from][0],
                         market_samples[date_to][0],
                         PRICE_BONUS)
      items.append('er%d:%.4f' % (m, v))
    for m in ev_months:
      date_from = compute_date(date_to, m)
      if date_from not in stock_samples:
        continue
      assert date_from in market_samples
      v = compute_excess(stock_samples[date_from][1],
                         stock_samples[date_to][1],
                         market_samples[date_from][1],
                         market_samples[date_to][1],
                         VOLUME_BONUS)
      items.append('ev%d:%.4f' % (m, v))
    if len(items) == 0:
      lines.append(date_to)
    else:
      lines.append('%s %s' % (date_to, ' '.join(items)))

  with open(output_path, 'w') as fp:
    for line in lines:
      print(line, file=fp)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--sample_dir', required=True)
  parser.add_argument('--market_sample_path', required=True)
  parser.add_argument('--output_dir', required=True)
  parser.add_argument('--er_months', default=ER_MONTHS)
  parser.add_argument('--ev_months', default=EV_MONTHS)
  parser.add_argument('--overwrite', action='store_true')
  parser.add_argument('--verbose', action='store_true')
  args = parser.parse_args()

  utils.setup_logging(args.verbose)

  market_samples = read_samples(args.market_sample_path)
  er_months = [int(m) for m in args.er_months.split(',')]
  ev_months = [int(m) for m in args.ev_months.split(',')]

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
    stock_samples = read_samples(stock_sample_path)
    compute_features(stock_samples, market_samples, er_months, ev_months,
                     output_path)

if __name__ == '__main__':
  main()

