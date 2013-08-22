#!/usr/local/bin/python3

""" Utilities shared by other scripts.
"""

import logging
from os import environ
from time import tzset

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

def setup_logging(verbose):
  environ['TZ'] = 'US/Pacific'
  tzset()
  level = logging.INFO
  if verbose:
    level = logging.DEBUG
  logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s',
                      level=level)

