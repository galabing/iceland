#!/usr/local/bin/python3

""" Samples adjusted closing price and volume for each month of the input files.
    Fills in holes if a whole month of data is missing, by interpolating
    the adjacent two months' data.  Fails if the hole is bigger than one month.
"""

import argparse
import logging
from os import environ, path
from time import tzset

def print_sample(sample, fp):
  print('%s %.2f %.2f' % (sample[0], sample[1], sample[2]), file=fp)

def distance(ym1, ym2):
  y1, m1 = ym1.split('-')
  y2, m2 = ym2.split('-')
  y1, m1 = int(y1), int(m1)
  y2, m2 = int(y2), int(m2)
  return (y1 - y2) * 12 + m1 - m2

def next(ym):
  y, m = ym.split('-')
  y, m = int(y), int(m)
  if m < 12: return '%04d-%02d' % (y, m+1)
  assert m == 12
  return '%04d-%02d' % (y+1, 1)

def sample(input_path, output_path):
  with open(input_path, 'r') as fp:
    lines = fp.read().splitlines()
  samples = []
  pd, pv, pa = None, None, None
  for i in range(1, len(lines)):
    if lines[i].startswith('#'):
      logging.warning('Skipping line: %s' % lines[i])
      continue
    d, o, h, l, c, v, a = lines[i].split(',')
    m = d[5:7]
    if pd is not None and pd[5:7] != m:
      samples.append((pd[:7], float(pv), float(pa)))
    pd, pv, pa = d, v, a
  samples.append((d[:7], float(v), float(a)))  # Last month.
  with open(output_path, 'w') as fp:
    print_sample(samples[0], fp)
    for i in range(1, len(samples)):
      d = distance(samples[i-1][0], samples[i][0])
      assert d >= 1 and d <= 2
      if d == 2:
        logging.warning('Inserting sample between %s and %s'
                        % (samples[i-1][0], samples[i][0]))
        print_sample((next(samples[i][0]),
                      (samples[i][1] + samples[i-1][1]) * 0.5,
                      (samples[i][2] + samples[i-1][2]) * 0.5), fp)
      print_sample(samples[i], fp)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--input_dir', required=True)
  parser.add_argument('--output_dir', required=True)
  parser.add_argument('--overwrite', action='store_true')
  parser.add_argument('--verbose', action='store_true')
  args = parser.parse_args()

  # Sanity check.
  assert args.input_dir != args.output_dir

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

  for i in range(len(tickers)):
    ticker = tickers[i]
    logging.info('%d/%d: %s' % (i+1, len(tickers), ticker))
    input_path = '%s/%s.csv' % (args.input_dir, ticker.replace('^', '_'))
    if not path.isfile(input_path):
      logging.warning('Input file is missing: %s' % input_path)
      continue
    output_path = '%s/%s.csv' % (args.output_dir, ticker.replace('^', '_'))
    if path.isfile(output_path) and not args.overwrite:
      logging.warning('Output file exists and not overwritable: %s'
                      % output_path)
      continue
    sample(input_path, output_path)

if __name__ == '__main__':
  main()

