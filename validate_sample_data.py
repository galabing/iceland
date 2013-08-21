#!/usr/local/bin/python3

""" Validates sample data with some basic rules.
"""

import argparse
import logging
from os import environ, path
from time import tzset

def distance(ym1, ym2):
  y1, m1 = ym1.split('-')
  y2, m2 = ym2.split('-')
  y1, m1 = int(y1), int(m1)
  y2, m2 = int(y2), int(m2)
  return (y1 - y2) * 12 + m1 - m2

def bad(i):
  return 'Detected bad line at %d' % (i+1)

def validate(input_path):
  with open(input_path, 'r') as fp:
    lines = fp.read().splitlines()
  assert len(lines) > 0
  pd, pv, pp = lines[0].split(' ')
  pv, pp = float(pv), float(pp)
  assert pv >= 0
  assert pp >= 0
  for i in range(1, len(lines)):
    cd, cv, cp = lines[i].split(' ')
    assert distance(pd, cd) == 1
    cv, cp = float(cv), float(cp)
    assert cv >= 0
    assert cp >= 0
    pd, pv, pp = cd, cv, cp 

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--input_dir', required=True)
  parser.add_argument('--from_ticker', default='')
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
    lines = fp.read().splitlines()
  tickers = []
  for line in lines:
    if line >= args.from_ticker:
      tickers.append(line)
  logging.info('Processing %d tickers' % len(tickers))

  for i in range(len(tickers)):
    ticker = tickers[i]
    logging.info('%d/%d: %s' % (i+1, len(tickers), ticker))
    input_path = '%s/%s.csv' % (args.input_dir, ticker.replace('^', '_'))
    if not path.isfile(input_path):
      logging.warning('Input file does not exist: %s' % input_path)
      continue
    validate(input_path)

if __name__ == '__main__':
  main()

