#!/usr/local/bin/python3

""" Strips raw data to be libsvm compatible.  This is another way of getting
    libsvm training data (the first would be split_data_for_cv.py).  This one
    does not split the data; it only strips the ticker and date from each line
    and writes them to a separate index file.
"""

import argparse
import logging
import utils

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--input_path', required=True)
  parser.add_argument('--output_data_path', required=True)
  parser.add_argument('--output_index_path', required=True)
  parser.add_argument('--verbose', action='store_true')
  args = parser.parse_args()

  utils.setup_logging(args.verbose)

  with open(args.input_path, 'r') as fp:
    lines = fp.read().splitlines()

  # This block below is to keep the output data in sync with the ones
  # produced by split_data_for_cv.py.  I.e. the date and ticker of each
  # input line are swapped (such that date goes before ticker), and the
  # lines are sorted (by date and then by ticker).

  # Swap date and ticker in place.
  item_count = -1
  for i in range(len(lines)):
    items = lines[i].split(' ')
    if item_count < 0: item_count = len(items)
    else: assert item_count == len(items)
    items[0], items[1] = items[1], items[0]
    lines[i] = ' '.join(items)
  # This will sort lines by entry and then ticker.
  lines.sort()

  data_fp = open(args.output_data_path, 'w')
  index_fp = open(args.output_index_path, 'w')
  for line in lines:
    items = line.split(' ')
    assert len(items) > 3
    data = '%s %s' % (utils.make_label(float(items[2]), False),
                      ' '.join(items[3:]))
    index = ' '.join(items[:2])
    print(data, file=data_fp)
    print(index, file=index_fp)

  data_fp.close()
  index_fp.close()

if __name__ == '__main__':
  main()

