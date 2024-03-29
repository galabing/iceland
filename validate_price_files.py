#!/usr/local/bin/python3

""" Validates price files with some basic rules.
"""

import argparse
import logging
import utils
from os import path

def bad(i):
  return 'Detected bad line at %d' % (i+1)

def validate(input_path):
  with open(input_path, 'r') as fp:
    lines = fp.read().splitlines()
  assert len(lines) > 0
  assert lines[0] == 'Date,Open,High,Low,Close,Volume,Adj Close'
  pd = None
  for i in range(1, len(lines)):
    if lines[i].startswith('#'):
      logging.warning('Line %d is commented out: %s' % (i+1, lines[i]))
      continue
    d, o, h, l, c, v, a = lines[i].split(',')
    if pd is None: pd = d
    else:
      assert pd > d, bad(i)
      # eg, 2013-08-20
      ay, am, ad = pd.split('-')
      by, bm, bd = d.split('-')
      ay, am, ad = int(ay), int(am), int(ad)
      by, bm, bd = int(by), int(bm), int(bd)
      if am != bm:
        if ay == by: assert am - bm <= 2, bad(i)
        else:
          assert ay - by == 1, bad(i)
          assert am + 12 - bm <= 2, bad(i)
      else: assert ay == by
      pd = d
        
    o = float(o)
    h = float(h)
    l = float(l)
    c = float(c)
    v = float(v)
    a = float(a)
    # For EPM.csv, some old lows are 0, probably due to rounding.
    assert l >= 0, bad(i)
    assert l <= h, bad(i)
    assert v >= 0, bad(i)
    # For CNP.csv, some very old adj closes are 0, probably due to rounding.
    assert a >= 0, bad(i)
    # We give a 20% buffer for high, low bounds.
    # A close > high case was found in BA.csv, line 12983.
    assert o <= h * 1.2, bad(i)
    assert c <= h * 1.2, bad(i)
    assert o >= l * 0.8, bad(i)
    assert c >= l * 0.8, bad(i)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--input_dir', required=True)
  parser.add_argument('--from_ticker', default='')
  parser.add_argument('--verbose', action='store_true')
  args = parser.parse_args()

  utils.setup_logging(args.verbose)

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

