#!/usr/local/bin/python3

""" Creates training data for libsvm.
"""

import argparse
import logging
import utils
from os import path

FEATURES = ('er1,er2,er3,er6,er9,er12,er15,er18,er21,er24'
            ',ev1,ev2,ev3,ev6,ev9,ev12,ev15,ev18,ev21,ev24')
LABEL = '1'
MIN_DATE = '0000-00'
MAX_DATE = '9999-99'

def read_data(file_path, min_date, max_date):
  with open(file_path, 'r') as fp:
    lines = fp.read().splitlines()
  d = dict()
  for line in lines:
    items = line.split(' ')
    assert len(items) > 0
    date = items[0]
    if date < min_date or date > max_date: continue
    dd = dict()
    for i in range(1, len(items)):
      k, v = items[i].split(':')
      dd[k] = float(v)
    d[date] = dd
  return d

def make_label(label, regression):
  if regression: return str(label)
  if label > 0: return '+1'
  return '-1'

def create_training_data(feature_path, label_path, features, label,
                         min_date, max_date, regression, fp):
  feature_map = read_data(feature_path, min_date, max_date)
  label_map = read_data(label_path, min_date, max_date)
  count = 0
  for d in sorted(feature_map.keys() & label_map.keys(), reverse=True):
    if label not in label_map[d]: continue
    ok = True
    for f in features:
      if f not in feature_map[d]:
        ok = False
        break
    if not ok: continue
    items = [make_label(label_map[d][label], regression)]
    for i in range(len(features)):
      items.append('%d:%f' % (i+1, feature_map[d][features[i]]))
    print(' '.join(items), file=fp)
    count += 1
  logging.info('%d data points' % count)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--feature_dir', required=True)
  parser.add_argument('--label_dir', required=True)
  parser.add_argument('--output_path', required=True)
  parser.add_argument('--regression', action='store_true')
  parser.add_argument('--features', default=FEATURES)
  parser.add_argument('--label', default=LABEL)
  parser.add_argument('--min_date', default=MIN_DATE)
  parser.add_argument('--max_date', default=MAX_DATE)
  parser.add_argument('--verbose', action='store_true')
  args = parser.parse_args()

  utils.setup_logging(args.verbose)

  # Tickers are listed one per line.
  with open(args.ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()
  logging.info('Processing %d tickers' % len(tickers))

  fp = open(args.output_path, 'w')
  for i in range(len(tickers)):
    ticker = tickers[i]
    assert ticker.find('^') == -1  # ^GSPC should not be in tickers.
    logging.info('%d/%d: %s' % (i+1, len(tickers), ticker))

    feature_path = '%s/%s.txt' % (args.feature_dir, ticker)
    label_path = '%s/%s.txt' % (args.label_dir, ticker)
    has_input = path.isfile(feature_path)
    assert has_input == path.isfile(label_path)
    if not has_input:
      logging.warning('Input files do not exist for %s' % ticker)
      continue
    create_training_data(feature_path, label_path, args.features.split(','),
                         args.label, args.min_date, args.max_date,
                         args.regression, fp)
  fp.close()

if __name__ == '__main__':
  main()

